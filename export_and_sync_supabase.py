import sqlite3
import sys
import os
from pathlib import Path

# Paths
APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path("D:/KHOA_XET_NGHIEM_DATA/DATABASE/khoa_xet_nghiem.db")
if not DB_PATH.exists():
    DB_PATH = APP_DIR / "data_storage" / "DATABASE" / "khoa_xet_nghiem.db"

OUTPUT_SQL = APP_DIR / "import_data_to_supabase.sql"

def escape_sql_val(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    # String
    escaped = str(val).replace("'", "''")
    return f"'{escaped}'"

def export_sqlite_to_sql_file():
    print(f"Reading SQLite database from: {DB_PATH}")
    if not DB_PATH.exists():
        print(f"ERROR: Database file {DB_PATH} not found!")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    tables = [
        "users",
        "positions",
        "schedules",
        "leave_requests",
        "documents",
        "employee_files",
        "system_logs",
        "allowed_ips"
    ]

    with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
        f.write("-- =========================================================================\n")
        f.write("-- DỮ LIỆU ĐỒNG BỘ TỪ HỆ THỐNG CŨ LÊN CLOUD SUPABASE (POSTGRESQL)\n")
        f.write("-- Bệnh viện Đa khoa Thiên Ân - Viễn Đông | Khoa Xét nghiệm\n")
        f.write("-- =========================================================================\n\n")

        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                if not rows:
                    continue

                col_names = [col[0] for col in cursor.description]
                f.write(f"\n-- DATA FOR TABLE: {table} ({len(rows)} rows)\n")

                for row in rows:
                    cols_str = ", ".join(col_names)
                    vals_str = ", ".join(escape_sql_val(row[col]) for col in col_names)
                    
                    if table == "users":
                        f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str}) ON CONFLICT (username) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;\n")
                    elif table == "positions":
                        f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str}) ON CONFLICT (code) DO NOTHING;\n")
                    elif table == "schedules":
                        f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str}) ON CONFLICT (work_date, shift, position_id) DO NOTHING;\n")
                    else:
                        f.write(f"INSERT INTO {table} ({cols_str}) VALUES ({vals_str}) ON CONFLICT DO NOTHING;\n")

                # Reset sequence for PostgreSQL auto-increment IDs
                f.write(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1));\n")

            except Exception as e:
                print(f"Table {table} skipped or not found: {e}")

    conn.close()
    print(f"EXPORT COMPLETE! File saved to: {OUTPUT_SQL}")
    return True

def sync_direct_to_supabase(db_url):
    """Directly push data to Supabase using connection string."""
    print(f"Connecting directly to Supabase PostgreSQL...")
    sys.path.insert(0, str(APP_DIR))
    from backend.db_adapter import connect_postgres
    pg_conn = connect_postgres(db_url)
    pg_cursor = pg_conn.cursor()

    # Read exported SQL
    with open(OUTPUT_SQL, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Execute statement by statement
    statements = [stmt.strip() for stmt in sql_content.split(";\n") if stmt.strip() and not stmt.strip().startswith("--")]
    print(f"Executing {len(statements)} SQL statements on Supabase...")

    success_count = 0
    for stmt in statements:
        if not stmt:
            continue
        try:
            pg_cursor.execute(stmt)
            success_count += 1
        except Exception as e:
            print(f"Notice during statement execution: {e}")

    pg_conn.commit()
    pg_conn.close()
    print(f"SYNC SUCCESSFUL! {success_count}/{len(statements)} statements committed to Supabase!")

if __name__ == "__main__":
    export_sqlite_to_sql_file()

    # Check if DATABASE_URL was provided as argument or in env
    db_target = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DATABASE_URL")
    if db_target and db_target.startswith(("postgres://", "postgresql://")):
        sync_direct_to_supabase(db_target)
    else:
        print("\nĐể đồng bộ tự động lên Supabase ngay từ máy này, chạy lệnh:")
        print("  python export_and_sync_supabase.py \"postgresql://postgres:MAT_KHAU@db.xxx.supabase.co:5432/postgres\"")
        print("Hoặc mở file 'import_data_to_supabase.sql' vừa tạo và copy-paste vào Supabase SQL Editor!")
