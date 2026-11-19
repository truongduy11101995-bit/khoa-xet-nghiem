import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body

from backend.database import get_db, is_cloud_db
from backend.auth import get_current_user

router = APIRouter(prefix="/api/environment", tags=["Sổ Nhiệt Độ & Môi Trường"])

# Standard limits according to Decision 2429/QD-BYT and ISO 15189:2022
LIMITS = {
    "room_temp_min": 18.0,
    "room_temp_max": 25.0,
    "room_hum_min": 40.0,
    "room_hum_max": 75.0,
    "fridge_temp_min": 2.0,
    "fridge_temp_max": 8.0,
    "fridge_sample_temp_min": 2.0,
    "fridge_sample_temp_max": 8.0,
    "freezer_temp_max": -15.0,
    "incubator_temp_min": 35.0,
    "incubator_temp_max": 37.0,
}

DEVICES = [
    {
        "id": "all",
        "code": "ALL",
        "name": "Toàn Bộ Vị Trí (Ghi nhận tổng hợp theo ca)",
        "category": "all",
        "icon": "🏢",
        "standard": "Phòng máy + Tủ lạnh + Tủ đông",
        "desc": "Đo và ghi nhận đồng thời cả phòng xét nghiệm và các tủ lưu trữ"
    },
    {
        "id": "tl01",
        "code": "TL-01",
        "name": "Tủ Lạnh Hóa Chất & Sinh Phẩm (TL-01)",
        "category": "fridge",
        "icon": "🧊",
        "target_field": "fridge_temp",
        "temp_min": 2.0,
        "temp_max": 8.0,
        "unit": "°C",
        "standard": "2.0 - 8.0°C",
        "desc": "Bảo quản hóa chất máy xét nghiệm, sinh phẩm miễn dịch và kit thử"
    },
    {
        "id": "tl02",
        "code": "TL-02",
        "name": "Tủ Lạnh Lưu Mẫu Bệnh Phẩm & Huyết Thanh (TL-02)",
        "category": "fridge",
        "icon": "🧪",
        "target_field": "fridge_sample_temp",
        "temp_min": 2.0,
        "temp_max": 8.0,
        "unit": "°C",
        "standard": "2.0 - 8.0°C",
        "desc": "Lưu trữ mẫu bệnh phẩm, huyết thanh chờ chạy lại hoặc đối chứng"
    },
    {
        "id": "td01",
        "code": "TĐ-01",
        "name": "Tủ Đông Âm Sâu Lưu Mẫu & QC (TĐ-01)",
        "category": "freezer",
        "icon": "❄️",
        "target_field": "freezer_temp",
        "temp_max": -15.0,
        "unit": "°C",
        "standard": "≤ -15.0°C (chuẩn -18 đến -25°C)",
        "desc": "Lưu trữ huyết thanh mẫu chuẩn ngoại kiểm, Calibrator & Control"
    },
    {
        "id": "ta01",
        "code": "TÂ-01",
        "name": "Tủ Ấm Ủ Mẫu & Vi Sinh (TÂ-01)",
        "category": "incubator",
        "icon": "🌡️",
        "target_field": "incubator_temp",
        "temp_min": 35.0,
        "temp_max": 37.0,
        "unit": "°C",
        "standard": "35.0 - 37.0°C",
        "desc": "Ủ phản ứng hóa sinh, phản ứng ngưng kết hoặc vi sinh"
    },
    {
        "id": "room",
        "code": "PM-01",
        "name": "Không Gian Phòng Máy Xét Nghiệm (PM-01)",
        "category": "room",
        "icon": "🏢",
        "target_field": "room_temp",
        "temp_min": 18.0,
        "temp_max": 25.0,
        "hum_min": 40.0,
        "hum_max": 75.0,
        "unit": "°C / %",
        "standard": "18.0 - 25.0°C | 40 - 75%",
        "desc": "Điều kiện môi trường hoạt động của hệ thống máy xét nghiệm tự động"
    }
]

