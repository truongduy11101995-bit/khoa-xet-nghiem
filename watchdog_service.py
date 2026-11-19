import os
import sys
import time
import traceback

log_file = r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\watchdog_error.log"

try:
    import subprocess
    import socket
    import re
    from pathlib import Path

    APP_DIR = Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
    DESKTOP_DIR = Path(os.path.expanduser("~/Desktop"))
    PYTHONW_EXE = r"C:\Users\TP.KHOAXETNGHIEM\AppData\Local\Programs\Python\Python312\pythonw.exe"
    if not os.path.exists(PYTHONW_EXE):
        PYTHONW_EXE = sys.executable

    CLOUDFLARED_EXE = str(APP_DIR / "cloudflared.exe")
    TUNNEL_LOG = APP_DIR / "tunnel.log"
    SERVER_SCRIPT = APP_DIR / "run_server_background.py"
    URL_SHORTCUT = DESKTOP_DIR / "QUẢN LÝ XÉT NGHIỆM.url"
    LINK_TXT = DESKTOP_DIR / "LINK_TRUY_CAP_ONLINE.txt"

    server_proc = None
    tunnel_proc = None
    last_found_url = None

    def get_stealth_startupinfo():
        if os.name == 'nt':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0 # SW_HIDE
            return si
        return None

    def is_port_in_use(port=8000):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                return s.connect_ex(('127.0.0.1', port)) == 0
        except Exception:
            return False

    def ensure_server():
        global server_proc
        if not is_port_in_use(8000):
            try:
                server_proc = subprocess.Popen(
                    [PYTHONW_EXE, str(SERVER_SCRIPT)],
                    cwd=str(APP_DIR),
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                    startupinfo=get_stealth_startupinfo()
                )
                time.sleep(2)
            except Exception as e:
                with open(log_file, "a") as f:
                    f.write(f"ensure_server err: {e}\n")

    def is_cloudflared_running():
        global tunnel_proc
        if tunnel_proc and tunnel_proc.poll() is None:
            return True
        try:
            res = subprocess.run(
                ["tasklist", "/fi", "imagename eq cloudflared.exe"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                startupinfo=get_stealth_startupinfo()
            )
            return "cloudflared.exe" in res.stdout.lower()
        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"is_cloudflared_running err: {e}\n")
            return False

    def update_shortcuts(url):
        global last_found_url
        if not url or url == last_found_url:
            return
        last_found_url = url
        try:
            content = f"[InternetShortcut]\nURL={url}\nIconIndex=0\nIconFile=C:\\Windows\\System32\\shell32.dll\n"
            with open(URL_SHORTCUT, "w", encoding="utf-8") as f:
                f.write(content)
            
            info = (
                f"=== HỆ THỐNG QUẢN LÝ KHOA XÉT NGHIỆM - BVĐK THIÊN ÂN ===\n\n"
                f"ĐƯỜNG LINK TRUY CẬP DUY NHẤT (Dùng chung cho mọi thiết bị: điện thoại, máy tính, 4G, ở nhà hay ở viện):\n"
                f"👉 {url}\n\n"
                f"(Riêng trên máy tính này: Chỉ cần nhấp đúp biểu tượng 'QUẢN LÝ XÉT NGHIỆM' ngoài Desktop)\n\n"
                f"---\n"
                f"* Tài khoản Trưởng khoa: le_dinh_tu / Mật khẩu: 123456\n"
                f"* Tài khoản KTV Trưởng: nguyen_truong_duy / Mật khẩu: 123456\n"
                f"* Trạng thái: Hoạt động trực tuyến 24/7\n"
            )
            with open(LINK_TXT, "w", encoding="utf-8") as f:
                f.write(info)
        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"update_shortcuts err: {e}\n")

    def verify_url_active(url):
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as res:
                return res.status == 200
        except Exception:
            return False

    def extract_tunnel_url():
        if not TUNNEL_LOG.exists():
            return None
        try:
            with open(TUNNEL_LOG, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            for line in reversed(lines):
                match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if match:
                    candidate = match.group(0)
                    if verify_url_active(candidate):
                        return candidate
        except Exception:
            pass
        return None

    def ensure_tunnel():
        global tunnel_proc
        if not is_cloudflared_running():
            try:
                tunnel_proc = subprocess.Popen(
                    [CLOUDFLARED_EXE, "tunnel", "--url", "http://localhost:8000", "--logfile", str(TUNNEL_LOG)],
                    cwd=str(APP_DIR),
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                    startupinfo=get_stealth_startupinfo()
                )
                time.sleep(3)
            except Exception as e:
                with open(log_file, "a") as f:
                    f.write(f"ensure_tunnel err: {e}\n")

    with open(log_file, "a") as f:
        f.write("Watchdog starting loop...\n")

    while True:
        try:
            ensure_server()
            ensure_tunnel()
            url = extract_tunnel_url()
            if url:
                update_shortcuts(url)
        except Exception as e:
            with open(log_file, "a") as f:
                f.write(f"main loop err: {e}\n")
        time.sleep(30)

except Exception as ex:
    with open(log_file, "a") as f:
        f.write(f"Fatal crash: {traceback.format_exc()}\n")
