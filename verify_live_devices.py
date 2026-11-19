import urllib.request
import json

base = "http://127.0.0.1:8000"

login_payload = json.dumps({"username": "le_dinh_tu", "password": "123456"}).encode()
req = urllib.request.Request(f"{base}/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req)
token = json.loads(resp.read().decode())["token"]

print("1. Testing GET /api/environment/devices on live server...")
req = urllib.request.Request(f"{base}/api/environment/devices", headers={"Authorization": f"Bearer {token}"})
resp = urllib.request.urlopen(req)
devices_data = json.loads(resp.read().decode())
print("Devices count:", len(devices_data["devices"]))

print("\n2. Testing POST /api/environment/logs specifically for Tủ Lạnh TL-01 on live server...")
post_payload = json.dumps({
    "log_date": "2026-11-17",
    "shift": "chieu",
    "target_device": "tl01",
    "fridge_temp": 4.3
}).encode()
req = urllib.request.Request(f"{base}/api/environment/logs", data=post_payload, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
})
resp = urllib.request.urlopen(req)
result = json.loads(resp.read().decode())
print("Save result:", result["message"])

print("\nLive server verified successfully!")
