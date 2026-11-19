import urllib.request
import json
import urllib.parse
import sys
import datetime
import random

BASE_URL = "http://127.0.0.1:8000"

def request_json(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode("utf-8")), response.headers
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8")), e.headers

print("=== STARTING FULL SYSTEM VERIFICATION FOR 4 STAFF ===")

# 1. Health check
status_code, data, _ = request_json("/api/health")
assert status_code == 200 and data["status"] == "healthy", f"Health check failed: {data}"
print("[PASS] 1. API Health Check OK")

# 2. Login as Trưởng khoa: CN. Lê Đình Tú
status_code, data, _ = request_json("/api/auth/login", method="POST", data={"username": "le_dinh_tu", "password": "123456"})
assert status_code == 200 and data["success"], f"Login failed: {data}"
admin_token = data["token"]
admin_user = data["user"]
assert admin_user["role"] == "truong_khoa"
assert "Lê Đình Tú" in admin_user["full_name"]
print(f"[PASS] 2. Login Trưởng khoa OK: {admin_user['full_name']}")

# 3. Login as KTV: CN. Lê Phát Đại
status_code, data, _ = request_json("/api/auth/login", method="POST", data={"username": "le_phat_dai", "password": "123456"})
assert status_code == 200 and data["success"]
ktv_token = data["token"]
ktv_user = data["user"]
assert ktv_user["role"] == "ktv"
assert "Lê Phát Đại" in ktv_user["full_name"]
print(f"[PASS] 3. Login KTV OK: {ktv_user['full_name']}")

# 4. Login as KTV: CN. Tống Mọng Tiền
status_code, data, _ = request_json("/api/auth/login", method="POST", data={"username": "tong_mong_tien", "password": "123456"})
assert status_code == 200 and data["success"]
ktv2_token = data["token"]
assert "Tống Mọng Tiền" in data["user"]["full_name"]
print(f"[PASS] 4. Login KTV 2 OK: {data['user']['full_name']}")

# 5. Login as KTV Trưởng: Nguyễn Trường Duy
status_code, data, _ = request_json("/api/auth/login", method="POST", data={"username": "nguyen_truong_duy", "password": "123456"})
assert status_code == 200 and data["success"]
ktv_truong_token = data["token"]
assert data["user"]["role"] == "ktv_truong"
print(f"[PASS] 5. Login KTV Trưởng OK: {data['user']['full_name']}")

# 6. Module 1: Schedule
status_code, data, _ = request_json("/api/schedule/weekly", token=admin_token)
assert status_code == 200 and data["success"]
assert len(data["positions"]) >= 11
print(f"[PASS] 6. Module 1: Weekly schedule loaded ({len(data['positions'])} positions)")

# Test schedule assign
pos_id = data["positions"][0]["id"]
test_date = data["week_dates"][0]
status_code, data, _ = request_json("/api/schedule/assign", method="POST", data={
    "work_date": test_date,
    "shift": "sang",
    "position_id": pos_id,
    "user_id": ktv_user["id"],
    "note": "Kiem tra phan cong test"
}, token=admin_token)
assert status_code == 200 and data["success"]
print("[PASS] 7. Module 1: Position assigned successfully")

# Test export excel
req = urllib.request.Request(f"{BASE_URL}/api/schedule/export-excel?start_date={test_date}", headers={"Authorization": f"Bearer {admin_token}"})
with urllib.request.urlopen(req) as resp:
    excel_bytes = resp.read()
    assert len(excel_bytes) > 2000
    assert "spreadsheetml" in resp.headers.get("Content-Type", "")
print(f"[PASS] 8. Module 1: Excel export OK ({len(excel_bytes)} bytes)")

# 7. Module 2: Leave & Smart Warning
unique_day = random.randint(1, 28)
test_leave_date = f"2026-12-{unique_day:02d}"

