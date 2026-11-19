# -*- coding: utf-8 -*-
import json
from pathlib import Path

# Master Data for 10 Binders
binders = [
    {
        "id": "cuon_00",
        "code": "DM.TONG.00",
        "title": "Cuốn 00: Mục Lục & Bảng Thống Kê Tổng Thể Toàn Khoa",
        "volume": "Mục lục trung tâm",
        "scale": "Toàn bộ 10 Cuốn (147 tài liệu)",
        "legal": "QĐ 2429/QĐ-BYT, NĐ 103/2016/NĐ-CP & NĐ 96/2023/NĐ-CP",
        "desc": "Bản đồ tra cứu tổng thể, bảng thống kê chuẩn hóa toàn bộ tên tài liệu, mã hiệu từ Cuốn 01 đến Cuốn 10 phục vụ quản lý nội bộ và thanh tra Bộ Y tế / Sở Y tế."
    },
    {
        "id": "cuon_01",
        "code": "CUON-01",
        "title": "Cuốn 01: Hồ sơ Quản lý An toàn sinh học Cấp II",
        "volume": "Tập 1",
        "scale": "23 văn bản / SOP / sổ",
        "legal": "NĐ 103/2016, TT 37/2017, Chương XII QĐ 2429",
        "desc": "Bản tự công bố đạt tiêu chuẩn An toàn sinh học Cấp II, bản kê khai nhân sự Mẫu 08, bản kê khai thiết bị Mẫu 09, Sổ tay ATSH (ST.ATSH.01), Đánh giá nguy cơ (ĐGNC.01), Nội quy, Biển báo cửa, 09 SOP ATSH và 07 sổ nhật ký."
    },
    {
        "id": "cuon_02",
        "code": "CUON-02",
        "title": "Cuốn 02: Hồ sơ Pháp lý, Tổ chức Nhân sự & Cơ sở vật chất",
        "volume": "Tập 2",
        "scale": "13 biểu mẫu / kế hoạch",
        "legal": "Chương I, II, III – Quyết định 2429/QĐ-BYT & TT 32/2023/TT-BYT",
        "desc": "Sơ đồ tổ chức (BM.QL.01), Bảng phân công & mô tả công việc 04 Cử nhân (BM.QL.02), Chính sách & Mục tiêu chất lượng 2026 (BM.QL.03), Kế hoạch QLCL (BM.QL.04), Họp giao ban, Danh sách CCHN & CME (BM.NS.01), Đào tạo hội nhập, Đánh giá năng lực, Lịch trực, Giám sát môi trường nhiệt ẩm và chất lượng nước RO."
    },
    {
        "id": "cuon_03",
        "code": "CUON-03",
        "title": "Cuốn 03: Sổ tay Chất lượng & Bộ 10 Quy trình Quản lý (SOP)",
        "volume": "Tập 3",
        "scale": "12 tài liệu / SOP",
        "legal": "Chương I → XII – Quyết định 2429/QĐ-BYT",
        "desc": "Sổ tay Chất lượng Khoa Xét nghiệm (ST.QLCL.01) xây dựng theo 12 Chương QĐ 2429 và bộ 10 Quy trình quản lý chuẩn (QT.QL.01 đến QT.QL.10): Kiểm soát tài liệu, Kiểm soát hồ sơ, Quản lý nhân sự, Thiết bị, Hóa chất, IQC Westgard, EQA, Xác nhận PP, CAPA, Đánh giá nội bộ & LIS."
    },
    {
        "id": "cuon_04",
        "code": "CUON-04",
        "title": "Cuốn 04: Sổ tay Lấy mẫu, 07 SOP Chuyên môn & 07 Sổ ghi chép",
        "volume": "Tập 4",
        "scale": "16 tài liệu / SOP / sổ",
        "legal": "Chương V, VI, VII, IX – Quyết định 2429/QĐ-BYT",
        "desc": "Sổ tay lấy mẫu xét nghiệm (ST.LM.01), Bảng quy định ngưỡng Giá trị nguy hiểm (GVNH.01), 07 SOP chuyên môn kỹ thuật Trước – Trong – Sau xét nghiệm và 07 sổ ghi chép hằng ngày (Từ chối mẫu, Giá trị nguy hiểm, Lỗi IQC, Kho FIFO, Lô mới, Hủy hóa chất, CAPA)."
    },
    {
        "id": "cuon_05",
        "code": "CUON-05",
        "title": "Cuốn 05: Tự đánh giá Chất lượng QĐ 2429 & Khung Hồ sơ Thiết bị",
        "volume": "Tập 5",
        "scale": "10 biểu mẫu / hồ sơ",
        "legal": "Chương IV, X, XI – Quyết định 2429/QĐ-BYT",
        "desc": "Bảng kiểm tự đánh giá mức chất lượng theo 12 Chương QĐ 2429 (BK.2429.01), Bảng kê khai thiết bị Mẫu số 09 để trống chờ máy mới, 05 biểu mẫu quản lý thiết bị (Lý lịch, Nghiệm thu IQ/OQ/PQ, Nhật ký bảo dưỡng, Phiếu sửa chữa), Biên bản đánh giá nội bộ và Phiếu khảo sát hài lòng BS lâm sàng, Người bệnh."
    },
    {
        "id": "cuon_06",
        "code": "CUON-06",
        "title": "Cuốn 06: Hồ sơ IQC, EQA, Xác nhận phương pháp & Quản lý LIS",
        "volume": "Tập 6",
        "scale": "07 biểu mẫu / báo cáo",
        "legal": "Chương VI, VII, VIII, X – Quyết định 2429/QĐ-BYT",
        "desc": "Báo cáo xác nhận phương pháp định lượng (BM.XNPP.01 Độ chụm & Độ đúng, BM.XNPP.02 Khoảng tham chiếu 20 mẫu), Bảng 20 điểm dữ liệu IQC ban đầu (BM.IQC.01), Sổ tổng hợp Ngoại kiểm EQA năm 2026 (BM.EQA.01), Sổ bàn giao kết quả (BM.KQ.01), Phân quyền & sao lưu LIS (BM.LIS.01), Bảng tổng hợp tự chấm điểm 169 tiêu chí 268 điểm (TH.2429.01)."
    },
    {
        "id": "cuon_07a",
        "code": "CUON-07A",
        "title": "Cuốn 07A: Sổ Checklist Sáng – Chiều (Tủ lạnh, Tủ đông, Tủ ATSH)",
        "volume": "Tập 7A",
        "scale": "06 biểu mẫu & nhãn tủ",
        "legal": "Chương III, IV, XII – Kiểm tra thực địa",
        "desc": "Checklist Sáng – Chiều hằng ngày cho Tủ lạnh (2°C–8°C, BM.TD.01), Tủ đông (≤ -20°C, BM.TD.02), Tủ ATSH Cấp II (BM.TD.03), Bảng tổng hợp gộp 3 thiết bị (BM.TD.04-1, BM.TD.04-2), Biểu đồ theo dõi đường biểu diễn nhiệt độ (BM.TD.05) và bộ nhãn dán cửa tủ."
    },
    {
        "id": "cuon_07b",
        "code": "CUON-07B",
        "title": "Cuốn 07B: Bộ Checklist & Sổ theo dõi vận hành mở rộng tại phòng",
        "volume": "Tập 7B",
        "scale": "10 biểu mẫu & bộ nhãn",
        "legal": "Chương III, IV, VI, XII – Kiểm tra thực địa",
        "desc": "Checklist Nhiệt ẩm phòng XN (BM.BS.01), Tủ ấm 37°C / Bể điều nhiệt (BM.BS.02), Vận hành máy ly tâm (BM.BS.03), Bảo dưỡng Pipet tự động (BM.BS.04), Nhật ký pha Cloramin B (BM.BS.05), Trạm rửa mắt/Spill Kit (BM.BS.06), Lưu và hủy mẫu (BM.BS.07), Sổ giao ca trực (BM.BS.08), Sổ giám sát TAT (BM.BS.09), Bộ 06 nhãn dán quản lý tại chỗ (BM.BS.10)."
    },
    {
        "id": "cuon_08",
        "code": "CUON-08",
        "title": "Cuốn 08: Bộ Quyết định Giám đốc BV, Kiểm soát Tài liệu, Xem xét LĐ & MSDS",
        "volume": "Tập 8",
        "scale": "17 quyết định / biểu mẫu",
        "legal": "Chương I, VI, VIII, X, XI, XII – QĐ 2429",
        "desc": "Công văn gửi Sở Y tế nộp hồ sơ tự công bố ATSH Cấp II (CV.ATSH.01), 03 Quyết định Giám đốc BV (QĐ.BV.01 bổ nhiệm Tổ QLCL & ATSH, QĐ.BV.02 ban hành Sổ tay & SOP, QĐ.BV.03 phê duyệt Danh mục XN, KTC, GVNH & TAT), Danh mục tài liệu bên ngoài (BM.TL.01), Sổ phân phối & đọc hiểu (BM.TL.02), Rà soát tài liệu (BM.TL.03), Thời hạn lưu hồ sơ (BM.TL.04), Biên bản Xem xét Lãnh đạo đủ 12 đầu vào (BM.XX.01), Chỉ số chất lượng KPIs (BM.CT.01), Đề án PDCA (BM.CT.02), So sánh tương đồng KTV (BM.SS.01), Gửi mẫu ngoại viện (BM.GXN.01), Bảng MSDS Tiếng Việt (BM.AT.01), Khử nhiễm máy (BM.AT.02), Sổ ra vào (BM.AT.03), Checklist an toàn điện nước PCCC cuối ngày (BM.AT.04)."
    },
    {
        "id": "cuon_09",
        "code": "CUON-09",
        "title": "Cuốn 09: Hồ sơ Ủy quyền, Bảo mật, Quản lý Rủi ro, Hoàn nguyên QC & Nhóm máu",
        "volume": "Tập 9",
        "scale": "15 văn bản / SOP / sổ",
        "legal": "Chương I, II, IV, V, VI, VII, XI & TT 26/2013",
        "desc": "Giấy ủy quyền điều hành & ký duyệt kết quả khi Trưởng khoa vắng mặt (BM.NS.05), Bản cam kết đạo đức nghề nghiệp, bảo mật & không xung đột lợi ích của 04 Cử nhân (BM.NS.06), Kế hoạch đào tạo & Đề thi Pre/Post-test (BM.NS.07), Biên bản kiểm nhập hóa chất đầu vào (BM.HC.01), Sổ hoàn nguyên/Aliquot QC (BM.HC.02), Job Aid & Thẻ trạng thái máy (BM.TB.06), Quản lý rủi ro 3 giai đoạn (BM.QLRR.01), Phương án dự phòng liên tục (BM.DP.01), Mẫu phiếu kết quả chuẩn (BM.KQ.02), Sửa đổi kết quả đã trả (BM.KQ.03), Tư vấn lâm sàng (BM.LS.01), Quy trình kỹ thuật định nhóm máu hệ ABO/Rh 2 phương pháp (QT.TM.01), Sổ nhóm máu (BM.TM.01), Sổ quản lý mẫu VSV nguy cơ (BM.ATSH.08), Bản đồ tra cứu tổng thể 10 cuốn (DM.TONG.01)."
    },
    {
        "id": "cuon_10",
        "code": "CUON-10",
        "title": "Cuốn 10: Hồ sơ Test nhanh, HIV, Truyền nhiễm, Cấp cứu lấy máu, NCC, POCT & 6 Poster",
        "volume": "Tập 10",
        "scale": "18 SOP / sổ / poster",
        "legal": "TT 04/2023, TT 54/2015, TT 20/2021, QĐ 2429",
        "desc": "SOP & Sổ kết quả Test nhanh định tính (QT.CM.08, BM.CM.08), Kiểm tra thuốc nhuộm & Anti (BM.CM.09), Cấp cứu choáng ngất khi lấy máu (QT.CM.09), Sổ giao nhận mẫu đầu vào (BM.CM.10), Add-on Test (BM.CM.11), Tư vấn & Sổ HIV sàng lọc (QT.CM.10, BM.HIV.01), Báo cáo bệnh truyền nhiễm (BM.BTN.01), Bìa checklist túi nhân sự 04 cử nhân (BM.NS.08), Đánh giá NCC (BM.NCC.01), Quản lý POCT (BM.POCT.01), Quy trình & Sổ sấy khử nhiễm dụng cụ (QT.ATSH.10, BM.ATSH.09), Bộ 06 Poster trực quan dán tường in màu ép plastic (PT.01 đến PT.06)."
    }
]

# Write initial JSON
with open(Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\binders_def.json"), "w", encoding="utf-8") as f:
    json.dump(binders, f, ensure_ascii=False, indent=2)

print("Saved binders_def.json successfully.")
