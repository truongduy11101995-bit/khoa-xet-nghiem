-- =========================================================================
-- BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG | KHOA XÉT NGHIỆM
-- HỆ THỐNG QUẢN LÝ CHẤT LƯỢNG & CHẤM CÔNG THEO QUYẾT ĐỊNH 2429/QĐ-BYT
-- CƠ SỞ DỮ LIỆU CLOUD SUPABASE (POSTGRESQL) - MIỄN PHÍ 24/7
-- =========================================================================

-- Bật extension mở rộng nếu cần
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. BẢNG TÀI KHOẢN NHÂN VIÊN (USERS)
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

-- 2. BẢNG VỊ TRÍ CÔNG TÁC TRONG KHOA (POSITIONS)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL CHECK(category IN ('blood', 'machine', 'warehouse', 'quality_2429', 'direct')),
    description TEXT,
    sort_order INTEGER DEFAULT 0
);

-- 3. BẢNG PHÂN CÔNG LỊCH LÀM VIỆC & TRỰC (SCHEDULES)
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

-- 4. BẢNG ĐƠN XIN NGHỈ PHÉP / NGHỈ BÙ (LEAVE REQUESTS)
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

-- 5. BẢNG HUB BIỂU MẪU 2429 & SỔ SÁCH (DOCUMENTS)
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

-- 6. BẢNG HỒ SƠ TÀI LIỆU CÁ NHÂN NHÂN VIÊN (EMPLOYEE FILES)
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

-- 7. BẢNG NHẬT KÝ HỆ THỐNG (SYSTEM LOGS)
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. BẢNG DANH SÁCH IP WI-FI ĐƯỢC PHÉP TRUY CẬP (ALLOWED IPS)
CREATE TABLE IF NOT EXISTS allowed_ips (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    added_by VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- TẠO CHỈ MỤC (INDEXES) TỐI ƯU HIỆU NĂNG TRUY VẤN
CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(work_date);
CREATE INDEX IF NOT EXISTS idx_schedules_user ON schedules(user_id);
CREATE INDEX IF NOT EXISTS idx_leave_user ON leave_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_leave_date ON leave_requests(leave_date);
CREATE INDEX IF NOT EXISTS idx_documents_cat ON documents(category);
