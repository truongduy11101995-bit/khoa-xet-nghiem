import sys
from pathlib import Path
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

app_dir = Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
sys.path.insert(0, str(app_dir))
os.chdir(str(app_dir))

from backend.database import get_db

# 129 items from VN MED quotation
ITEMS_DATA = [
    # HÓA CHẤT MÁY SINH HÓA (1 - 65)
    ("SH-ALB-01", "Albumin", "hoa_chat", "R1: 4x60ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2601", "2027-11-30", "2-8°C", 6, 2, 4, 465000, "Tủ lạnh Sinh hóa 2-8°C", "Hóa chất máy sinh hóa tự động"),
    ("SH-ALC-02", "Alcohol, Ammoniac, CO2 calibrator", "qc_chuan", "1x2ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2602", "2027-10-31", "2-8°C", 3, 1, 1, 424000, "Tủ lạnh Sinh hóa 2-8°C", "Chuẩn nồng độ cồn, NH3, CO2"),
    ("SH-ALC-03", "Alcohol, Ammoniac, CO2 control L1", "qc_chuan", "1x2ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2603", "2027-10-31", "2-8°C", 3, 1, 1, 424000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng kiểm tra mức 1"),
    ("SH-ALC-04", "Alcohol, Ammoniac, CO2 control L2", "qc_chuan", "1x2ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2604", "2027-10-31", "2-8°C", 3, 1, 1, 424000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng kiểm tra mức 2"),
    ("SH-ALT-05", "ALT(GPT)", "hoa_chat", "R1: 6x30ml; R2: 2x18ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2605", "2027-12-31", "2-8°C", 8, 3, 6, 583000, "Tủ lạnh Sinh hóa 2-8°C", "Men gan ALT"),
    ("SH-AMM-06", "Ammonia", "hoa_chat", "R1: 10x10ml; Cal: 1x1ml; Ctl1: 1x1ml; Ctl2: 1x1ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2606", "2027-09-30", "2-8°C", 4, 1, 2, 1525000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Amoniac máu"),
    ("SH-ASO-07", "ASO", "hoa_chat", "R1: 2x40ml; R2: 2x10ml; Cal: 1x1ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2607", "2027-10-31", "2-8°C", 3, 1, 2, 2222000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Antistreptolysin O"),
    ("SH-AST-08", "AST(GOT)", "hoa_chat", "R1: 6x30ml; R2: 2x18ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2608", "2027-12-31", "2-8°C", 8, 3, 6, 583000, "Tủ lạnh Sinh hóa 2-8°C", "Men gan AST"),
    ("SH-CAL-09", "Calcium", "hoa_chat", "R1: 4x60ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2609", "2027-11-30", "2-8°C", 5, 2, 3, 758000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Canxi toàn phần"),
    ("SH-CS-10", "Calibration Serum", "qc_chuan", "10x3ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2610", "2027-08-31", "2-8°C", 4, 1, 2, 3283000, "Tủ lạnh Sinh hóa 2-8°C", "Huyết thanh chuẩn đa thông số"),
    ("SH-CRP-11", "CRP Full Range", "hoa_chat", "R1: 2x40ml; R2: 2x10ml; Cal: 1x1ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2611", "2027-11-30", "2-8°C", 6, 2, 4, 2677000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng C-Reactive Protein dải rộng"),
    ("SH-CHO-12", "Cholesterol (CHOD PAP)", "hoa_chat", "R1: 8x60ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2612", "2027-12-31", "2-8°C", 10, 3, 7, 1162000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Cholesterol toàn phần"),
    ("SH-CHE-13", "Cholinesterase", "hoa_chat", "R1: 5x20ml; R2: 2x10ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2613", "2027-10-31", "2-8°C", 3, 1, 2, 1010000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng men Cholinesterase"),
    ("SH-FER-14", "Ferritin", "hoa_chat", "R1: 1x20ml; R2: 1x5ml; Cal: 1ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2614", "2027-09-30", "2-8°C", 4, 1, 2, 1333000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng dự trữ sắt Ferritin"),
    ("SH-GGT-15", "Gamma-GT", "hoa_chat", "R1: 6x30ml; R2: 2x18ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2615", "2027-12-31", "2-8°C", 7, 2, 5, 1339000, "Tủ lạnh Sinh hóa 2-8°C", "Men gan GGT"),
    ("SH-GLU-16", "Glucose GOD PAP", "hoa_chat", "R1: 8x60ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2616", "2027-12-31", "2-8°C", 12, 4, 8, 567000, "Tủ lạnh Sinh hóa 2-8°C", "Đường huyết Glucose GOD-PAP"),
    ("SH-HAC-17", "Human Assayed Control L3 (Elevated)", "qc_chuan", "10x5ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2617", "2027-08-31", "2-8°C", 3, 1, 1, 3283000, "Tủ lạnh Sinh hóa 2-8°C", "Huyết thanh kiểm tra mức cao"),
    ("SH-HAC-18", "Human Assayed Control L2 (normal)", "qc_chuan", "10x5ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2618", "2027-08-31", "2-8°C", 4, 1, 2, 3283000, "Tủ lạnh Sinh hóa 2-8°C", "Huyết thanh kiểm tra mức bình thường"),
    ("SH-IRO-19", "Iron Monoliquid", "hoa_chat", "R1: 4x30ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2619", "2027-11-30", "2-8°C", 4, 1, 2, 707000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Sắt huyết thanh"),
    ("SH-LAC-20", "Lactate", "hoa_chat", "R1: 2x30ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2620", "2027-09-30", "2-8°C", 3, 1, 2, 1768000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Axit Lactic máu"),
    ("SH-LIP-21", "Lipase", "hoa_chat", "R1: 2x10ml; R2: 1x10ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2621", "2027-10-31", "2-8°C", 4, 1, 2, 1768000, "Tủ lạnh Sinh hóa 2-8°C", "Men tụy Lipase"),
    ("SH-MAG-22", "Magnesium", "hoa_chat", "R1: 2x20ml; R2: 2x20ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2622", "2027-11-30", "2-8°C", 5, 2, 3, 586000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Magie huyết thanh"),
    ("SH-SPC-23", "Specific Protein Control Level 1", "qc_chuan", "1x1ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2623", "2027-09-30", "2-8°C", 3, 1, 1, 606000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng Protein đặc hiệu mức 1"),
    ("SH-SPC-24", "Specific Protein Control Level 2", "qc_chuan", "1x1ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2624", "2027-09-30", "2-8°C", 3, 1, 1, 606000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng Protein đặc hiệu mức 2"),
    ("SH-RF-25", "RF", "hoa_chat", "R1: 4x40ml; R2: 4x10ml; Cal: 1x2ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2625", "2027-10-31", "2-8°C", 3, 1, 2, 3131000, "Tủ lạnh Sinh hóa 2-8°C", "Yếu tố dạng thấp Rheumatoid Factor"),
    ("SH-TRA-26", "Transferrin", "hoa_chat", "R1: 2x20ml; R2: 1x8ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2626", "2027-10-31", "2-8°C", 3, 1, 2, 1414000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Transferrin"),
    ("SH-TP-27", "Total Protein", "hoa_chat", "R1: 6x60ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2627", "2027-12-31", "2-8°C", 6, 2, 4, 606000, "Tủ lạnh Sinh hóa 2-8°C", "Protein toàn phần"),
    ("SH-ALB-28", "ALBUMIN (Dirui)", "hoa_chat", "5x50ml, Cal: 2ml", "Hộp", "Dirui/Trung Quốc", "LOT2628", "2027-11-30", "2-8°C", 5, 2, 4, 262000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Albumin"),
    ("SH-AMY-29", "Amylase", "hoa_chat", "R1: 4x50ml; R2: 1x50ml", "Hộp", "Dirui/Trung Quốc", "LOT2629", "2027-09-30", "2-8°C", 3, 1, 2, 6263000, "Tủ lạnh Sinh hóa 2-8°C", "Men Amylase máu và nước tiểu"),
    ("SH-ALT-30", "Alanine Aminotransferase Liquid (ALT/GPT)", "hoa_chat", "R1: 4x50ml; R2: 1x50ml", "Hộp", "Dirui/Trung Quốc", "LOT2630", "2027-12-31", "2-8°C", 6, 2, 5, 435000, "Tủ lạnh Sinh hóa 2-8°C", "Men gan ALT Dirui"),
    ("SH-AST-31", "Aspartate Aminotransferase Reagent kit (AST/GOT)", "hoa_chat", "R1: 4x50ml; R2: 1x50ml", "Hộp", "Dirui/Trung Quốc", "LOT2631", "2027-12-31", "2-8°C", 6, 2, 5, 435000, "Tủ lạnh Sinh hóa 2-8°C", "Men gan AST Dirui"),
    ("SH-DBIL-32", "Direct Bilirubin", "hoa_chat", "R1: 4x50ml; R2: 1x50ml", "Hộp", "Dirui/Trung Quốc", "LOT2632", "2027-10-31", "2-8°C", 4, 1, 3, 1088000, "Tủ lạnh Sinh hóa 2-8°C", "Bilirubin trực tiếp"),
    ("SH-TBIL-33", "Total Bilirubin", "hoa_chat", "R1: 4x50ml; R2: 1x50ml", "Hộp", "Dirui/Trung Quốc", "LOT2633", "2027-10-31", "2-8°C", 4, 1, 3, 1088000, "Tủ lạnh Sinh hóa 2-8°C", "Bilirubin toàn phần"),
    ("SH-CHO-34", "Cholesterol Reagent Kit", "hoa_chat", "R1: 4x50ml; R2: 1x50ml, Cal: 2ml", "Hộp", "Dirui/Trung Quốc", "LOT2634", "2027-12-31", "2-8°C", 6, 2, 5, 1044000, "Tủ lạnh Sinh hóa 2-8°C", "Cholesterol toàn phần Dirui"),
    ("SH-CRE-35", "CREATININE (Enzymatic Method)", "hoa_chat", "R1: 3 x 60mL; R2: 1 x 60mL", "Hộp", "BSBE/Trung Quốc", "LOT2635", "2027-12-31", "2-8°C", 8, 3, 6, 1469000, "Tủ lạnh Sinh hóa 2-8°C", "Creatinine phương pháp Enzymatic độ chính xác cao"),
    ("SH-GGT-36", "Gamma-GT (Dirui)", "hoa_chat", "R1: 4x50ml; R2: 1x50ml", "Hộp", "Dirui/Trung Quốc", "LOT2636", "2027-11-30", "2-8°C", 5, 2, 4, 914000, "Tủ lạnh Sinh hóa 2-8°C", "GGT Dirui"),
    ("SH-GLU-37", "GLUCOSE REAGENT KIT (HEXOKINASE METHOD)", "hoa_chat", "R1: 4x50ml; R2: 1x50ml", "Hộp", "Dirui/Trung Quốc", "LOT2637", "2027-12-31", "2-8°C", 8, 3, 6, 522000, "Tủ lạnh Sinh hóa 2-8°C", "Glucose Hexokinase chuẩn tham chiếu"),
    ("SH-TP-38", "TOTAL PROTEIN REAGENT KIT (BIURET METHOD)", "hoa_chat", "5x50ml; CAL 2ml", "Hộp", "Dirui/Trung Quốc", "LOT2638", "2027-12-31", "2-8°C", 5, 2, 4, 305000, "Tủ lạnh Sinh hóa 2-8°C", "Protein toàn phần Biuret"),
    ("SH-PHO-39", "Inorganic Phosphorous Reagent Kit", "hoa_chat", "5x50ml, cal: 2mL", "Hộp", "Dirui/Trung Quốc", "LOT2639", "2027-10-31", "2-8°C", 4, 1, 2, 305000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Photpho vô cơ"),
    ("SH-TRI-40", "TRIGLYCERIDES REAGENT KIT", "hoa_chat", "R1: 4x50ml; R2: 1x50ml, Cal: 2ml", "Hộp", "Dirui/Trung Quốc", "LOT2640", "2027-12-31", "2-8°C", 8, 3, 6, 1218000, "Tủ lạnh Sinh hóa 2-8°C", "Triglyceride Dirui"),
    ("SH-URE-41", "Urea Reagent kit", "hoa_chat", "R1: 4x50ml; R2: 1x50ml, Cal: 2ml", "Hộp", "Dirui/Trung Quốc", "LOT2641", "2027-12-31", "2-8°C", 9, 3, 7, 827000, "Tủ lạnh Sinh hóa 2-8°C", "Ure máu Dirui"),
    ("SH-URI-42", "Uric Acid Reagent Kit", "hoa_chat", "R1: 4x50ml; R2: 1x50ml, Cal: 2ml", "Hộp", "Dirui/Trung Quốc", "LOT2642", "2027-12-31", "2-8°C", 8, 3, 6, 697000, "Tủ lạnh Sinh hóa 2-8°C", "Axit Uric máu"),
    ("SH-IRO-43", "Iron Assay Kit", "hoa_chat", "R1: 2x40 ml; R2: 2x10 ml", "Hộp", "BSBE/Trung Quốc", "LOT2643", "2027-10-31", "2-8°C", 4, 1, 2, 478000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Sắt BSBE"),
    ("SH-TRA-44", "TRANSFERRIN REAGENT KIT", "hoa_chat", "1x50, 1x10, Cal 1x1", "Hộp", "Dirui/Trung Quốc", "LOT2644", "2027-10-31", "2-8°C", 3, 1, 2, 1305000, "Tủ lạnh Sinh hóa 2-8°C", "Transferrin Dirui"),
    ("SH-LIP-45", "Lipase Assay Kit", "hoa_chat", "R1: 1x60 ml; R2: 1x20 ml", "Hộp", "BSBE/Trung Quốc", "LOT2645", "2027-09-30", "2-8°C", 3, 1, 2, 3045000, "Tủ lạnh Sinh hóa 2-8°C", "Lipase BSBE"),
    ("SH-HDL-46", "High Desity Lipoprotein Cholesterol (HDL-C)", "hoa_chat", "R1: 3x50ml, R2: 2x25ml, Calib: 0.8ml", "Hộp", "Dirui/Trung Quốc", "LOT2646", "2027-12-31", "2-8°C", 6, 2, 5, 871000, "Tủ lạnh Sinh hóa 2-8°C", "HDL-Cholesterol"),
    ("SH-LDL-47", "Low density lipoprotein Cholesterol (LDL-C)", "hoa_chat", "R1: 1 x 60mL; R2: 1 x 20mL", "Hộp", "BSBE/Trung Quốc", "LOT2647", "2027-12-31", "2-8°C", 6, 2, 5, 1233000, "Tủ lạnh Sinh hóa 2-8°C", "LDL-Cholesterol"),
    ("SH-CAL-48", "HDL/LDL Calibrator", "qc_chuan", "1x1,0ml, 1x1,0ml", "Hộp", "BSBE/Trung Quốc", "LOT2648", "2027-09-30", "2-8°C", 3, 1, 1, 435000, "Tủ lạnh Sinh hóa 2-8°C", "Chuẩn HDL và LDL"),
    ("SH-CLN-49", "CELL-CLEANER", "vat_tu", "2,000ml", "Hộp", "Labno", "LOT2649", "2028-06-30", "Phòng", 5, 2, 3, 305000, "Kho vật tư", "Dung dịch rửa kim và buồng phản ứng"),
    ("SH-FER-50", "Ferritin (Dirui)", "hoa_chat", "4x40; 2x40, Cal: 5x0.5, control: 2x0,5", "Hộp", "Dirui/Trung Quốc", "LOT2650", "2027-08-31", "2-8°C", 2, 1, 1, 12940000, "Tủ lạnh Sinh hóa 2-8°C", "Bộ kít Ferritin Dirui đầy đủ Cal/Ctl"),
    ("SH-ETH-51", "Ethanol (Alcohol)", "hoa_chat", "R1: 2 x 30mL; R2: 2 x 10mL; cal: 1x2ml, control: 2x1ml", "Hộp", "BSBE/Trung Quốc", "LOT2651", "2027-09-30", "2-8°C", 3, 1, 1, 1549000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng nồng độ cồn trong máu"),
    ("SH-HBA-52", "Hemoglobin A1c Assay Kit (HbA1c)", "hoa_chat", "R1: 1 x 60mL; R2: 1 x 20mL; Lyse: 2 x 90mL", "Hộp", "BSBE/Trung Quốc", "LOT2652", "2027-11-30", "2-8°C", 4, 1, 3, 5263000, "Tủ lạnh Sinh hóa 2-8°C", "Theo dõi đường huyết HbA1c 3 tháng"),
    ("SH-HBA-53", "HBA1C Calibrator", "qc_chuan", "4x0.5ml", "Hộp", "BSBE/Trung Quốc", "LOT2653", "2027-09-30", "2-8°C", 3, 1, 1, 652000, "Tủ lạnh Sinh hóa 2-8°C", "Chuẩn nồng độ HbA1c"),
    ("SH-HBA-54", "HBA1C control", "qc_chuan", "2x0.5ml", "Hộp", "BSBE/Trung Quốc", "LOT2654", "2027-09-30", "2-8°C", 3, 1, 1, 262000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng kiểm tra HbA1c"),
    ("SH-B2M-55", "beta 2 microglobulin", "hoa_chat", "R1: 3x15ml, R2: 1x15ml", "Hộp", "BSBE/Trung Quốc", "LOT2655", "2027-10-31", "2-8°C", 2, 1, 1, 3915000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng beta 2 microglobulin"),
    ("SH-B2M-56", "beta 2 microglobulin Calibrator (Serum)", "qc_chuan", "4x1ml", "Hộp", "BSBE/Trung Quốc", "LOT2656", "2027-08-31", "2-8°C", 2, 1, 1, 435000, "Tủ lạnh Sinh hóa 2-8°C", "Chuẩn beta 2 microglobulin huyết thanh"),
    ("SH-B2M-57", "beta 2 microglobulin Control (Serum & Urine)", "qc_chuan", "2x1ml", "Hộp", "BSBE/Trung Quốc", "LOT2657", "2027-08-31", "2-8°C", 2, 1, 1, 202000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng beta 2 microglobulin"),
    ("SH-D3H-58", "D3-Hydroxybutyrate (b2-Hydroxybutyrate)", "hoa_chat", "R1: 1x60ml; R2: 1x20ml", "Hộp", "BSBE/Trung Quốc", "LOT2658", "2027-09-30", "2-8°C", 2, 1, 1, 1455000, "Tủ lạnh Sinh hóa 2-8°C", "Thể Ceton máu trong đái tháo đường"),
    ("SH-D3H-59", "D3-Hydroxybutyrate (b2-Hydroxybutyrate) Calibrator", "qc_chuan", "1x2ml", "Hộp", "BSBE/Trung Quốc", "LOT2659", "2027-08-31", "2-8°C", 2, 1, 1, 202000, "Tủ lạnh Sinh hóa 2-8°C", "Chuẩn Ceton"),
    ("SH-MYO-60", "Myoglobin", "hoa_chat", "R1: 1x60ml; R2: 1x20ml", "Hộp", "BSBE/Trung Quốc", "LOT2660", "2027-09-30", "2-8°C", 2, 1, 1, 10004000, "Tủ lạnh Sinh hóa 2-8°C", "Dấu ấn nhồi máu cơ tim sớm"),
    ("SH-MYO-61", "Myoglobin Calibrator", "qc_chuan", "4x1ml", "Hộp", "BSBE/Trung Quốc", "LOT2661", "2027-08-31", "2-8°C", 2, 1, 1, 651000, "Tủ lạnh Sinh hóa 2-8°C", "Chuẩn Myoglobin"),
    ("SH-MYO-62", "Myoglobin Control", "qc_chuan", "2x3ml", "Hộp", "BSBE/Trung Quốc", "LOT2662", "2027-08-31", "2-8°C", 2, 1, 1, 392000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng Myoglobin"),
    ("SH-MAL-63", "Microalbumin (mALB)", "hoa_chat", "R1: 1 x 60mL; R2: 1 x 20ml", "Hộp", "BSBE/Trung Quốc", "LOT2663", "2027-10-31", "2-8°C", 3, 1, 2, 2001000, "Tủ lạnh Sinh hóa 2-8°C", "Định lượng Microalbumin niệu"),
    ("SH-MAL-64", "Microalbumin Calibrator", "qc_chuan", "6x2ml", "Hộp", "BSBE/Trung Quốc", "LOT2664", "2027-08-31", "2-8°C", 2, 1, 1, 435000, "Tủ lạnh Sinh hóa 2-8°C", "Chuẩn Microalbumin"),
    ("SH-MAL-65", "Microalbumin Control", "qc_chuan", "2x1ml", "Hộp", "BSBE/Trung Quốc", "LOT2665", "2027-08-31", "2-8°C", 2, 1, 1, 218000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng Microalbumin niệu"),

    # HÓA CHẤT HUYẾT HỌC 5 THÀNH PHẦN (66 - 71)
    ("HH-GD5-66", "Automatic Hematology Analyzer GD-5 Diluent A", "hoa_chat", "20Lx1", "Hộp", "Maccura/Trung Quốc", "LOT2666", "2028-06-30", "15-25°C", 6, 2, 4, 331000, "Kho hóa chất huyết học", "Dung dịch pha loãng máy Maccura 5 thành phần"),
    ("HH-DD5-67", "Automatic Hematology Analyzer DD-5 Fluorescent Dye A", "hoa_chat", "42mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2667", "2027-11-30", "2-8°C", 3, 1, 2, 3045000, "Tủ lạnh Huyết học 2-8°C", "Thuốc nhuộm huỳnh quang đếm bạch cầu"),
    ("HH-LD5-68", "Automatic Hematology Analyzer LD-5 Lysing Reagent A", "hoa_chat", "1Lx1", "Hộp", "Maccura/Trung Quốc", "LOT2668", "2027-12-31", "15-25°C", 4, 1, 2, 1393000, "Kho hóa chất huyết học", "Dung dịch phá hủy hồng cầu LD-5"),
    ("HH-LH5-69", "Automatic Hematology Analyzer LH-5 Lysing Reagent A", "hoa_chat", "500ML", "Hộp", "Maccura/Trung Quốc", "LOT2669", "2027-12-31", "15-25°C", 4, 1, 2, 1914000, "Kho hóa chất huyết học", "Dung dịch phá hủy hồng cầu LH-5"),
    ("HH-CTL-70", "Hematology Analyzer Control", "qc_chuan", "3x2,5 ml", "Bộ", "Maccura/Trung Quốc", "LOT2670", "2027-06-30", "2-8°C", 3, 1, 1, 3636000, "Tủ lạnh Huyết học 2-8°C", "Huyết thanh kiểm tra huyết học 3 mức"),
    ("HH-CC5-71", "Automatic Hematology Analyzer CC-5 Cell Clean A", "vat_tu", "2 mLx6", "Hộp", "Maccura/Trung Quốc", "LOT2671", "2028-05-31", "15-25°C", 5, 2, 3, 1403000, "Kho hóa chất huyết học", "Dung dịch bảo dưỡng tẩy rửa định kỳ máy huyết học"),

    # NƯỚC TIỂU (72 - 74)
    ("NT-STR-72", "Urine Strip 11", "sinh_pham", "100 Test", "Hộp", "Fortress Diagnostics/Anh", "LOT2672", "2027-12-31", "15-25°C", 10, 3, 6, 247000, "Bàn nước tiểu", "Que thử nước tiểu 11 thông số"),
    ("NT-POS-73", "Positive control (Urine)", "qc_chuan", "4x8ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2673", "2027-09-30", "2-8°C", 3, 1, 1, 1414000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng dương nước tiểu"),
    ("NT-NEG-74", "Negative Control (Urine)", "qc_chuan", "4x8ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2674", "2027-09-30", "2-8°C", 3, 1, 1, 1414000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng âm nước tiểu"),

    # HÓA CHẤT MÁY ION ĐỒ 5 THÔNG SỐ (75 - 90)
    ("ID-PCK-75", "Reagent Pack (Electalyte-200/500)", "hoa_chat", "1000mL", "Hộp", "Fortress Diagnostics/Anh", "LOT2675", "2027-12-31", "15-25°C", 4, 1, 2, 3636000, "Phòng máy Điện giải", "Gói hóa chất máy điện giải Ion đồ"),
    ("ID-CTL-76", "Electrolytes control L1& L2 & L3", "qc_chuan", "L1: 10x2ml; L2: 10x2ml; L3: 10x2ml", "Hộp", "Fortress Diagnostics/Anh", "LOT2676", "2027-10-31", "2-8°C", 3, 1, 1, 752000, "Tủ lạnh Sinh hóa 2-8°C", "Chứng kiểm tra điện giải 3 mức"),
    ("ID-CAL-77", "Cal solution", "qc_chuan", "100ml", "Lọ", "Fortress Diagnostics/Anh", "LOT2677", "2027-12-31", "15-25°C", 4, 1, 2, 465000, "Phòng máy Điện giải", "Dung dịch hiệu chuẩn Ion đồ"),
    ("ID-CLN-78", "Weekly cleaning solution", "vat_tu", "100mL", "Lọ", "Fortress Diagnostics/Anh", "LOT2678", "2028-06-30", "15-25°C", 4, 1, 2, 1209000, "Phòng máy Điện giải", "Dung dịch rửa hàng tuần máy Ion đồ"),
    ("ID-DIL-79", "Urine diluent", "hoa_chat", "100mL", "Lọ", "Fortress Diagnostics/Anh", "LOT2679", "2028-06-30", "15-25°C", 3, 1, 1, 556000, "Phòng máy Điện giải", "Dung dịch pha loãng điện giải niệu"),
    ("ID-CND-80", "Na Conditioner", "hoa_chat", "100mL", "Lọ", "Fortress Diagnostics/Anh", "LOT2680", "2028-06-30", "15-25°C", 3, 1, 1, 626000, "Phòng máy Điện giải", "Dung dịch hoạt hóa điện cực Natri"),
    ("ID-KFL-81", "K Filling Solution", "hoa_chat", "15mL", "Lọ", "Fortress Diagnostics/Anh", "LOT2681", "2028-06-30", "15-25°C", 4, 1, 2, 313000, "Phòng máy Điện giải", "Dung dịch châm điện cực Kali"),
    ("ID-CFL-82", "Ca Filling Solution", "hoa_chat", "15mL", "Lọ", "Fortress Diagnostics/Anh", "LOT2682", "2028-06-30", "15-25°C", 4, 1, 2, 313000, "Phòng máy Điện giải", "Dung dịch châm điện cực Canxi"),
    ("ID-RFL-83", "Reference Filling Solution", "hoa_chat", "15mL", "Lọ", "Fortress Diagnostics/Anh", "LOT2683", "2028-06-30", "15-25°C", 4, 1, 2, 313000, "Phòng máy Điện giải", "Dung dịch châm điện cực so sánh"),
    ("ID-PFL-84", "pH, Na, Cl Filling solution", "hoa_chat", "15mL", "Lọ", "Fortress Diagnostics/Anh", "LOT2684", "2028-06-30", "15-25°C", 4, 1, 2, 313000, "Phòng máy Điện giải", "Dung dịch châm điện cực pH, Na, Cl"),
    ("ID-ELD-85", "Na Electrode", "vat_tu", "Cái", "Cái", "Fortress Diagnostics/Anh", "LOT2685", "2029-12-31", "Phòng", 2, 1, 1, 3081000, "Phòng máy Điện giải", "Điện cực đo Natri"),
    ("ID-ELD-86", "K Electrode", "vat_tu", "Cái", "Cái", "Fortress Diagnostics/Anh", "LOT2686", "2029-12-31", "Phòng", 2, 1, 1, 3081000, "Phòng máy Điện giải", "Điện cực đo Kali"),
    ("ID-ELD-87", "Ca Electrode", "vat_tu", "Cái", "Cái", "Fortress Diagnostics/Anh", "LOT2687", "2029-12-31", "Phòng", 2, 1, 1, 3081000, "Phòng máy Điện giải", "Điện cực đo Canxi ion hóa"),
    ("ID-ELD-88", "Cl Electrode", "vat_tu", "Cái", "Cái", "Fortress Diagnostics/Anh", "LOT2688", "2029-12-31", "Phòng", 2, 1, 1, 3081000, "Phòng máy Điện giải", "Điện cực đo Clo"),
    ("ID-ELD-89", "pH Electrode", "vat_tu", "Cái", "Cái", "Fortress Diagnostics/Anh", "LOT2689", "2029-12-31", "Phòng", 2, 1, 1, 3081000, "Phòng máy Điện giải", "Điện cực đo pH máu"),
    ("ID-ELD-90", "Reference Electrode", "vat_tu", "Cái", "Cái", "Fortress Diagnostics/Anh", "LOT2690", "2029-12-31", "Phòng", 2, 1, 1, 3081000, "Phòng máy Điện giải", "Điện cực so sánh Ref"),

    # HÓA CHẤT MIỄN DỊCH (91 - 117)
    ("MD-TSH-91", "TSH (CLIA)", "hoa_chat", "2 x 100 Test", "Hộp", "Maccura/Trung Quốc", "LOT2691", "2027-11-30", "2-8°C", 4, 1, 3, 2749000, "Tủ lạnh Miễn dịch 2-8°C", "Xét nghiệm chức năng tuyến giáp TSH"),
    ("MD-FT3-92", "FT3 (CLIA)", "hoa_chat", "2 x 100 Test", "Hộp", "Maccura/Trung Quốc", "LOT2692", "2027-11-30", "2-8°C", 4, 1, 3, 2749000, "Tủ lạnh Miễn dịch 2-8°C", "Định lượng Triiodothyronine tự do FT3"),
    ("MD-FT4-93", "FT4 (CLIA)", "hoa_chat", "2 x 100 Test", "Hộp", "Maccura/Trung Quốc", "LOT2693", "2027-11-30", "2-8°C", 4, 1, 3, 2749000, "Tủ lạnh Miễn dịch 2-8°C", "Định lượng Thyroxine tự do FT4"),
    ("MD-TPO-94", "Anti-TPO (CLIA)", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2694", "2027-10-31", "2-8°C", 2, 1, 1, 5584000, "Tủ lạnh Miễn dịch 2-8°C", "Kháng thể tuyến giáp Anti-TPO"),
    ("MD-HBA-95", "HBsAb (CLIA)", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2695", "2027-12-31", "2-8°C", 4, 1, 2, 3525000, "Tủ lạnh Miễn dịch 2-8°C", "Định lượng kháng thể viêm gan B"),
    ("MD-CTL-96", "Anti-HBsAb Control Level 1", "qc_chuan", "2mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2696", "2027-09-30", "2-8°C", 2, 1, 1, 488000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBsAb mức 1"),
    ("MD-CTL-97", "Anti-HBsAb Control Level 2", "qc_chuan", "2mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2697", "2027-09-30", "2-8°C", 2, 1, 1, 488000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBsAb mức 2"),
    ("MD-HBG-98", "HBsAg (CLIA)", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2698", "2027-12-31", "2-8°C", 5, 2, 4, 3727000, "Tủ lạnh Miễn dịch 2-8°C", "Kháng nguyên bề mặt viêm gan B HBsAg"),
    ("MD-CTL-99", "HBsAg Quantitative Control L1", "qc_chuan", "2mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2699", "2027-09-30", "2-8°C", 2, 1, 1, 488000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBsAg mức 1"),
    ("MD-CTL-100", "HBsAg Quantitative Control L2", "qc_chuan", "2mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2700", "2027-09-30", "2-8°C", 2, 1, 1, 488000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBsAg mức 2"),
    ("MD-CTL-101", "HBsAg Quantitative Control L3", "qc_chuan", "2mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2701", "2027-09-30", "2-8°C", 2, 1, 1, 488000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBsAg mức 3"),
    ("MD-HBE-102", "HBeAg (CLIA)", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2702", "2027-11-30", "2-8°C", 3, 1, 2, 4732000, "Tủ lạnh Miễn dịch 2-8°C", "Kháng nguyên viêm gan B thể hoạt động HBeAg"),
    ("MD-CTL-103", "HBeAg Quantitative Control L1", "qc_chuan", "1mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2703", "2027-08-31", "2-8°C", 2, 1, 1, 469000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBeAg mức 1"),
    ("MD-CTL-104", "HBeAg Quantitative Control L2", "qc_chuan", "1mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2704", "2027-08-31", "2-8°C", 2, 1, 1, 469000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBeAg mức 2"),
    ("MD-CTL-105", "HBeAg Quantitative Control L3", "qc_chuan", "1mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2705", "2027-08-31", "2-8°C", 2, 1, 1, 469000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra HBeAg mức 3"),
    ("MD-HCV-106", "Anti-HCV Chemiluminescent Immunoassay Kit", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2706", "2027-12-31", "2-8°C", 4, 1, 2, 7215000, "Tủ lạnh Miễn dịch 2-8°C", "Kháng thể viêm gan C Anti-HCV CLIA"),
    ("MD-CTL-107", "anti-HCV Control", "qc_chuan", "QC1~2 1.0mLx2", "Hộp", "Maccura/Trung Quốc", "LOT2707", "2027-09-30", "2-8°C", 2, 1, 1, 1462000, "Tủ lạnh Miễn dịch 2-8°C", "Chứng kiểm tra Anti-HCV"),
    ("MD-BUF-108", "Chemiluminescence Analyzer Substrate Buffer", "hoa_chat", "A:500 ml x 1; B: 500 ml x 1", "Hộp", "Maccura/Trung Quốc", "LOT2708", "2028-06-30", "2-8°C", 3, 1, 2, 2147000, "Tủ lạnh Miễn dịch 2-8°C", "Dung dịch cơ chất phát quang hóa học A+B"),
    ("MD-WSH-109", "Chemiluminescence Analyzer Wash Buffer", "vat_tu", "250 ml x 2", "Hộp", "Maccura/Trung Quốc", "LOT2709", "2028-06-30", "15-25°C", 4, 1, 2, 387000, "Kho miễn dịch", "Dung dịch đệm rửa máy miễn dịch phát quang"),
    ("MD-CUV-110", "Chemiluminescence Analyzer Reaction Cuvettes", "vat_tu", "3500 / boxes", "Hộp", "Maccura/Trung Quốc", "LOT2710", "2029-12-31", "Phòng", 5, 2, 3, 6443000, "Kho miễn dịch", "Cuvette phản ứng máy phát quang Maccura"),
    ("MD-WSB-111", "WS Wash Buffer", "vat_tu", "60mLx2", "Hộp", "Maccura/Trung Quốc", "LOT2711", "2028-06-30", "15-25°C", 4, 1, 2, 258000, "Kho miễn dịch", "Dung dịch rửa WS Wash Buffer"),
    ("MD-HIV-112", "HIV Ag/Ab (CLIA)", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2712", "2027-12-31", "2-8°C", 4, 1, 2, 7111000, "Tủ lạnh Miễn dịch 2-8°C", "Sàng lọc HIV Ag/Ab thế hệ thứ 4 phát quang"),
    ("MD-AFP-113", "AFP (CLIA) 2x100", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2713", "2027-11-30", "2-8°C", 3, 1, 2, 4296000, "Tủ lạnh Miễn dịch 2-8°C", "Dấu ấn ung thư gan Alpha-Fetoprotein"),
    ("MD-AFP-114", "AFP (CLIA) 2x50", "hoa_chat", "2x50", "Hộp", "Maccura/Trung Quốc", "LOT2714", "2027-11-30", "2-8°C", 3, 1, 2, 2792000, "Tủ lạnh Miễn dịch 2-8°C", "Dấu ấn AFP đóng gói 100 test"),
    ("MD-CEA-115", "CEA Chemiluminescent Immunoassay Kit", "hoa_chat", "2x100", "Hộp", "Maccura/Trung Quốc", "LOT2715", "2027-11-30", "2-8°C", 3, 1, 2, 4296000, "Tủ lạnh Miễn dịch 2-8°C", "Dấu ấn ung thư tiêu hóa Carcinoembryonic Antigen"),
    ("MD-CA125-116", "CA 125 Chemiluminescent Immunoassay Kit", "hoa_chat", "2x50 tests", "Hộp", "Maccura/Trung Quốc", "LOT2716", "2027-10-31", "2-8°C", 2, 1, 1, 2244000, "Tủ lạnh Miễn dịch 2-8°C", "Dấu ấn ung thư buồng trứng CA 125"),
    ("MD-CA153-117", "CA 15-3 Chemiluminescent Immunoassay Kit", "hoa_chat", "2x50 tests", "Hộp", "Maccura/Trung Quốc", "LOT2717", "2027-10-31", "2-8°C", 2, 1, 1, 2244000, "Tủ lạnh Miễn dịch 2-8°C", "Dấu ấn ung thư vú CA 15-3"),

    # HÓA CHẤT ĐÔNG MÁU (118 - 124)
    ("DM-PT-118", "Prothrombin Time (PT) Assay Kit by Clotting Method", "hoa_chat", "4.0mLx10", "Hộp", "Maccura/Trung Quốc", "LOT2718", "2027-11-30", "2-8°C", 4, 1, 3, 1697000, "Tủ lạnh Đông máu 2-8°C", "Khảo sát con đường đông máu ngoại sinh PT/INR"),
    ("DM-APTT-119", "Activated Partial Thromboplastin Time (APTT) Assay Kit by Clotting Method", "hoa_chat", "R1 5.0mLx5; R2 5.0mLx5", "Hộp", "Maccura/Trung Quốc", "LOT2719", "2027-11-30", "2-8°C", 4, 1, 3, 1013000, "Tủ lạnh Đông máu 2-8°C", "Khảo sát con đường đông máu nội sinh APTT"),
    ("DM-TT-120", "Thrombin Time (TT) Assay Kit by Clotting Method", "hoa_chat", "5.0mLx10", "Hộp", "Maccura/Trung Quốc", "LOT2720", "2027-10-31", "2-8°C", 3, 1, 2, 1267000, "Tủ lạnh Đông máu 2-8°C", "Định lượng thời gian Thrombin TT"),
    ("DM-FIB-121", "Fibrinogen (FIB) Assay Kit by Clotting Method (Clauss)", "hoa_chat", "R1 2.0mLx5; R2 25mLx1", "Hộp", "Maccura/Trung Quốc", "LOT2721", "2027-11-30", "2-8°C", 4, 1, 2, 1350000, "Tủ lạnh Đông máu 2-8°C", "Định lượng Fibrinogen theo phương pháp Clauss"),
    ("DM-CTL-122", "Coagulation Quality Control Plasma L1", "qc_chuan", "5x1ml", "Hộp", "Maccura/Trung Quốc", "LOT2722", "2027-08-31", "2-8°C", 3, 1, 1, 611000, "Tủ lạnh Đông máu 2-8°C", "Huyết tương kiểm soát đông máu mức 1"),
    ("DM-CTL-123", "Coagulation Quality Control Plasma L2", "qc_chuan", "5x1ml", "Hộp", "Maccura/Trung Quốc", "LOT2723", "2027-08-31", "2-8°C", 3, 1, 1, 611000, "Tủ lạnh Đông máu 2-8°C", "Huyết tương kiểm soát đông máu mức 2"),
    ("DM-BAL-124", "Demagnetization Small Steel Ball (bán tự động Thrombo PT4)", "vat_tu", "1700 viên", "Hộp", "Maccura/Trung Quốc", "LOT2724", "2030-12-31", "Phòng", 3, 1, 1, 1413000, "Kho đông máu", "Bi từ phản ứng cho máy đo đông máu bán tự động"),

    # VẬT TƯ TIÊU HAO & LINH KIỆN MÁY (125 - 129)
    ("VT-NDL-125", "Kim hút mẫu (Sampling needle) máy celldiff 580/560", "vat_tu", "Mới 100%", "Cái", "Maccura/Trung Quốc", "LOT2725", "2030-12-31", "Phòng", 2, 1, 1, 6161000, "Tủ vật tư dự phòng", "Bảo hành 3 tháng hoặc 10.000 mẫu"),
    ("VT-TUB-126", "Dây bơm (Pump Tube) máy ION ĐỒ", "vat_tu", "Mới 100%", "Cái", "Fortress Diagnostics/Anh", "LOT2726", "2030-12-31", "Phòng", 2, 1, 1, 505000, "Tủ vật tư dự phòng", "Bảo hành 01 tháng"),
    ("VT-PRB-127", "Kim hút mẫu thử (Sample Probe) máy Monarch 1000", "vat_tu", "Mới 100%", "Cái", "Monarch", "LOT2727", "2030-12-31", "Phòng", 1, 1, 1, 27674000, "Tủ vật tư dự phòng", "Bảo hành 03 tháng"),
    ("VT-CUV-128", "Giếng phản ứng (Cuvette) máy Monarch 1000", "vat_tu", "Mới 100%", "Cái", "Monarch", "LOT2728", "2030-12-31", "Phòng", 2, 1, 1, 26573000, "Tủ vật tư dự phòng", "Bảo hành 03 tháng"),
    ("VT-PMP-129", "Bơm chân không (Vacuum Pump) máy celldiff 580/560", "vat_tu", "Mới 100%", "Cái", "Maccura/Trung Quốc", "LOT2729", "2030-12-31", "Phòng", 1, 1, 1, 6000000, "Tủ vật tư dự phòng", "Bảo hành 3 tháng hoặc 10.000 mẫu"),

    # VẬT TƯ TIÊU HAO THỰC ĐỊA BỔ SUNG (LẤY MÁU NGOẠI TRÚ & LƯU MẪU)
    ("VT-EDTA-130", "Ống nghiệm hút chân không EDTA K2/K3 2ml", "vat_tu", "Hộp 100 ống", "Hộp", "Việt Nam", "LOT26130", "2028-12-31", "Phòng", 25, 10, 15, 120000, "Kệ lấy máu", "Dùng cho huyết học và HbA1c"),
    ("VT-GEL-131", "Ống nghiệm tách huyết thanh Serum Gel Clot 4ml", "vat_tu", "Hộp 100 ống", "Hộp", "Việt Nam", "LOT26131", "2028-12-31", "Phòng", 30, 10, 20, 145000, "Kệ lấy máu", "Dùng cho sinh hóa và miễn dịch"),
    ("VT-KIM-132", "Kim lấy máu chân không 2 đầu 21G/22G", "vat_tu", "Hộp 100 kim", "Hộp", "Hàn Quốc", "LOT26132", "2028-12-31", "Phòng", 20, 8, 15, 180000, "Bàn lấy máu", "Lấy máu hệ thống chân không"),
    ("VT-TIP-133", "Đầu côn vàng (Yellow Tip 10 - 100 ul)", "vat_tu", "Túi 1.000 đầu", "Túi", "Axygen/Mỹ", "LOT26133", "2030-12-31", "Phòng", 10, 3, 5, 85000, "Bàn thao tác", "Dùng pipet lấy mẫu"),
    ("VT-TIP-134", "Đầu côn xanh (Blue Tip 100 - 1000 ul)", "vat_tu", "Túi 1.000 đầu", "Túi", "Axygen/Mỹ", "LOT26134", "2030-12-31", "Phòng", 8, 3, 4, 95000, "Bàn thao tác", "Dùng pipet hút hóa chất"),
    ("VT-CON-135", "Cồn y tế 70 độ sát khuẩn can 5 lít", "vat_tu", "Can 5L", "Can", "Việt Nam", "LOT26135", "2028-06-30", "Phòng", 6, 2, 3, 110000, "Kho hóa chất", "Sát khuẩn tay và bề mặt làm việc")
]

def update_inventory_database():
    print(f"Updating database with {len(ITEMS_DATA)} items from VN MED quotation...")
    conn = get_db()
    cursor = conn.cursor()

    # Clear old items to replace cleanly with the quotation items
    cursor.execute("DELETE FROM inventory_items;")

    for item in ITEMS_DATA:
        code, name, category, spec, unit, manufacturer, lot, exp, temp, qty, min_s, usage, price, loc, notes = item
        cursor.execute("""
            INSERT INTO inventory_items (
                code, name, category, spec, unit, manufacturer, lot_number,
                expiry_date, storage_temp, quantity, min_stock, monthly_usage,
                unit_price, location, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (code, name, category, spec, unit, manufacturer, lot, exp, temp, qty, min_s, usage, price, loc, notes))

    conn.commit()
    conn.close()
    print("Database updated successfully!")

def update_excel_files():
    excel_dir = Path(r"D:\01_TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026\06_QUAN_LY_HOA_CHAT_VAT_TU_SINH_PHAM")
    if not excel_dir.exists():
        print(f"Directory {excel_dir} does not exist.")
        return

    # Update 04_SO_THEO_DOI_XUAT_NHAP_TON_KHO_HOA_CHAT_SINH_PHAM_2026.xlsx
    file_xnt = excel_dir / "04_SO_THEO_DOI_XUAT_NHAP_TON_KHO_HOA_CHAT_SINH_PHAM_2026.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "XUAT_NHAP_TON_2026"
    ws.views.sheetView[0].showGridLines = True

    # Title header
    ws.merge_cells("A1:M1")
    ws["A1"] = "BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG • KHOA XÉT NGHIỆM"
    ws["A1"].font = Font(name="Times New Roman", size=11, bold=True, color="0369A1")
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:M2")
    ws["A2"] = "SỔ THEO DÕI XUẤT NHẬP TỒN HÓA CHẤT, SINH PHẨM & VẬT TƯ TIÊU HAO 2026"
    ws["A2"].font = Font(name="Times New Roman", size=14, bold=True, color="1E3A8A")
    ws["A2"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A3:M3")
    ws["A3"] = f"Căn cứ Bảng báo giá chính thức VN MED (Ngày 16/11/2026) • Tổng số: {len(ITEMS_DATA)} mặt hàng chuẩn hóa"
    ws["A3"].font = Font(name="Times New Roman", size=10, italic=True)
    ws["A3"].alignment = Alignment(horizontal="center")

    headers = [
        "STT", "Mã Hàng", "Tên Hóa Chất / Sinh Phẩm / Vật Tư", "ĐVT",
        "Quy Cách", "Hãng Sản Xuất", "Số Lô (Lot)", "Hạn Dùng", "Bảo Quản",
        "Tồn Đầu Kỳ", "Tổng Nhập", "Tổng Xuất", "Tồn Cuối Kỳ"
    ]

    header_font = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    ws.row_dimensions[5].height = 28

    for idx, item in enumerate(ITEMS_DATA, 1):
        row_num = 5 + idx
        code, name, cat, spec, unit, mfg, lot, exp, temp, qty, min_s, usage, price, loc, notes = item
        ton_dau = qty + 2
        nhap = usage
        xuat = usage + 2
        
        ws.cell(row=row_num, column=1, value=idx).alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=2, value=code).alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=3, value=name).alignment = Alignment(horizontal="left")
        ws.cell(row=row_num, column=4, value=unit).alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=5, value=spec).alignment = Alignment(horizontal="left")
        ws.cell(row=row_num, column=6, value=mfg).alignment = Alignment(horizontal="left")
        ws.cell(row=row_num, column=7, value=lot).alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=8, value=exp).alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=9, value=temp).alignment = Alignment(horizontal="center")
        ws.cell(row=row_num, column=10, value=ton_dau).alignment = Alignment(horizontal="right")
        ws.cell(row=row_num, column=11, value=nhap).alignment = Alignment(horizontal="right")
        ws.cell(row=row_num, column=12, value=xuat).alignment = Alignment(horizontal="right")
        ws.cell(row=row_num, column=13, value=f"=J{row_num}+K{row_num}-L{row_num}").alignment = Alignment(horizontal="right")

        for c in range(1, 14):
            ws.cell(row=row_num, column=c).border = thin_border
            ws.cell(row=row_num, column=c).font = Font(name="Times New Roman", size=10)

    # Set column widths
    col_widths = [6, 14, 38, 8, 22, 24, 12, 12, 12, 12, 12, 12, 14]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    wb.save(file_xnt)
    print(f"Updated Excel file: {file_xnt}")

if __name__ == "__main__":
    update_inventory_database()
    update_excel_files()
