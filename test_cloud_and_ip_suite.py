import os
import sys
from pathlib import Path

# Add project path
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

os.environ["ALLOWED_OFFICE_IPS"] = "113.161.45.12, 172.16.12.*, 127.0.0.1"
os.environ["ADMIN_BYPASS_KEY"] = "ThienAn2026@BypassLab"

from fastapi.testclient import TestClient
from backend.main import app
from backend.db_adapter import PostgresCursorWrapper

client = TestClient(app)

def test_ip_whitelist_and_admin_bypass():
    print("--- [TEST 1] Testing IP Whitelisting ---")
    
    # 1. Health check is always exempt
    r = client.get("/api/health")
    assert r.status_code == 200, "Health check must be 200"
    print("  ✓ /api/health is exempt and returns 200")

    # 2. Allowed static IP
    r = client.get("/login", headers={"x-forwarded-for": "113.161.45.12"})
    assert r.status_code == 200, "Allowed IP must pass"
    print("  ✓ Allowed office IP (113.161.45.12) passed with 200")

    # 3. Wildcard subnet IP
    r = client.get("/login", headers={"x-forwarded-for": "172.16.12.88"})
    assert r.status_code == 200, "Wildcard subnet IP must pass"
    print("  ✓ Allowed hospital LAN wildcard (172.16.12.88) passed with 200")

    # 4. Blocked External IP (e.g. 4G/Home Wi-Fi: 203.113.15.99)
    r = client.get("/login", headers={"x-forwarded-for": "203.113.15.99"})
    assert r.status_code == 403, "Blocked IP must return 403"
    assert "TRUY CẬP BỊ TỪ CHỐI" in r.text
    assert "203.113.15.99" in r.text
    print("  ✓ Blocked external IP returned 403 HTML with warning and IP display")

    # 5. Blocked External API call
    r = client.get("/api/schedule/positions", headers={"x-forwarded-for": "203.113.15.99"})
    assert r.status_code == 403, "Blocked API must return 403"
    data = r.json()
    assert data["error_code"] == "IP_FORBIDDEN"
    print("  ✓ Blocked external API returned 403 JSON format correctly")

    print("\n--- [TEST 2] Testing Admin Emergency Bypass ---")
    # 6. Invalid bypass key
    r = client.post("/api/admin/bypass", json={"bypass_key": "WrongPassword"})
    assert r.status_code == 401
    print("  ✓ Invalid Admin Bypass key rejected with 401")

    # 7. Valid bypass key
    r = client.post("/api/admin/bypass", json={"bypass_key": "ThienAn2026@BypassLab"})
    assert r.status_code == 200
    assert "admin_bypass_token" in client.cookies
    print("  ✓ Valid Admin Bypass key authenticated and issued secure cookie")

    # 8. Access from blocked IP with bypass cookie
    r = client.get("/login", headers={"x-forwarded-for": "203.113.15.99"})
    assert r.status_code == 200
    print("  ✓ Remote access from blocked IP successfully unlocked via Admin Bypass cookie")

    print("\n--- [TEST 3] Testing Dynamic IP Management ---")
    # 9. Get IP list
    r = client.get("/api/admin/ip-whitelist")
    assert r.status_code == 200
    ip_data = r.json()
    assert "113.161.45.12" in ip_data["env_allowed_ips"]
    print("  ✓ Fetched IP whitelist rules successfully")

    # 10. Add dynamic IP
    r = client.post("/api/admin/ip-whitelist", json={
        "ip_address": "14.161.99.100",
        "description": "Viettel Backup Line"
    })
    assert r.status_code == 200
    print("  ✓ Added dynamic IP to database whitelist")

    # Verify newly added IP can access
    # Clear bypass cookie first
    client.cookies.clear()
    r = client.get("/login", headers={"x-forwarded-for": "14.161.99.100"})
    assert r.status_code == 200
    print("  ✓ Newly added dynamic IP (14.161.99.100) immediately allowed access!")

    print("\n--- [TEST 4] Testing Database Adapter & SQL Export ---")
    class DummyCursor:
        def __init__(self):
            self.description = [("id",), ("name",)]
    wrapper = PostgresCursorWrapper(DummyCursor())
    conv = wrapper._convert_query("SELECT * FROM users WHERE VN_LOWER(title) LIKE ?")
    assert conv == "SELECT * FROM users WHERE LOWER(title) LIKE %s"
    print("  ✓ Query conversion ? -> %s and VN_LOWER -> LOWER verified")

    sql_file = APP_DIR / "import_data_to_supabase.sql"
    assert sql_file.exists() and sql_file.stat().st_size > 1000
    print(f"  ✓ Export SQL file verified: {sql_file.name} ({sql_file.stat().st_size} bytes)")

    print("\n>>> ALL CLOUD & IP WHITELIST TESTS PASSED 100%! <<<")

if __name__ == "__main__":
    test_ip_whitelist_and_admin_bypass()
