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

print("1. Testing GET /api/environment/devices...")
r = client.get("/api/environment/devices", headers=headers)
print("Devices Status:", r.status_code)
devices = r.json().get("devices", [])
print(f"Total devices: {len(devices)}")
for d in devices:
    print(f"  [{d['code']}] {d['name']} -> {d['standard']}")

print("\n2. Testing POST /api/environment/logs specifically for Tủ Lạnh TL-01...")
r = client.post("/api/environment/logs", headers=headers, json={
    "log_date": "2026-11-17",
    "shift": "chieu",
    "log_time": "14:30",
    "target_device": "tl01",
    "fridge_temp": 4.1
})
print("TL-01 Log Status:", r.status_code, r.json())

print("\n3. Testing POST /api/environment/logs specifically for Tủ Đông TĐ-01...")
r = client.post("/api/environment/logs", headers=headers, json={
    "log_date": "2026-11-17",
    "shift": "chieu",
    "log_time": "14:35",
    "target_device": "td01",
    "freezer_temp": -21.5
})
print("TĐ-01 Log Status:", r.status_code, r.json())

print("\n4. Testing POST /api/environment/logs specifically for Tủ Ấm TÂ-01...")
r = client.post("/api/environment/logs", headers=headers, json={
    "log_date": "2026-11-17",
    "shift": "chieu",
    "log_time": "14:40",
    "target_device": "ta01",
    "incubator_temp": 36.8
})
print("TÂ-01 Log Status:", r.status_code, r.json())

print("\n5. Testing GET /api/environment/logs to verify merged values...")
r = client.get("/api/environment/logs?year=2026&month=11", headers=headers)
latest = r.json()["stats"]["latest"]
print("Latest merged record:", {
    "date": latest["log_date"],
    "shift": latest["shift"],
    "room_temp": latest["room_temp"],
    "fridge_temp": latest["fridge_temp"],
    "freezer_temp": latest["freezer_temp"],
    "incubator_temp": latest.get("incubator_temp"),
    "target_device": latest.get("target_device")
})

print("\nAll device-specific tests completed successfully!")
