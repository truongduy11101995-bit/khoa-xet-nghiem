import urllib.request
import json

base = "http://127.0.0.1:8000"

print("1. Testing static file: /static/js/module7_environment.js")
req = urllib.request.urlopen(f"{base}/static/js/module7_environment.js")
print(f"Status: {req.status}, Length: {len(req.read())} bytes")

print("\n2. Testing login API...")
login_payload = json.dumps({"username": "le_dinh_tu", "password": "123456"}).encode()
req = urllib.request.Request(f"{base}/api/auth/login", data=login_payload, headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req)
login_data = json.loads(resp.read().decode())
token = login_data["token"]
print("Login success! User:", login_data["user"]["full_name"])

print("\n3. Testing /api/inventory/open-vials...")
req = urllib.request.Request(f"{base}/api/inventory/open-vials", headers={"Authorization": f"Bearer {token}"})
resp = urllib.request.urlopen(req)
vials_data = json.loads(resp.read().decode())
print(f"Open Vials Stats: {vials_data['stats']}")
print(f"Total vials: {len(vials_data['vials'])}")

print("\n4. Testing /api/environment/logs...")
req = urllib.request.Request(f"{base}/api/environment/logs?year=2026&month=11", headers={"Authorization": f"Bearer {token}"})
resp = urllib.request.urlopen(req)
env_data = json.loads(resp.read().decode())
print(f"Env logs count: {len(env_data['logs'])}, Safe: {env_data['stats']['safe_count']}, Warning: {env_data['stats']['warning_count']}")

print("\nAll live HTTP server checks passed 100%!")
