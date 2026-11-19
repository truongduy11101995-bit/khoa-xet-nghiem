import os
import sys
from pathlib import Path

app_dir = Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
os.chdir(str(app_dir))
sys.path.insert(0, str(app_dir))
os.environ["PYTHONPATH"] = str(app_dir)

log_dir = Path(r"D:\KHOA_XET_NGHIEM_DATA\DATABASE")
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "server.log"

try:
    log_fp = open(log_file, "a", encoding="utf-8")
    sys.stdout = log_fp
    sys.stderr = log_fp
except BaseException:
    pass

import uvicorn
from backend.main import app

if __name__ == "__main__":
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("=== Khoa Xet Nghiem Server Starting ===\n")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning", access_log=False)
    except BaseException as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"Server exited/error: {type(e).__name__} - {e}\n")
