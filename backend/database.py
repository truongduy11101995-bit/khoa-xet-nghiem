import sqlite3
import os
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.config import (
    DATABASE_URL, DB_PATH, init_directories, BIEU_MAU_PHIEU_KQ,
    BIEU_MAU_2429, BIEU_MAU_HANH_CHINH, HO_SO_DIR, MAX_ACTIVE_STAFF
)
from backend.auth import hash_password
from backend.db_adapter import connect_postgres

def is_cloud_db() -> bool:
    """Return True if using Cloud PostgreSQL (Supabase) via DATABASE_URL."""
    return bool(DATABASE_URL and DATABASE_URL.strip().startswith(("postgres://", "postgresql://")))

def get_db():
    """
    Returns active database connection:
    - If DATABASE_URL is configured: connects to Supabase (PostgreSQL) via adapter.
    - Otherwise: connects to local SQLite file with WAL mode and Vietnamese lowercase support.
    """
    if is_cloud_db():
        return connect_postgres(DATABASE_URL)

    # Local SQLite
    init_directories()
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.create_function("VN_LOWER", 1, lambda s: s.lower() if s else "")
    return conn

def init_db():
    """Initialize schema and seed initial data if needed."""
    if is_cloud_db():
        _init_postgres_db()
    else:
        _init_sqlite_db()

