import datetime
import io
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from backend.database import get_db
from backend.auth import get_current_user, require_admin
from backend.models import ScheduleAssignRequest, ScheduleBatchAssignRequest
from backend.config import HOSPITAL_NAME, DEPARTMENT_NAME

router = APIRouter(prefix="/api/schedule", tags=["Schedule & Positions"])

@router.get("/positions")
def get_positions(user: dict = Depends(get_current_user)):
    """List all positions ordered by sort_order and categorized."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, code, name, category, description, sort_order
        FROM positions
        ORDER BY sort_order ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"success": True, "positions": rows}

@router.get("/users")
def get_staff_for_schedule(user: dict = Depends(get_current_user)):
    """List active staff members for assignment."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, full_name, title, role
        FROM users
        WHERE status = 'active'
        ORDER BY id ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"success": True, "users": rows}

@router.get("/daily")
def get_daily_schedule(
    date: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get schedule for a specific date (defaults to today)."""
    if not date:
        date = datetime.date.today().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.work_date, s.shift, s.note,
               p.id as position_id, p.code as position_code, p.name as position_name, p.category as position_category,
               u.id as user_id, u.username, u.full_name, u.title as user_title
        FROM positions p
        LEFT JOIN schedules s ON s.position_id = p.id AND s.work_date = ?
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY p.sort_order ASC, s.shift ASC
    """, (date,))

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {
        "success": True,
        "date": date,
        "assignments": rows,
        "current_user_id": user["id"]
    }

