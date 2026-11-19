import os
import hmac
import hashlib
import base64
import json
import time
import ipaddress
from typing import List, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import HTMLResponse, JSONResponse

from backend.config import ALLOWED_OFFICE_IPS, ADMIN_BYPASS_KEY, SECRET_KEY, HOSPITAL_NAME, DEPARTMENT_NAME

# Token duration for Admin Bypass session (e.g. 12 hours)
BYPASS_TOKEN_EXPIRE_HOURS = 12

def get_client_ip(request: Request) -> str:
    """Extract real public client IP from proxy headers or connection host."""
    # Cloudflare Header
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    # Nginx / AWS ALB / Reverse proxy header
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    # Vercel / Standard Forwarded For: "client, proxy1, proxy2"
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_part = x_forwarded_for.split(",")[0].strip()
        if client_part:
            return client_part

    # Direct client connection
    if request.client and request.client.host:
        return request.client.host.strip()

    return "127.0.0.1"

def create_bypass_token(admin_key: str) -> Optional[str]:
    """Create signed cookie token for admin remote bypass."""
    if not hmac.compare_digest(admin_key.strip(), ADMIN_BYPASS_KEY.strip()):
        return None

    payload = {
        "admin_bypass": True,
        "exp": int(time.time()) + (BYPASS_TOKEN_EXPIRE_HOURS * 3600),
        "created_at": int(time.time())
    }
    payload_str = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    return f"{payload_str}.{signature}"

def verify_bypass_token(token: Optional[str]) -> bool:
    """Verify signed admin bypass token."""
    if not token:
        return False
    try:
        parts = token.split(".", 1)
        if len(parts) != 2:
            return False
        payload_str, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return False

        payload = json.loads(base64.urlsafe_b64decode(payload_str.encode()).decode())
        if payload.get("exp", 0) < time.time():
            return False
        return payload.get("admin_bypass") is True
    except Exception:
        return False

def is_ip_allowed(client_ip: str, allowed_rules: List[str]) -> bool:
    """Check if client_ip matches any allowed IP, CIDR subnet, or wildcard rule."""
    if not allowed_rules:
        # If no rules configured, allow access (or set * in env)
        return True

    # Normalize client IP (handle IPv4-mapped IPv6 like ::ffff:192.168.1.1)
    clean_client_ip = client_ip.replace("::ffff:", "").strip()

    for rule in allowed_rules:
        rule = rule.strip()
        if not rule:
            continue

        # Wildcard / Allow all
        if rule in ("*", "allow_all", "any", "ALL"):
            return True

        # Exact match
        if clean_client_ip == rule:
            return True

        # Localhost synonyms
        if clean_client_ip in ("127.0.0.1", "::1", "localhost", "testclient") and rule in ("127.0.0.1", "localhost", "::1"):
            return True

        # Wildcard prefix (e.g. "172.16.12.*" or "113.161.*")
        if rule.endswith(".*"):
            prefix = rule[:-2]
            if clean_client_ip.startswith(prefix):
                return True

        # CIDR Subnet match (e.g. "172.16.12.0/24" or "113.161.45.0/28")
        if "/" in rule:
            try:
                network = ipaddress.ip_network(rule, strict=False)
                addr = ipaddress.ip_address(clean_client_ip)
                if addr in network:
                    return True
            except ValueError:
                pass

    return False

def get_configured_allowed_ips() -> List[str]:
    """Get list of allowed IPs from ALLOWED_OFFICE_IPS environment variable."""
    raw_env = os.getenv("ALLOWED_OFFICE_IPS", ALLOWED_OFFICE_IPS)
    if not raw_env:
        return ["*"]
    rules = [r.strip() for r in raw_env.split(",") if r.strip()]
    return rules