def _init_postgres_db():
    """Initialize schema on PostgreSQL / Supabase."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        title VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL CHECK(role IN ('truong_khoa', 'ktv_truong', 'ktv')),
        folder_name VARCHAR(255) NOT NULL,
        dob VARCHAR(50),
        phone VARCHAR(50),
        email VARCHAR(255),
        cchn VARCHAR(100),
        cchn_date VARCHAR(50),
        cchn_scope TEXT,
        education TEXT,
        specialty TEXT,
        status VARCHAR(20) DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (
        id SERIAL PRIMARY KEY,
        code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(50) NOT NULL CHECK(category IN ('blood', 'machine', 'warehouse', 'quality_2429', 'direct')),
        description TEXT,
        sort_order INTEGER DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id SERIAL PRIMARY KEY,
        work_date VARCHAR(50) NOT NULL,
        shift VARCHAR(20) NOT NULL CHECK(shift IN ('sang', 'chieu', 'truc')),
        position_id INTEGER NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        note TEXT,
        created_by INTEGER REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT unique_schedule_slot UNIQUE(work_date, shift, position_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        leave_date VARCHAR(50) NOT NULL,
        leave_type VARCHAR(50) NOT NULL CHECK(leave_type IN ('phep_nam', 'nghi_bu', 'di_hoc', 'viec_rieng')),
        shift VARCHAR(20) DEFAULT 'all' CHECK(shift IN ('all', 'sang', 'chieu')),
        reason TEXT NOT NULL,
        status VARCHAR(20) DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
        reviewed_by INTEGER REFERENCES users(id),
        review_note TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        category VARCHAR(50) NOT NULL CHECK(category IN ('phieu_kq_hen', 'so_sach_2429', 'bia_hanh_chinh')),
        code VARCHAR(100),
        title VARCHAR(255) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_ext VARCHAR(50) NOT NULL,
        file_path TEXT NOT NULL,
        file_size BIGINT DEFAULT 0,
        version VARCHAR(50) DEFAULT '1.0',
        description TEXT,
        uploaded_by INTEGER REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_files (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        doc_type VARCHAR(50) NOT NULL CHECK(doc_type IN ('bang_cap', 'cchn', 'atsh', 'gksk', 'syll', 'mo_ta_cv', 'khac')),
        title VARCHAR(255) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_path TEXT NOT NULL,
        file_size BIGINT DEFAULT 0,
        uploaded_by INTEGER REFERENCES users(id),
        uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        action VARCHAR(100) NOT NULL,
        details TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allowed_ips (
        id SERIAL PRIMARY KEY,
        ip_address VARCHAR(100) UNIQUE NOT NULL,
        description VARCHAR(255),
        added_by VARCHAR(100),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qaqc_store (
        id SERIAL PRIMARY KEY,
        store_key VARCHAR(100) UNIQUE NOT NULL,
        data_json TEXT NOT NULL,
        version VARCHAR(100) NOT NULL,
        updated_by VARCHAR(255),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shift_handovers (
        id SERIAL PRIMARY KEY,
        handover_date VARCHAR(20) NOT NULL,
        shift_time VARCHAR(50) NOT NULL,
        outgoing_user_id INTEGER,
        outgoing_name VARCHAR(255) NOT NULL,
        incoming_user_id INTEGER,
        incoming_name VARCHAR(255) NOT NULL,
        equipment_status TEXT,
        pending_samples TEXT,
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    _seed_users(cursor)
    _seed_positions(cursor)
    _seed_sample_schedules(cursor)
    _sync_real_inventory_20261125(cursor)
    _sync_staff_list_20261127(cursor)

    conn.commit()
    conn.close()

def _init_sqlite_db():
    """Initialize schema on local SQLite."""
    init_directories()
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        title TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('truong_khoa', 'ktv_truong', 'ktv')),
        folder_name TEXT NOT NULL,
        dob TEXT,
        phone TEXT,
        email TEXT,
        cchn TEXT,
        cchn_date TEXT,
        cchn_scope TEXT,
        education TEXT,
        specialty TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL CHECK(category IN ('blood', 'machine', 'warehouse', 'quality_2429', 'direct')),
        description TEXT,
        sort_order INTEGER DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        work_date TEXT NOT NULL,
        shift TEXT NOT NULL CHECK(shift IN ('sang', 'chieu', 'truc')),
        position_id INTEGER NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
        note TEXT,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(work_date, shift, position_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        leave_date TEXT NOT NULL,
        leave_type TEXT NOT NULL CHECK(leave_type IN ('phep_nam', 'nghi_bu', 'di_hoc', 'viec_rieng')),
        shift TEXT DEFAULT 'all' CHECK(shift IN ('all', 'sang', 'chieu')),
        reason TEXT NOT NULL,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
        reviewed_by INTEGER REFERENCES users(id),
        review_note TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL CHECK(category IN ('phieu_kq_hen', 'so_sach_2429', 'bia_hanh_chinh')),
        code TEXT,
        title TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_ext TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        version TEXT DEFAULT '1.0',
        description TEXT,
        uploaded_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employee_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        doc_type TEXT NOT NULL CHECK(doc_type IN ('bang_cap', 'cchn', 'atsh', 'gksk', 'syll', 'mo_ta_cv', 'khac')),
        title TEXT NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER DEFAULT 0,
        uploaded_by INTEGER REFERENCES users(id),
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allowed_ips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT UNIQUE NOT NULL,
        description TEXT,
        added_by TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qaqc_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_key TEXT UNIQUE NOT NULL,
        data_json TEXT NOT NULL,
        version TEXT NOT NULL,
        updated_by TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shift_handovers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        handover_date TEXT NOT NULL,
        shift_time TEXT NOT NULL,
        outgoing_user_id INTEGER,
        outgoing_name TEXT NOT NULL,
        incoming_user_id INTEGER,
        incoming_name TEXT NOT NULL,
        equipment_status TEXT,
        pending_samples TEXT,
        notes TEXT,
        created_by INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()

    _seed_users(cursor)
    _seed_positions(cursor)
    _seed_sample_schedules(cursor)
    _seed_documents_from_disk(cursor)
    _seed_employee_files_from_disk(cursor)
    _sync_real_inventory_20261125(cursor)
    _sync_staff_list_20261127(cursor)

    conn.commit()
    conn.close()

def _sync_real_inventory_20261125(cursor):
    """One-time sync: replace old inventory with exact 37 real stock-take items."""
    try:
        cursor.execute("SELECT version FROM qaqc_store WHERE store_key = 'real_inventory_sync'")
        row = cursor.fetchone()
        if row and (dict(row).get("version") if hasattr(row, "keys") else row[0]) == "20261125_37items":
            return

        # Clear old inventory & forecasts (no chemicals, only real physical stock)
        try:
            cursor.execute("DELETE FROM inventory_forecasts")
        except Exception:
            pass
        cursor.execute("DELETE FROM inventory_items")

        real_items = [
            ("VT-001", "Cuvet chỉ (đông máu)", "vat_tu", "vỉ", "Vật tư tiêu hao xét nghiệm • 2 vĩ + 5 vĩ", "", "", None, "Nhiệt độ phòng", 7, 2, 0, 0, "Kho vật tư XN", ""),
            ("VT-002", "Lacet", "vat_tu", "cái", "Vật tư tiêu hao xét nghiệm • 150", "", "", None, "Nhiệt độ phòng", 150, 30, 0, 0, "Kho vật tư XN", "Kim trích máu (Lancet)"),
            ("VT-003", "Kim chích máu", "vat_tu", "cái", "Vật tư tiêu hao xét nghiệm • 47 + 17 = 64", "", "", None, "Nhiệt độ phòng", 64, 20, 0, 0, "Kho vật tư XN", ""),
            ("VT-004", "Đầu col có lọc", "vat_tu", "cái", "Vật tư tiêu hao xét nghiệm • 96 + 51 = 147", "", "", None, "Nhiệt độ phòng", 147, 50, 0, 0, "Kho vật tư XN", ""),
            ("VT-005", "Găng tay 75", "vat_tu", "đôi", "Găng tay & Bảo hộ • 50 đôi", "", "", None, "Nhiệt độ phòng", 50, 10, 0, 0, "Kho vật tư XN", ""),
            ("VT-006", "Găng tay VGlove", "vat_tu", "thùng", "Găng tay & Bảo hộ • 2 thùng (100 đôi)", "VGlove", "", None, "Nhiệt độ phòng", 2, 1, 0, 0, "Kho vật tư XN", "Tổng 100 đôi"),
            ("VT-007", "Đầu col có lọc 100-1000µl (Thùng)", "vat_tu", "thùng", "Vật tư tiêu hao xét nghiệm • 1 thùng", "", "", None, "Nhiệt độ phòng", 1, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-008", "Khẩu trang", "vat_tu", "bịch", "Găng tay & Bảo hộ • 3 bịch", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-009", "Găng tay size S không bột", "vat_tu", "hộp", "Găng tay & Bảo hộ • 2 hộp", "", "", None, "Nhiệt độ phòng", 2, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-010", "Găng tay size M không bột", "vat_tu", "hộp", "Găng tay & Bảo hộ • 1 hộp", "", "", None, "Nhiệt độ phòng", 1, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-011", "Găng tay size S có bột", "vat_tu", "hộp", "Găng tay & Bảo hộ • 3 hộp", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-012", "Ống Serum", "vat_tu", "vỉ", "Vật tư tiêu hao xét nghiệm • 15 vĩ", "", "", None, "Nhiệt độ phòng", 15, 3, 0, 0, "Kho vật tư XN", ""),
            ("VT-013", "Lam kính", "vat_tu", "hộp", "Vật tư tiêu hao xét nghiệm • 5 hộp", "", "", None, "Nhiệt độ phòng", 5, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-014", "Đầu col xanh", "vat_tu", "bịch", "Vật tư tiêu hao xét nghiệm • 3 bịch", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-015", "Đầu col trắng có khía", "vat_tu", "bịch", "Vật tư tiêu hao xét nghiệm • 1 bịch", "", "", None, "Nhiệt độ phòng", 1, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-016", "Cuvet miễn dịch", "vat_tu", "bịch", "Vật tư tiêu hao xét nghiệm • 3 bịch", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-017", "Đầu col có lọc 200µl", "vat_tu", "hộp", "Vật tư tiêu hao xét nghiệm • 2 hộp", "", "", None, "Nhiệt độ phòng", 2, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-018", "Đầu col có lọc 100-1000µl", "vat_tu", "hộp", "Vật tư tiêu hao xét nghiệm • 4 hộp + 1 hộp = 5 hộp", "", "", None, "Nhiệt độ phòng", 5, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-019", "Đầu col có lọc 1-200µl", "vat_tu", "hộp", "Vật tư tiêu hao xét nghiệm • 6 hộp + 4 hộp = 10 hộp", "", "", None, "Nhiệt độ phòng", 10, 2, 0, 0, "Kho vật tư XN", ""),
            ("VT-020", "Đầu col có lọc 200µl (zerotip)", "vat_tu", "hộp", "Vật tư tiêu hao xét nghiệm • 2 hộp (zerotip)", "", "", None, "Nhiệt độ phòng", 2, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-021", "Khay inox vuông", "vat_tu", "khay", "Dụng cụ y tế & Inox • 1 khay + 1 khay", "", "", None, "Nhiệt độ phòng", 2, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-022", "Hộp gòn", "vat_tu", "hộp", "Dụng cụ y tế & Inox • 2 hộp + 1 hộp", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-023", "Bình đựng pen", "vat_tu", "cây", "Dụng cụ y tế & Inox • 1 cây", "", "", None, "Nhiệt độ phòng", 1, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-024", "Kéo", "vat_tu", "cây", "Dụng cụ y tế & Inox • 1 cây", "", "", None, "Nhiệt độ phòng", 1, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-025", "Pen", "vat_tu", "cây", "Dụng cụ y tế & Inox • 3 cây", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-026", "Cây hốt rác", "vat_tu", "cây", "Vệ sinh & Hóa chất • 3 cây", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-027", "Chổi quét", "vat_tu", "cây", "Vệ sinh & Hóa chất • 3 cây", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-028", "Nước Javel", "vat_tu", "chai", "Vệ sinh & Hóa chất • 3 chai", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-029", "Cồn y tế", "vat_tu", "chai", "Vệ sinh & Hóa chất • 3 chai", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-030", "Kẹp, pen", "vat_tu", "cái", "Dụng cụ y tế & Inox • 3 cái mỗi loại + 2 cái nữa/loại = 5/5", "", "", None, "Nhiệt độ phòng", 10, 2, 0, 0, "Kho vật tư XN", "Mỗi loại 5 cái (Kẹp: 5, Pen: 5)"),
            ("VT-031", "Kính bảo vệ mắt", "vat_tu", "cái", "Găng tay & Bảo hộ • 5 cái", "", "", None, "Nhiệt độ phòng", 5, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-032", "Khẩu trang N95", "vat_tu", "túi", "Găng tay & Bảo hộ • 3 túi", "", "", None, "Nhiệt độ phòng", 3, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-033", "Tạp dề sử dụng 1 lần", "vat_tu", "cái", "Găng tay & Bảo hộ • 5 cái", "", "", None, "Nhiệt độ phòng", 5, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-034", "Khăn giấy", "vat_tu", "cây", "Vệ sinh & Hóa chất • 1 cây", "", "", None, "Nhiệt độ phòng", 1, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-035", "Khay inox lớn", "vat_tu", "cái", "Dụng cụ y tế & Inox • 2 cái", "", "", None, "Nhiệt độ phòng", 2, 1, 0, 0, "Kho vật tư XN", ""),
            ("VT-036", "Nón bao tóc", "vat_tu", "cái", "Găng tay & Bảo hộ • Chưa ghi số lượng", "", "", None, "Nhiệt độ phòng", 0, 1, 0, 0, "Kho vật tư XN", "Cần kiểm tra & bổ sung số lượng"),
            ("VT-037", "Giấy in nhiệt", "vat_tu", "cuộn", "Văn phòng & In ấn • 16 cuộn", "", "", None, "Nhiệt độ phòng", 16, 4, 0, 0, "Kho vật tư XN", ""),
        ]

        for item in real_items:
            cursor.execute("""
                INSERT INTO inventory_items (
                    code, name, category, unit, spec, manufacturer, lot_number,
                    expiry_date, storage_temp, quantity, min_stock, monthly_usage,
                    unit_price, location, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, item)

        cursor.execute("""
            INSERT INTO qaqc_store (store_key, data_json, version, updated_by)
            VALUES ('real_inventory_sync', '{"count": 37}', '20261125_37items', 'system')
            ON CONFLICT(store_key) DO UPDATE SET
                data_json = excluded.data_json,
                version = excluded.version,
                updated_at = CURRENT_TIMESTAMP
        """)
    except Exception as e:
        print("Sync real inventory warning:", e)

