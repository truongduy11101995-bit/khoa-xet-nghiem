# HỆ THỐNG WEB QUẢN LÝ NỘI BỘ KHOA XÉT NGHIỆM
### BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG (TIÊU CHUẨN QĐ 2429/QĐ-BYT)

---

## 1. Giới thiệu tổng quan
Ứng dụng Web phục vụ công tác điều hành, phân công vị trí làm việc, chấm công, xếp lịch trực, theo dõi nghỉ phép thông minh, quản lý biểu mẫu chuẩn 2429 và lưu trữ hồ sơ nhân sự của Khoa Xét nghiệm.

### Các chế độ vận hành:
1. **Chế độ Cloud 24/7 (Khuyến nghị):**
   - Triển khai miễn phí trên **Vercel** hoặc **Render**.
   - Cơ sở dữ liệu Cloud **Supabase (PostgreSQL)** đồng bộ dữ liệu thời gian thực giữa mọi máy tính và điện thoại thông minh trong viện 24/7.
   - **Lớp bảo vệ Wi-Fi nội bộ:** Tự động chặn toàn bộ truy cập từ mạng ngoài (4G, Wi-Fi nhà riêng), chỉ cho phép thiết bị kết nối vào đúng mạng Wi-Fi cơ quan mới có thể chấm công.
   - **Chìa khóa Quản trị viên dự phòng (Admin Bypass):** Giúp Trưởng khoa xem báo cáo từ xa và cập nhật lại IP Wi-Fi mới nếu nhà mạng reset modem làm đổi IP động.

2. **Chế độ Mạng LAN nội bộ (Offline / Localhost):**
   - Máy chủ tại khoa: `http://localhost:8000`
   - Các máy con trong viện truy cập: `http://172.16.12.12:8000`
   - Dữ liệu lưu tại ổ cứng `D:\KHOA_XET_NGHIEM_DATA\DATABASE\khoa_xet_nghiem.db`

---

## 2. Danh sách 4 tài khoản nhân sự hiện tại (Mật khẩu mặc định: `123456`)

| STT | Họ và Tên | Tên Đăng Nhập | Chức Danh & Nhiệm Vụ | Phân Quyền |
| :---: | :--- | :--- | :--- | :--- |
| 1 | **CN. Lê Đình Tú** | `le_dinh_tu` | Trưởng Khoa Xét Nghiệm | **Trưởng khoa (Admin)** |
| 2 | **CN. Nguyễn Trường Duy** | `nguyen_truong_duy` | Kỹ Thuật Viên Trưởng | **KTV Trưởng (Quản lý)** |
| 3 | **CN. Lê Phát Đại** | `le_phat_dai` | KTV Vận hành máy & Lấy máu | Kỹ thuật viên (User) |
| 4 | **CN. Tống Mọng Tiền** | `tong_mong_tien` | KTV Tiếp nhận mẫu & Lấy máu | Kỹ thuật viên (User) |

---

## 3. Cấu hình biến môi trường (`.env` trên Cloud)

| Biến Môi Trường | Ý Nghĩa | Ví Dụ |
| :--- | :--- | :--- |
| `DATABASE_URL` | Chuỗi kết nối Supabase PostgreSQL | `postgresql://postgres.[REF]:[PASS]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres` |
| `ALLOWED_OFFICE_IPS` | Danh sách IP Public Wi-Fi cơ quan | `113.161.45.12, 14.161.22.88, 172.16.12.*` (để trống nếu muốn cho phép mọi IP) |
| `ADMIN_BYPASS_KEY` | Mật khẩu dự phòng mở khóa từ xa | `ThienAn2026@BypassLab` |
| `SECRET_KEY` | Khóa mã hóa session token | `thien-an-vien-dong-khoa-xet-nghiem-super-secure-key-2429` |

---

## 4. Chuyển đổi dữ liệu cũ lên Cloud Supabase
1. Vào Supabase Dashboard -> **SQL Editor** -> Dán nội dung file **`supabase_schema.sql`** -> Bấm **Run** để tạo bảng.
2. Dán tiếp nội dung file **`import_data_to_supabase.sql`** (đã xuất sẵn 164 lịch phân công, 12 đơn nghỉ phép, 32 biểu mẫu, 4 tài khoản cán bộ) -> Bấm **Run** để nạp dữ liệu lịch sử.
3. Hoặc chạy lệnh đồng bộ tự động từ máy:
   ```bash
   python export_and_sync_supabase.py "CHUỖI_KET_NOI_SUPABASE"
   ```

---

## 5. Triển khai Cloud (Deploy)
- **Vercel:** Đẩy code lên GitHub, kết nối vào Vercel, cài đặt biến môi trường trong *Settings -> Environment Variables*, chọn Deploy.
- **Render:** Đẩy code lên GitHub, tạo *New Web Service* (hoặc dùng `render.yaml`), điền biến môi trường, Render tự động chạy `uvicorn backend.main:app`.