# Staff 1 (Lê Phát Đại) requests leave
status_code, data1, _ = request_json("/api/leave/request", method="POST", data={
    "leave_date": test_leave_date,
    "leave_type": "phep_nam",
    "shift": "all",
    "reason": "Test xin nghi phep 1"
}, token=ktv_token)
if status_code != 200:
    test_leave_date = f"2026-12-{(unique_day + 1) % 28 + 1:02d}"
    status_code, data1, _ = request_json("/api/leave/request", method="POST", data={
        "leave_date": test_leave_date,
        "leave_type": "phep_nam",
        "shift": "all",
        "reason": "Test xin nghi phep 1"
    }, token=ktv_token)

assert status_code == 200 and data1["success"]
print(f"[PASS] 9. Module 2: First leave request submitted for {test_leave_date}")

# Staff 2 (Tống Mộng Tiền) requests leave on SAME DATE -> Smart warning trigger!
status_code, data2, _ = request_json("/api/leave/request", method="POST", data={
    "leave_date": test_leave_date,
    "leave_type": "nghi_bu",
    "shift": "sang",
    "reason": "Test xin nghi bu 2 trung ngay"
}, token=ktv2_token)
assert status_code == 200 and data2["success"]
assert data2["has_staff_warning"] == True, "Smart warning not activated!"
print("[PASS] 10. Module 2: Smart Warning activated for >= 2 staff on same day!")

# Check Calendar view warning
t_year, t_month, _ = test_leave_date.split('-')
status_code, cal_data, _ = request_json(f"/api/leave/calendar?year={t_year}&month={int(t_month)}", token=admin_token)
day_cell = cal_data["days"][test_leave_date]
assert day_cell["has_warning"] == True
assert day_cell["leave_count"] >= 2
print(f"[PASS] 11. Module 2: Calendar day has red warning: {day_cell['warning_message'][:60]}...")

# 8. Module 3: Document Hub
status_code, doc_data, _ = request_json("/api/documents/list?category=all", token=ktv_token)
assert status_code == 200 and doc_data["success"]
total_docs = doc_data["total"]
assert total_docs >= 15
print(f"[PASS] 12. Module 3: Document Hub loaded {total_docs} files from D:\\KHOA_XET_NGHIEM_DATA\\BIEU_MAU")

# Search test: search for '2429'
status_code, search_data, _ = request_json("/api/documents/list?q=2429", token=ktv_token)
assert search_data["total"] > 0
print(f"[PASS] 13. Module 3: Fast search for '2429' returned {search_data['total']} documents")

# 9. Module 4: Employee Profiles & Privacy
status_code, prof_data, _ = request_json("/api/profiles/list", token=admin_token)
assert status_code == 200 and len(prof_data["profiles"]) == 4
print(f"[PASS] 14. Module 4: 4 Employee profiles verified exactly!")

# Check security: KTV cannot view details of Trưởng khoa (id 1)
status_code, err_data, _ = request_json("/api/profiles/1", token=ktv_token)
assert status_code == 403, f"Expected 403 Forbidden for unauthorized profile view, got {status_code}"
print("[PASS] 15. Module 4: Security policy enforced (KTV blocked from unauthorized profile access)")

# KTV can view own profile (id 3: Lê Phát Đại)
status_code, own_data, _ = request_json(f"/api/profiles/{ktv_user['id']}", token=ktv_token)
assert status_code == 200 and own_data["profile"]["id"] == ktv_user["id"]
print(f"[PASS] 16. Module 4: Staff can view own profile: {own_data['profile']['full_name']}")

# Check stats KPI
status_code, stats, _ = request_json("/api/stats/summary", token=admin_token)
assert status_code == 200 and stats["active_staff"] == 4
print(f"[PASS] 17. KPI Stats: Active staff {stats['active_staff']}, Docs {stats['total_docs']}")

print("\n>>> ALL 17 AUTOMATED TESTS PASSED WITH 4 NEW PERSONNEL! <<<")
