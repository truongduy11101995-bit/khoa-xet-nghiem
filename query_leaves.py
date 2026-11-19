import sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")

from backend.database import get_db

conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT * FROM leave_requests ORDER BY id DESC")
rows = [dict(r) for r in cursor.fetchall()]
print(f"Total leave requests: {len(rows)}")
for r in rows:
    print(r)
conn.close()
