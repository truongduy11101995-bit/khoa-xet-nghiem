import os
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

TARGET_DIR = Path(r"D:\01_TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026\06_QUAN_LY_HOA_CHAT_VAT_TU_SINH_PHAM")
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. SO THEO DOI XUAT NHAP TON KHO HOA CHAT SINH PHAM 2026.xlsx
# -------------------------------------------------------------
def create_so_theo_doi_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Theo_Doi_Xuat_Nhap_Ton"
    ws.views.sheetView[0].showGridLines = True

    # Styling
    font_header = Font(name="Times New Roman", size=11, bold=True, color="1E3A8A")
    font_title = Font(name="Times New Roman", size=15, bold=True, color="1E3A8A")
    font_bold = Font(name="Times New Roman", size=11, bold=True)
    font_regular = Font(name="Times New Roman", size=10)
    font_th = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
    
    fill_th = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_group = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
    fill_warning = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # Hospital Header
    ws["A1"] = "SỞ Y TẾ TỈNH VĨNH LONG"
    ws["A2"] = "BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG"
    ws["A3"] = "KHOA XÉT NGHIỆM"
    ws["A1"].font = Font(name="Times New Roman", size=10, bold=True)
    ws["A2"].font = Font(name="Times New Roman", size=11, bold=True, color="0369A1")
    ws["A3"].font = Font(name="Times New Roman", size=10, bold=True)

    ws["I1"] = "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"
    ws["I2"] = "Độc lập - Tự do - Hạnh phúc"
    ws["I3"] = "Tiêu chuẩn: QĐ 2429/QĐ-BYT (Chương VI)"
    ws["I1"].font = Font(name="Times New Roman", size=10, bold=True)
    ws["I2"].font = Font(name="Times New Roman", size=10, italic=True)
    ws["I3"].font = Font(name="Times New Roman", size=9, bold=True, color="047857")

    # Title
    ws["A5"] = "SỔ THEO DÕI XUẤT - NHẬP - TỒN KHO HÓA CHẤT, SINH PHẨM & VẬT TƯ TIÊU HAO"
    ws["A5"].font = font_title
    ws["A5"].alignment = Alignment(horizontal="center", vertical="center")
    ws.merge_cells("A5:L5")

    ws["A6"] = "Năm theo dõi: 2026 • Địa điểm: Kho bảo quản Hóa chất - Khoa Xét nghiệm"
    ws["A6"].font = Font(name="Times New Roman", size=11, italic=True)
    ws["A6"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A6:L6")

    # Headers
    headers = [
        "STT", "Mã Hàng", "Tên Hóa Chất / Sinh Phẩm / Vật Tư", "Quy Cách", "ĐVT",
        "Số Lô (Lot)", "Hạn Dùng", "Nhiệt Độ Bảo Quản", "Tồn Đầu Kỳ", "Nhập Trong Kỳ",
        "Xuất Trong Kỳ", "Tồn Cuối Kỳ"
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=8, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_th
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[8].height = 32

    # Sample standard lab chemicals & reagents
    items = [
        # (group, name, code, spec, unit, lot, exp, temp, ton_dau, nhap, xuat)
        ("A. HÓA CHẤT XÉT NGHIỆM HÓA SINH - MIỄN DỊCH", None),
        (None, "Hóa chất Glucose AU", "HC-GLU", "4 x 50ml", "Hộp", "L84920", "2027-08-15", "2 - 8°C", 10, 15, 12),
        (None, "Hóa chất Urea / BUN AU", "HC-UREA", "4 x 50ml", "Hộp", "L84921", "2027-06-20", "2 - 8°C", 8, 10, 9),
        (None, "Hóa chất Creatinine AU", "HC-CREAT", "4 x 50ml", "Hộp", "L84922", "2027-09-10", "2 - 8°C", 12, 12, 14),
        (None, "Hóa chất AST (GOT) AU", "HC-AST", "4 x 50ml", "Hộp", "L85101", "2027-05-18", "2 - 8°C", 6, 8, 7),
        (None, "Hóa chất ALT (GPT) AU", "HC-ALT", "4 x 50ml", "Hộp", "L85102", "2027-05-18", "2 - 8°C", 6, 8, 7),
        (None, "Hóa chất Cholesterol toàn phần", "HC-CHOL", "4 x 50ml", "Hộp", "L85230", "2027-10-12", "2 - 8°C", 7, 10, 8),
        (None, "Hóa chất Triglyceride AU", "HC-TRIG", "4 x 50ml", "Hộp", "L85231", "2027-11-05", "2 - 8°C", 8, 10, 9),
        (None, "Hóa chất Acid Uric AU", "HC-URIC", "4 x 50ml", "Hộp", "L85340", "2027-07-22", "2 - 8°C", 5, 6, 5),
        (None, "Hóa chất HbA1c Direct Enzymatic", "HC-HBA1C", "100 test", "Kit", "L85499", "2027-01-15", "2 - 8°C", 4, 6, 5),
        
        ("B. HÓA CHẤT HUYẾT HỌC & ĐÔNG MÁU", None),
        (None, "Dung dịch pha loãng Cell-Dyn Diluent", "HH-DIL", "20 Lít", "Can", "CD9120", "2027-12-30", "15 - 25°C", 5, 8, 6),
        (None, "Dung dịch phá hồng cầu Lyse", "HH-LYSE", "5 Lít", "Chai", "CD9121", "2027-09-15", "15 - 25°C", 4, 6, 5),
        (None, "Dung dịch rửa đầu đo Probe Cleanser", "HH-CLEAN", "1 Lít", "Chai", "CD9122", "2028-02-10", "15 - 25°C", 3, 4, 3),
        (None, "Hóa chất đo đông máu Thromboplastin PT", "DM-PT", "10 x 2ml", "Hộp", "DM4012", "2026-12-25", "2 - 8°C", 6, 8, 8),
        (None, "Hóa chất đông máu APTT Actin FS", "DM-APTT", "10 x 2ml", "Hộp", "DM4013", "2027-04-10", "2 - 8°C", 5, 6, 5),

        ("C. SINH PHẨM CHẨN ĐOÁN & TEST NHANH", None),
        (None, "Kit test nhanh Viêm gan B (HBsAg)", "SP-HBSAG", "100 test", "Hộp", "HBS2601", "2027-11-30", "2 - 30°C", 6, 10, 8),
        (None, "Kit test nhanh Viêm gan C (Anti-HCV)", "SP-HCV", "100 test", "Hộp", "HCV2602", "2027-10-15", "2 - 30°C", 4, 6, 5),
        (None, "Kit test nhanh HIV 1/2 Alere Determine", "SP-HIV", "100 test", "Hộp", "HIV2603", "2027-08-20", "2 - 30°C", 4, 5, 4),
        (None, "Kit test nhanh Giang mai (Syphilis TP)", "SP-SYPH", "100 test", "Hộp", "SYP2604", "2027-09-10", "2 - 30°C", 3, 5, 4),
        (None, "Kit test nhanh Sốt xuất huyết Dengue NS1", "SP-DENG", "25 test", "Hộp", "DEN2605", "2027-06-30", "2 - 30°C", 8, 12, 10),
        (None, "Que thử nước tiểu 10 thông số Uriscan", "SP-NT10", "100 que", "Hộp", "NT10260", "2027-05-15", "15 - 30°C", 10, 15, 12),

        ("D. VẬT TƯ TIÊU HAO CHUYÊN DÙNG LẤY MÁU & XÉT NGHIỆM", None),
        (None, "Ống nghiệm chân không EDTA K2 2ml nắp tím", "VT-EDTA", "100 ống", "Khay", "E2601", "2028-06-30", "Phòng", 25, 40, 35),
        (None, "Ống nghiệm chân không Serum hạt Gel 4ml", "VT-GEL", "100 ống", "Khay", "G2602", "2028-06-30", "Phòng", 30, 50, 42),
        (None, "Ống nghiệm Natri Citrat 3.2% 1.8ml nắp xanh", "VT-CITR", "100 ống", "Khay", "C2603", "2028-04-15", "Phòng", 12, 20, 16),
        (None, "Kim lấy máu chân không 2 đầu 21G", "VT-KIM21", "100 kim", "Hộp", "K2604", "2029-01-01", "Phòng", 20, 30, 25),
        (None, "Đầu côn tip vàng 10 - 200 µl", "VT-TIP-V", "1000 cái", "Gói", "T2605", "Không HSD", "Phòng", 15, 20, 18),
        (None, "Đầu côn tip xanh 100 - 1000 µl", "VT-TIP-X", "500 cái", "Gói", "T2606", "Không HSD", "Phòng", 10, 15, 12),
        (None, "Găng tay y tế cao su không bột Size M", "VT-GANG-M", "100 cái", "Hộp", "GT2607", "2029-05-01", "Phòng", 40, 60, 50),
        (None, "Cồn y tế 70 độ sát khuẩn", "VT-CON70", "5 Lít", "Can", "CO2608", "2028-10-10", "15 - 25°C", 6, 10, 8),
    ]

    cur_row = 9
    stt = 1
    for item in items:
        if item[1] is None:
            # Group row
            ws.cell(row=cur_row, column=1, value="")
            cell_grp = ws.cell(row=cur_row, column=2, value=item[0])
            cell_grp.font = font_bold
            ws.merge_cells(start_row=cur_row, start_column=2, end_row=cur_row, end_column=12)
            for c in range(1, 13):
                ws.cell(row=cur_row, column=c).fill = fill_group
                ws.cell(row=cur_row, column=c).border = thin_border
            ws.row_dimensions[cur_row].height = 24
            cur_row += 1
        else:
            _, name, code, spec, unit, lot, exp, temp, t_dau, nhap, xuat = item
            t_cuoi = t_dau + nhap - xuat

            ws.cell(row=cur_row, column=1, value=stt).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=2, value=code).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=3, value=name)
            ws.cell(row=cur_row, column=4, value=spec).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=5, value=unit).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=6, value=lot).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=7, value=exp).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=8, value=temp).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=9, value=t_dau).alignment = Alignment(horizontal="right")
            ws.cell(row=cur_row, column=10, value=nhap).alignment = Alignment(horizontal="right")
            ws.cell(row=cur_row, column=11, value=xuat).alignment = Alignment(horizontal="right")
            
            cell_end = ws.cell(row=cur_row, column=12, value=t_cuoi)
            cell_end.alignment = Alignment(horizontal="right")
            cell_end.font = font_bold

            # Highlight near expiry
            if "2026" in exp:
                ws.cell(row=cur_row, column=7).fill = fill_warning
                ws.cell(row=cur_row, column=7).font = Font(name="Times New Roman", size=10, bold=True, color="B45309")

            for c in range(1, 13):
                cell = ws.cell(row=cur_row, column=c)
                if not cell.font or cell.font.name != "Times New Roman":
                    cell.font = font_regular
                cell.border = thin_border

            ws.row_dimensions[cur_row].height = 20
            cur_row += 1
            stt += 1

    # Footer signatures
    cur_row += 2
    ws.cell(row=cur_row, column=2, value="NGƯỜI LẬP SỔ / THỦ KHO").font = font_bold
    ws.cell(row=cur_row, column=6, value="KỸ THUẬT VIÊN TRƯỞNG").font = font_bold
    ws.cell(row=cur_row, column=10, value="TRƯỞNG KHOA XÉT NGHIỆM").font = font_bold

    cur_row += 1
    ws.cell(row=cur_row, column=2, value="(Ký và ghi rõ họ tên)").font = Font(name="Times New Roman", size=10, italic=True)
    ws.cell(row=cur_row, column=6, value="(Ký và ghi rõ họ tên)").font = Font(name="Times New Roman", size=10, italic=True)
    ws.cell(row=cur_row, column=10, value="(Ký và ghi rõ họ tên)").font = Font(name="Times New Roman", size=10, italic=True)

    cur_row += 4
    ws.cell(row=cur_row, column=2, value="CN. Tống Mọng Tiền").font = font_bold
    ws.cell(row=cur_row, column=6, value="CN. Nguyễn Trường Duy").font = font_bold
    ws.cell(row=cur_row, column=10, value="CN. Lê Đình Tú").font = font_bold

    # Column widths
    col_widths = {1: 6, 2: 14, 3: 38, 4: 14, 5: 8, 6: 12, 7: 14, 8: 18, 9: 13, 10: 14, 11: 14, 12: 14}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    out_path = TARGET_DIR / "04_SO_THEO_DOI_XUAT_NHAP_TON_KHO_HOA_CHAT_SINH_PHAM_2026.xlsx"
    wb.save(str(out_path))
    print(f"Created: {out_path.name}")

