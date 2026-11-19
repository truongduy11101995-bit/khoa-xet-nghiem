import datetime
from fastapi import APIRouter, Depends
from backend.database import get_db, is_cloud_db
from backend.auth import get_current_user
from backend.config import ALLOWED_OFFICE_IPS

router = APIRouter(prefix="/api/stats", tags=["Dashboard Statistics"])

@router.get("/summary")
def get_dashboard_summary(user: dict = Depends(get_current_user)):
    """Summary KPI metrics for the header/dashboard."""
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    conn = get_db()
    cursor = conn.cursor()

    # Staff count
    cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
    active_staff = cursor.fetchone()[0]

    # Today's on-duty count
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) FROM schedules
        WHERE work_date = ? AND user_id IS NOT NULL
    """, (today_str,))
    today_scheduled = cursor.fetchone()[0]

    # Today's leaves count
    cursor.execute("""
        SELECT COUNT(*) FROM leave_requests
        WHERE leave_date = ? AND status = 'approved'
    """, (today_str,))
    today_leaves = cursor.fetchone()[0]

    # Pending leaves count
    cursor.execute("SELECT COUNT(*) FROM leave_requests WHERE status = 'pending'")
    pending_leaves = cursor.fetchone()[0]

    # Document count
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]

    # Inventory count & alerts
    total_inventory = 0
    low_stock_count = 0
    open_vials_count = 0
    near_expiry_count = 0
    try:
        cursor.execute("SELECT COUNT(*) FROM inventory_items")
        total_inventory = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM inventory_items WHERE quantity <= min_stock")
        low_stock_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM open_vials WHERE status = 'active'")
        open_vials_count = cursor.fetchone()[0]
    except Exception:
        pass

    # Check if today has >= 2 leaves (warning)
    cursor.execute("""
        SELECT COUNT(*) FROM leave_requests
        WHERE leave_date = ? AND status != 'rejected'
    """, (today_str,))
    today_all_leaves = cursor.fetchone()[0]
    has_today_warning = today_all_leaves >= 2

    # Current user's today position
    cursor.execute("""
        SELECT s.shift, p.name as position_name, p.category
        FROM schedules s
        JOIN positions p ON s.position_id = p.id
        WHERE s.work_date = ? AND s.user_id = ?
        ORDER BY CASE WHEN s.shift = 'sang' THEN 1 WHEN s.shift = 'chieu' THEN 2 ELSE 3 END, p.sort_order ASC
    """, (today_str, user["id"]))
    my_today_positions = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "success": True,
        "today": today_str,
        "active_staff": active_staff,
        "max_staff": active_staff if active_staff > 0 else 4,
        "today_scheduled": today_scheduled,
        "today_leaves": today_leaves,
        "pending_leaves": pending_leaves,
        "total_docs": total_docs,
        "total_inventory": total_inventory,
        "low_stock_count": low_stock_count,
        "open_vials_count": open_vials_count,
        "has_today_warning": has_today_warning,
        "my_today_positions": my_today_positions,
        "db_type": "Cloud Supabase (Online 24/7)" if is_cloud_db() else "Dữ liệu Nội bộ (Ổ D:)",
        "ip_protection_active": bool(ALLOWED_OFFICE_IPS)
    }
