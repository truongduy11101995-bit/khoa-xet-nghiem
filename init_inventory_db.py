import sys
import os
import json
from pathlib import Path

app_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(app_dir))

from backend.database import get_db, is_cloud_db

def setup_inventory():
    conn = get_db()
    cursor = conn.cursor()
    cloud = is_cloud_db()

    print(f"Connecting to database (cloud={cloud})...")

    # Table: inventory_items
    if cloud:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_items (
            id SERIAL PRIMARY KEY,
            code VARCHAR(50) NOT NULL,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            unit VARCHAR(50) NOT NULL,
            spec VARCHAR(100),
            manufacturer VARCHAR(150),
            lot_number VARCHAR(100),
            expiry_date VARCHAR(50),
            storage_temp VARCHAR(50) DEFAULT '2-8°C',
            quantity REAL DEFAULT 0,
            min_stock REAL DEFAULT 0,
            monthly_usage REAL DEFAULT 0,
            unit_price REAL DEFAULT 0,
            open_date VARCHAR(50),
            open_expiry_days INTEGER DEFAULT 0,
            location VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_forecasts (
            id SERIAL PRIMARY KEY,
            period VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'draft',
            created_by INTEGER REFERENCES users(id),
            total_cost REAL DEFAULT 0,
            items_json TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit TEXT NOT NULL,
            spec TEXT,
            manufacturer TEXT,
            lot_number TEXT,
            expiry_date TEXT,
            storage_temp TEXT DEFAULT '2-8°C',
            quantity REAL DEFAULT 0,
            min_stock REAL DEFAULT 0,
            monthly_usage REAL DEFAULT 0,
            unit_price REAL DEFAULT 0,
            open_date TEXT,
            open_expiry_days INTEGER DEFAULT 0,
            location TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            created_by INTEGER REFERENCES users(id),
            total_cost REAL DEFAULT 0,
            items_json TEXT NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

    conn.commit()

    # Seed initial items if empty
    cursor.execute("SELECT COUNT(*) FROM inventory_items")
    first_res = cursor.fetchone()
    count = first_res[0] if first_res else 0

    if count == 0:
        print("Seeding inventory items for Khoa Xét Nghiệm BVĐK Thiên Ân...")
        initial_items = [
            # Hóa sinh
            ("HC-GLU", "Hóa chất Glucose AU", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L84920", "2027-08-15", "2-8°C", 12, 5, 12, 650000, "2026-11-10", 30, "Tủ lạnh 2-8°C Ngăn 1", "Chạy máy AU480"),
            ("HC-UREA", "Hóa chất Urea / BUN AU", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L84921", "2027-06-20", "2-8°C", 9, 4, 9, 720000, "2026-11-05", 30, "Tủ lạnh 2-8°C Ngăn 1", "Chạy máy AU480"),
            ("HC-CREAT", "Hóa chất Creatinine Enzymatic AU", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L84922", "2027-09-10", "2-8°C", 10, 6, 14, 850000, "2026-11-12", 30, "Tủ lạnh 2-8°C Ngăn 1", "Chạy máy AU480"),
            ("HC-AST", "Hóa chất Men gan AST (GOT) AU", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L85101", "2027-05-18", "2-8°C", 7, 3, 7, 780000, "2026-11-01", 30, "Tủ lạnh 2-8°C Ngăn 2", "Chạy máy AU480"),
            ("HC-ALT", "Hóa chất Men gan ALT (GPT) AU", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L85102", "2027-05-18", "2-8°C", 7, 3, 7, 780000, "2026-11-01", 30, "Tủ lạnh 2-8°C Ngăn 2", "Chạy máy AU480"),
            ("HC-CHOL", "Hóa chất Cholesterol toàn phần", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L85230", "2027-10-12", "2-8°C", 9, 4, 8, 690000, "2026-11-08", 30, "Tủ lạnh 2-8°C Ngăn 2", "Chạy máy AU480"),
            ("HC-TRIG", "Hóa chất Triglyceride AU", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L85231", "2027-11-05", "2-8°C", 9, 4, 9, 820000, "2026-11-08", 30, "Tủ lạnh 2-8°C Ngăn 2", "Chạy máy AU480"),
            ("HC-URIC", "Hóa chất Acid Uric AU", "hoa_chat", "Hộp", "4 x 50ml", "Beckman Coulter", "L85340", "2027-07-22", "2-8°C", 6, 3, 5, 750000, "2026-11-14", 30, "Tủ lạnh 2-8°C Ngăn 3", "Chạy máy AU480"),
            ("HC-HBA1C", "Kit định lượng HbA1c Direct", "hoa_chat", "Kit", "100 test", "Bio-Rad", "L85499", "2027-01-15", "2-8°C", 3, 3, 5, 2300000, "2026-11-02", 45, "Tủ lạnh 2-8°C Ngăn 3", "Cảnh báo cận định mức tối thiểu"),
            ("HC-ELE", "Dung dịch điện giải Điện cực AU (Na/K/Cl)", "hoa_chat", "Hộp", "2 x 500ml", "Beckman Coulter", "L85520", "2027-03-30", "15-25°C", 4, 2, 3, 1600000, None, 0, "Kệ hóa chất phòng máy", "ISE unit"),

            # Huyết học & Đông máu
            ("HH-DIL", "Dung dịch pha loãng Cell-Dyn Diluent", "hoa_chat", "Can", "20 Lít", "Abbott Diagnostics", "CD9120", "2027-12-30", "15-25°C", 6, 3, 6, 1450000, "2026-11-10", 60, "Kho hóa chất khô", "Máy Cell-Dyn"),
            ("HH-LYSE", "Dung dịch phá vỡ hồng cầu Lyse", "hoa_chat", "Chai", "5 Lít", "Abbott Diagnostics", "CD9121", "2027-09-15", "15-25°C", 5, 2, 5, 2100000, "2026-11-10", 60, "Kho hóa chất khô", "Máy Cell-Dyn"),
            ("HH-CLEAN", "Dung dịch rửa Probe Cleanser", "hoa_chat", "Chai", "1 Lít", "Abbott Diagnostics", "CD9122", "2028-02-10", "15-25°C", 4, 2, 3, 850000, "2026-11-01", 90, "Kho hóa chất khô", "Rửa đầu kim hằng ngày"),
            ("DM-PT", "Hóa chất đông máu PT Thromboplastin", "hoa_chat", "Hộp", "10 x 2ml", "Siemens / Sysmex", "DM4012", "2026-12-25", "2-8°C", 3, 4, 8, 1950000, "2026-11-12", 14, "Tủ lạnh 2-8°C Ngăn 4", "CẢNH BÁO: Cận date < 45 ngày & Dưới định mức"),
            ("DM-APTT", "Hóa chất đông máu APTT Actin FS", "hoa_chat", "Hộp", "10 x 2ml", "Siemens / Sysmex", "DM4013", "2027-04-10", "2-8°C", 5, 3, 5, 1850000, "2026-11-12", 14, "Tủ lạnh 2-8°C Ngăn 4", "Máy đông máu bán tự động"),

            # Sinh phẩm / Test Nhanh
            ("SP-HBSAG", "Kit test nhanh HBsAg Viêm gan B", "sinh_pham", "Hộp", "100 test", "SD Bioline / Abbott", "HBS2601", "2027-11-30", "2-30°C", 8, 4, 8, 1200000, None, 0, "Tủ sinh phẩm phòng lấy máu", "Test sàng lọc Viêm gan B"),
            ("SP-HCV", "Kit test nhanh Anti-HCV Viêm gan C", "sinh_pham", "Hộp", "100 test", "SD Bioline / Abbott", "HCV2602", "2027-10-15", "2-30°C", 5, 2, 5, 1650000, None, 0, "Tủ sinh phẩm phòng lấy máu", "Test sàng lọc Viêm gan C"),
            ("SP-HIV", "Kit test nhanh HIV 1/2 Alere Determine", "sinh_pham", "Hộp", "100 test", "Abbott", "HIV2603", "2027-08-20", "2-30°C", 4, 2, 4, 1850000, None, 0, "Tủ sinh phẩm niêm phong", "Test sàng lọc HIV"),
            ("SP-SYPH", "Kit test nhanh Giang mai (Syphilis TP)", "sinh_pham", "Hộp", "100 test", "CTK Biotech", "SYP2604", "2027-09-10", "2-30°C", 4, 2, 4, 1100000, None, 0, "Tủ sinh phẩm phòng lấy máu", "Test giang mai"),
            ("SP-DENG", "Kit test nhanh Sốt xuất huyết Dengue Combo", "sinh_pham", "Hộp", "25 test", "SD Bioline", "DEN2605", "2027-06-30", "2-30°C", 10, 4, 10, 1450000, None, 0, "Tủ sinh phẩm phòng lấy máu", "Dengue NS1 & Ab"),
            ("SP-NT10", "Que thử nước tiểu 10 thông số Uriscan", "sinh_pham", "Hộp", "100 que", "YD Diagnostics", "NT10260", "2027-05-15", "15-30°C", 12, 5, 12, 550000, "2026-11-05", 90, "Phòng soi nước tiểu", "Đo máy Uriscan Pro"),

            # Vật tư tiêu hao
            ("VT-EDTA", "Ống nghiệm chân không EDTA K2 2ml nắp tím", "vat_tu", "Khay", "100 ống", "Becton Dickinson", "E2601", "2028-06-30", "Phòng", 35, 15, 35, 180000, None, 0, "Kệ vật tư Tầng 1", "Ống lấy máu huyết học"),
            ("VT-GEL", "Ống nghiệm chân không Serum có hạt Gel 4ml", "vat_tu", "Khay", "100 ống", "Becton Dickinson", "G2602", "2028-06-30", "Phòng", 42, 20, 42, 210000, None, 0, "Kệ vật tư Tầng 1", "Ống lấy máu sinh hóa"),
            ("VT-CITR", "Ống nghiệm Natri Citrat 3.2% 1.8ml nắp xanh", "vat_tu", "Khay", "100 ống", "Becton Dickinson", "C2603", "2028-04-15", "Phòng", 16, 8, 16, 195000, None, 0, "Kệ vật tư Tầng 1", "Ống đông máu"),
            ("VT-KIM21", "Kim lấy máu chân không 2 đầu 21G", "vat_tu", "Hộp", "100 kim", "Becton Dickinson", "K2604", "2029-01-01", "Phòng", 25, 10, 25, 250000, None, 0, "Kệ vật tư Tầng 2", "Kim lấy máu ven"),
            ("VT-TIP-V", "Đầu côn tip vàng 10 - 200 µl", "vat_tu", "Gói", "1000 cái", "Axygen", "T2605", "2030-01-01", "Phòng", 18, 5, 18, 120000, None, 0, "Kệ vật tư Tầng 2", "Đầu tip hút mẫu"),
            ("VT-TIP-X", "Đầu côn tip xanh 100 - 1000 µl", "vat_tu", "Gói", "500 cái", "Axygen", "T2606", "2030-01-01", "Phòng", 12, 4, 12, 110000, None, 0, "Kệ vật tư Tầng 2", "Đầu tip hút hóa chất"),
            ("VT-GANG-M", "Găng tay y tế cao su không bột Size M", "vat_tu", "Hộp", "100 cái", "Khải Hoàn VRG", "GT2607", "2029-05-01", "Phòng", 50, 20, 50, 95000, None, 0, "Kho vật tư khô", "Bảo hộ lao động"),
            ("VT-CON70", "Cồn y tế 70 độ sát khuẩn", "vat_tu", "Can", "5 Lít", "Dược Vĩnh Long", "CO2608", "2028-10-10", "15-25°C", 8, 3, 8, 140000, None, 0, "Kho vật tư khô", "Sát khuẩn bàn lấy máu"),
        ]

        insert_sql = """
            INSERT INTO inventory_items (
                code, name, category, unit, spec, manufacturer, lot_number,
                expiry_date, storage_temp, quantity, min_stock, monthly_usage,
                unit_price, open_date, open_expiry_days, location, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for item in initial_items:
            cursor.execute(insert_sql, item)

        # Seed sample forecast
        sample_forecast_items = [
            {"code": "HC-GLU", "name": "Hóa chất Glucose AU", "unit": "Hộp", "current_stock": 12, "monthly_usage": 12, "suggested_qty": 15, "order_qty": 15, "unit_price": 650000, "total_cost": 9750000, "notes": "Dự trù định kỳ"},
            {"code": "HC-UREA", "name": "Hóa chất Urea / BUN AU", "unit": "Hộp", "current_stock": 9, "monthly_usage": 9, "suggested_qty": 12, "order_qty": 12, "unit_price": 720000, "total_cost": 8640000, "notes": "Dự trù định kỳ"},
            {"code": "HC-CREAT", "name": "Hóa chất Creatinine Enzymatic AU", "unit": "Hộp", "current_stock": 10, "monthly_usage": 14, "suggested_qty": 18, "order_qty": 18, "unit_price": 850000, "total_cost": 15300000, "notes": "Tăng thêm do lượng BN đông"},
            {"code": "DM-PT", "name": "Hóa chất đông máu PT Thromboplastin", "unit": "Hộp", "current_stock": 3, "monthly_usage": 8, "suggested_qty": 12, "order_qty": 12, "unit_price": 1950000, "total_cost": 23400000, "notes": "Kho sắp hết hàng, ưu tiên giao sớm"},
            {"code": "VT-EDTA", "name": "Ống nghiệm chân không EDTA K2 2ml nắp tím", "unit": "Khay", "current_stock": 35, "monthly_usage": 35, "suggested_qty": 45, "order_qty": 45, "unit_price": 180000, "total_cost": 8100000, "notes": "Dự trù định kỳ"},
            {"code": "VT-GEL", "name": "Ống nghiệm chân không Serum Gel 4ml", "unit": "Khay", "current_stock": 42, "monthly_usage": 42, "suggested_qty": 50, "order_qty": 50, "unit_price": 210000, "total_cost": 10500000, "notes": "Dự trù định kỳ"}
        ]
        total_forecast_cost = sum(i["total_cost"] for i in sample_forecast_items)

        cursor.execute("SELECT id FROM users WHERE role = 'truong_khoa' LIMIT 1")
        tk_row = cursor.fetchone()
        admin_id = tk_row[0] if tk_row else None

        cursor.execute("""
            INSERT INTO inventory_forecasts (
                period, title, status, created_by, total_cost, items_json, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Tháng 12/2026",
            "Dự Trù Hóa Chất, Sinh Phẩm & Vật Tư Tiêu Hao Tháng 12/2026",
            "submitted",
            admin_id,
            total_forecast_cost,
            json.dumps(sample_forecast_items, ensure_ascii=False),
            "Căn cứ cơ số mẫu trung bình ngày và lượng tồn kho thực tế tính đến cuối tháng 11/2026."
        ))

        conn.commit()
        print(f"Successfully seeded {len(initial_items)} inventory items and 1 sample forecast plan!")

    conn.close()

if __name__ == "__main__":
    setup_inventory()
