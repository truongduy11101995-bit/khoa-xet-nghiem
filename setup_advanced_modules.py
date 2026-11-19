import sys
import datetime
from pathlib import Path

app_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(app_dir))

from backend.database import get_db, is_cloud_db

def init_advanced_tables():
    conn = get_db()
    cursor = conn.cursor()
    cloud = is_cloud_db()
    print(f"Creating advanced tables (cloud={cloud})...")

    # Table 1: open_vials
    if cloud:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS open_vials (
            id SERIAL PRIMARY KEY,
            item_id INTEGER,
            item_code VARCHAR(50) NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            lot_number VARCHAR(100),
            vial_label VARCHAR(100) DEFAULT 'Lọ 01',
            open_date VARCHAR(50) NOT NULL,
            open_time VARCHAR(20) DEFAULT '08:00',
            stability_days INTEGER DEFAULT 30,
            expiry_date VARCHAR(50) NOT NULL,
            location VARCHAR(100) DEFAULT 'Máy sinh hóa',
            opened_by INTEGER REFERENCES users(id),
            opened_by_name VARCHAR(100),
            status VARCHAR(50) DEFAULT 'active',
            discard_reason TEXT,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS environment_logs (
            id SERIAL PRIMARY KEY,
            log_date VARCHAR(50) NOT NULL,
            shift VARCHAR(20) NOT NULL,
            log_time VARCHAR(20) NOT NULL,
            logged_by INTEGER REFERENCES users(id),
            logged_by_name VARCHAR(100),
            room_temp REAL NOT NULL,
            room_humidity REAL NOT NULL,
            fridge_temp REAL NOT NULL,
            freezer_temp REAL NOT NULL,
            is_safe BOOLEAN DEFAULT TRUE,
            warning_note TEXT,
            action_taken TEXT,
            reviewer_id INTEGER REFERENCES users(id),
            reviewer_name VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_env_date_shift UNIQUE(log_date, shift)
        );
        """)
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS open_vials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            item_code TEXT NOT NULL,
            item_name TEXT NOT NULL,
            lot_number TEXT,
            vial_label TEXT DEFAULT 'Lọ 01',
            open_date TEXT NOT NULL,
            open_time TEXT DEFAULT '08:00',
            stability_days INTEGER DEFAULT 30,
            expiry_date TEXT NOT NULL,
            location TEXT DEFAULT 'Máy sinh hóa',
            opened_by INTEGER REFERENCES users(id),
            opened_by_name TEXT,
            status TEXT DEFAULT 'active',
            discard_reason TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS environment_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            shift TEXT NOT NULL,
            log_time TEXT NOT NULL,
            logged_by INTEGER REFERENCES users(id),
            logged_by_name TEXT,
            room_temp REAL NOT NULL,
            room_humidity REAL NOT NULL,
            fridge_temp REAL NOT NULL,
            freezer_temp REAL NOT NULL,
            is_safe INTEGER DEFAULT 1,
            warning_note TEXT,
            action_taken TEXT,
            reviewer_id INTEGER REFERENCES users(id),
            reviewer_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(log_date, shift)
        );
        """)

    conn.commit()

    # Seed initial active open vials if empty
    cursor.execute("SELECT COUNT(*) FROM open_vials")
    vial_count = cursor.fetchone()[0]
    if vial_count == 0:
        today = datetime.date.today()
        sample_vials = [
            (
                "SH-GLU-16", "Glucose GOD PAP", "LOT2616", "Lọ R1 (60ml)",
                (today - datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "07:45", 30,
                (today - datetime.timedelta(days=10) + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                "Máy sinh hóa tự động", 3, "CN. Lê Phát Đại", "active", "Đang chạy trên máy số 01"
            ),
            (
                "SH-URE-41", "Urea Reagent kit", "LOT2641", "Lọ R1+R2",
                (today - datetime.timedelta(days=15)).strftime("%Y-%m-%d"), "08:15", 30,
                (today - datetime.timedelta(days=15) + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                "Máy sinh hóa tự động", 4, "CN. Tống Mọng Tiền", "active", "Kiểm tra QC đạt yêu cầu"
            ),
            (
                "SH-CRE-35", "CREATININE (Enzymatic Method)", "LOT2635", "Lọ R1+R2 (BSBE)",
                (today - datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "07:30", 28,
                (today - datetime.timedelta(days=5) + datetime.timedelta(days=28)).strftime("%Y-%m-%d"),
                "Máy sinh hóa tự động", 3, "CN. Lê Phát Đại", "active", "Phương pháp Enzymatic dải rộng"
            ),
            (
                "SH-ALT-05", "ALT(GPT)", "LOT2605", "Lọ R1 (30ml)",
                (today - datetime.timedelta(days=22)).strftime("%Y-%m-%d"), "08:00", 30,
                (today - datetime.timedelta(days=22) + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
                "Máy sinh hóa tự động", 2, "CN. Nguyễn Trường Duy", "active", "Sắp hết hạn mở nắp (còn 8 ngày)"
            ),
            (
                "MD-HBSAG-61", "Maccura HBsAg CLIA", "LOT2661", "Hộp 100 Test",
                (today - datetime.timedelta(days=12)).strftime("%Y-%m-%d"), "09:00", 56,
                (today - datetime.timedelta(days=12) + datetime.timedelta(days=56)).strftime("%Y-%m-%d"),
                "Máy miễn dịch Maccura", 1, "CN. Lê Đình Tú", "active", "Mở khay hóa chất miễn dịch"
            )
        ]

        for v in sample_vials:
            cursor.execute("""
            INSERT INTO open_vials (
                item_code, item_name, lot_number, vial_label, open_date, open_time,
                stability_days, expiry_date, location, opened_by, opened_by_name, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, v)
        conn.commit()
        print(f"Seeded {len(sample_vials)} sample open vials.")

    # Seed environment logs for November 2026 up to today
    cursor.execute("SELECT COUNT(*) FROM environment_logs")
    env_count = cursor.fetchone()[0]
    if env_count == 0:
        today = datetime.date.today()
        staff_names = {
            1: "CN. Lê Đình Tú",
            2: "CN. Nguyễn Trường Duy",
            3: "CN. Lê Phát Đại",
            4: "CN. Tống Mọng Tiền"
        }

        # Seed from 1st of month to today
        import random
        random.seed(42)
        start_day = datetime.date(today.year, today.month, 1)
        curr = start_day
        seeded = 0

        while curr <= today:
            d_str = curr.strftime("%Y-%m-%d")
            # Morning log (08:00)
            u_id = ((curr.day % 4) + 1)
            u_name = staff_names[u_id]
            r_temp_m = round(21.5 + random.uniform(-1.0, 1.2), 1)
            r_hum_m = round(58.0 + random.uniform(-4.0, 6.0), 1)
            fridge_m = round(4.2 + random.uniform(-0.8, 1.0), 1)
            freezer_m = round(-21.0 + random.uniform(-1.5, 1.5), 1)

            is_safe_val = True if cloud else 1
            cursor.execute("""
            INSERT INTO environment_logs (
                log_date, shift, log_time, logged_by, logged_by_name,
                room_temp, room_humidity, fridge_temp, freezer_temp,
                is_safe, warning_note, action_taken, reviewer_name
            ) VALUES (?, 'sang', '08:00', ?, ?, ?, ?, ?, ?, ?, '', '', 'CN. Lê Đình Tú')
            """, (d_str, u_id, u_name, r_temp_m, r_hum_m, fridge_m, freezer_m, is_safe_val))
            seeded += 1

            # Afternoon log (14:00)
            u_id2 = (((curr.day + 1) % 4) + 1)
            u_name2 = staff_names[u_id2]
            r_temp_a = round(22.8 + random.uniform(-0.8, 1.4), 1)
            r_hum_a = round(61.0 + random.uniform(-3.0, 5.0), 1)
            fridge_a = round(4.6 + random.uniform(-0.7, 1.1), 1)
            freezer_a = round(-20.5 + random.uniform(-1.2, 1.2), 1)

            cursor.execute("""
            INSERT INTO environment_logs (
                log_date, shift, log_time, logged_by, logged_by_name,
                room_temp, room_humidity, fridge_temp, freezer_temp,
                is_safe, warning_note, action_taken, reviewer_name
            ) VALUES (?, 'chieu', '14:00', ?, ?, ?, ?, ?, ?, ?, '', '', 'CN. Lê Đình Tú')
            """, (d_str, u_id2, u_name2, r_temp_a, r_hum_a, fridge_a, freezer_a, is_safe_val))
            seeded += 1

            curr += datetime.timedelta(days=1)

        conn.commit()
        print(f"Seeded {seeded} environment log entries for the month.")

    conn.close()
    print("Advanced tables setup completed successfully!")

if __name__ == "__main__":
    init_advanced_tables()