@router.get("/weekly")
def get_weekly_schedule(
    start_date: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """
    Get 7-day schedule grid starting from start_date (defaults to Monday of current week).
    """
    if not start_date:
        today = datetime.date.today()
        # Find Monday of this week
        monday = today - datetime.timedelta(days=today.weekday())
        start_date = monday.strftime("%Y-%m-%d")

    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    week_dates = [(start_dt + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    end_date = week_dates[-1]

    conn = get_db()
    cursor = conn.cursor()

    # Get all positions
    cursor.execute("SELECT * FROM positions ORDER BY sort_order ASC")
    positions = [dict(p) for p in cursor.fetchall()]

    # Get schedules in this week range
    cursor.execute("""
        SELECT s.id, s.work_date, s.shift, s.note, s.position_id,
               u.id as user_id, u.username, u.full_name, u.title as user_title
        FROM schedules s
        JOIN users u ON s.user_id = u.id
        WHERE s.work_date >= ? AND s.work_date <= ?
    """, (start_date, end_date))
    schedules = [dict(s) for s in cursor.fetchall()]

    # Also get approved leaves for this week to highlight conflicts/absences
    cursor.execute("""
        SELECT l.id, l.leave_date, l.leave_type, l.shift, l.reason, l.status,
               u.id as user_id, u.full_name
        FROM leave_requests l
        JOIN users u ON l.user_id = u.id
        WHERE l.leave_date >= ? AND l.leave_date <= ? AND l.status = 'approved'
    """, (start_date, end_date))
    leaves = [dict(l) for l in cursor.fetchall()]
    conn.close()

    # Organize schedules into a lookup map: (position_id, work_date, shift) -> schedule
    sched_map = {}
    for s in schedules:
        key = f"{s['position_id']}_{s['work_date']}_{s['shift']}"
        sched_map[key] = s

    return {
        "success": True,
        "start_date": start_date,
        "end_date": end_date,
        "week_dates": week_dates,
        "positions": positions,
        "schedule_map": sched_map,
        "approved_leaves": leaves,
        "current_user_id": user["id"]
    }

@router.post("/assign")
def assign_position(
    req: ScheduleAssignRequest,
    admin: dict = Depends(require_admin)
):
    """Assign or clear a position for a specific date and shift (Admin only)."""
    conn = get_db()
    cursor = conn.cursor()

    if req.user_id is None or req.user_id == 0:
        # Clear assignment
        cursor.execute("""
            DELETE FROM schedules
            WHERE work_date = ? AND shift = ? AND position_id = ?
        """, (req.work_date, req.shift, req.position_id))
    else:
        cursor.execute("""
            INSERT INTO schedules (work_date, shift, position_id, user_id, note, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(work_date, shift, position_id) DO UPDATE SET
                user_id = excluded.user_id,
                note = excluded.note,
                created_by = excluded.created_by,
                created_at = CURRENT_TIMESTAMP
        """, (req.work_date, req.shift, req.position_id, req.user_id, req.note, admin["id"]))

    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'SCHEDULE_ASSIGN', ?)
    """, (admin["id"], f"Phân công vị trí {req.position_id} ngày {req.work_date} ({req.shift}) cho user {req.user_id}"))

    conn.commit()
    conn.close()
    return {"success": True, "message": "Cập nhật phân công thành công!"}

@router.post("/batch-assign")
def batch_assign_positions(
    req: ScheduleBatchAssignRequest,
    admin: dict = Depends(require_admin)
):
    """Batch assign multiple positions."""
    conn = get_db()
    cursor = conn.cursor()

    for item in req.assignments:
        if item.user_id is None or item.user_id == 0:
            cursor.execute("""
                DELETE FROM schedules
                WHERE work_date = ? AND shift = ? AND position_id = ?
            """, (item.work_date, item.shift, item.position_id))
        else:
            cursor.execute("""
                INSERT INTO schedules (work_date, shift, position_id, user_id, note, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(work_date, shift, position_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    note = excluded.note,
                    created_by = excluded.created_by,
                    created_at = CURRENT_TIMESTAMP
            """, (item.work_date, item.shift, item.position_id, item.user_id, item.note, admin["id"]))

    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'SCHEDULE_BATCH_ASSIGN', ?)
    """, (admin["id"], f"Lưu hàng loạt {len(req.assignments)} phân công lịch làm việc"))

    conn.commit()
    conn.close()
    return {"success": True, "message": f"Đã cập nhật {len(req.assignments)} vị trí thành công!"}

@router.post("/copy-week")
def copy_week_schedule(
    from_start_date: str = Query(..., description="YYYY-MM-DD of source Monday"),
    to_start_date: str = Query(..., description="YYYY-MM-DD of target Monday"),
    admin: dict = Depends(require_admin)
):
    """Copy an entire week's schedule to another week."""
    from_dt = datetime.datetime.strptime(from_start_date, "%Y-%m-%d").date()
    to_dt = datetime.datetime.strptime(to_start_date, "%Y-%m-%d").date()

    conn = get_db()
    cursor = conn.cursor()

    copied_count = 0
    for day_offset in range(7):
        src_day = (from_dt + datetime.timedelta(days=day_offset)).strftime("%Y-%m-%d")
        tgt_day = (to_dt + datetime.timedelta(days=day_offset)).strftime("%Y-%m-%d")

        cursor.execute("SELECT shift, position_id, user_id, note FROM schedules WHERE work_date = ?", (src_day,))
        rows = cursor.fetchall()

        for r in rows:
            cursor.execute("""
                INSERT INTO schedules (work_date, shift, position_id, user_id, note, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(work_date, shift, position_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    note = excluded.note,
                    created_by = excluded.created_by,
                    created_at = CURRENT_TIMESTAMP
            """, (tgt_day, r["shift"], r["position_id"], r["user_id"], r["note"], admin["id"]))
            copied_count += 1

    conn.commit()
    conn.close()
    return {"success": True, "message": f"Đã sao chép {copied_count} lượt phân công sang tuần mới thành công!"}

@router.get("/export-excel")
def export_schedule_excel(
    start_date: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Generate high-quality, printable Excel file of weekly laboratory roster."""
    if not start_date:
        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        start_date = monday.strftime("%Y-%m-%d")

    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    week_dates = [(start_dt + datetime.timedelta(days=i)) for i in range(7)]
    end_date = week_dates[-1].strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM positions ORDER BY sort_order ASC")
    positions = [dict(p) for p in cursor.fetchall()]

    cursor.execute("""
        SELECT s.work_date, s.shift, s.position_id, u.full_name
        FROM schedules s
        JOIN users u ON s.user_id = u.id
        WHERE s.work_date >= ? AND s.work_date <= ?
    """, (start_date, end_date))
    sched_rows = cursor.fetchall()
    conn.close()

    sched_map = {}
    for r in sched_rows:
        sched_map[f"{r['position_id']}_{r['work_date']}_{r['shift']}"] = r["full_name"]

    # Build workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lich_Phan_Cong_Tuan"
    ws.views.sheetView[0].showGridLines = True

    # Styling definitions
    font_header_title = Font(name="Calibri", size=13, bold=True, color="003366")
    font_bold = Font(name="Calibri", size=11, bold=True)
    font_regular = Font(name="Calibri", size=10)
    font_category = Font(name="Calibri", size=10, bold=True, color="004085")

    fill_title = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    fill_day_header = PatternFill(start_color="005B96", end_color="005B96", fill_type="solid")
    fill_shift_header = PatternFill(start_color="6497B1", end_color="6497B1", fill_type="solid")
    fill_cat = PatternFill(start_color="E9ECEF", end_color="E9ECEF", fill_type="solid")
    fill_cell_even = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='B0BEC5'),
        right=Side(style='thin', color='B0BEC5'),
        top=Side(style='thin', color='B0BEC5'),
        bottom=Side(style='thin', color='B0BEC5')
    )

    align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    align_left = Alignment(horizontal='left', vertical='center')

    # Hospital Header
    ws.merge_cells("A1:I1")
    ws["A1"] = f"{HOSPITAL_NAME} - {DEPARTMENT_NAME}"
    ws["A1"].font = font_header_title
    ws["A1"].alignment = align_center

    ws.merge_cells("A2:I2")
    ws["A2"] = f"BẢNG PHÂN CÔNG VỊ TRÍ LÀM VIỆC & LỊCH TRỰC KHOA XÉT NGHIỆM"
    ws["A2"].font = Font(name="Calibri", size=14, bold=True, color="B30000")
    ws["A2"].alignment = align_center

    ws.merge_cells("A3:I3")
    ws["A3"] = f"Tuần từ ngày {start_dt.strftime('%d/%m/%Y')} đến ngày {week_dates[-1].strftime('%d/%m/%Y')} (Quy định 2429/QĐ-BYT)"
    ws["A3"].font = Font(name="Calibri", size=10, italic=True)
    ws["A3"].alignment = align_center

    # Table Header (Row 5 & 6)
    day_names = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

    ws.merge_cells("A5:B6")
    ws["A5"] = "VỊ TRÍ CÔNG TÁC / NHIỆM VỤ"
    ws["A5"].font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    ws["A5"].fill = fill_day_header
    ws["A5"].alignment = align_center

    col_idx = 3
    for i, d in enumerate(week_dates):
        c_letter = get_column_letter(col_idx)
        cell = ws[f"{c_letter}5"]
        cell.value = f"{day_names[i]}\n({d.strftime('%d/%m')})"
        cell.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        cell.fill = fill_day_header
        cell.alignment = align_center
        col_idx += 1

    # Shift sub-row or indicators
    row_idx = 7
    cat_names = {
        "blood": "1. VỊ TRÍ LẤY MÁU NGOẠI TRÚ & NỘI TRÚ (4 BÀN LẤY MÁU)",
        "machine": "2. VẬN HÀNH PHÒNG MÁY XÉT NGHIỆM (HUYẾT HỌC, SINH HÓA, ĐÔNG MÁU...)",
        "warehouse": "3. QUẢN LÝ KHO HÓA CHẤT & VẬT TƯ TIÊU HAO",
        "quality_2429": "4. QUẢN LÝ SỔ SÁCH & HỒ SƠ CHẤT LƯỢNG THEO QĐ 2429",
        "direct": "5. THƯỜNG TRỰC CẤP CỨU & TRỰC ĐÊM 24/24"
    }

    current_cat = None
    for p in positions:
        if p["category"] != current_cat:
            current_cat = p["category"]
            # Category banner row
            ws.merge_cells(f"A{row_idx}:I{row_idx}")
            cat_cell = ws[f"A{row_idx}"]
            cat_cell.value = cat_names.get(current_cat, current_cat.upper())
            cat_cell.font = font_category
            cat_cell.fill = fill_cat
            cat_cell.alignment = align_left
            for col in range(1, 10):
                ws.cell(row=row_idx, column=col).border = thin_border
            row_idx += 1

        # Morning shift row
        ws.cell(row=row_idx, column=1, value=p["name"]).font = font_bold
        ws.cell(row=row_idx, column=1).alignment = align_left
        ws.cell(row=row_idx, column=2, value="Sáng").font = font_regular
        ws.cell(row=row_idx, column=2).alignment = align_center

        for day_i, d in enumerate(week_dates):
            d_str = d.strftime("%Y-%m-%d")
            assigned_name = sched_map.get(f"{p['id']}_{d_str}_sang", "")
            cell = ws.cell(row=row_idx, column=3 + day_i, value=assigned_name)
            cell.font = font_regular
            cell.alignment = align_center

        for col in range(1, 10):
            ws.cell(row=row_idx, column=col).border = thin_border
        row_idx += 1

        # Afternoon shift row (skip for direct night shift)
        if p["category"] != "direct":
            ws.cell(row=row_idx, column=1, value="")
            ws.cell(row=row_idx, column=2, value="Chiều").font = font_regular
            ws.cell(row=row_idx, column=2).alignment = align_center

            for day_i, d in enumerate(week_dates):
                d_str = d.strftime("%Y-%m-%d")
                assigned_name = sched_map.get(f"{p['id']}_{d_str}_chieu", "")
                cell = ws.cell(row=row_idx, column=3 + day_i, value=assigned_name)
                cell.font = font_regular
                cell.alignment = align_center

            for col in range(1, 10):
                ws.cell(row=row_idx, column=col).border = thin_border
            row_idx += 1

    # Night shift section if direct
    for d_i, d in enumerate(week_dates):
        pass

    # Signature rows
    row_idx += 2
    ws.cell(row=row_idx, column=2, value="KỸ THUẬT VIÊN TRƯỞNG").font = font_bold
    ws.cell(row=row_idx, column=2).alignment = align_center
    ws.cell(row=row_idx, column=7, value="TRƯỞNG KHOA XÉT NGHIỆM").font = font_bold
    ws.cell(row=row_idx, column=7).alignment = align_center

    row_idx += 1
    ws.cell(row=row_idx, column=2, value="(Ký và ghi rõ họ tên)").font = Font(name="Calibri", size=9, italic=True)
    ws.cell(row=row_idx, column=2).alignment = align_center
    ws.cell(row=row_idx, column=7, value="(Ký và ghi rõ họ tên)").font = Font(name="Calibri", size=9, italic=True)
    ws.cell(row=row_idx, column=7).alignment = align_center

    row_idx += 3
    ws.cell(row=row_idx, column=2, value="CN. Nguyễn Trường Duy").font = font_bold
    ws.cell(row=row_idx, column=2).alignment = align_center
    ws.cell(row=row_idx, column=7, value="CN. Lê Đình Tú").font = font_bold
    ws.cell(row=row_idx, column=7).alignment = align_center

    # Adjust column widths
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 10
    for i in range(3, 10):
        ws.column_dimensions[get_column_letter(i)].width = 18

    # Save to buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Lich_Phan_Cong_Khoa_Xet_Nghiem_Tuan_{start_date}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
