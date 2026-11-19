import sys
sys.path.insert(0, r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")

from backend.database import get_db
from backend.auth import create_token
from backend.routers.leave import get_all_leave_requests, review_leave_request, get_leave_balances
from backend.models import LeaveReviewRequest

# Create admin mock user
admin_user = {
    "id": 1,
    "username": "le_dinh_tu",
    "full_name": "CN. Lê Đình Tú",
    "role": "truong_khoa",
    "title": "Trưởng Khoa Xét Nghiệm"
}

print("1. Testing GET /api/leave/all-requests...")
all_reqs = get_all_leave_requests(status_filter="all", year=2026, admin=admin_user)
print(f"Total requests returned: {len(all_reqs['requests'])}")
for r in all_reqs['requests'][:3]:
    print(f" - #{r['id']} {r['full_name']} | {r['leave_date']} ({r['shift']}) | {r['leave_type']} | status: {r['status']} | remain: {r['remaining_days']}")

print("\n2. Testing Leave Approval with Annual Leave Deduction on request #28 (phep_nam by CN. Le Phat Dai)...")
# Let's inspect initial balance
bal_res = get_leave_balances(year=2026, user=admin_user)
dai_bal = next(b for b in bal_res["balances"] if b["user_id"] == 3)
print(f"CN. Le Phat Dai before approval: Remaining = {dai_bal['remaining_days']}, Approved used = {dai_bal['used_approved']}")

# Approve request #28
rev_req = LeaveReviewRequest(status="approved", review_note="Trưởng khoa duyệt - trừ 1 ngày phép năm")
rev_res = review_leave_request(leave_id=28, req=rev_req, admin=admin_user)
print("Review response:", rev_res)

# Verify updated balance
bal_res2 = get_leave_balances(year=2026, user=admin_user)
dai_bal2 = next(b for b in bal_res2["balances"] if b["user_id"] == 3)
print(f"CN. Le Phat Dai after approval: Remaining = {dai_bal2['remaining_days']}, Approved used = {dai_bal2['used_approved']}")

assert dai_bal2['remaining_days'] == 11.0, f"Expected 11.0 but got {dai_bal2['remaining_days']}"
assert dai_bal2['used_approved'] == 1.0, f"Expected 1.0 but got {dai_bal2['used_approved']}"
print("VERIFICATION PASSED: 1 day was deducted accurately from 12 days quota!")

# Reset back to pending for realistic testing in browser
conn = get_db()
conn.execute("UPDATE leave_requests SET status = 'pending', reviewed_by = NULL, review_note = NULL WHERE id = 28")
conn.commit()
conn.close()
print("Reset đơn #28 back to 'pending' for live user/browser testing.")