def get_blocked_html(client_ip: str, request_path: str) -> str:
    """Generate professional, medical-grade 403 Forbidden page in Vietnamese."""
    current_time = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QUẢN LÝ XÉT NGHIỆM - Truy Cập Bị Từ Chối</title>
    <style>
        :root {{
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --danger: #dc2626;
            --danger-bg: #fef2f2;
            --danger-border: #fecaca;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --card-bg: #ffffff;
            --body-bg: #f8fafc;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--body-bg);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            width: 100%;
            max-width: 580px;
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%);
            color: white;
            padding: 24px;
            text-align: center;
        }}
        .header h2 {{
            font-size: 16px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .header p {{
            font-size: 13px;
            opacity: 0.9;
        }}
        .content {{
            padding: 32px 24px;
            text-align: center;
        }}
        .icon-wrap {{
            width: 72px;
            height: 72px;
            background-color: var(--danger-bg);
            color: var(--danger);
            border: 2px solid var(--danger-border);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
        }}
        .icon-wrap svg {{
            width: 40px;
            height: 40px;
        }}
        h1 {{
            font-size: 22px;
            font-weight: 700;
            color: #b91c1c;
            margin-bottom: 12px;
        }}
        .alert-message {{
            font-size: 15px;
            line-height: 1.6;
            color: #334155;
            margin-bottom: 24px;
            font-weight: 500;
        }}
        .ip-card {{
            background-color: #f1f5f9;
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 16px;
            text-align: left;
            margin-bottom: 24px;
            font-size: 13px;
        }}
        .ip-row {{
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
            border-bottom: 1px dashed #e2e8f0;
        }}
        .ip-row:last-child {{
            border-bottom: none;
        }}
        .ip-label {{
            color: var(--text-muted);
        }}
        .ip-value {{
            font-weight: 600;
            font-family: monospace;
            font-size: 14px;
            color: #0f172a;
        }}
        .ip-value.danger {{
            color: var(--danger);
        }}
        .guide-box {{
            background-color: #eff6ff;
            border-left: 4px solid var(--primary);
            padding: 12px 16px;
            border-radius: 6px;
            text-align: left;
            font-size: 13px;
            color: #1e40af;
            line-height: 1.5;
            margin-bottom: 24px;
        }}
        .actions {{
            display: flex;
            gap: 12px;
            flex-direction: column;
        }}
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.15s ease;
            border: none;
        }}
        .btn-primary {{
            background-color: var(--primary);
            color: white;
        }}
        .btn-primary:hover {{
            background-color: var(--primary-dark);
        }}
        .btn-secondary {{
            background-color: #f8fafc;
            color: #475569;
            border: 1px solid #cbd5e1;
        }}
        .btn-secondary:hover {{
            background-color: #f1f5f9;
            color: #0f172a;
        }}
        .admin-form {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            display: none;
            text-align: left;
        }}
        .admin-form.show {{
            display: block;
        }}
        .admin-form label {{
            display: block;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 6px;
            color: #334155;
        }}
        .admin-form input {{
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 12px;
            outline: none;
        }}
        .admin-form input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15);
        }}
        .error-msg {{
            color: var(--danger);
            font-size: 12px;
            margin-bottom: 10px;
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{HOSPITAL_NAME}</h2>
            <p>{DEPARTMENT_NAME} &bull; Hệ Thống Quản Lý 2429/QĐ-BYT</p>
        </div>
        <div class="content">
            <div class="icon-wrap">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>
                </svg>
            </div>
            <h1>TRUY CẬP BỊ TỪ CHỐI</h1>
            <p class="alert-message">
                Vui lòng kết nối đúng <strong>mạng Wi-Fi nội bộ của cơ quan</strong> để chấm công và sử dụng phần mềm.
            </p>

            <div class="ip-card">
                <div class="ip-row">
                    <span class="ip-label">Địa chỉ IP thiết bị:</span>
                    <span class="ip-value danger">{client_ip}</span>
                </div>
                <div class="ip-row">
                    <span class="ip-label">Tình trạng mạng:</span>
                    <span class="ip-value" style="color: #b91c1c;">Ngoài mạng Wi-Fi cơ quan</span>
                </div>
                <div class="ip-row">
                    <span class="ip-label">Thời gian kiểm tra:</span>
                    <span class="ip-value">{current_time}</span>
                </div>
            </div>

            <div class="guide-box">
                <strong>Hướng dẫn:</strong>
                <ol style="margin-left: 18px; margin-top: 4px;">
                    <li>Tắt dữ liệu di động (4G/5G) trên điện thoại.</li>
                    <li>Bật và kết nối vào sóng Wi-Fi của Bệnh viện / Khoa Xét nghiệm.</li>
                    <li>Bấm nút <strong>"Thử Lại Kết Nối"</strong> bên dưới.</li>
                </ol>
            </div>

            <div class="actions">
                <button class="btn btn-primary" onclick="window.location.reload();">
                    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <polyline points="23 4 23 10 17 10"></polyline>
                        <polyline points="1 20 1 14 7 14"></polyline>
                        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                    </svg>
                    Thử Lại Kết Nối (Wi-Fi Cơ Quan)
                </button>
                <button class="btn btn-secondary" onclick="toggleAdminForm();">
                    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    Đăng Nhập Quản Trị Viên (Admin Bypass Từ Xa)
                </button>
            </div>

            <div class="admin-form" id="adminForm">
                <label for="adminKey">Mật khẩu Quản trị viên (ADMIN_BYPASS_KEY):</label>
                <input type="password" id="adminKey" placeholder="Nhập mã mở khóa từ xa..." onkeyup="if(event.key==='Enter') submitBypass();">
                <div class="error-msg" id="errorMsg">Mật khẩu không đúng. Vui lòng thử lại.</div>
                <button class="btn btn-primary" style="width: 100%;" onclick="submitBypass();">
                    Xác Nhận Mở Khóa Truy Cập
                </button>
            </div>
        </div>
    </div>

    <script>
        function toggleAdminForm() {{
            const form = document.getElementById('adminForm');
            form.classList.toggle('show');
            if (form.classList.contains('show')) {{
                document.getElementById('adminKey').focus();
            }}
        }}

        async function submitBypass() {{
            const key = document.getElementById('adminKey').value.trim();
            const errorMsg = document.getElementById('errorMsg');
            if (!key) {{
                errorMsg.innerText = "Vui lòng nhập mật khẩu quản trị.";
                errorMsg.style.display = "block";
                return;
            }}

            try {{
                const res = await fetch('/api/admin/bypass', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ bypass_key: key }})
                }});
                const data = await res.json();
                if (res.ok && data.success) {{
                    window.location.href = '{request_path if request_path else "/"}';
                }} else {{
                    errorMsg.innerText = data.detail || "Mật khẩu không đúng.";
                    errorMsg.style.display = "block";
                }}
            }} catch (err) {{
                errorMsg.innerText = "Lỗi kết nối máy chủ.";
                errorMsg.style.display = "block";
            }}
        }}
    </script>