# -------------------------------------------------------------
# 2. BANG DU TRU HOA CHAT VAT TU TIEU HAO DINH KY 2026.xlsx
# -------------------------------------------------------------
def create_bang_du_tru_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Du_Tru_Hoa_Chat_Vat_Tu"
    ws.views.sheetView[0].showGridLines = True

    font_title = Font(name="Times New Roman", size=15, bold=True, color="1E3A8A")
    font_bold = Font(name="Times New Roman", size=11, bold=True)
    font_regular = Font(name="Times New Roman", size=10)
    font_th = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
    fill_th = PatternFill(start_color="0369A1", end_color="0369A1", fill_type="solid")
    fill_group = PatternFill(start_color="F0F9FF", end_color="F0F9FF", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # Hospital Header
    ws["A1"] = "SỞ Y TẾ TỈNH VĨNH LONG"
    ws["A2"] = "BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG"
    ws["A3"] = "KHOA XÉT NGHIỆM"
    ws["A1"].font = Font(name="Times New Roman", size=10, bold=True)
    ws["A2"].font = Font(name="Times New Roman", size=11, bold=True, color="0369A1")
    ws["A3"].font = Font(name="Times New Roman", size=10, bold=True)

    ws["H1"] = "MÃ BIỂU MẪU: BM.HC.01"
    ws["H2"] = "BAN HÀNH: 2026 • LẦN SOÁT XÉT: 01"
    ws["H3"] = "Căn cứ: QĐ 2429/QĐ-BYT"
    ws["H1"].font = Font(name="Times New Roman", size=10, bold=True, color="1E3A8A")
    ws["H2"].font = Font(name="Times New Roman", size=9, italic=True)
    ws["H3"].font = Font(name="Times New Roman", size=9, bold=True, color="047857")

    # Title
    ws["A5"] = "BẢNG DỰ TRÙ HÓA CHẤT, SINH PHẨM & VẬT TƯ TIÊU HAO ĐỊNH KỲ"
    ws["A5"].font = font_title
    ws["A5"].alignment = Alignment(horizontal="center", vertical="center")
    ws.merge_cells("A5:K5")

    ws["A6"] = "Kỳ dự trù: Tháng 12/2026 & Quý I/2027 • Khoa Xét Nghiệm BVĐK Thiên Ân"
    ws["A6"].font = Font(name="Times New Roman", size=11, italic=True)
    ws["A6"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A6:K6")

    headers = [
        "STT", "Mã Hàng", "Tên Hóa Chất / Sinh Phẩm / Vật Tư", "Quy Cách", "ĐVT",
        "Tồn Hiện Tại", "Tiêu Hao TB/Tháng", "Đề Xuất Mua", "Đơn Giá Ước Tính (VNĐ)", "Thành Tiền (VNĐ)", "Ghi Chú"
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=8, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_th
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[8].height = 32

    du_tru_items = [
        ("I. HÓA CHẤT XÉT NGHIỆM MÁY SINH HÓA AU", None),
        (None, "Hóa chất Glucose AU", "HC-GLU", "4 x 50ml", "Hộp", 13, 12, 15, 650000),
        (None, "Hóa chất Urea AU", "HC-UREA", "4 x 50ml", "Hộp", 9, 9, 12, 720000),
        (None, "Hóa chất Creatinine AU", "HC-CREAT", "4 x 50ml", "Hộp", 10, 14, 18, 850000),
        (None, "Hóa chất AST (GOT) AU", "HC-AST", "4 x 50ml", "Hộp", 7, 7, 10, 780000),
        (None, "Hóa chất ALT (GPT) AU", "HC-ALT", "4 x 50ml", "Hộp", 7, 7, 10, 780000),
        (None, "Hóa chất Cholesterol AU", "HC-CHOL", "4 x 50ml", "Hộp", 9, 8, 10, 690000),
        (None, "Hóa chất Triglyceride AU", "HC-TRIG", "4 x 50ml", "Hộp", 9, 9, 12, 820000),
        (None, "Hóa chất Acid Uric AU", "HC-URIC", "4 x 50ml", "Hộp", 6, 5, 8, 750000),

        ("II. DUNG DỊCH HUYẾT HỌC & ĐÔNG MÁU", None),
        (None, "Cell-Dyn Diluent Pha loãng", "HH-DIL", "20 Lít", "Can", 7, 6, 8, 1450000),
        (None, "Cell-Dyn Lyse Phá hồng cầu", "HH-LYSE", "5 Lít", "Chai", 5, 5, 6, 2100000),
        (None, "Dung dịch rửa Probe Cleanser", "HH-CLEAN", "1 Lít", "Chai", 4, 3, 4, 850000),
        (None, "Hóa chất đông máu PT Thromboplastin", "DM-PT", "10 x 2ml", "Hộp", 6, 8, 12, 1950000),
        (None, "Hóa chất đông máu APTT", "DM-APTT", "10 x 2ml", "Hộp", 6, 5, 8, 1850000),

        ("III. KIT TEST NHANH & SINH PHẨM MIỄN DỊCH", None),
        (None, "Kit test nhanh HBsAg Viêm gan B", "SP-HBSAG", "100 test", "Hộp", 8, 8, 10, 1200000),
        (None, "Kit test nhanh Anti-HCV Viêm gan C", "SP-HCV", "100 test", "Hộp", 5, 5, 8, 1650000),
        (None, "Kit test nhanh HIV 1/2 Determine", "SP-HIV", "100 test", "Hộp", 5, 4, 6, 1850000),
        (None, "Kit test nhanh Dengue NS1 & IgG/IgM", "SP-DENG", "25 test", "Hộp", 10, 10, 15, 1450000),
        (None, "Que thử nước tiểu 10 thông số Uriscan", "SP-NT10", "100 que", "Hộp", 13, 12, 15, 550000),

        ("IV. VẬT TƯ TIÊU HAO LẤY MÁU & XÉT NGHIỆM", None),
        (None, "Ống nghiệm chân không EDTA K2 2ml", "VT-EDTA", "100 ống", "Khay", 30, 35, 45, 180000),
        (None, "Ống nghiệm chân không Serum Gel 4ml", "VT-GEL", "100 ống", "Khay", 38, 42, 50, 210000),
        (None, "Ống nghiệm Natri Citrat 3.2% 1.8ml", "VT-CITR", "100 ống", "Khay", 16, 16, 20, 195000),
        (None, "Kim lấy máu chân không 2 đầu 21G", "VT-KIM21", "100 kim", "Hộp", 25, 25, 30, 250000),
        (None, "Găng tay y tế cao su không bột Size M", "VT-GANG-M", "100 cái", "Hộp", 50, 50, 60, 95000),
        (None, "Cồn y tế 70 độ sát khuẩn", "VT-CON70", "5 Lít", "Can", 8, 8, 10, 140000),
    ]

    cur_row = 9
    stt = 1
    total_cost_formula_cells = []

    for item in du_tru_items:
        if item[1] is None:
            # Section row
            cell_grp = ws.cell(row=cur_row, column=2, value=item[0])
            cell_grp.font = font_bold
            ws.merge_cells(start_row=cur_row, start_column=2, end_row=cur_row, end_column=11)
            for c in range(1, 12):
                ws.cell(row=cur_row, column=c).fill = fill_group
                ws.cell(row=cur_row, column=c).border = thin_border
            ws.row_dimensions[cur_row].height = 24
            cur_row += 1
        else:
            _, name, code, spec, unit, ton_hientai, tieu_hao, de_xuat, don_gia = item
            thanh_tien = de_xuat * don_gia

            ws.cell(row=cur_row, column=1, value=stt).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=2, value=code).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=3, value=name)
            ws.cell(row=cur_row, column=4, value=spec).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=5, value=unit).alignment = Alignment(horizontal="center")
            ws.cell(row=cur_row, column=6, value=ton_hientai).alignment = Alignment(horizontal="right")
            ws.cell(row=cur_row, column=7, value=tieu_hao).alignment = Alignment(horizontal="right")
            
            cell_dx = ws.cell(row=cur_row, column=8, value=de_xuat)
            cell_dx.alignment = Alignment(horizontal="right")
            cell_dx.font = font_bold
            cell_dx.fill = PatternFill(start_color="FEF9C3", end_color="FEF9C3", fill_type="solid")

            cell_dg = ws.cell(row=cur_row, column=9, value=don_gia)
            cell_dg.alignment = Alignment(horizontal="right")
            cell_dg.number_format = "#,##0"

            cell_tt = ws.cell(row=cur_row, column=10, value=f"=H{cur_row}*I{cur_row}")
            cell_tt.alignment = Alignment(horizontal="right")
            cell_tt.font = font_bold
            cell_tt.number_format = "#,##0"
            total_cost_formula_cells.append(f"J{cur_row}")

            ws.cell(row=cur_row, column=11, value="Dự trù định kỳ").font = font_regular

            for c in range(1, 12):
                cell = ws.cell(row=cur_row, column=c)
                if not cell.font or cell.font.name != "Times New Roman":
                    cell.font = font_regular
                cell.border = thin_border

            ws.row_dimensions[cur_row].height = 20
            cur_row += 1
            stt += 1

    # Total Sum Row
    ws.cell(row=cur_row, column=2, value="TỔNG CỘNG KINH PHÍ DỰ TRÙ:").font = font_bold
    ws.merge_cells(start_row=cur_row, start_column=2, end_row=cur_row, end_column=9)
    sum_cell = ws.cell(row=cur_row, column=10, value=f"=SUM({'+'.join(total_cost_formula_cells)})" if len(total_cost_formula_cells) < 15 else f"=SUM(J9:J{cur_row-1})")
    sum_cell.font = Font(name="Times New Roman", size=11, bold=True, color="B91C1C")
    sum_cell.alignment = Alignment(horizontal="right")
    sum_cell.number_format = "#,##0 VNĐ"

    for c in range(1, 12):
        ws.cell(row=cur_row, column=c).fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        ws.cell(row=cur_row, column=c).border = thin_border
    ws.row_dimensions[cur_row].height = 26

    # Signatures
    cur_row += 2
    ws.cell(row=cur_row, column=2, value="NGƯỜI LẬP DỰ TRÙ").font = font_bold
    ws.cell(row=cur_row, column=5, value="KỸ THUẬT VIÊN TRƯỞNG").font = font_bold
    ws.cell(row=cur_row, column=8, value="TRƯỞNG KHOA XÉT NGHIỆM").font = font_bold
    ws.cell(row=cur_row, column=10, value="BAN GIÁM ĐỐC BỆNH VIỆN").font = font_bold

    cur_row += 1
    ws.cell(row=cur_row, column=2, value="(Ký và ghi rõ họ tên)").font = Font(name="Times New Roman", size=10, italic=True)
    ws.cell(row=cur_row, column=5, value="(Ký và ghi rõ họ tên)").font = Font(name="Times New Roman", size=10, italic=True)
    ws.cell(row=cur_row, column=8, value="(Ký và ghi rõ họ tên)").font = Font(name="Times New Roman", size=10, italic=True)
    ws.cell(row=cur_row, column=10, value="(Phê duyệt)").font = Font(name="Times New Roman", size=10, italic=True)

    cur_row += 4
    ws.cell(row=cur_row, column=2, value="CN. Tống Mọng Tiền").font = font_bold
    ws.cell(row=cur_row, column=5, value="CN. Nguyễn Trường Duy").font = font_bold
    ws.cell(row=cur_row, column=8, value="CN. Lê Đình Tú").font = font_bold
    ws.cell(row=cur_row, column=10, value="GIÁM ĐỐC").font = font_bold

    col_widths = {1: 6, 2: 13, 3: 36, 4: 13, 5: 8, 6: 12, 7: 15, 8: 13, 9: 18, 10: 20, 11: 18}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    out_path = TARGET_DIR / "05_BANG_DU_TRU_HOA_CHAT_VAT_TU_TIEU_HAO_DINH_KY_2026.xlsx"
    wb.save(str(out_path))
    print(f"Created: {out_path.name}")

