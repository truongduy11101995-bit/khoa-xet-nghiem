import sys
sys.path.insert(0, r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")

from backend.database import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) as c, SUM(unit_price * quantity) as s FROM inventory_items")
row = cursor.fetchone()
print("Raw row:", dict(row) if hasattr(row, "keys") else row)

cursor.execute("SELECT code, name, unit, unit_price, manufacturer FROM inventory_items LIMIT 5")
print("\nFirst 5 items:")
for r in cursor.fetchall():
    print(" -", dict(r) if hasattr(r, "keys") else r)

cursor.execute("SELECT id, username, full_name, role FROM users")
print("\nUsers:")
for u in cursor.fetchall():
    print(" -", dict(u) if hasattr(u, "keys") else u)

cursor.execute("SELECT id, user_id, leave_date, leave_type, shift, status FROM leave_requests")
print("\nLeave requests:")
for lr in cursor.fetchall():
    print(" -", dict(lr) if hasattr(lr, "keys") else lr)

conn.close()
