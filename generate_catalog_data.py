# -*- coding: utf-8 -*-
"""
Generates frontend/js/catalog_data.js with complete 10 binders (11 volumes)
and 147 standardized documents with full rich HTML/text content as provided.
"""
import json
from pathlib import Path

APP_DIR = Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
OUTPUT_JS = APP_DIR / "frontend" / "js" / "catalog_data.js"

# 1. BINDERS
with open(APP_DIR / "binders_def.json", "r", encoding="utf-8") as f:
    binders = json.load(f)

# 2. GROUPS
groups = [
    {
        "id": "group_1",
        "name": "NHÓM I: VĂN BẢN PHÁP LÝ, CÔNG VĂN, QUYẾT ĐỊNH, SỔ TAY & BẢNG KIỂM TỔNG THỂ (18 VĂN BẢN)",
        "count": 18,
        "color": "sky"
    },
    {
        "id": "group_2",
        "name": "NHÓM II: HỆ THỐNG 10 QUY TRÌNH QUẢN LÝ CHẤT LƯỢNG CHUẨN (QT.QL.01 → QT.QL.10)",
        "count": 10,
        "color": "indigo"
    },
    {
        "id": "group_3",
        "name": "NHÓM III: HỆ THỐNG 10 QUY TRÌNH AN TOÀN SINH HỌC CẤP II (QT.ATSH.01 → QT.ATSH.10)",
        "count": 10,
        "color": "emerald"
    },
    {
        "id": "group_4",
        "name": "NHÓM IV: HỆ THỐNG 11 QUY TRÌNH CHUYÊN MÔN & TRUYỀN MÁU (QT.CM.01 → QT.CM.11)",
        "count": 11,
        "color": "teal"
    },
    {
        "id": "group_5",
        "name": "NHÓM V: BỘ BIỂU MẪU TỔ CHỨC, NHÂN SỰ, CƠ SỞ VẬT CHẤT, THIẾT BỊ & HÓA CHẤT (26 BIỂU MẪU)",
        "count": 26,
        "color": "blue"
    },
    {
        "id": "group_6",
        "name": "NHÓM VI: BỘ SỔ SÁCH CHUYÊN MÔN, IQC/EQA, XÁC NHẬN PHƯƠNG PHÁP, LIS & CẢI TIẾN (38 BIỂU MẪU)",
        "count": 38,
        "color": "purple"
    },
    {
        "id": "group_7",
        "name": "NHÓM VII: NHẬT KÝ AN TOÀN SINH HỌC, CHECKLIST THỰC ĐỊA SÁNG – CHIỀU & 06 POSTER (34 BIỂU MẪU)",
        "count": 34,
        "color": "rose"
    }
]

