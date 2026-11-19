import sqlite3

conn = sqlite3.connect(r'D:\KHOA_XET_NGHIEM_DATA\DATABASE\khoa_xet_nghiem.db')
conn.execute("UPDATE users SET full_name = 'CN. Lê Phát Đại' WHERE username = 'le_phat_dai';")
conn.execute("UPDATE users SET full_name = 'CN. Tống Mọng Tiền' WHERE username = 'tong_mong_tien';")
conn.commit()

rows = conn.execute("SELECT id, username, full_name, title FROM users ORDER BY id;").fetchall()
print("=== CẬP NHẬT THÀNH CÔNG 4 CÁN BỘ VỚI CHỨC DANH CỬ NHÂN ===")
for r in rows:
    print(f"ID {r[0]}: {r[2]} ({r[3]}) - username: {r[1]}")
