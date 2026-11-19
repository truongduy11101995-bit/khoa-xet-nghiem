import datetime
import calendar
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from backend.database import get_db
from backend.auth import get_current_user, require_admin
from backend.models import LeaveCreateRequest, LeaveReviewRequest

router = APIRouter(prefix="/api/leave", tags=["Leave Calendar"])

def get_leave_balances_helper(cursor, year: int, current_user_id: int):
    start_date = f"{year:04d}-01-01"
    end_date = f"{year:04d}-12-31"

    cursor.execute("""
        SELECT id, username, full_name, title, role
        FROM users
        WHERE status = 'active'
        ORDER BY id ASC
    """)
    users_list = [dict(u) for u in cursor.fetchall()]

    balances = []
    my_balance = None

    for u in users_list:
        u_id = u["id"]
        cursor.execute("""
            SELECT shift, status
            FROM leave_requests
            WHERE user_id = ?
              AND leave_type = 'phep_nam'
              AND leave_date >= ? AND leave_date <= ?
              AND status != 'rejected'
        """, (u_id, start_date, end_date))

        l_rows = cursor.fetchall()
        used_approved = 0.0
        used_pending = 0.0

        for lr in l_rows:
            d = dict(lr)
            day_val = 1.0 if d.get("shift") == "all" else 0.5
            if d.get("status") == "approved":
                used_approved += day_val
            elif d.get("status") == "pending":
                used_pending += day_val

        total_entitled = 12.0
        remaining = max(0.0, total_entitled - used_approved)

        bal = {
            "user_id": u_id,
            "username": u["username"],
            "full_name": u["full_name"],
            "title": u["title"],
            "role": u["role"],
            "total_entitled": total_entitled,
            "used_approved": used_approved,
            "used_pending": used_pending,
            "remaining_days": remaining,
            "percent_used": round((used_approved / total_entitled) * 100, 1)
        }
        balances.append(bal)

        if u_id == current_user_id:
            my_balance = bal

    return balances, my_balance

@router.get("/balances")
def get_leave_balances(
    year: Optional[int] = None,
    user: dict = Depends(get_current_user)
):
    """
    Get annual leave balances for all active staff (12 days quota per year).
    """
    if not year:
        year = datetime.date.today().year

    conn = get_db()
    cursor = conn.cursor()
    balances, my_balance = get_leave_balances_helper(cursor, year, user["id"])
    conn.close()

    return {
        "success": True,
        "year": year,
        "default_quota": 12.0,
        "balances": balances,
        "my_balance": my_balance
    }