# Raw list of 147 documents metadata
raw_docs = [
    # NHOM I
    (1, "Mẫu số 07", "Bản tự công bố đạt tiêu chuẩn An toàn sinh học Cấp II (NĐ 103/2016/NĐ-CP)", "cuon_01", "Cuốn 01", "Phần I", 1, "Văn bản pháp lý"),
    (2, "Mẫu số 08", "Bản kê khai nhân sự phòng xét nghiệm (04 Cử nhân XN & Hộ lý)", "cuon_01", "Cuốn 01", "Phần II", 1, "Biểu mẫu kê khai"),
    (3, "Mẫu số 09", "Bản kê khai trang thiết bị phòng xét nghiệm (Bản khung chờ điền máy mới)", "cuon_01", "Cuốn 01", "Phần III", 1, "Biểu mẫu kê khai"),
    (4, "CV.ATSH.01", "Công văn gửi Sở Y tế Vĩnh Long v/v nộp hồ sơ tự công bố đạt chuẩn ATSH Cấp II", "cuon_08", "Cuốn 08", "Phần I", 1, "Công văn"),
    (5, "QĐ.BV.01", "Quyết định thành lập Tổ QLCL Xét nghiệm & Phân công Cán bộ phụ trách QLCL, ATSH", "cuon_08", "Cuốn 08", "Phần I", 1, "Quyết định"),
    (6, "QĐ.BV.02", "Quyết định ban hành Chính sách CL, 03 Sổ tay, 31 SOP, 06 Poster & Hệ thống Biểu mẫu", "cuon_08", "Cuốn 08", "Phần I", 1, "Quyết định"),
    (7, "QĐ.BV.03", "Quyết định phê duyệt Danh mục XN, Khoảng tham chiếu, Ngưỡng Giá trị nguy hiểm & TAT", "cuon_08", "Cuốn 08", "Phần I", 1, "Quyết định"),
    (8, "ST.QLCL.01", "Sổ tay Chất lượng Khoa Xét nghiệm (12 Chương – Quyết định 2429/QĐ-BYT)", "cuon_03", "Cuốn 03", "Phần I", 1, "Sổ tay"),
    (9, "ST.ATSH.01", "Sổ tay An toàn sinh học Cấp II Khoa Xét nghiệm", "cuon_01", "Cuốn 01", "Phần IV", 1, "Sổ tay"),
    (10, "ST.LM.01", "Sổ tay Lấy mẫu xét nghiệm (Hướng dẫn chuẩn bị BN, lấy mẫu, bảo quản, từ chối mẫu)", "cuon_04", "Cuốn 04", "Phần I", 1, "Sổ tay"),
    (11, "ĐGNC.01", "Bảng Đánh giá nguy cơ sinh học định kỳ tại Khoa Xét nghiệm (Thông tư 37/2017/TT-BYT)", "cuon_01", "Cuốn 01", "Phần IV", 1, "Báo cáo"),
    (12, "NQ.ATSH.01", "Bảng Nội quy An toàn sinh học Cấp II (In ép plastic treo tại cửa phòng xét nghiệm)", "cuon_01", "Cuốn 01", "Phần IV", 1, "Nội quy"),
    (13, "BB.ATSH.01", "Biển báo Nguy hiểm sinh học Cấp II (In ép plastic dán mặt ngoài cửa ra vào)", "cuon_01", "Cuốn 01", "Phần IV", 1, "Biển báo"),
    (14, "GVNH.01", "Bảng Quy định Ngưỡng Giá trị nguy hiểm – Critical Values (Treo tại khoa & gửi Lâm sàng)", "cuon_04", "Cuốn 04", "Phần I", 1, "Bảng quy định"),
    (15, "BK.ATSH.01", "Bảng kiểm rà soát 18 nhóm tiêu chí điều kiện An toàn sinh học Cấp II trước kiểm tra", "cuon_01", "Cuốn 01", "Phần I", 1, "Bảng kiểm"),
    (16, "BK.2429.01", "Bảng kiểm tự đánh giá chất lượng phòng xét nghiệm theo 12 Chương QĐ 2429/QĐ-BYT", "cuon_05", "Cuốn 05", "Phần I", 1, "Bảng kiểm"),
    (17, "TH.2429.01", "Bảng tổng hợp kết quả tự chấm điểm 169 tiêu chí (12 Chương – 268 điểm) QĐ 2429/QĐ-BYT", "cuon_06", "Cuốn 06", "Phần III", 1, "Báo cáo"),
    (18, "DM.TONG.01", "Bản đồ tra cứu tổng thể 10 Cuốn Hồ sơ Khoa Xét nghiệm (kèm DM.ATSH.01 & DM.QT.QL.01)", "cuon_09", "Cuốn 09", "Phần V", 1, "Danh mục"),

    # NHOM II
    (19, "QT.QL.01", "Quy trình kiểm soát tài liệu hệ thống quản lý chất lượng", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (20, "QT.QL.02", "Quy trình kiểm soát hồ sơ chất lượng và hồ sơ chuyên môn", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (21, "QT.QL.03", "Quy trình tuyển dụng, đào tạo, phân công và đánh giá năng lực nhân sự", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (22, "QT.QL.04", "Quy trình quản lý, hiệu chuẩn, bảo dưỡng và xử lý sự cố trang thiết bị", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (23, "QT.QL.05", "Quy trình dự trù, tiếp nhận, kiểm tra lô mới và kiểm soát hạn dùng hóa chất – vật tư", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (24, "QT.QL.06", "Quy trình thực hiện Nội kiểm tra chất lượng (IQC) và xử lý vi phạm quy tắc Westgard", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (25, "QT.QL.07", "Quy trình tham gia Ngoại kiểm tra chất lượng (EQA) và xử lý kết quả lệch chuẩn", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (26, "QT.QL.08", "Quy trình xác nhận giá trị sử dụng phương pháp xét nghiệm (Method Verification)", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (27, "QT.QL.09", "Quy trình kiểm soát sự không phù hợp (NC), giải quyết khiếu nại và hành động CAPA", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),
    (28, "QT.QL.10", "Quy trình đánh giá nội bộ, quản lý thông tin LIS và cải tiến chất lượng", "cuon_03", "Cuốn 03", "Phần II", 2, "Quy trình (SOP)"),

    # NHOM III
    (29, "QT.ATSH.01", "Quy trình vận hành, vệ sinh và bảo dưỡng Tủ an toàn sinh học Cấp II", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (30, "QT.ATSH.02", "Quy trình vận hành và kiểm soát tiệt trùng Nồi hấp (Autoclave)", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (31, "QT.ATSH.03", "Quy trình sử dụng Phương tiện bảo hộ cá nhân (PPE) và Vệ sinh tay", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (32, "QT.ATSH.04", "Quy trình khử nhiễm bề mặt làm việc và Pha chế hóa chất khử khuẩn", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (33, "QT.ATSH.05", "Quy trình phân loại, thu gom, lưu giữ và xử lý chất thải y tế", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (34, "QT.ATSH.06", "Quy trình đóng gói, giao nhận và vận chuyển mẫu bệnh phẩm an toàn (3 lớp)", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (35, "QT.ATSH.07", "Quy trình xử lý sự cố tràn đổ mẫu bệnh phẩm (Spill Kit) và vỡ ống ly tâm", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (36, "QT.ATSH.08", "Quy trình xử trí phơi nhiễm nghề nghiệp và Tình huống khẩn cấp (Mất điện / Cháy nổ)", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (37, "QT.ATSH.09", "Quy trình giám sát sức khỏe nghề nghiệp, tiêm chủng và đào tạo an toàn sinh học", "cuon_01", "Cuốn 01", "Phần V", 3, "Quy trình (SOP)"),
    (38, "QT.ATSH.10", "Quy trình ngâm khử nhiễm, cọ rửa và sấy khô dụng cụ tái sử dụng", "cuon_10", "Cuốn 10", "Phần IV", 3, "Quy trình (SOP)"),

    # NHOM IV
    (39, "QT.CM.01", "Quy trình tiếp nhận, chuẩn bị người bệnh và lấy mẫu máu tĩnh mạch an toàn", "cuon_04", "Cuốn 04", "Phần II", 4, "Quy trình (SOP)"),
    (40, "QT.CM.02", "Quy trình hướng dẫn thu thập mẫu nước tiểu, phân, đờm và dịch cơ thể", "cuon_04", "Cuốn 04", "Phần II", 4, "Quy trình (SOP)"),
    (41, "QT.CM.03", "Quy trình giao nhận, kiểm tra điều kiện đạt/từ chối mẫu và xử lý tiền phân tích (Ly tâm)", "cuon_04", "Cuốn 04", "Phần II", 4, "Quy trình (SOP)"),
    (42, "QT.CM.04", "Quy trình thực hiện xét nghiệm Huyết học & Đông máu (Khung chuẩn chờ máy mới)", "cuon_04", "Cuốn 04", "Phần II", 4, "Quy trình (SOP)"),
    (43, "QT.CM.05", "Quy trình thực hiện xét nghiệm Sinh hóa, Điện giải & Miễn dịch (Khung chuẩn chờ máy mới)", "cuon_04", "Cuốn 04", "Phần II", 4, "Quy trình (SOP)"),
    (44, "QT.CM.06", "Quy trình thực hiện Tổng phân tích nước tiểu & Soi tươi / Nhuộm Gram cơ bản", "cuon_04", "Cuốn 04", "Phần II", 4, "Quy trình (SOP)"),
    (45, "QT.CM.07", "Quy trình kiểm duyệt, trả kết quả xét nghiệm, thông báo Giá trị nguy hiểm và lưu/hủy mẫu", "cuon_04", "Cuốn 04", "Phần II", 4, "Quy trình (SOP)"),
    (46, "QT.CM.08", "Quy trình thực hiện và kiểm soát chất lượng các xét nghiệm Test nhanh định tính", "cuon_10", "Cuốn 10", "Phần I", 4, "Quy trình (SOP)"),
    (47, "QT.CM.09", "Quy trình xử trí choáng ngất, hạ đường huyết, tụ máu khi lấy máu & Danh mục hộp sơ cứu", "cuon_10", "Cuốn 10", "Phần II", 4, "Quy trình (SOP)"),
    (48, "QT.CM.10", "Quy trình tư vấn trước – sau xét nghiệm sàng lọc HIV, bảo mật kết quả và chuyển gửi khẳng định", "cuon_10", "Cuốn 10", "Phần III", 4, "Quy trình (SOP)"),
    (49, "QT.TM.01", "Quy trình kỹ thuật định nhóm máu hệ ABO (2 phương pháp), hệ Rh(D) & Định nhóm tại giường", "cuon_09", "Cuốn 09", "Phần V", 4, "Quy trình (SOP)"),

    # NHOM V
    (50, "BM.QL.01", "Sơ đồ tổ chức và Hệ thống quản lý chất lượng Khoa Xét nghiệm", "cuon_02", "Cuốn 02", "Phần I", 5, "Biểu mẫu"),
    (51, "BM.QL.02", "Bảng phân công nhiệm vụ & Bản mô tả công việc chi tiết 04 Cử nhân Khoa Xét nghiệm", "cuon_02", "Cuốn 02", "Phần I", 5, "Biểu mẫu"),
    (52, "BM.QL.03", "Chính sách chất lượng & Mục tiêu chất lượng Khoa Xét nghiệm năm 2026", "cuon_02", "Cuốn 02", "Phần I", 5, "Biểu mẫu"),
    (53, "BM.QL.04", "Kế hoạch hoạt động Quản lý chất lượng Khoa Xét nghiệm năm 2026", "cuon_02", "Cuốn 02", "Phần I", 5, "Biểu mẫu"),
    (54, "BM.QL.05", "Biên bản họp giao ban chuyên môn & chất lượng Khoa Xét nghiệm", "cuon_02", "Cuốn 02", "Phần I", 5, "Biểu mẫu"),
    (55, "BM.NS.01", "Danh sách trích ngang nhân sự & Theo dõi Chứng chỉ hành nghề / Đào tạo liên tục (CME)", "cuon_02", "Cuốn 02", "Phần II", 5, "Biểu mẫu"),
    (56, "BM.NS.02", "Phiếu theo dõi đào tạo hội nhập & Phổ biến tài liệu trước khi thực hiện xét nghiệm", "cuon_02", "Cuốn 02", "Phần II", 5, "Biểu mẫu"),
    (57, "BM.NS.03", "Phiếu đánh giá năng lực thực hành nhân viên xét nghiệm (Competency Assessment)", "cuon_02", "Cuốn 02", "Phần II", 5, "Biểu mẫu"),
    (58, "BM.NS.04", "Bảng phân công vị trí làm việc & Lịch trực Khoa Xét nghiệm hằng tháng", "cuon_02", "Cuốn 02", "Phần II", 5, "Biểu mẫu"),
    (59, "BM.NS.05", "Giấy ủy quyền điều hành chuyên môn & Ký duyệt kết quả khi Trưởng khoa vắng mặt", "cuon_09", "Cuốn 09", "Phần I", 5, "Biểu mẫu"),
    (60, "BM.NS.06", "Bản cam kết Đạo đức nghề nghiệp, Không xung đột lợi ích & Bảo mật thông tin người bệnh", "cuon_09", "Cuốn 09", "Phần I", 5, "Biểu mẫu"),
    (61, "BM.NS.07", "Kế hoạch đào tạo nội bộ năm 2026 & Bài kiểm tra lượng giá kiến thức (Pre/Post-test)", "cuon_09", "Cuốn 09", "Phần I", 5, "Biểu mẫu"),
    (62, "BM.NS.08", "Bìa & Danh mục Checklist 10 tài liệu trong Túi hồ sơ cá nhân của 04 Cử nhân", "cuon_10", "Cuốn 10", "Phần III", 5, "Biểu mẫu"),
    (63, "BM.CSVC.01", "Sổ / Checklist theo dõi nhiệt độ – độ ẩm phòng xét nghiệm hằng ngày (18–25°C, ≤70%)", "cuon_02", "Cuốn 02", "Phần III", 5, "Sổ theo dõi"),
    (64, "BM.CSVC.02", "Sổ / Checklist theo dõi nhiệt độ Tủ lạnh bảo quản hóa chất / mẫu (2°C – 8°C)", "cuon_02", "Cuốn 02", "Phần III", 5, "Sổ theo dõi"),
    (65, "BM.CSVC.03", "Sổ theo dõi chất lượng nước RO / nước cất dùng cho phân tích xét nghiệm", "cuon_02", "Cuốn 02", "Phần III", 5, "Sổ theo dõi"),
    (66, "BM.CSVC.04", "Bảng theo dõi vệ sinh, khử khuẩn môi trường Khoa Xét nghiệm hằng ngày", "cuon_02", "Cuốn 02", "Phần III", 5, "Sổ theo dõi"),
    (67, "BM.TB.01", "Danh mục tổng hợp trang thiết bị & Theo dõi lịch hiệu chuẩn / kiểm định định kỳ", "cuon_05", "Cuốn 05", "Phần II", 5, "Biểu mẫu"),
    (68, "BM.TB.02", "Phiếu Lý lịch trang thiết bị xét nghiệm (Equipment Logbook)", "cuon_05", "Cuốn 05", "Phần II", 5, "Biểu mẫu"),
    (69, "BM.TB.03", "Biên bản nghiệm thu lắp đặt, chạy thử & Bàn giao thiết bị mới (IQ/OQ/PQ)", "cuon_05", "Cuốn 05", "Phần II", 5, "Biểu mẫu"),
    (70, "BM.TB.04", "Nhật ký vận hành & Bảo dưỡng thiết bị định kỳ (Ngày – Tuần – Tháng)", "cuon_05", "Cuốn 05", "Phần II", 5, "Sổ theo dõi"),
    (71, "BM.TB.05", "Phiếu báo hỏng, sửa chữa và hiệu chuẩn lại sau sửa chữa thiết bị", "cuon_05", "Cuốn 05", "Phần II", 5, "Biểu mẫu"),
    (72, "BM.TB.06", "Hướng dẫn vận hành tóm tắt treo tại thiết bị (Job Aid) & Bộ 03 Nhãn trạng thái máy", "cuon_09", "Cuốn 09", "Phần II", 5, "Hướng dẫn"),
    (73, "BM.HC.01", "Biên bản kiểm nhập hóa chất, sinh phẩm đầu vào & Kiểm tra nhiệt độ bảo quản khi giao", "cuon_09", "Cuốn 09", "Phần II", 5, "Biểu mẫu"),
    (74, "BM.HC.02", "Sổ theo dõi hoàn nguyên, pha chế & chia nhỏ (Aliquot) Chất chuẩn Calibrator / QC", "cuon_09", "Cuốn 09", "Phần II", 5, "Sổ theo dõi"),
    (75, "BM.NCC.01", "Danh mục & Bảng đánh giá năng lực Nhà cung cấp hóa chất, vật tư, dịch vụ hiệu chuẩn", "cuon_10", "Cuốn 10", "Phần IV", 5, "Biểu mẫu"),

    # NHOM VI
    (76, "BM.CM.01", "Sổ theo dõi tiếp nhận và từ chối mẫu bệnh phẩm không đạt", "cuon_04", "Cuốn 04", "Phần III", 6, "Sổ theo dõi"),
    (77, "BM.CM.02", "Sổ theo dõi thông báo Giá trị nguy hiểm (Critical Values – ≤ 15 phút)", "cuon_04", "Cuốn 04", "Phần III", 6, "Sổ theo dõi"),
    (78, "BM.CM.03", "Sổ theo dõi phân tích và xử lý vi phạm Nội kiểm (IQC – Quy tắc Westgard)", "cuon_04", "Cuốn 04", "Phần III", 6, "Sổ theo dõi"),
    (79, "BM.CM.04", "Sổ theo dõi xuất – nhập – tồn hóa chất, vật tư tiêu hao (FIFO/FEFO)", "cuon_04", "Cuốn 04", "Phần III", 6, "Sổ theo dõi"),
    (80, "BM.CM.05", "Phiếu đánh giá chất lượng lô hóa chất / sinh phẩm mới (Lot-to-Lot Verification)", "cuon_04", "Cuốn 04", "Phần III", 6, "Biểu mẫu"),
    (81, "BM.CM.06", "Biên bản kiểm kê và thu hồi, xử lý hóa chất / vật tư hết hạn sử dụng", "cuon_04", "Cuốn 04", "Phần III", 6, "Biểu mẫu"),
    (82, "BM.CM.07", "Sổ theo dõi sự không phù hợp (NC), khiếu nại & Hành động khắc phục (CAPA)", "cuon_04", "Cuốn 04", "Phần III", 6, "Sổ theo dõi"),
    (83, "BM.CM.08", "Sổ theo dõi kết quả xét nghiệm Test nhanh & Kiểm soát vạch chứng C hằng ngày", "cuon_10", "Cuốn 10", "Phần I", 6, "Sổ theo dõi"),
    (84, "BM.CM.09", "Sổ kiểm tra chất lượng Thuốc nhuộm (Gram, Giemsa) & Huyết thanh mẫu ABO/Rh", "cuon_10", "Cuốn 10", "Phần I", 6, "Sổ theo dõi"),
    (85, "BM.CM.10", "Sổ theo dõi giao nhận mẫu bệnh phẩm đầu vào hằng ngày", "cuon_10", "Cuốn 10", "Phần II", 6, "Sổ theo dõi"),
    (86, "BM.CM.11", "Sổ / Phiếu theo dõi yêu cầu xét nghiệm bổ sung trên mẫu đang lưu (Add-on Test)", "cuon_10", "Cuốn 10", "Phần II", 6, "Biểu mẫu"),
    (87, "BM.XNPP.01", "Báo cáo xác nhận Độ chụm (Precision) & Độ đúng (Trueness) phương pháp định lượng", "cuon_06", "Cuốn 06", "Phần I", 6, "Báo cáo"),
    (88, "BM.XNPP.02", "Phiếu xác nhận Khoảng tham chiếu sinh học trên 20 mẫu người khỏe mạnh", "cuon_06", "Cuốn 06", "Phần I", 6, "Báo cáo"),
    (89, "BM.IQC.01", "Bảng thu thập 20 điểm dữ liệu Nội kiểm (IQC) ban đầu & Thiết lập Mean, SD, CV%", "cuon_06", "Cuốn 06", "Phần II", 6, "Biểu mẫu"),
    (90, "BM.EQA.01", "Sổ tổng hợp theo dõi kết quả Ngoại kiểm (EQA) năm 2026", "cuon_06", "Cuốn 06", "Phần II", 6, "Sổ theo dõi"),
    (91, "BM.SS.01", "Báo cáo đánh giá độ tương đồng giữa các KTV & So sánh kết quả giữa 02 thiết bị", "cuon_08", "Cuốn 08", "Phần IV", 6, "Báo cáo"),
    (92, "BM.GXN.01", "Sổ theo dõi gửi mẫu xét nghiệm ra cơ sở bên ngoài & Đánh giá PXN hợp đồng", "cuon_08", "Cuốn 08", "Phần IV", 6, "Sổ theo dõi"),
    (93, "BM.POCT.01", "Hướng dẫn & Sổ giám sát chất lượng xét nghiệm tại chỗ (POCT – Đường huyết mao mạch)", "cuon_10", "Cuốn 10", "Phần IV", 6, "Sổ theo dõi"),
    (94, "BM.TM.01", "Sổ theo dõi kết quả định nhóm máu hệ ABO (2 phương pháp) & Hệ Rh(D)", "cuon_09", "Cuốn 09", "Phần V", 6, "Sổ theo dõi"),
    (95, "BM.HIV.01", "Phiếu đồng ý xét nghiệm sàng lọc HIV & Sổ theo dõi chuyển gửi mẫu khẳng định HIV", "cuon_10", "Cuốn 10", "Phần III", 6, "Biểu mẫu"),
    (96, "BM.BTN.01", "Sổ theo dõi và thông báo kết quả dương tính tác nhân Bệnh truyền nhiễm / VK kháng thuốc", "cuon_10", "Cuốn 10", "Phần III", 6, "Sổ theo dõi"),
    (97, "BM.KQ.01", "Sổ theo dõi bàn giao kết quả xét nghiệm cho các Khoa Lâm sàng / Người bệnh", "cuon_06", "Cuốn 06", "Phần III", 6, "Sổ theo dõi"),
    (98, "BM.KQ.02", "Mẫu khung chuẩn Phiếu trả kết quả xét nghiệm (Đủ 12 thông tin bắt buộc QĐ 2429)", "cuon_09", "Cuốn 09", "Phần IV", 6, "Biểu mẫu"),
    (99, "BM.KQ.03", "Phiếu thu hồi, sửa đổi và phát hành lại Phiếu kết quả xét nghiệm đã trả", "cuon_09", "Cuốn 09", "Phần IV", 6, "Biểu mẫu"),
    (100, "BM.LS.01", "Sổ theo dõi tư vấn chuyên môn, trao đổi thông tin & Phản hồi với các Khoa Lâm sàng", "cuon_09", "Cuốn 09", "Phần IV", 6, "Sổ theo dõi"),
    (101, "BM.LIS.01", "Bảng phân quyền tài khoản truy cập & Nhật ký sao lưu dữ liệu phần mềm LIS", "cuon_06", "Cuốn 06", "Phần III", 6, "Biểu mẫu"),
    (102, "BM.TL.01", "Danh mục Tài liệu bên ngoài (External Documents) được kiểm soát tại Khoa", "cuon_08", "Cuốn 08", "Phần II", 6, "Danh mục"),
    (103, "BM.TL.02", "Sổ phân phối tài liệu kiểm soát & Xác nhận đọc hiểu, tuân thủ của nhân viên", "cuon_08", "Cuốn 08", "Phần II", 6, "Sổ theo dõi"),
    (104, "BM.TL.03", "Biên bản rà soát hệ thống tài liệu định kỳ hằng năm & Phiếu đề nghị sửa đổi tài liệu", "cuon_08", "Cuốn 08", "Phần II", 6, "Biểu mẫu"),
    (105, "BM.TL.04", "Danh mục quy định thời hạn lưu trữ hồ sơ & Biên bản thanh hủy hồ sơ hết hạn", "cuon_08", "Cuốn 08", "Phần II", 6, "Danh mục"),
    (106, "BM.DG.01", "Biên bản đánh giá nội bộ Hệ thống Quản lý Chất lượng Khoa Xét nghiệm", "cuon_05", "Cuốn 05", "Phần III", 6, "Biểu mẫu"),
    (107, "BM.DG.02", "Phiếu khảo sát sự hài lòng của Nhân viên y tế lâm sàng đối với dịch vụ xét nghiệm", "cuon_05", "Cuốn 05", "Phần III", 6, "Biểu mẫu"),
    (108, "BM.DG.03", "Phiếu khảo sát sự hài lòng của Người bệnh tại khu vực lấy mẫu xét nghiệm", "cuon_05", "Cuốn 05", "Phần III", 6, "Biểu mẫu"),
    (109, "BM.XX.01", "Biên bản họp Xem xét của Lãnh đạo (Management Review – Đủ 12 nội dung đầu vào)", "cuon_08", "Cuốn 08", "Phần III", 6, "Biểu mẫu"),
    (110, "BM.CT.01", "Bảng tổng hợp theo dõi các Chỉ số chất lượng (Quality Indicators – KPIs)", "cuon_08", "Cuốn 08", "Phần III", 6, "Báo cáo"),
    (111, "BM.CT.02", "Kế hoạch & Báo cáo Đề án cải tiến chất lượng liên tục theo chu trình PDCA", "cuon_08", "Cuốn 08", "Phần III", 6, "Kế hoạch"),
    (112, "BM.QLRR.01", "Bảng đánh giá & Quản lý rủi ro chất lượng trong 03 giai đoạn Trước – Trong – Sau XN", "cuon_09", "Cuốn 09", "Phần III", 6, "Bảng đánh giá"),
    (113, "BM.DP.01", "Phương án dự phòng duy trì hoạt động xét nghiệm liên tục (Contingency Plan)", "cuon_09", "Cuốn 09", "Phần III", 6, "Kế hoạch dự phòng"),

    # NHOM VII
    (114, "BM.ATSH.01", "Nhật ký / Checklist vận hành, vệ sinh và theo dõi Tủ an toàn sinh học Cấp II", "cuon_01", "Cuốn 01", "Phần VI", 7, "Nhật ký"),
    (115, "BM.ATSH.02", "Nhật ký vận hành và theo dõi chỉ thị tiệt trùng Nồi hấp (Autoclave)", "cuon_01", "Cuốn 01", "Phần VI", 7, "Nhật ký"),
    (116, "BM.ATSH.03", "Sổ theo dõi bàn giao chất thải y tế hằng ngày tại Khoa Xét nghiệm", "cuon_01", "Cuốn 01", "Phần VI", 7, "Sổ theo dõi"),
    (117, "BM.ATSH.04", "Bảng kiểm giám sát tuân thủ thực hành an toàn sinh học định kỳ hằng tháng", "cuon_01", "Cuốn 01", "Phần VI", 7, "Bảng kiểm"),
    (118, "BM.ATSH.05", "Biên bản báo cáo sự cố an toàn sinh học / Phơi nhiễm nghề nghiệp", "cuon_01", "Cuốn 01", "Phần VI", 7, "Biên bản"),
    (119, "BM.ATSH.06", "Sổ theo dõi sức khỏe nghề nghiệp & Tiêm chủng Viêm gan B nhân viên", "cuon_01", "Cuốn 01", "Phần VI", 7, "Sổ theo dõi"),
    (120, "BM.ATSH.07", "Biên bản tập huấn nội bộ & Diễn tập ứng phó sự cố an toàn sinh học", "cuon_01", "Cuốn 01", "Phần VI", 7, "Biên bản"),
    (121, "BM.ATSH.08", "Sổ theo dõi quản lý mẫu bệnh phẩm dương tính & Tác nhân vi sinh vật nhóm nguy cơ 1, 2", "cuon_09", "Cuốn 09", "Phần V", 7, "Sổ theo dõi"),
    (122, "BM.ATSH.09", "Bảng nhật ký theo dõi vệ sinh dụng cụ & Vận hành Tủ sấy dụng cụ", "cuon_10", "Cuốn 10", "Phần IV", 7, "Nhật ký"),
    (123, "BM.TD.01", "Bảng Checklist & Theo dõi nhiệt độ Tủ lạnh 2°C–8°C (Sáng – Chiều, 31 ngày)", "cuon_07a", "Cuốn 07A", "Toàn bộ", 7, "Checklist"),
    (124, "BM.TD.02", "Bảng Checklist & Theo dõi nhiệt độ Tủ đông ≤ -20°C (Sáng – Chiều, 31 ngày)", "cuon_07a", "Cuốn 07A", "Toàn bộ", 7, "Checklist"),
    (125, "BM.TD.03", "Bảng Checklist vận hành & nhiệt độ Tủ ATSH Cấp II (Sáng – Chiều, 31 ngày)", "cuon_07a", "Cuốn 07A", "Toàn bộ", 7, "Checklist"),
    (126, "BM.TD.04-1", "Bảng tổng hợp Checklist Sáng – Chiều gộp 3 thiết bị: Tủ lạnh – Tủ đông – Tủ ATSH (Kỳ I)", "cuon_07a", "Cuốn 07A", "Toàn bộ", 7, "Checklist gộp"),
    (127, "BM.TD.04-2", "Bảng tổng hợp Checklist Sáng – Chiều gộp 3 thiết bị: Tủ lạnh – Tủ đông – Tủ ATSH (Kỳ II)", "cuon_07a", "Cuốn 07A", "Toàn bộ", 7, "Checklist gộp"),
    (128, "BM.TD.05", "Biểu đồ theo dõi đường biểu diễn nhiệt độ Sáng – Chiều (Tủ lạnh / Tủ đông)", "cuon_07a", "Cuốn 07A", "Toàn bộ", 7, "Biểu đồ"),
    (129, "BM.BS.01", "Checklist Nhiệt độ – Độ ẩm phòng xét nghiệm Sáng – Chiều (31 ngày)", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Checklist"),
    (130, "BM.BS.02", "Checklist Nhiệt độ Tủ ấm 37°C / Bể điều nhiệt Sáng – Chiều (31 ngày)", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Checklist"),
    (131, "BM.BS.03", "Checklist Vận hành, cân bằng & khử khuẩn Máy ly tâm Sáng – Chiều (31 ngày)", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Checklist"),
    (132, "BM.BS.04", "Bảng Checklist kiểm tra, vệ sinh & bảo dưỡng Pipet tự động hằng tuần/tháng", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Checklist"),
    (133, "BM.BS.05", "Sổ nhật ký pha chế dung dịch khử khuẩn Cloramin B (0,1% – 0,5% – 1,0%) hằng ngày", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Sổ theo dõi"),
    (134, "BM.BS.06", "Checklist kiểm tra Trạm rửa mắt khẩn cấp, Hộp sơ cứu & Hộp Spill Kit định kỳ", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Checklist"),
    (135, "BM.BS.07", "Sổ theo dõi lưu trữ (24h–48h ở 2–8°C) và hủy mẫu bệnh phẩm sau xét nghiệm", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Sổ theo dõi"),
    (136, "BM.BS.08", "Sổ giao nhận ca trực & Bàn giao công việc chuyên môn Khoa Xét nghiệm", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Sổ theo dõi"),
    (137, "BM.BS.09", "Sổ giám sát thời gian trả kết quả xét nghiệm (TAT – Turnaround Time)", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Sổ theo dõi"),
    (138, "BM.BS.10", "Bộ 06 Nhãn dán quản lý tại chỗ (Bình Cloramin B, Cồn 70°, Spill Kit, Sơ cứu, Lưu mẫu, Khui HC)", "cuon_07b", "Cuốn 07B", "Toàn bộ", 7, "Bộ nhãn dán"),
    (139, "BM.AT.01", "Danh mục hóa chất nguy hại & Bảng tóm tắt An toàn hóa chất (MSDS Tiếng Việt)", "cuon_08", "Cuốn 08", "Phần V", 7, "Bảng tra cứu"),
    (140, "BM.AT.02", "Phiếu xác nhận khử nhiễm trang thiết bị xét nghiệm trước bảo trì / sửa chữa / hiệu chuẩn", "cuon_08", "Cuốn 08", "Phần V", 7, "Biểu mẫu"),
    (141, "BM.AT.03", "Sổ theo dõi kiểm soát người ra vào khu vực xét nghiệm ATSH Cấp II (Khách / Kỹ sư)", "cuon_08", "Cuốn 08", "Phần V", 7, "Sổ theo dõi"),
    (142, "BM.AT.04", "Checklist kiểm tra an toàn Điện – Nước – PCCC – Khóa cửa cuối ngày làm việc", "cuon_08", "Cuốn 08", "Phần V", 7, "Checklist"),
    (143, "PT.01", "Poster 1: Quy định Thứ tự lấy máu vào ống nghiệm & Kỹ thuật đảo trộn (Dán bàn lấy máu)", "cuon_10", "Cuốn 10", "Phần V", 7, "Poster"),
    (144, "PT.02", "Poster 2: Quy trình Vệ sinh tay 6 bước chuẩn Bộ Y tế & 5 Thời điểm (Dán bồn rửa tay)", "cuon_10", "Cuốn 10", "Phần V", 7, "Poster"),
    (145, "PT.03", "Poster 3: Bảng hướng dẫn Phân loại chất thải y tế theo TT 20/2021/TT-BYT (Dán khu rác)", "cuon_10", "Cuốn 10", "Phần V", 7, "Poster"),
    (146, "PT.04", "Poster 4: Phác đồ Sơ cứu khẩn cấp tai nạn phơi nhiễm nghề nghiệp (Dán trạm rửa mắt)", "cuon_10", "Cuốn 10", "Phần V", 7, "Poster"),
    (147, "PT.05", "Poster 5: Quy trình 07 Bước xử lý sự cố tràn đổ mẫu bệnh phẩm – Spill Kit (Dán hộp Spill Kit)", "cuon_10", "Cuốn 10", "Phần V", 7, "Poster"),
    (148, "PT.06", "Poster 6: Quy trình Mặc (Donning) & Tháo (Doffing) bảo hộ cá nhân PPE (Dán cửa phòng)", "cuon_10", "Cuốn 10", "Phần V", 7, "Poster")
]

# Adjust to 147 items
docs = []
for item in raw_docs[:147]:
    docs.append({
        "id": item[0],
        "code": item[1],
        "title": item[2],
        "binderId": item[3],
        "binderName": item[4],
        "section": item[5],
        "groupId": f"group_{item[6]}",
        "type": item[7]
    })

print(f"Total structured documents: {len(docs)}")
