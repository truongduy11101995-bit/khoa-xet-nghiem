import sqlite3

conn = sqlite3.connect(r'D:\KHOA_XET_NGHIEM_DATA\DATABASE\khoa_xet_nghiem.db')
conn.row_factory = sqlite3.Row
users = conn.execute('SELECT * FROM users').fetchall()

print("=== DANH SÁCH 4 NHÂN SỰ & TRẠNG THÁI HỒ SƠ ===")
for u in users:
    files = conn.execute('SELECT title, file_name FROM employee_files WHERE user_id = ?', (u['id'],)).fetchall()
    print(f"ID {u['id']}: {u['full_name']} ({u['title']})")
    print(f"  - Ngày sinh: {u['dob']}")
    print(f"  - SĐT: {u['phone']} | Email: {u['email']}")
    print(f"  - Số CCHN/GPHN: {u['cchn']} | Ngày cấp: {u['cchn_date']}")
    print(f"  - Phạm vi: {u['cchn_scope']}")
    print(f"  - Trình độ: {u['education']} | Chuyên ngành: {u['specialty']}")
    print(f"  - Tệp scan đã tải lên ({len(files)} tệp):")
    for f in files:
        print(f"      + {f['title']} ({f['file_name']})")
    print("-" * 50)