@router.get("/calendar")
def get_leave_calendar(
    year: Optional[int] = None,
    month: Optional[int] = None,
    user: dict = Depends(get_current_user)
):
    """
    Get full calendar view for a given month with smart conflict detection.
    If >= 2 staff request leave on the same date, is_warning is True (red alert).
    """
    today = datetime.date.today()
    if not year:
        year = today.year
    if not month:
        month = today.month

    # Calculate month range
    num_days = calendar.monthrange(year, month)[1]
    start_date = f"{year:04d}-{month:02d}-01"
    end_date = f"{year:04d}-{month:02d}-{num_days:02d}"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.id, l.user_id, l.leave_date, l.leave_type, l.shift, l.reason,
               l.status, l.review_note, l.created_at,
               u.username, u.full_name, u.title as user_title, u.role as user_role,
               reviewer.full_name as reviewer_name
        FROM leave_requests l
        JOIN users u ON l.user_id = u.id
        LEFT JOIN users reviewer ON l.reviewed_by = reviewer.id
        WHERE l.leave_date >= ? AND l.leave_date <= ?
        ORDER BY l.leave_date ASC, l.created_at ASC
    """, (start_date, end_date))
    rows = [dict(r) for r in cursor.fetchall()]

    # Leave Balances for 12 days quota per year
    balances, my_balance = get_leave_balances_helper(cursor, year, user["id"])
    conn.close()

    # Group by date
    days_data = {}
    for d in range(1, num_days + 1):
        date_str = f"{year:04d}-{month:02d}-{d:02d}"
        days_data[date_str] = {
            "date": date_str,
            "day": d,
            "leaves": [],
            "leave_count": 0,
            "has_warning": False,
            "warning_message": ""
        }

    for item in rows:
        d_str = item["leave_date"]
        if d_str in days_data:
            days_data[d_str]["leaves"].append(item)
            # Count active or pending leaves for staffing safety
            days_data[d_str]["leave_count"] += 1

    # Apply smart warning: >= 2 staff on leave on the same date
    warning_dates_count = 0
    for d_str, data in days_data.items():
        if data["leave_count"] >= 2:
            data["has_warning"] = True
            names = [l["full_name"] for l in data["leaves"]]
            data["warning_message"] = (
                f"CẢNH BÁO NHÂN SỰ: Có {data['leave_count']} nhân viên đăng ký nghỉ ngày này ({', '.join(names)}). "
                f"Vui lòng cân đối người thay thế tại 4 bàn lấy máu và phòng máy!"
            )
            warning_dates_count += 1

    # First day weekday (0 = Monday, 6 = Sunday)
    first_weekday = datetime.date(year, month, 1).weekday()

    return {
        "success": True,
        "year": year,
        "month": month,
        "num_days": num_days,
        "first_weekday": first_weekday,
        "days": days_data,
        "warning_dates_count": warning_dates_count,
        "current_user_id": user["id"],
        "is_admin": user.get("role") in ("truong_khoa", "ktv_truong"),
        "balances": balances,
        "my_balance": my_balance
    }

@router.post("/request")
def create_leave_request(
    req: LeaveCreateRequest,
    target_user_id: Optional[int] = Query(None, description="Optional user_id if admin registers for staff"),
    user: dict = Depends(get_current_user)
):
    """
    Submit a leave request.
    Normal staff register for themselves.
    Admin (Trưởng khoa / KTV Trưởng) can also register on behalf of staff.
    """
    actual_user_id = user["id"]
    if target_user_id and user.get("role") in ("truong_khoa", "ktv_truong"):
        actual_user_id = target_user_id

    conn = get_db()
    cursor = conn.cursor()

    # Check remaining annual leave if applying for 'phep_nam' (12 days quota per year)
    req_year = int(req.leave_date.split("-")[0])
    if req.leave_type == "phep_nam":
        req_days = 1.0 if req.shift == "all" else 0.5
        cursor.execute("""
            SELECT shift, status
            FROM leave_requests
            WHERE user_id = ?
              AND leave_type = 'phep_nam'
              AND leave_date >= ? AND leave_date <= ?
              AND status = 'approved'
        """, (actual_user_id, f"{req_year}-01-01", f"{req_year}-12-31"))
        approved_rows = cursor.fetchall()
        used_phep = sum(1.0 if dict(r).get("shift") == "all" else 0.5 for r in approved_rows)
        remaining_phep = max(0.0, 12.0 - used_phep)

        if remaining_phep < req_days:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Số ngày phép năm còn lại không đủ ({remaining_phep} ngày / định mức 12 ngày). Bạn đang xin {req_days} ngày. Vui lòng chọn 'Nghỉ bù' hoặc 'Việc riêng'."
            )

    # Check for duplicate registration on same date and shift
    cursor.execute("""
        SELECT id FROM leave_requests
        WHERE user_id = ? AND leave_date = ? AND (shift = ? OR shift = 'all' OR ? = 'all')
    """, (actual_user_id, req.leave_date, req.shift, req.shift))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Bạn đã đăng ký xin nghỉ vào ngày/ca này rồi."
        )

    # Check how many people already registered on this date
    cursor.execute("""
        SELECT COUNT(*) FROM leave_requests
        WHERE leave_date = ? AND status != 'rejected'
    """, (req.leave_date,))
    existing_count = cursor.fetchone()[0]

    # Auto-approve if created by Trưởng khoa or KTV Trưởng for themselves
    initial_status = "approved" if user.get("role") in ("truong_khoa", "ktv_truong") and not target_user_id else "pending"
    reviewed_by = user["id"] if initial_status == "approved" else None

    cursor.execute("""
        INSERT INTO leave_requests (
            user_id, leave_date, leave_type, shift, reason, status, reviewed_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (actual_user_id, req.leave_date, req.leave_type, req.shift, req.reason.strip(), initial_status, reviewed_by))

    req_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'LEAVE_REQUEST', ?)
    """, (user["id"], f"Đăng ký nghỉ ngày {req.leave_date} ({req.leave_type})"))

    conn.commit()
    conn.close()

    warning_alert = None
    if existing_count >= 1:
        warning_alert = (
            f"Lưu ý: Ngày {req.leave_date} hiện đã có tổng cộng {existing_count + 1} nhân viên đăng ký nghỉ. "
            f"Hệ thống đã kích hoạt Cảnh báo cân đối nhân lực cho Trưởng khoa / KTV Trưởng."
        )

    return {
        "success": True,
        "leave_id": req_id,
        "status": initial_status,
        "message": "Đăng ký nghỉ phép thành công!" if not warning_alert else warning_alert,
        "has_staff_warning": existing_count >= 1
    }

@router.get("/all-requests")
def get_all_leave_requests(
    status_filter: Optional[str] = Query("all", description="all, pending, approved, rejected"),
    year: Optional[int] = None,
    admin: dict = Depends(require_admin)
):
    """
    Get all leave requests across the department for Trưởng khoa or KTV Trưởng.
    Includes applicant info, current remaining leave quota, and status.
    """
    if not year:
        year = datetime.date.today().year

    conn = get_db()
    cursor = conn.cursor()

    # Get balances for all users in this year
    balances, _ = get_leave_balances_helper(cursor, year, admin["id"])
    bal_map = {b["user_id"]: b for b in balances}

    sql = """
        SELECT l.*, u.username, u.full_name, u.title as user_title, u.role as user_role,
               reviewer.full_name as reviewer_name
        FROM leave_requests l
        JOIN users u ON l.user_id = u.id
        LEFT JOIN users reviewer ON l.reviewed_by = reviewer.id
    """
    params = []
    conditions = []

    if status_filter and status_filter != "all":
        conditions.append("l.status = ?")
        params.append(status_filter)

    if year:
        conditions.append("l.leave_date >= ? AND l.leave_date <= ?")
        params.extend([f"{year:04d}-01-01", f"{year:04d}-12-31"])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY CASE WHEN l.status = 'pending' THEN 0 ELSE 1 END, l.leave_date DESC, l.id DESC"

    cursor.execute(sql, tuple(params))
    rows = [dict(r) for r in cursor.fetchall()]

    for r in rows:
        u_id = r["user_id"]
        bal = bal_map.get(u_id, {
            "total_entitled": 12.0,
            "used_approved": 0.0,
            "used_pending": 0.0,
            "remaining_days": 12.0
        })
        r["total_entitled"] = bal["total_entitled"]
        r["used_approved"] = bal["used_approved"]
        r["used_pending"] = bal["used_pending"]
        r["remaining_days"] = bal["remaining_days"]
        r["day_deduction"] = 1.0 if r.get("shift") == "all" else 0.5

    conn.close()
    return {"success": True, "requests": rows}

@router.post("/{leave_id}/review")
def review_leave_request(
    leave_id: int,
    req: LeaveReviewRequest,
    admin: dict = Depends(require_admin)
):
    """
    Trưởng khoa or KTV Trưởng approves or rejects leave.
    When approving a 'phep_nam' leave, automatically deducts the leave days from staff's quota (12 days total).
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (leave_id,))
    leave = cursor.fetchone()
    if not leave:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn đăng ký nghỉ phép.")

    leave_dict = dict(leave)
    user_id = leave_dict["user_id"]
    leave_date = leave_dict["leave_date"]
    leave_type = leave_dict["leave_type"]
    shift = leave_dict["shift"]
    day_val = 1.0 if shift == "all" else 0.5
    leave_year = int(leave_date.split("-")[0])

    # If approving a 'phep_nam' request, verify that remaining quota is sufficient
    if req.status == "approved" and leave_type == "phep_nam":
        cursor.execute("""
            SELECT shift, status
            FROM leave_requests
            WHERE user_id = ?
              AND leave_type = 'phep_nam'
              AND leave_date >= ? AND leave_date <= ?
              AND status = 'approved'
              AND id != ?
        """, (user_id, f"{leave_year}-01-01", f"{leave_year}-12-31", leave_id))
        app_rows = cursor.fetchall()
        already_used = sum(1.0 if dict(r).get("shift") == "all" else 0.5 for r in app_rows)
        remaining_before = max(0.0, 12.0 - already_used)

        if remaining_before < day_val:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Không thể phê duyệt: Cán bộ này chỉ còn {remaining_before} ngày phép năm, không đủ trừ {day_val} ngày!"
            )

    cursor.execute("""
        UPDATE leave_requests
        SET status = ?, reviewed_by = ?, review_note = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (req.status, admin["id"], req.review_note, leave_id))

    action_text = "Phê duyệt nghỉ phép (Đã trừ phép)" if req.status == "approved" else "Từ chối nghỉ phép"
    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'LEAVE_REVIEW', ?)
    """, (admin["id"], f"{action_text} cho đơn #{leave_id} ngày {leave_date} (Người duyệt: {admin['full_name']})"))

    # Calculate new remaining days for annual leave
    new_remaining = None
    if leave_type == "phep_nam":
        cursor.execute("""
            SELECT shift, status
            FROM leave_requests
            WHERE user_id = ?
              AND leave_type = 'phep_nam'
              AND leave_date >= ? AND leave_date <= ?
              AND status = 'approved'
        """, (user_id, f"{leave_year}-01-01", f"{leave_year}-12-31"))
        app_rows = cursor.fetchall()
        tot_used = sum(1.0 if dict(r).get("shift") == "all" else 0.5 for r in app_rows)
        new_remaining = max(0.0, 12.0 - tot_used)

    conn.commit()
    conn.close()

    status_vn = "ĐÃ PHÊ DUYỆT" if req.status == "approved" else "TỪ CHỐI"
    msg = f"Đơn đăng ký #{leave_id} đã được {status_vn} bởi {admin['full_name']}."
    if req.status == "approved" and leave_type == "phep_nam":
        msg += f" Đã trừ {day_val} ngày phép năm. Số phép năm còn lại của nhân viên: {new_remaining} / 12 ngày."

    return {
        "success": True,
        "message": msg,
        "status": req.status,
        "days_deducted": day_val if (req.status == "approved" and leave_type == "phep_nam") else 0,
        "remaining_days": new_remaining
    }

