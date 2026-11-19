import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    port_str = os.getenv("PORT", "10000")
    try:
        port = int(port_str)
    except ValueError:
        port = 10000

    print(f"Starting Khoa Xet Nghiem Production Server on port {port}...")
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")