</body>
</html>
"""

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces IP Whitelisting from ALLOWED_OFFICE_IPS.
    Bypasses for:
    - /api/health
    - /admin/bypass, /api/admin/bypass, /api/client-ip
    - Valid signed Admin Bypass cookie
    - Valid X-Admin-Bypass-Key header
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 1. Exempt critical endpoints
        exempt_paths = [
            "/api/health",
            "/api/client-ip",
            "/api/admin/bypass",
            "/api/admin/bypass-logout",
            "/favicon.ico"
        ]
        if path in exempt_paths:
            return await call_next(request)

        # Trạng thái luôn mở: Nếu cấu hình "*" thì cho phép mọi mạng truy cập ngay
        allowed_rules = get_configured_allowed_ips()
        if "*" in allowed_rules or "ALL" in allowed_rules or not allowed_rules:
            return await call_next(request)

        # Allow static files needed for bypass login / CSS if accessed
        if path.startswith("/static/assets/") or path.startswith("/static/css/"):
            return await call_next(request)

        # 2. Check Admin Remote Bypass
        # Method A: Cookie
        bypass_cookie = request.cookies.get("admin_bypass_token")
        if verify_bypass_token(bypass_cookie):
            return await call_next(request)

        # Method B: Header
        bypass_header = request.headers.get("x-admin-bypass-key")
        if bypass_header and hmac.compare_digest(bypass_header.strip(), ADMIN_BYPASS_KEY.strip()):
            return await call_next(request)

        # 3. Extract real client IP
        client_ip = get_client_ip(request)

        # 4. Check against allowed IP rules
        allowed_rules = get_configured_allowed_ips()

        # Check dynamic allowed IPs from DB (if available)
        try:
            from backend.database import get_db
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT ip_address FROM allowed_ips")
            for row in cursor.fetchall():
                ip_val = row["ip_address"] if isinstance(row, dict) else row[0]
                if ip_val:
                    allowed_rules.append(ip_val.strip())
            conn.close()
        except Exception:
            pass

        # If IP is allowed, proceed!
        if is_ip_allowed(client_ip, allowed_rules):
            return await call_next(request)

        # 5. IP is FORBIDDEN -> Block request!
        # If API request: return JSON 403
        if path.startswith("/api/"):
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error_code": "IP_FORBIDDEN",
                    "message": "Truy cập bị từ chối. Vui lòng kết nối đúng mạng Wi-Fi nội bộ của cơ quan để chấm công.",
                    "client_ip": client_ip,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            )

        # If web browser request: return rich branded HTML 403
        return HTMLResponse(
            status_code=403,
            content=get_blocked_html(client_ip, path)
        )