def check_environmental_safety(
    room_temp: Optional[float] = None,
    room_humidity: Optional[float] = None,
    fridge_temp: Optional[float] = None,
    freezer_temp: Optional[float] = None,
    fridge_sample_temp: Optional[float] = None,
    incubator_temp: Optional[float] = None
):
    warnings = []
    if room_temp is not None and (room_temp < LIMITS["room_temp_min"] or room_temp > LIMITS["room_temp_max"]):
        warnings.append(f"Nhiệt độ phòng {room_temp}°C ngoài dải chuẩn ({LIMITS['room_temp_min']}-{LIMITS['room_temp_max']}°C)")
    if room_humidity is not None and (room_humidity < LIMITS["room_hum_min"] or room_humidity > LIMITS["room_hum_max"]):
        warnings.append(f"Độ ẩm phòng {room_humidity}% ngoài dải chuẩn ({LIMITS['room_hum_min']}-{LIMITS['room_hum_max']}%)")
    if fridge_temp is not None and (fridge_temp < LIMITS["fridge_temp_min"] or fridge_temp > LIMITS["fridge_temp_max"]):
        warnings.append(f"Tủ lạnh sinh phẩm (TL-01) {fridge_temp}°C ngoài dải chuẩn ({LIMITS['fridge_temp_min']}-{LIMITS['fridge_temp_max']}°C)")
    if fridge_sample_temp is not None and (fridge_sample_temp < LIMITS["fridge_sample_temp_min"] or fridge_sample_temp > LIMITS["fridge_sample_temp_max"]):
        warnings.append(f"Tủ lạnh mẫu lưu (TL-02) {fridge_sample_temp}°C ngoài dải chuẩn ({LIMITS['fridge_sample_temp_min']}-{LIMITS['fridge_sample_temp_max']}°C)")
    if freezer_temp is not None and freezer_temp > LIMITS["freezer_temp_max"]:
        warnings.append(f"Tủ đông lưu mẫu (TĐ-01) {freezer_temp}°C cao hơn ngưỡng chuẩn (≤ {LIMITS['freezer_temp_max']}°C)")
    if incubator_temp is not None and (incubator_temp < LIMITS["incubator_temp_min"] or incubator_temp > LIMITS["incubator_temp_max"]):
        warnings.append(f"Tủ ấm (TÂ-01) {incubator_temp}°C ngoài dải chuẩn ({LIMITS['incubator_temp_min']}-{LIMITS['incubator_temp_max']}°C)")
    
    is_safe = (len(warnings) == 0)
    warning_str = "; ".join(warnings) if warnings else ""
    return is_safe, warning_str

@router.get("/devices")
def get_device_list(user: dict = Depends(get_current_user)):
    """
    Get registry of all cabinets, refrigerators and monitored rooms.
    """
    return {
        "success": True,
        "devices": DEVICES,
        "limits": LIMITS
    }

