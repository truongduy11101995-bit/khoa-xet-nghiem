import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent

# Automatically load .env file if present
env_file = APP_DIR / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

# Environment configurations
APP_ENV = os.getenv("APP_ENV", "production")
SECRET_KEY = os.getenv("SECRET_KEY", "thien-an-vien-dong-khoa-xet-nghiem-super-secure-key-2429")
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", 24 * 7))

# Cloud Database configuration (Neon / Supabase PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

# IP Whitelisting & Office Wi-Fi Protection (Set to "*" for always open to all networks)
ALLOWED_OFFICE_IPS = os.getenv("ALLOWED_OFFICE_IPS", "*").strip()

# Admin Emergency Bypass Password for remote access / dynamic IP updates
ADMIN_BYPASS_KEY = os.getenv("ADMIN_BYPASS_KEY", "ThienAn2026@BypassLab").strip()

# Local Base Paths (Fallback if DATABASE_URL is not set)
DATA_ROOT = Path("D:/KHOA_XET_NGHIEM_DATA")
if not os.path.exists("D:/"):
    DATA_ROOT = APP_DIR / "data_storage"

DB_DIR = DATA_ROOT / "DATABASE"
DB_PATH = DB_DIR / "khoa_xet_nghiem.db"

BIEU_MAU_DIR = DATA_ROOT / "BIEU_MAU"
BIEU_MAU_PHIEU_KQ = BIEU_MAU_DIR / "Phieu_KQ_Phieu_Hen"
BIEU_MAU_2429 = BIEU_MAU_DIR / "So_Sach_2429"
BIEU_MAU_HANH_CHINH = BIEU_MAU_DIR / "Bia_Ho_So_Hanh_Chinh"
HO_SO_10_CUON_DIR = DATA_ROOT / "HO_SO_10_CUON"

HO_SO_DIR = DATA_ROOT / "HO_SO_NHAN_SU"
FRONTEND_DIR = APP_DIR / "frontend"

# Hospital Branding
HOSPITAL_NAME = "BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG"
DEPARTMENT_NAME = "KHOA XÉT NGHIỆM"
STANDARD_NAME = "HỆ THỐNG QUẢN LÝ CHẤT LƯỢNG THEO QUYẾT ĐỊNH 2429/QĐ-BYT"

MAX_ACTIVE_STAFF = 8

def init_directories():
    """Ensure all required directories exist on local drive or cloud fallback."""
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        BIEU_MAU_PHIEU_KQ.mkdir(parents=True, exist_ok=True)
        BIEU_MAU_2429.mkdir(parents=True, exist_ok=True)
        BIEU_MAU_HANH_CHINH.mkdir(parents=True, exist_ok=True)
        HO_SO_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
