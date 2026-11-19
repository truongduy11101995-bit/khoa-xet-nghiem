import sqlite3

conn = sqlite3.connect(r'D:\KHOA_XET_NGHIEM_DATA\DATABASE\khoa_xet_nghiem.db')
conn.execute("UPDATE users SET full_name = 'Tống Mọng Tiền' WHERE id = 4;")
conn.commit()

row = conn.execute("SELECT id, username, full_name, title FROM users WHERE id = 4;").fetchone()
print(f"Updated successfully: ID {row[0]}, Username: {row[1]}, Full Name: {row[2]}, Title: {row[3]}")