def _sync_staff_list_20261127(cursor):
    """One-time sync: add 3 new staff members (total 7) and update phone numbers."""
    try:
        cursor.execute("SELECT version FROM qaqc_store WHERE store_key = 'staff_sync_20261127'")
        row = cursor.fetchone()
        current_ver = (dict(row).get("version") if hasattr(row, "keys") else row[0]) if row else None
        if current_ver == "20261127_7staff_ktv":
            return

        phone_updates = [
            ("0911761707", "le_dinh_tu"),
            ("0327087363", "nguyen_truong_duy"),
            ("0389948626", "le_phat_dai"),
            ("0325858123", "tong_mong_tien"),
        ]
        for phone, uname in phone_updates:
            cursor.execute(
                "UPDATE users SET phone = ?, status = 'active', updated_at = CURRENT_TIMESTAMP WHERE username = ?",
                (phone, uname),
            )

        default_pw = hash_password("123456")
        new_staff = [
            (
                "ly_thi_my_loan", default_pw, "Lý Thị Mỹ Loan",
                "Kỹ Thuật Viên Xét Nghiệm", "ktv", "Ly_Thi_My_Loan",
                "2001", "0364740976", "loan.lythimy@thienanhospital.vn",
                "", "", "", "", "Size đồng phục: M nữ"
            ),
            (
                "truong_huynh_anh_thu", default_pw, "Trương Huỳnh Anh Thư",
                "Kỹ Thuật Viên Xét Nghiệm", "ktv", "Truong_Huynh_Anh_Thu",
                "2000", "03773030260", "thu.truonghuynhanh@thienanhospital.vn",
                "", "", "", "", "Size đồng phục: M nữ • Nhận đồ rồi"
            ),
            (
                "phan_ngoc_nhu", default_pw, "Phan Ngọc Như",
                "Kỹ Thuật Viên Xét Nghiệm", "ktv", "Phan_Ngoc_Nhu",
                "1995", "0399496533", "nhu.phanngoc@thienanhospital.vn",
                "", "", "", "", "Size đồng phục: L nữ • Nhận đồ rồi"
            ),
        ]

        for member in new_staff:
            cursor.execute("SELECT id FROM users WHERE username = ?", (member[0],))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO users (
                        username, password_hash, full_name, title, role, folder_name,
                        dob, phone, email, cchn, cchn_date, cchn_scope, education, specialty
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, member)
            else:
                cursor.execute(
                    "UPDATE users SET title = ?, specialty = ?, status = 'active', updated_at = CURRENT_TIMESTAMP WHERE username = ?",
                    (member[3], member[13], member[0]),
                )

        cursor.execute("""
            INSERT INTO qaqc_store (store_key, data_json, version, updated_by)
            VALUES ('staff_sync_20261127', '{"count": 7}', '20261127_7staff_ktv', 'system')
            ON CONFLICT(store_key) DO UPDATE SET
                data_json = excluded.data_json,
                version = excluded.version,
                updated_at = CURRENT_TIMESTAMP
        """)
    except Exception as e:
        print("Sync staff list warning:", e)