# -------------------------------------------------------------
# 3. THE KHO THEO DOI HOA CHAT SINH PHAM CHUAN 2429.xlsx
# -------------------------------------------------------------
def create_the_kho_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "The_Kho_Mau"
    ws.views.sheetView[0].showGridLines = True

    font_title = Font(name="Times New Roman", size=15, bold=True, color="1E3A8A")
    font_bold = Font(name="Times New Roman", size=11, bold=True)
    font_regular = Font(name="Times New Roman", size=10)
    font_th = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
    fill_th = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    ws["A1"] = "BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG"
    ws["A2"] = "KHOA XÉT NGHIỆM - BỘ PHẬN KHO"
    ws["A1"].font = Font(name="Times New Roman", size=11, bold=True, color="0369A1")
    ws["A2"].font = Font(name="Times New Roman", size=10, bold=True)

    ws["G1"] = "MÃ HIỆU: TK.HC.01"
    ws["G2"] = "Theo QĐ 2429/QĐ-BYT"
    ws["G1"].font = Font(name="Times New Roman", size=10, bold=True)
    ws["G2"].font = Font(name="Times New Roman", size=9, italic=True)

    ws["A4"] = "THẺ KHO THEO DÕI HÓA CHẤT / SINH PHẨM"
    ws["A4"].font = font_title
    ws["A4"].alignment = Alignment(horizontal="center")
    ws.merge_cells("A4:H4")

    # Item details
    ws["A6"] = "Tên hóa chất, sinh phẩm: Hóa chất Glucose AU (Beckman Coulter)"
    ws["A6"].font = font_bold
    ws["F6"] = "Mã số: HC-GLU"
    ws["F6"].font = font_bold

    ws["A7"] = "Quy cách đóng gói: 4 x 50ml / Hộp"
    ws["F7"] = "Đơn vị tính: Hộp"
    ws["A8"] = "Điều kiện bảo quản: Nhiệt độ 2°C - 8°C (Tủ lạnh chuyên dụng Khoa)"
    ws["F8"] = "Định mức tồn tối thiểu: 05 Hộp"

    for r in range(6, 9):
        ws.cell(row=r, column=1).font = font_regular
        ws.cell(row=r, column=6).font = font_regular

    headers = [
        "Ngày Tháng", "Số Chứng Từ", "Diễn Giải Nội Dung", "Số Lô (Lot)", "Hạn Dùng",
        "Số Lượng Nhập", "Số Lượng Xuất", "Số Lượng Tồn", "Ký Xác Nhận"
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=10, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_th
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[10].height = 28

    entries = [
        ("01/11/2026", "TỒN ĐẦU", "Số dư chuyển sang tháng 11/2026", "L84920", "15/08/2027", 0, 0, 10, "Tiền"),
        ("05/11/2026", "XK-01", "Xuất phòng máy Sinh hóa vận hành tuần 45", "L84920", "15/08/2027", 0, 3, 7, "Duy"),
        ("12/11/2026", "XK-02", "Xuất phòng máy Sinh hóa vận hành tuần 46", "L84920", "15/08/2027", 0, 3, 4, "Duy"),
        ("14/11/2026", "NK-08", "Nhập kho theo dự trù đợt 1 tháng 11", "L84920", "15/08/2027", 15, 0, 19, "Tiền"),
        ("19/11/2026", "XK-03", "Xuất phòng máy Sinh hóa vận hành tuần 47", "L84920", "15/08/2027", 0, 4, 15, "Duy"),
        ("26/11/2026", "XK-04", "Xuất phòng máy Sinh hóa vận hành tuần 48", "L84920", "15/08/2027", 0, 3, 12, "Duy"),
        ("30/11/2026", "KK-11", "Kiểm kê định kỳ cuối tháng 11/2026", "L84920", "15/08/2027", 0, 0, 12, "Tú"),
    ]

    cur_row = 11
    for row_data in entries:
        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.font = font_regular
            cell.border = thin_border
            if col_idx in [1, 2, 4, 5, 9]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in [6, 7, 8]:
                cell.alignment = Alignment(horizontal="right")
                if col_idx == 8:
                    cell.font = font_bold
        ws.row_dimensions[cur_row].height = 20
        cur_row += 1

    col_widths = {1: 14, 2: 14, 3: 36, 4: 14, 5: 14, 6: 15, 7: 15, 8: 15, 9: 15}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    out_path = TARGET_DIR / "06_THE_KHO_THEO_DOI_HOA_CHAT_SINH_PHAM_CHUAN_2429.xlsx"
    wb.save(str(out_path))
    print(f"Created: {out_path.name}")

# -------------------------------------------------------------
# 4. BIEN BAN KIEM KE KHO HOA CHAT VAT TU DINH KY THANG.docx
# -------------------------------------------------------------
def create_bien_ban_kiem_ke_doc():
    doc = docx.Document()
    
    # Page setup A4
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Header table
    t_head = doc.add_table(rows=1, cols=2)
    t_head.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_left = t_head.cell(0, 0)
    c_right = t_head.cell(0, 1)

    p_l = c_left.paragraphs[0]
    p_l.add_run("SỞ Y TẾ TỈNH VĨNH LONG\n").bold = True
    r_bv = p_l.add_run("BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG\n")
    r_bv.bold = True
    r_bv.font.color.rgb = RGBColor(3, 105, 161)
    p_l.add_run("KHOA XÉT NGHIỆM\nSố: ...../BB-KK-XN").italic = True
    p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_r = c_right.paragraphs[0]
    p_r.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    p_r.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    p_r.add_run("-------------------\n").bold = True
    p_r.add_run("Vĩnh Long, ngày 28 tháng 11 năm 2026").italic = True
    p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(14)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("BIÊN BẢN KIỂM KÊ KHO HÓA CHẤT, SINH PHẨM & VẬT TƯ TIÊU HAO")
    r_t.bold = True
    r_t.font.size = Pt(14)
    r_t.font.color.rgb = RGBColor(30, 58, 138)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_s = p_sub.add_run("(Thực hiện định kỳ theo Quyết định 2429/QĐ-BYT - Chương VI: Quản lý hóa chất, vật tư)")
    r_s.italic = True
    r_s.font.size = Pt(10)

    # Content
    doc.add_paragraph("Hôm nay, vào lúc 16 giờ 30 phút, ngày 28 tháng 11 năm 2026, tại Kho bảo quản Hóa chất & Vật tư - Khoa Xét nghiệm Bệnh viện Đa Khoa Thiên Ân - Viễn Đông, Hội đồng kiểm kê tiến hành kiểm tra thực tế bao gồm:")
    
    doc.add_paragraph("1. Thành phần Hội đồng kiểm kê:", style='List Bullet')
    doc.add_paragraph("   - CN. Lê Đình Tú - Trưởng Khoa Xét Nghiệm (Chủ tịch Hội đồng)")
    doc.add_paragraph("   - CN. Nguyễn Trường Duy - Kỹ Thuật Viên Trưởng (Ủy viên)")
    doc.add_paragraph("   - CN. Tống Mọng Tiền - KTV Quản lý Kho hóa chất, vật tư (Thư ký)")
    doc.add_paragraph("   - Đại diện Phòng Kế toán / Phòng Vật tư - TTB Y tế Bệnh viện (Ủy viên giám sát)")

    doc.add_paragraph("2. Nội dung và kết quả kiểm kê thực tế:", style='List Bullet')
    
    # Table of sample inventory check
    table = doc.add_table(rows=7, cols=7)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    
    headers = ["STT", "Tên Hóa Chất / Sinh Phẩm / Vật Tư", "ĐVT", "Số Sổ Sách", "Thực Tế", "Chênh Lệch", "Tình Trạng Hạn Dùng / Bảo Quản"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        # shade header
        shading = parse_xml(r'<w:shd {} w:fill="1E3A8A"/>'.format(nsdecls('w')))
        cell._tc.get_or_add_tcPr().append(shading)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)

    sample_rows = [
        ("1", "Hóa chất Glucose AU (4x50ml)", "Hộp", "12", "12", "0", "HSD 08/2027 • Tủ lạnh 2-8°C Đạt"),
        ("2", "Hóa chất Urea AU (4x50ml)", "Hộp", "9", "9", "0", "HSD 06/2027 • Tủ lạnh 2-8°C Đạt"),
        ("3", "Hóa chất Creatinine AU (4x50ml)", "Hộp", "10", "10", "0", "HSD 09/2027 • Tủ lạnh 2-8°C Đạt"),
        ("4", "Cell-Dyn Diluent Pha loãng (20L)", "Can", "6", "6", "0", "HSD 12/2027 • Kho khô ráo Đạt"),
        ("5", "Kit test nhanh HBsAg (100 test)", "Hộp", "8", "8", "0", "HSD 11/2027 • Tủ mát 2-8°C Đạt"),
        ("6", "Ống nghiệm EDTA 2ml nắp tím", "Khay", "35", "35", "0", "HSD 06/2028 • Kệ kho Đạt"),
    ]

    for row_idx, r_data in enumerate(sample_rows, 1):
        for col_idx, val in enumerate(r_data):
            cell = table.cell(row_idx, col_idx)
            cell.paragraphs[0].text = val
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            if col_idx in [0, 2, 3, 4, 5]:
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    doc.add_paragraph("3. Kết luận và kiến nghị của Hội đồng kiểm kê:", style='List Bullet')
    doc.add_paragraph("   - Số lượng tồn kho thực tế khớp 100% với số liệu thẻ kho và phần mềm quản lý nội bộ.")
    doc.add_paragraph("   - Nhiệt độ kho bảo quản duy trì liên tục đạt chuẩn: Tủ lạnh 2°C - 8°C và kho khô mát 18°C - 24°C.")
    doc.add_paragraph("   - Không có hóa chất, sinh phẩm nào bị hư hỏng, biến màu, rò rỉ hoặc quá hạn sử dụng.")
    doc.add_paragraph("   - Đề xuất Ban Giám Đốc phê duyệt bảng dự trù bổ sung Hóa chất Creatinine và Ống nghiệm EDTA cho tháng 12/2026.")

    doc.add_paragraph("Biên bản được lập thành 03 bản có giá trị như nhau, thông qua các thành viên đồng ý ký tên dưới đây:")

    # Signature table
    t_sig = doc.add_table(rows=3, cols=3)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    t_sig.cell(0, 0).paragraphs[0].add_run("THƯ KÝ / THỦ KHO").bold = True
    t_sig.cell(0, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_sig.cell(0, 1).paragraphs[0].add_run("KỸ THUẬT VIÊN TRƯỞNG").bold = True
    t_sig.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_sig.cell(0, 2).paragraphs[0].add_run("CHỦ TỊCH HỘI ĐỒNG / TRƯỞNG KHOA").bold = True
    t_sig.cell(0, 2).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    t_sig.cell(1, 0).paragraphs[0].add_run("(Ký, họ tên)").italic = True
    t_sig.cell(1, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_sig.cell(1, 1).paragraphs[0].add_run("(Ký, họ tên)").italic = True
    t_sig.cell(1, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_sig.cell(1, 2).paragraphs[0].add_run("(Ký, họ tên)").italic = True
    t_sig.cell(1, 2).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sig0 = t_sig.cell(2, 0).paragraphs[0]
    p_sig0.paragraph_format.space_before = Pt(40)
    p_sig0.add_run("CN. Tống Mọng Tiền").bold = True
    p_sig0.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sig1 = t_sig.cell(2, 1).paragraphs[0]
    p_sig1.paragraph_format.space_before = Pt(40)
    p_sig1.add_run("CN. Nguyễn Trường Duy").bold = True
    p_sig1.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sig2 = t_sig.cell(2, 2).paragraphs[0]
    p_sig2.paragraph_format.space_before = Pt(40)
    p_sig2.add_run("CN. Lê Đình Tú").bold = True
    p_sig2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    out_path = TARGET_DIR / "07_BIEN_BAN_KIEM_KE_KHO_HOA_CHAT_VAT_TU_DINH_KY_THANG.docx"
    doc.save(str(out_path))
    print(f"Created: {out_path.name}")

# -------------------------------------------------------------
# 5. QUY DINH KIEM SOAT NHIET DO BAO QUAN HAN DUNG VA MO NAP.docx
# -------------------------------------------------------------
def create_quy_dinh_doc():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Header
    t_head = doc.add_table(rows=1, cols=2)
    t_head.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_left = t_head.cell(0, 0)
    c_right = t_head.cell(0, 1)

    p_l = c_left.paragraphs[0]
    p_l.add_run("BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG\n").bold = True
    p_l.add_run("KHOA XÉT NGHIỆM\nSố: 08/QĐ-KHO-XN").bold = True
    p_l.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_r = c_right.paragraphs[0]
    p_r.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\n").bold = True
    p_r.add_run("Độc lập - Tự do - Hạnh phúc\n").bold = True
    p_r.add_run("-------------------\n").bold = True
    p_r.add_run("Vĩnh Long, ngày 10 tháng 01 năm 2026").italic = True
    p_r.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(14)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("QUY ĐỊNH KIỂM SOÁT NHIỆT ĐỘ BẢO QUẢN, HẠN SỬ DỤNG\nVÀ THỜI GIAN MỞ NẮP HÓA CHẤT, SINH PHẨM XÉT NGHIỆM")
    r_t.bold = True
    r_t.font.size = Pt(13)
    r_t.font.color.rgb = RGBColor(30, 58, 138)

    doc.add_paragraph("Căn cứ Quyết định số 2429/QĐ-BYT ngày 12/06/2017 của Bộ Y tế về Tiêu chí đánh giá mức chất lượng phòng xét nghiệm y học (Chương VI: Quản lý hóa chất, vật tư tiêu hao và sinh phẩm);\nKhoa Xét nghiệm Bệnh viện Đa Khoa Thiên Ân - Viễn Đông ban hành quy định kiểm soát chi tiết như sau:")

    doc.add_heading("Điều 1: Nguyên tắc kiểm soát điều kiện bảo quản nhiệt độ", level=2)
    doc.add_paragraph("1. Toàn bộ hóa chất, sinh phẩm xét nghiệm phải được bảo quản đúng khoảng nhiệt độ theo hướng dẫn của nhà sản xuất (Ghi trên nhãn hộp):\n   - Tủ lạnh bảo quản hóa chất thường quy: Duy trì nghiêm ngặt từ +2°C đến +8°C.\n   - Tủ âm sâu trữ mẫu chuẩn/QC: Duy trì từ -20°C đến -25°C.\n   - Kho vật tư, hóa chất khô: Duy trì nhiệt độ phòng 18°C - 25°C, độ ẩm < 70%.")
    doc.add_paragraph("2. Kỹ thuật viên phụ trách phải đọc và ghi chép nhiệt độ tối thiểu 02 lần/ngày (Sáng 08h00, Chiều 16h00) vào Sổ theo dõi nhiệt độ - độ ẩm phòng và tủ lạnh.")

    doc.add_heading("Điều 2: Nguyên tắc quản lý hạn sử dụng (FEFO - Hết hạn trước xuất trước)", level=2)
    doc.add_paragraph("1. Áp dụng nguyên tắc FEFO (First Expired, First Out): Hóa chất nào có hạn sử dụng gần hơn phải được xếp ở phía ngoài và xuất sử dụng trước.")
    doc.add_paragraph("2. Định kỳ hàng tuần, thủ kho phải rà soát hạn sử dụng trên phần mềm và sổ kho:\n   - Cảnh báo vàng: Khi hóa chất còn hạn dưới 60 ngày.\n   - Cảnh báo đỏ: Khi hóa chất còn hạn dưới 30 ngày (cận date) -> Phải lập biên bản báo cáo Trưởng khoa để ưu tiên sử dụng hoặc điều phối khẩn.")

    doc.add_heading("Điều 3: Quy định dán nhãn ngày mở nắp và hạn dùng sau mở nắp", level=2)
    doc.add_paragraph("1. Ngay khi mở nắp lọ hóa chất, sinh phẩm hoặc kit test, KTV thực hiện phải ghi ngay nhãn phụ dán lên thân lọ gồm:\n   - Ngày mở nắp (Ví dụ: Mở: 16/11/2026)\n   - Hạn dùng sau mở nắp (Ví dụ: Hạn sau mở: 16/12/2026)\n   - Tên người mở (Ví dụ: Duy / Tiền)")
    doc.add_paragraph("2. Nghiêm cấm sử dụng các lọ hóa chất không có nhãn ngày mở nắp hoặc đã quá thời hạn quy định trên máy phân tích.")

    # Signatures
    t_sig = doc.add_table(rows=2, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_sig.cell(0, 0).paragraphs[0].add_run("KỸ THUẬT VIÊN TRƯỞNG").bold = True
    t_sig.cell(0, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_sig.cell(0, 1).paragraphs[0].add_run("TRƯỞNG KHOA XÉT NGHIỆM\n(Phê duyệt)").bold = True
    t_sig.cell(0, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_s0 = t_sig.cell(1, 0).paragraphs[0]
    p_s0.paragraph_format.space_before = Pt(45)
    p_s0.add_run("CN. Nguyễn Trường Duy").bold = True
    p_s0.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_s1 = t_sig.cell(1, 1).paragraphs[0]
    p_s1.paragraph_format.space_before = Pt(45)
    p_s1.add_run("CN. Lê Đình Tú").bold = True
    p_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER

    out_path = TARGET_DIR / "08_QUY_DINH_KIEM_SOAT_NHIET_DO_BAO_QUAN_HAN_DUNG_VA_MO_NAP.docx"
    doc.save(str(out_path))
    print(f"Created: {out_path.name}")

if __name__ == "__main__":
    create_so_theo_doi_excel()
    create_bang_du_tru_excel()
    create_the_kho_excel()
    create_bien_ban_kiem_ke_doc()
    create_quy_dinh_doc()
    print("All 5 inventory documents created successfully!")
