import sys
from pathlib import Path

app_dir = Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
sys.path.insert(0, str(app_dir))

from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import create_token

client = TestClient(app)

token = create_token({
    "id": 1,
    "username": "le_dinh_tu",
    "role": "truong_khoa",
    "full_name": "CN. Lê Đình Tú",
    "title": "Trưởng Khoa Xét Nghiệm"
})
headers = {"Authorization": f"Bearer {token}"}

print("Testing POST /api/inventory/open-vials...")
post_vial = client.post("/api/inventory/open-vials", headers=headers, json={
    "item_code": "HH-TEST-01",
    "item_name": "Dung dịch ly giải BC (Lyse)",
    "lot_number": "LOT9988",
    "vial_label": "Bình 500ml",
    "open_date": "2026-11-17",
    "open_time": "09:30",
    "stability_days": 60,
    "location": "Máy huyết học",
    "notes": "Mở nắp bình mới thử nghiệm"
})
print("POST Vial Status:", post_vial.status_code, post_vial.json())

print("\nTesting POST /api/environment/logs (Morning shift update)...")
post_env = client.post("/api/environment/logs", headers=headers, json={
    "log_date": "2026-11-17",
    "shift": "chieu",
    "log_time": "14:15",
    "room_temp": 23.0,
    "room_humidity": 59.5,
    "fridge_temp": 4.2,
    "freezer_temp": -21.0,
    "action_taken": "Điều kiện máy móc và tủ lạnh ổn định"
})
print("POST Env Status:", post_env.status_code, post_env.json())

print("\nAll POST tests completed successfully!")