@router.delete("/{leave_id}")
def cancel_leave_request(
    leave_id: int,
    user: dict = Depends(get_current_user)
):
    """User can cancel their own pending request; Admin can delete any request."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leave_requests WHERE id = ?", (leave_id,))
    leave = cursor.fetchone()

    if not leave:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn đăng ký nghỉ phép.")

    is_owner = leave["user_id"] == user["id"]
    is_admin = user.get("role") in ("truong_khoa", "ktv_truong")

    if not (is_owner or is_admin):
        conn.close()
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa đơn này.")

    cursor.execute("DELETE FROM leave_requests WHERE id = ?", (leave_id,))
    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'LEAVE_CANCEL', ?)
    """, (user["id"], f"Hủy đơn nghỉ phép #{leave_id}"))

    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã hủy đơn đăng ký nghỉ thành công."}

@router.get("/{leave_id}/print-data")
def get_leave_print_data(
    leave_id: int,
    user: dict = Depends(get_current_user)
):
    """Get full details formatted for printing the official hospital leave application."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, u.full_name, u.phone, u.title as user_title,
               reviewer.full_name as reviewer_name
        FROM leave_requests l
        JOIN users u ON l.user_id = u.id
        LEFT JOIN users reviewer ON l.reviewed_by = reviewer.id
        WHERE l.id = ?
    """, (leave_id,))
    leave = cursor.fetchone()

    if not leave:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn xin nghỉ phép.")

    d = dict(leave)
    leave_dt = datetime.datetime.strptime(d["leave_date"], "%Y-%m-%d").date()
    leave_year = leave_dt.year

    # Annual leave quota & usage calculation
    cursor.execute("""
        SELECT shift, status
        FROM leave_requests
        WHERE user_id = ?
          AND leave_type = 'phep_nam'
          AND leave_date >= ? AND leave_date <= ?
          AND status = 'approved'
    """, (d["user_id"], f"{leave_year}-01-01", f"{leave_year}-12-31"))
    app_rows = cursor.fetchall()
    used_annual = sum(1.0 if dict(r).get("shift") == "all" else 0.5 for r in app_rows)
    total_quota = 12.0
    remaining_annual = max(0.0, total_quota - used_annual)

    conn.close()

    # Permissions: owner or admin
    is_owner = leave["user_id"] == user["id"]
    is_admin = user.get("role") in ("truong_khoa", "ktv_truong")
    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Không có quyền in đơn của người khác.")

    today = datetime.date.today()
    shift_val = d.get("shift", "all")
    leave_day_str = leave_dt.strftime("%d/%m/%Y")
    l_type = d.get("leave_type", "phep_nam")

    type_suffix = ""
    if l_type == "phep_cuoi":
        type_suffix = " (Phép cưới / Kết hôn)"
    elif l_type == "nghi_bu":
        type_suffix = " (Nghỉ bù)"
    elif l_type == "di_hoc":
        type_suffix = " (Đi học / Tập huấn)"

    if shift_val == "all":
        shift_text = f"Cả ngày (07h00 - 11h00 & 13h00 - 17h00){type_suffix}"
        duration_text = f"01 ngày{type_suffix}, ngày {leave_day_str} (Từ 07h00 - 11h00 và 13h00 - 17h00)"
    elif shift_val == "sang":
        shift_text = f"Buổi sáng (07h00 - 11h00){type_suffix}"
        duration_text = f"0.5 ngày (Buổi sáng: 07h00 - 11h00){type_suffix}, ngày {leave_day_str}"
    else:
        shift_text = f"Buổi chiều (13h00 - 17h00){type_suffix}"
        duration_text = f"0.5 ngày (Buổi chiều: 13h00 - 17h00){type_suffix}, ngày {leave_day_str}"

    assigned_manager = d.get("reviewer_name") if d.get("reviewer_name") else "CN. Lê Đình Tú"

    return {
        "success": True,
        "print_data": {
            "id": d["id"],
            "full_name": d["full_name"],
            "phone": "0911761707",
            "department": "Khoa Xét Nghiệm",
            "leave_type": d["leave_type"],
            "shift": d["shift"],
            "shift_text": shift_text,
            "duration_text": duration_text,
            "leave_date_formatted": leave_dt.strftime("%d/%m/%Y"),
            "reason": d["reason"],
            "status": d["status"],
            "annual_leave_quota": total_quota,
            "annual_leave_used": used_annual,
            "annual_leave_remaining": remaining_annual,
            "today_day": f"{today.day:02d}",
            "today_month": f"{today.month:02d}",
            "today_year": f"{today.year}",
            "manager_name": assigned_manager,
            "manager_phone": "0911761707"
        }
    }

@router.get("/my-history")
def get_my_leave_history(
    user: dict = Depends(get_current_user)
):
    """Get current user's leave requests."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, reviewer.full_name as reviewer_name
        FROM leave_requests l
        LEFT JOIN users reviewer ON l.reviewed_by = reviewer.id
        WHERE l.user_id = ?
        ORDER BY l.leave_date DESC
    """, (user["id"],))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"success": True, "leaves": rows}
