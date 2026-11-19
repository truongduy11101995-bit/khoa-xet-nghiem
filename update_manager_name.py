import sqlite3

conn = sqlite3.connect(r'D:\KHOA_XET_NGHIEM_DATA\DATABASE\khoa_xet_nghiem.db')
conn.execute("UPDATE users SET full_name = 'CN. Lê Đình Tú' WHERE username = 'le_dinh_tu';")
conn.commit()

row = conn.execute("SELECT id, username, full_name, title FROM users WHERE username = 'le_dinh_tu';").fetchone()
print(f"Updated successfully: ID {row[0]}, Username: {row[1]}, Full Name: {row[2]}, Title: {row[3]}")