def _seed_users(cursor):
    """Seed the 4 personnel of the department."""
    cursor.execute("SELECT COUNT(*) FROM users")
    first_res = cursor.fetchone()
    count = first_res[0] if first_res else 0
    if count > 0:
        return

    default_pw = hash_password("123456")
    staff_list = [
        (
            "le_dinh_tu", default_pw, "CN. Lê Đình Tú",
            "Trưởng Khoa Xét Nghiệm", "truong_khoa", "Le_Dinh_Tu",
            "1988-06-15", "0908123456", "tu.ledinh@thienanhospital.vn",
            "006321/VL-CCHN", "2017-08-10", "Chuyên khoa Xét nghiệm y học",
            "Cử nhân / Bác sĩ Xét nghiệm", "Phụ trách chuyên môn, duyệt kết quả & Quản lý chất lượng"
        ),
        (
            "nguyen_truong_duy", default_pw, "CN. Nguyễn Trường Duy",
            "Kỹ Thuật Viên Trưởng", "ktv_truong", "Nguyen_Truong_Duy",
            "1992-03-10", "0939112233", "duy.nguyen@thienanhospital.vn",
            "005891/VL-CCHN", "2019-04-12", "Kỹ thuật viên Xét nghiệm y học",
            "Cử nhân Xét nghiệm Y học", "Quản lý điều hành khoa, xếp lịch trực, thiết bị & ATSH"
        ),
        (
            "le_phat_dai", default_pw, "CN. Lê Phát Đại",
            "Kỹ Thuật Viên Xét Nghiệm", "ktv", "Le_Phat_Dai",
            "1996-08-20", "0918556677", "dai.lephat@thienanhospital.vn",
            "008452/VL-CCHN", "2022-03-15", "Kỹ thuật viên Xét nghiệm",
            "Cử nhân Xét nghiệm Y học", "Vận hành phòng máy Hóa sinh - Huyết học, Lấy máu"
        ),
        (
            "tong_mong_tien", default_pw, "CN. Tống Mọng Tiền",
            "KTV Lấy Máu & Test Nhanh", "ktv", "Tong_Mong_Tien",
            "1998-10-12", "0972445566", "tien.tongmong@thienanhospital.vn",
            "009124/VL-CCHN", "2023-05-20", "Kỹ thuật viên Xét nghiệm",
            "Cử nhân Xét nghiệm Y học", "Tiếp nhận bệnh phẩm, Lấy máu ngoại trú & Test nhanh"
        ),
    ]

    cursor.executemany("""
    INSERT INTO users (
        username, password_hash, full_name, title, role, folder_name,
        dob, phone, email, cchn, cchn_date, cchn_scope, education, specialty
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, staff_list)

def _seed_positions(cursor):
    """Seed department work positions."""
    cursor.execute("SELECT COUNT(*) FROM positions")
    first_res = cursor.fetchone()
    count = first_res[0] if first_res else 0
    if count > 0:
        return

    positions = [
        ("BLOOD_1", "Bàn lấy máu 01 (Ngoại trú)", "blood", "Tiếp nhận & Lấy máu bệnh nhân ngoại trú thường", 1),
        ("BLOOD_2", "Bàn lấy máu 02 (Khám SK - Đoàn)", "blood", "Lấy máu đoàn khám sức khỏe công ty, trường học", 2),
        ("BLOOD_3", "Bàn lấy máu 03 (Nhi - Phụ sản)", "blood", "Lấy máu trẻ nhỏ, phụ nữ mang thai, ưu tiên cao", 3),
        ("BLOOD_4", "Bàn lấy máu 04 (VIP / Cấp cứu)", "blood", "Lấy máu khu khám VIP, khách hẹn trước & cấp cứu", 4),
        ("MACH_HEM", "Phòng máy Huyết học", "machine", "Vận hành máy tổng phân tích tế bào máu Celldiff 580", 10),
        ("MACH_BIO", "Phòng máy Sinh hóa - Miễn dịch", "machine", "Vận hành hệ thống Monarch 1000/600, xét nghiệm hóa sinh", 11),
        ("MACH_COAG", "Phòng máy Đông máu", "machine", "Vận hành máy đo đông máu tự động Thrombo, PT, APTT, Fibrinogen", 12),
        ("MACH_ELEC", "Phòng máy Điện giải", "machine", "Vận hành máy điện giải đồ Na+, K+, Cl-, Ca++", 13),
        ("MACH_URI", "Phòng Nước tiểu & Test nhanh", "machine", "Vận hành máy phân tích 10-14 thông số nước tiểu, test nhanh", 14),
        ("WAREHOUSE", "Kho Hóa chất & Vật tư tiêu hao", "warehouse", "Kiểm kê, xuất nhập tồn hóa chất, chuẩn bị vật tư lấy máu", 20),
        ("QUALITY_2429", "Quản lý Sổ sách & Hồ sơ 2429", "quality_2429", "Ghi chép nhiệt độ phòng/tủ lạnh, kiểm soát IQC/EQC, bảo dưỡng", 30),
        ("ON_DUTY", "Thường trực cấp cứu 24h", "direct", "Phụ trách xét nghiệm cấp cứu ban đêm và trực ngày nghỉ", 40),
    ]

    cursor.executemany("""
    INSERT INTO positions (code, name, category, description, sort_order)
    VALUES (?, ?, ?, ?, ?)
    """, positions)

def _seed_sample_schedules(cursor):
    """Seed sample assignments for current week so schedule is immediately visible."""
    cursor.execute("SELECT COUNT(*) FROM schedules")
    first_res = cursor.fetchone()
    count = first_res[0] if first_res else 0
    if count > 0:
        return

    cursor.execute("SELECT id, username FROM users")
    users = {row["username"]: row["id"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, code FROM positions")
    positions = {row["code"]: row["id"] for row in cursor.fetchall()}

    admin_id = users.get("le_dinh_tu", 1)
    today = datetime.date.today()
    assignments = [
        ("sang", "BLOOD_1", "le_phat_dai"),
        ("sang", "BLOOD_2", "tong_mong_tien"),
        ("sang", "BLOOD_3", "le_phat_dai"),
        ("sang", "BLOOD_4", "tong_mong_tien"),
        ("sang", "MACH_HEM", "le_phat_dai"),
        ("sang", "MACH_BIO", "le_phat_dai"),
        ("sang", "MACH_COAG", "tong_mong_tien"),
        ("sang", "MACH_URI", "tong_mong_tien"),
        ("sang", "WAREHOUSE", "nguyen_truong_duy"),
        ("sang", "QUALITY_2429", "nguyen_truong_duy"),
        ("sang", "ON_DUTY", "le_dinh_tu"),
        ("chieu", "BLOOD_1", "tong_mong_tien"),
        ("chieu", "BLOOD_2", "le_phat_dai"),
        ("chieu", "BLOOD_3", "tong_mong_tien"),
        ("chieu", "BLOOD_4", "le_phat_dai"),
        ("chieu", "MACH_HEM", "le_phat_dai"),
        ("chieu", "MACH_BIO", "le_phat_dai"),
        ("chieu", "MACH_COAG", "tong_mong_tien"),
        ("chieu", "MACH_URI", "tong_mong_tien"),
        ("chieu", "WAREHOUSE", "nguyen_truong_duy"),
        ("chieu", "QUALITY_2429", "nguyen_truong_duy"),
        ("chieu", "ON_DUTY", "le_dinh_tu"),
        ("truc", "ON_DUTY", "nguyen_truong_duy"),
    ]

    for d in range(7):
        cur_date = (today + datetime.timedelta(days=d)).strftime("%Y-%m-%d")
        for shift, pos_code, uname in assignments:
            pos_id = positions.get(pos_code)
            u_id = users.get(uname)
            if pos_id and u_id:
                try:
                    cursor.execute("""
                    INSERT INTO schedules (work_date, shift, position_id, user_id, created_by)
                    VALUES (?, ?, ?, ?, ?)
                    """, (cur_date, shift, pos_id, u_id, admin_id))
                except Exception:
                    pass

def _seed_documents_from_disk(cursor):
    """Scan disk and register forms if on local drive."""
    try:
        cursor.execute("SELECT COUNT(*) FROM documents")
        first_res = cursor.fetchone()
        count = first_res[0] if first_res else 0
        if count > 0:
            return

        doc_meta = [
            ("01_PHIEU_HEN_TRA_KET_QUA_XET_NGHIEM", "phieu_kq_hen", "PH-XN-01", "Phiếu Hẹn Trả Kết Quả Xét Nghiệm"),
            ("02_PHIEU_KET_QUA_TEST_NHANH_TONG_HOP_16_THONG_SO", "phieu_kq_hen", "KQ-TN-16TS", "Phiếu Kết Quả Test Nhanh Tổng Hợp 16 Thông Số"),
            ("03_PHIEU_KET_QUA_TEST_NHANH_TIEN_PHAU_DONG_MAU", "phieu_kq_hen", "KQ-TN-TPDM", "Phiếu Kết Quả Test Nhanh Tiền Phẫu & Đông Máu"),
            ("04_PHIEU_KET_QUA_TEST_NHANH_KSK_XUAT_KHAU_LAO_DONG", "phieu_kq_hen", "KQ-KSK-XKLĐ", "Phiếu Kết Quả Test Nhanh Khám Sức Khỏe XKLĐ"),
            ("05_PHIEU_KET_QUA_TEST_HOI_THO_HP_C13_C14", "phieu_kq_hen", "KQ-HP-C13C14", "Phiếu Kết Quả Test Hơi Thở HP (C13 / C14)"),
            ("06_PHIEU_KET_QUA_HUYET_TRANG_SOI_TUOI_NHUOM_SOI", "phieu_kq_hen", "KQ-HT-STNS", "Phiếu Kết Quả Huyết Trắng Soi Tươi & Nhuộm Soi"),
            ("08_SO_THEO_DOI_GIAO_NHAN_MAU_BENH_PHAM", "so_sach_2429", "XN.QTQL.5.08", "Sổ Theo Dõi Giao Nhận Mẫu Bệnh Phẩm"),
            ("09_SO_THEO_DOI_NHIET_DO_DO_AM_PHONG_XET_NGHIEM", "so_sach_2429", "XN.QTQL.5.12", "Sổ Theo Dõi Nhiệt Độ & Độ Ẩm Phòng Xét Nghiệm"),
            ("10_SO_THEO_DOI_NHIET_DO_TU_LANH_LUU_MAU_2_8_DO_C", "so_sach_2429", "XN.QTQL.5.13", "Sổ Theo Dõi Nhiệt Độ Tủ Lạnh Lưu Mẫu 2 - 8°C"),
            ("11_PHIEU_THEO_DOI_KHU_NHIEM_TRANG_THIET_BI", "so_sach_2429", "K47-QTQL-27", "Phiếu Theo Dõi Khử Nhiễm Trang Thiết Bị Hằng Ngày"),
            ("12_NHAT_KY_VAN_HANH_BAO_DUONG_THIET_BI_HANG_NGAY", "so_sach_2429", "K47-QTQL-42", "Nhật Ký Vận Hành & Bảo Dưỡng Thiết Bị Hằng Ngày"),
            ("13_BIEN_BAN_THANH_HUY_HOA_CHAT_VA_MAU_BENH_PHAM", "so_sach_2429", "K47-QTQL-50", "Biên Bản Thanh Hủy Hóa Chất & Mẫu Bệnh Phẩm Quá Hạn"),
            ("07_BAN_GIAO_VA_BAO_CAO_THUONG_TRUC_GIAO_BAN", "bia_hanh_chinh", "PL-HC-07", "Bản Giao Ban & Báo Cáo Thường Trực"),
            ("14_DON_XIN_NGHI_PHEP_NGHI_BU_DOI_CA", "bia_hanh_chinh", "PL8", "Đơn Xin Nghỉ Phép / Nghỉ Bù / Đổi Ca"),
            ("15_BANG_KIEM_DINH_HUONG_NHAN_VIEN_MOI_BM02", "bia_hanh_chinh", "BM02-NS", "Bảng Kiểm Định Hướng Nhân Viên Mới"),
            ("TRON_BO_BIEU_MAU_IN_SAN_KHOA_XET_NGHIEM", "bia_hanh_chinh", "BIA-TRON-BO", "Trọn Bộ Bìa Hồ Sơ & Biểu Mẫu In Sẵn Khoa Xét Nghiệm"),
        ]

        cat_folders = {
            "phieu_kq_hen": BIEU_MAU_PHIEU_KQ,
            "so_sach_2429": BIEU_MAU_2429,
            "bia_hanh_chinh": BIEU_MAU_HANH_CHINH,
        }

        for base_name, cat, code, title in doc_meta:
            folder = cat_folders.get(cat)
            if not folder or not folder.exists():
                continue
            for ext in ["docx", "pdf"]:
                f_name = f"{base_name}.{ext}"
                f_path = folder / f_name
                if f_path.exists():
                    size = f_path.stat().st_size
                    cursor.execute("""
                    INSERT INTO documents (
                        category, code, title, file_name, file_ext, file_path, file_size, version, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, '1.0', ?)
                    """, (cat, code, f"{title} ({ext.upper()})", f_name, ext, str(f_path), size, f"Biểu mẫu chuẩn Khoa Xét nghiệm - BV Thiên Ân Viễn Đông ({ext.upper()})"))
    except Exception:
        pass

def _seed_employee_files_from_disk(cursor):
    """Scan disk and link existing CVs/job descriptions if on local drive."""
    try:
        cursor.execute("SELECT id, folder_name FROM users")
        users = cursor.fetchall()
        for u in users:
            u_id = u["id"]
            folder_name = u["folder_name"]
            u_dir = HO_SO_DIR / folder_name
            if u_dir.exists():
                for f in u_dir.iterdir():
                    if f.is_file():
                        cursor.execute("""
                        SELECT id FROM employee_files WHERE user_id = ? AND file_name = ?
                        """, (u_id, f.name))
                        if not cursor.fetchone():
                            cursor.execute("""
                            INSERT INTO employee_files (
                                user_id, doc_type, title, file_name, file_path, file_size
                            ) VALUES (?, 'mo_ta_cv', ?, ?, ?, ?)
                            """, (u_id, f"Bản mô tả công việc nhân viên ({f.name})", f.name, str(f), f.stat().st_size))
    except Exception:
        pass
