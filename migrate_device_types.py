import sys
from pathlib import Path

app_dir = Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
sys.path.insert(0, str(app_dir))

from backend.database import get_db, is_cloud_db

def migrate():
    conn = get_db()
    cursor = conn.cursor()
    cloud = is_cloud_db()
    print(f"Migrating environment_logs table (cloud={cloud})...")

    # Add columns if not exists
    columns_to_add = [
        ("fridge_sample_temp", "REAL"),
        ("incubator_temp", "REAL"),
        ("target_device", "VARCHAR(100) DEFAULT 'all'")
    ]

    for col, col_type in columns_to_add:
        try:
            if cloud:
                cursor.execute(f"ALTER TABLE environment_logs ADD COLUMN IF NOT EXISTS {col} {col_type};")
            else:
                cursor.execute(f"ALTER TABLE environment_logs ADD COLUMN {col} {col_type};")
            print(f"Added column: {col}")
        except Exception as e:
            print(f"Column {col} notice/already exists: {e}")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
