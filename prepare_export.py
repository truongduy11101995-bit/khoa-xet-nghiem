import json
import datetime
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from backend.database import get_db

out_dir = r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\export_drive"
os.makedirs(out_dir, exist_ok=True)

# 1. Export Database Backup
conn = get_db()
c = conn.cursor()
tables = ['users', 'positions', 'schedules', 'leave_requests', 'inventory_items', 'inventory_forecasts', 'open_vials', 'environment_logs', 'documents']
backup_data = {}
for t in tables:
    try:
        c.execute(f"SELECT * FROM {t}")
        rows = [dict(r) for r in c.fetchall()]
        for r in rows:
            for k, v in r.items():
                if isinstance(v, (datetime.date, datetime.datetime)):
                    r[k] = v.isoformat()
        backup_data[t] = rows
    except Exception as e:
        print(f"Error reading {t}: {e}")

backup_file = os.path.join(out_dir, f"Backup_Du_Lieu_Khoa_XN_{datetime.date.today().strftime('%Y%m%d')}.json")
with open(backup_file, "w", encoding="utf-8") as f:
    json.dump(backup_data, f, ensure_ascii=False, indent=2)
print("Exported database backup:", backup_file)

# 2. Export Inventory Excel
c.execute("SELECT * FROM inventory_items ORDER BY category ASC, name ASC")
items = [dict(r) for r in c.fetchall()]
conn.close()

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Ton_Kho_Thuc_Te"
ws.views.sheetView[0].showGridLines = True

font_title = Font(name="Times New Roman", size=14, bold=True, color="1E3A8A")
font_th = Font(name="Times New Roman", size=11, bold=True, color="FFFFFF")
font_regular = Font(name="Times New Roman", size=10)
fill_th = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
thin_border = Border(
    left=Side(style='thin', color='CBD5E1'),
    right=Side(style='thin', color='CBD5E1'),
    top=Side(style='thin', color='CBD5E1'),
    bottom=Side(style='thin', color='CBD5E1')
)

ws.merge_cells("A1:N1")
ws["A1"] = "BẢNG THEO DÕI TỒN KHO HÓA CHẤT, SINH PHẨM & VẬT TƯ TIÊU HAO"
ws["A1"].font = font_title
ws["A1"].alignment = Alignment(horizontal="center", vertical="center")

headers = [
    "STT", "Mã Hàng", "Tên Hóa Chất / Sinh Phẩm / Vật Tư", "Phân Loại", "Quy Cách", "ĐVT",
    "Số Lô", "Hạn Sử Dụng", "Nhiệt Độ", "Tồn Kho Hiện Có", "Định Mức Tối Thiểu", "Tiêu Hao TB", "Vị Trí Lưu Trữ", "Tình Trạng"
]
for col_idx, h in enumerate(headers, 1):
    cell = ws.cell(row=3, column=col_idx, value=h)
    cell.font = font_th
    cell.fill = fill_th
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    cell.border = thin_border
ws.row_dimensions[3].height = 28

cur_row = 4
for idx, item in enumerate(items, 1):
    qty = float(item.get("quantity") or 0)
    min_s = float(item.get("min_stock") or 0)
    is_low = qty <= min_s
    exp_str = item.get("expiry_date") or ""
    status_text = "An toàn"
    if is_low:
        status_text = "Dưới định mức"

    row_data = [
        idx, item["code"], item["name"], item.get("category", ""),
        item["spec"] or "", item["unit"], item["lot_number"] or "", exp_str,
        item["storage_temp"] or "", qty, min_s, item["monthly_usage"] or 0,
        item["location"] or "", status_text
    ]

    for col_idx, val in enumerate(row_data, 1):
        cell = ws.cell(row=cur_row, column=col_idx, value=val)
        cell.font = font_regular
        cell.border = thin_border
        if col_idx in [1, 2, 4, 6, 7, 8, 9, 14]:
            cell.alignment = Alignment(horizontal="center")
        elif col_idx in [10, 11, 12]:
            cell.alignment = Alignment(horizontal="right")
    cur_row += 1

excel_file = os.path.join(out_dir, f"Bao_Cao_Ton_Kho_Hien_Tai_{datetime.date.today().strftime('%Y%m%d')}.xlsx")
wb.save(excel_file)
print("Exported inventory excel:", excel_file)

# 3. Create Web Access Shortcut File (HTML)
link_url = "https://happens-annie-daniel-sunset.trycloudflare.com"
html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Khoa Xét Nghiệm - BVĐK Thiên Ân Viễn Đông</title>
  <meta http-equiv="refresh" content="2; url={link_url}">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f0f9ff; }}
    .card {{ background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); text-align: center; max-width: 480px; border: 1px solid #bae6fd; }}
    h1 {{ color: #0369a1; font-size: 20px; margin-bottom: 8px; text-transform: uppercase; }}
    p {{ color: #475569; font-size: 14px; margin-bottom: 24px; }}
    .btn {{ display: inline-block; background: #0284c7; color: white; padding: 12px 28px; border-radius: 12px; font-weight: bold; text-decoration: none; font-size: 15px; box-shadow: 0 4px 12px rgba(2,132,199,0.3); }}
    .btn:hover {{ background: #0369a1; }}
    .hint {{ font-size: 12px; color: #94a3b8; margin-top: 20px; }}
  </style>
</head>
<body>
  <div class="card">
    <div style="font-size: 48px; margin-bottom: 12px;">🏥</div>
    <h1>Khoa Xét Nghiệm - BVĐK Thiên Ân</h1>
    <p>Hệ Thống Quản Lý Trực Tuyến 24/7 (Lịch trực, Nghỉ phép, Tồn kho, Sổ nhiệt độ BM.MT.01)</p>
    <a href="{link_url}" class="btn" target="_blank">👉 BẤM VÀO ĐÂY ĐỂ MỞ PHẦN MỀM</a>
    <div class="hint">Tự động chuyển tiếp sau 2 giây...</div>
  </div>
</body>
</html>
"""
shortcut_file = os.path.join(out_dir, "00_LINK_TRUY_CAP_PHAN_MEM_KHOA_XET_NGHIEM_24_7.html")
with open(shortcut_file, "w", encoding="utf-8") as f:
    f.write(html_content)
print("Created access shortcut:", shortcut_file)
