# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
from backend.database import get_db

conn = get_db()
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE documents DROP CONSTRAINT IF EXISTS documents_category_check;")
    cur.execute("""
        ALTER TABLE documents ADD CONSTRAINT documents_category_check 
        CHECK(category IN ('phieu_kq_hen', 'so_sach_2429', 'bia_hanh_chinh', 'ho_so_10_cuon'));
    """)
    conn.commit()
    print("PostgreSQL constraint updated successfully!")
except Exception as e:
    print("Constraint update notice:", e)

# Now run sync_disk_documents
from backend.routers.documents import sync_disk_documents
res = sync_disk_documents({'id': 1, 'role': 'truong_khoa'})
print("Sync result:", res)
conn.close()