@router.get("/logs")
def get_environment_logs(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    user: dict = Depends(get_current_user)
):
    """
    Get environmental logs for a specific month with stats and warnings.
    """
    now = datetime.date.today()
    target_year = year or now.year
    target_month = month or now.month

    month_str = f"{target_year:04d}-{target_month:02d}%"

    conn = get_db()
    cursor = conn.cursor()

    sql = """
    SELECT * FROM environment_logs 
    WHERE log_date LIKE ? 
    ORDER BY log_date ASC, shift ASC
    """
    cursor.execute(sql, (month_str,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    total_logs = len(rows)
    safe_count = 0
    warning_count = 0

    room_temps = []
    humidities = []
    fridge_temps = []
    freezer_temps = []
    fridge_sample_temps = []
    incubator_temps = []

    today_str = now.strftime("%Y-%m-%d")
    today_sang_logged = False
    today_chieu_logged = False

    for r in rows:
        # Normalize boolean is_safe
        r["is_safe"] = bool(r.get("is_safe"))
        if r["is_safe"]:
            safe_count += 1
        else:
            warning_count += 1

        if r.get("log_date") == today_str:
            if r.get("shift") == "sang":
                today_sang_logged = True
            elif r.get("shift") == "chieu":
                today_chieu_logged = True

        if r.get("room_temp") is not None:
            room_temps.append(float(r["room_temp"]))
        if r.get("room_humidity") is not None:
            humidities.append(float(r["room_humidity"]))
        if r.get("fridge_temp") is not None:
            fridge_temps.append(float(r["fridge_temp"]))
        if r.get("freezer_temp") is not None:
            freezer_temps.append(float(r["freezer_temp"]))
        if r.get("fridge_sample_temp") is not None:
            fridge_sample_temps.append(float(r["fridge_sample_temp"]))
        if r.get("incubator_temp") is not None:
            incubator_temps.append(float(r["incubator_temp"]))

    # Latest record for KPI cards
    latest = rows[-1] if rows else None

    stats = {
        "year": target_year,
        "month": target_month,
        "total_logs": total_logs,
        "safe_count": safe_count,
        "warning_count": warning_count,
        "today_str": today_str,
        "today_sang_logged": today_sang_logged,
        "today_chieu_logged": today_chieu_logged,
        "latest": latest,
        "summary": {
            "room_temp": {
                "avg": round(sum(room_temps)/len(room_temps), 1) if room_temps else None,
                "min": min(room_temps) if room_temps else None,
                "max": max(room_temps) if room_temps else None
            },
            "humidity": {
                "avg": round(sum(humidities)/len(humidities), 1) if humidities else None,
                "min": min(humidities) if humidities else None,
                "max": max(humidities) if humidities else None
            },
            "fridge_temp": {
                "avg": round(sum(fridge_temps)/len(fridge_temps), 1) if fridge_temps else None,
                "min": min(fridge_temps) if fridge_temps else None,
                "max": max(fridge_temps) if fridge_temps else None
            },
            "freezer_temp": {
                "avg": round(sum(freezer_temps)/len(freezer_temps), 1) if freezer_temps else None,
                "min": min(freezer_temps) if freezer_temps else None,
                "max": max(freezer_temps) if freezer_temps else None
            },
            "fridge_sample_temp": {
                "avg": round(sum(fridge_sample_temps)/len(fridge_sample_temps), 1) if fridge_sample_temps else None,
                "min": min(fridge_sample_temps) if fridge_sample_temps else None,
                "max": max(fridge_sample_temps) if fridge_sample_temps else None
            },
            "incubator_temp": {
                "avg": round(sum(incubator_temps)/len(incubator_temps), 1) if incubator_temps else None,
                "min": min(incubator_temps) if incubator_temps else None,
                "max": max(incubator_temps) if incubator_temps else None
            }
        },
        "limits": LIMITS
    }

    return {
        "stats": stats,
        "logs": rows,
        "devices": DEVICES
    }

@router.post("/logs")
def save_environment_log(
    payload: Dict[str, Any] = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Save or update an environmental log entry for a date & shift,
    supporting logging for a specific cabinet/device or all devices at once.
    """
    log_date = payload.get("log_date") or datetime.date.today().strftime("%Y-%m-%d")
    shift = payload.get("shift") or ("sang" if datetime.datetime.now().hour < 12 else "chieu")
    log_time = payload.get("log_time") or datetime.datetime.now().strftime("%H:%M")
    target_device = payload.get("target_device") or "all"

    conn = get_db()
    cursor = conn.cursor()
    cloud = is_cloud_db()

    # Find existing row for this date and shift
    cursor.execute("SELECT * FROM environment_logs WHERE log_date = ? AND shift = ?", (log_date, shift))
    existing_row = cursor.fetchone()
    existing = dict(existing_row) if existing_row else None

    # Baseline defaults if no existing row
    default_room_temp = 22.0
    default_room_hum = 60.0
    default_fridge_temp = 4.5
    default_freezer_temp = -20.0
    default_fridge_sample = 4.5
    default_incubator = 36.5

    # If no existing record for this shift, try getting latest from DB for baseline continuity
    if not existing:
        cursor.execute("SELECT * FROM environment_logs ORDER BY log_date DESC, shift DESC LIMIT 1")
        last_row = cursor.fetchone()
        if last_row:
            last_dict = dict(last_row)
            default_room_temp = float(last_dict.get("room_temp") or 22.0)
            default_room_hum = float(last_dict.get("room_humidity") or 60.0)
            default_fridge_temp = float(last_dict.get("fridge_temp") or 4.5)
            default_freezer_temp = float(last_dict.get("freezer_temp") or -20.0)
            default_fridge_sample = float(last_dict.get("fridge_sample_temp") or 4.5)
            default_incubator = float(last_dict.get("incubator_temp") or 36.5)

    # Resolve values (payload overrides existing/default)
    def parse_optional_float(val, fallback):
        if val is None or val == "":
            return fallback
        try:
            return float(val)
        except (ValueError, TypeError):
            return fallback

    cur_room_temp = existing.get("room_temp") if existing else default_room_temp
    cur_room_hum = existing.get("room_humidity") if existing else default_room_hum
    cur_fridge_temp = existing.get("fridge_temp") if existing else default_fridge_temp
    cur_freezer_temp = existing.get("freezer_temp") if existing else default_freezer_temp
    cur_fridge_sample = existing.get("fridge_sample_temp") if existing else default_fridge_sample
    cur_incubator = existing.get("incubator_temp") if existing else default_incubator

    # Validate based on target_device
    device_name = "Toàn bộ vị trí"
    if target_device == "tl01":
        device_name = "Tủ Lạnh Hóa Chất & Sinh Phẩm (TL-01)"
        if payload.get("fridge_temp") is None or payload.get("fridge_temp") == "":
            raise HTTPException(status_code=400, detail="Vui lòng nhập nhiệt độ cho Tủ Lạnh Hóa Chất (TL-01)!")
        cur_fridge_temp = float(payload["fridge_temp"])
    elif target_device == "tl02":
        device_name = "Tủ Lạnh Mẫu Bệnh Phẩm (TL-02)"
        sample_val = payload.get("fridge_sample_temp") or payload.get("fridge_temp")
        if sample_val is None or sample_val == "":
            raise HTTPException(status_code=400, detail="Vui lòng nhập nhiệt độ cho Tủ Lạnh Mẫu Bệnh Phẩm (TL-02)!")
        cur_fridge_sample = float(sample_val)
    elif target_device == "td01":
        device_name = "Tủ Đông Âm Sâu (TĐ-01)"
        if payload.get("freezer_temp") is None or payload.get("freezer_temp") == "":
            raise HTTPException(status_code=400, detail="Vui lòng nhập nhiệt độ cho Tủ Đông Âm Sâu (TĐ-01)!")
        cur_freezer_temp = float(payload["freezer_temp"])
    elif target_device == "ta01":
        device_name = "Tủ Ấm Ủ Mẫu (TÂ-01)"
        inc_val = payload.get("incubator_temp")
        if inc_val is None or inc_val == "":
            raise HTTPException(status_code=400, detail="Vui lòng nhập nhiệt độ cho Tủ Ấm (TÂ-01)!")
        cur_incubator = float(inc_val)
    elif target_device == "room":
        device_name = "Không Gian Phòng Máy (PM-01)"
        if payload.get("room_temp") is None or payload.get("room_humidity") is None:
            raise HTTPException(status_code=400, detail="Vui lòng nhập đầy đủ nhiệt độ và độ ẩm phòng máy!")
        cur_room_temp = float(payload["room_temp"])
        cur_room_hum = float(payload["room_humidity"])
    else:
        # "all" - update all fields provided
        cur_room_temp = parse_optional_float(payload.get("room_temp"), cur_room_temp)
        cur_room_hum = parse_optional_float(payload.get("room_humidity"), cur_room_hum)
        cur_fridge_temp = parse_optional_float(payload.get("fridge_temp"), cur_fridge_temp)
        cur_freezer_temp = parse_optional_float(payload.get("freezer_temp"), cur_freezer_temp)
        cur_fridge_sample = parse_optional_float(payload.get("fridge_sample_temp"), cur_fridge_sample)
        cur_incubator = parse_optional_float(payload.get("incubator_temp"), cur_incubator)

    # Check environmental safety across all active parameters
    is_safe, auto_warning = check_environmental_safety(
        room_temp=cur_room_temp,
        room_humidity=cur_room_hum,
        fridge_temp=cur_fridge_temp,
        freezer_temp=cur_freezer_temp,
        fridge_sample_temp=cur_fridge_sample,
        incubator_temp=cur_incubator
    )
    manual_warning = payload.get("warning_note", "")
    full_warning = "; ".join(filter(None, [auto_warning, manual_warning]))
    action_taken = payload.get("action_taken", "")

    logged_by = user.get("id")
    logged_by_name = user.get("full_name") or user.get("username")
    is_safe_db = is_safe if cloud else (1 if is_safe else 0)

    if existing:
        log_id = existing["id"]
        cursor.execute("""
        UPDATE environment_logs
        SET log_time = ?, logged_by = ?, logged_by_name = ?,
            room_temp = ?, room_humidity = ?, fridge_temp = ?, freezer_temp = ?,
            fridge_sample_temp = ?, incubator_temp = ?, target_device = ?,
            is_safe = ?, warning_note = ?, action_taken = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """, (
            log_time, logged_by, logged_by_name,
            cur_room_temp, cur_room_hum, cur_fridge_temp, cur_freezer_temp,
            cur_fridge_sample, cur_incubator, target_device,
            is_safe_db, full_warning, action_taken, log_id
        ))
    else:
        cursor.execute("""
        INSERT INTO environment_logs (
            log_date, shift, log_time, logged_by, logged_by_name,
            room_temp, room_humidity, fridge_temp, freezer_temp,
            fridge_sample_temp, incubator_temp, target_device,
            is_safe, warning_note, action_taken, reviewer_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CN. Lê Đình Tú')
        """, (
            log_date, shift, log_time, logged_by, logged_by_name,
            cur_room_temp, cur_room_hum, cur_fridge_temp, cur_freezer_temp,
            cur_fridge_sample, cur_incubator, target_device,
            is_safe_db, full_warning, action_taken
        ))

    conn.commit()
    conn.close()

    shift_label = "Sáng" if shift == "sang" else "Chiều"
    return {
        "success": True,
        "message": f"Đã ghi nhận nhiệt độ cho {device_name} (Ca {shift_label} ngày {log_date})",
        "target_device": target_device,
        "is_safe": is_safe,
        "warning": full_warning
    }

@router.post("/logs/{log_id}/review")
def review_environment_log(
    log_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Reviewer (Trưởng khoa / KTV Trưởng) sign-off.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE environment_logs
    SET reviewer_id = ?, reviewer_name = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (user.get("id"), user.get("full_name") or user.get("username"), log_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã ký duyệt ghi nhận nhiệt độ."}

@router.get("/print-data")
def get_print_data(
    year: int = Query(...),
    month: int = Query(...),
    user: dict = Depends(get_current_user)
):
    """
    Format complete month data into 28-31 days for BM.MT.01 A4 printout.
    """
    import calendar
    _, num_days = calendar.monthrange(year, month)

    month_str = f"{year:04d}-{month:02d}%"
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM environment_logs WHERE log_date LIKE ? ORDER BY log_date ASC, shift ASC", (month_str,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    logs_map = {}
    for r in rows:
        key = f"{r['log_date']}_{r['shift']}"
        logs_map[key] = r

    days_data = []
    for day in range(1, num_days + 1):
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        morning = logs_map.get(f"{date_str}_sang")
        afternoon = logs_map.get(f"{date_str}_chieu")

        days_data.append({
            "day": day,
            "date": date_str,
            "morning": morning,
            "afternoon": afternoon
        })

    return {
        "hospital": "BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG",
        "department": "KHOA XÉT NGHIỆM",
        "form_code": "BM.MT.01",
        "form_title": "BẢNG THEO DÕI NHIỆT ĐỘ - ĐỘ ẨM KHÔNG GIAN VÀ THIẾT BỊ LƯU TRỮ",
        "standard_ref": "Quy định Quyết định 2429/QĐ-BYT & Tiêu chuẩn ISO 15189:2022",
        "year": year,
        "month": month,
        "limits": LIMITS,
        "days": days_data
    }
