import os
import hmac
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Request, Response, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from backend.config import ALLOWED_OFFICE_IPS, ADMIN_BYPASS_KEY, HOSPITAL_NAME, DEPARTMENT_NAME
from backend.database import get_db
from backend.auth import get_current_user_optional, require_admin
from backend.ip_whitelist import (
    get_client_ip, is_ip_allowed, get_configured_allowed_ips,
    create_bypass_token, verify_bypass_token, BYPASS_TOKEN_EXPIRE_HOURS
)

router = APIRouter(tags=["IP Whitelist & Admin Bypass"])

class BypassLoginRequest(BaseModel):
    bypass_key: str

class AddIpRequest(BaseModel):
    ip_address: str
    description: Optional[str] = "IP Wi-Fi cơ quan bổ sung"

@router.get("/api/client-ip")
def check_my_ip(request: Request):
    """Public helper endpoint for staff/admin to view their current public IP."""
    client_ip = get_client_ip(request)
    allowed_rules = get_configured_allowed_ips()

    # Add DB allowed IPs
    try:
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

    allowed = is_ip_allowed(client_ip, allowed_rules)
    bypass_active = verify_bypass_token(request.cookies.get("admin_bypass_token"))

    return {
        "client_ip": client_ip,
        "is_allowed": allowed or bypass_active,
        "is_office_ip": allowed,
        "bypass_active": bypass_active,
        "note": "IP của bạn hợp lệ để truy cập hệ thống" if (allowed or bypass_active) else "IP nằm ngoài danh sách Wi-Fi cơ quan"
    }

@router.post("/api/admin/bypass")
def admin_bypass_login(req: BypassLoginRequest, response: Response):
    """Authenticate with ADMIN_BYPASS_KEY and set signed HTTP-only cookie."""
    token = create_bypass_token(req.bypass_key)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mã mở khóa Quản trị viên (ADMIN_BYPASS_KEY) không chính xác."
        )

    # Set secure cookie
    response.set_cookie(
        key="admin_bypass_token",
        value=token,
        max_age=BYPASS_TOKEN_EXPIRE_HOURS * 3600,
        httponly=True,
        samesite="lax",
        secure=False  # Allow both http and https for versatility
    )

    return {
        "success": True,
        "message": "Mở khóa Quản trị viên từ xa thành công. Bạn có thể truy cập toàn bộ hệ thống.",
        "expires_in_hours": BYPASS_TOKEN_EXPIRE_HOURS
    }

@router.post("/api/admin/bypass-logout")
@router.get("/api/admin/bypass-logout")
def admin_bypass_logout(response: Response):
    """Clear admin bypass cookie."""
    response.delete_cookie(key="admin_bypass_token")
    return {"success": True, "message": "Đã thoát chế độ Quản trị viên từ xa."}

@router.get("/api/admin/ip-whitelist")
def get_ip_whitelist(request: Request):
    """Get all allowed IP rules (both env and database)."""
    # Verify Admin or Bypass token
    bypass_active = verify_bypass_token(request.cookies.get("admin_bypass_token"))
    current_user = get_current_user_optional(request)
    if not bypass_active and (not current_user or current_user.get("role") not in ("truong_khoa", "ktv_truong")):
        raise HTTPException(status_code=403, detail="Yêu cầu quyền Quản trị viên.")

    env_rules = get_configured_allowed_ips()

    db_rules = []
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ip_address, description, added_by, created_at FROM allowed_ips ORDER BY id DESC")
        for row in cursor.fetchall():
            db_rules.append(dict(row))
        conn.close()
    except Exception:
        pass

    client_ip = get_client_ip(request)

    return {
        "client_ip": client_ip,
        "env_allowed_ips": env_rules,
        "db_allowed_ips": db_rules,
        "current_device_status": {
            "ip": client_ip,
            "is_whitelisted": is_ip_allowed(client_ip, env_rules + [r["ip_address"] for r in db_rules])
        }
    }

@router.post("/api/admin/ip-whitelist")
def add_ip_to_whitelist(req: AddIpRequest, request: Request):
    """Add a new IP (e.g. current device IP or new office IP) to database whitelist."""
    bypass_active = verify_bypass_token(request.cookies.get("admin_bypass_token"))
    current_user = get_current_user_optional(request)
    if not bypass_active and (not current_user or current_user.get("role") not in ("truong_khoa", "ktv_truong")):
        raise HTTPException(status_code=403, detail="Yêu cầu quyền Quản trị viên.")

    clean_ip = req.ip_address.strip()
    if not clean_ip:
        raise HTTPException(status_code=400, detail="Địa chỉ IP không được để trống.")

    added_by = current_user.get("full_name", "Quản trị viên (Bypass)") if current_user else "Quản trị viên (Bypass)"

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO allowed_ips (ip_address, description, added_by)
            VALUES (?, ?, ?)
        """, (clean_ip, req.description, added_by))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail=f"IP này đã tồn tại hoặc không hợp lệ: {e}")

    conn.close()
    return {"success": True, "message": f"Đã thêm IP {clean_ip} vào danh sách Wi-Fi cơ quan."}

@router.delete("/api/admin/ip-whitelist/{ip_id}")
def delete_ip_from_whitelist(ip_id: int, request: Request):
    """Delete an IP from database whitelist."""
    bypass_active = verify_bypass_token(request.cookies.get("admin_bypass_token"))
    current_user = get_current_user_optional(request)
    if not bypass_active and (not current_user or current_user.get("role") not in ("truong_khoa", "ktv_truong")):
        raise HTTPException(status_code=403, detail="Yêu cầu quyền Quản trị viên.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM allowed_ips WHERE id = ?", (ip_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã xóa IP khỏi danh sách."}

@router.get("/admin/ip-whitelist", response_class=HTMLResponse)
def ip_whitelist_admin_page(request: Request):
    """Dedicated management page for Office Wi-Fi IPs."""
    bypass_active = verify_bypass_token(request.cookies.get("admin_bypass_token"))
    current_user = get_current_user_optional(request)
    if not bypass_active and (not current_user or current_user.get("role") not in ("truong_khoa", "ktv_truong")):
        return HTMLResponse("""<script>alert('Vui lòng đăng nhập quyền Quản trị viên hoặc Admin Bypass.'); window.location.href='/';</script>""")

    client_ip = get_client_ip(request)
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quản Lý IP Wi-Fi Cơ Quan - {HOSPITAL_NAME}</title>
    <link rel="stylesheet" href="/static/css/app.css">
    <style>
        .admin-box {{ max-width: 800px; margin: 40px auto; background: white; padding: 24px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .badge-ip {{ font-family: monospace; font-size: 14px; font-weight: bold; background: #e0f2fe; color: #0369a1; padding: 3px 8px; border-radius: 4px; }}
        .table-ips {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        .table-ips th, .table-ips td {{ border: 1px solid #e2e8f0; padding: 10px 14px; text-align: left; font-size: 13px; }}
        .table-ips th {{ background: #f8fafc; font-weight: 600; }}
        .add-row {{ display: flex; gap: 10px; margin-top: 16px; }}
        .add-row input {{ flex: 1; padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; }}
    </style>
</head>
<body style="background: #f1f5f9; padding: 20px;">
    <div class="admin-box">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 20px;">
            <div>
                <h2 style="color: #0369a1; margin: 0;">CẤU HÌNH IP WI-FI CƠ QUAN</h2>
                <small style="color: #64748b;">Khóa truy cập chỉ cho phép mạng nội bộ của viện sử dụng</small>
            </div>
            <a href="/" class="btn btn-secondary" style="padding: 8px 14px; text-decoration: none; border-radius: 6px; background: #e2e8f0; color: #1e293b; font-size: 13px;">&larr; Về Dashboard</a>
        </div>

        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px; border-radius: 8px; margin-bottom: 20px;">
            <strong>IP Hiện Tại Của Bạn:</strong> <span class="badge-ip" id="currentIpSpan">{client_ip}</span>
            <button onclick="addCurrentIp()" class="btn btn-primary" style="margin-left: 14px; padding: 5px 12px; font-size: 12px; background: #16a34a; color: white; border: none; border-radius: 4px; cursor: pointer;">
                + Thêm IP Này Vào Danh Sách Cho Phép
            </button>
        </div>

        <h4 style="margin-bottom: 8px;">1. Danh Sách IP Cố Định (Từ Biến Môi Trường ALLOWED_OFFICE_IPS)</h4>
        <div id="envIpsList" style="background: #f8fafc; padding: 10px 14px; border-radius: 6px; border: 1px dashed #cbd5e1; font-family: monospace; font-size: 13px; color: #334155;">
            Đang tải...
        </div>

        <h4 style="margin-top: 24px; margin-bottom: 8px;">2. Danh Sách IP Bổ Sung Trong Database</h4>
        <div class="add-row">
            <input type="text" id="newIpInput" placeholder="Nhập địa chỉ IP (ví dụ: 113.161.45.12 hoặc 172.16.12.*)">
            <input type="text" id="newIpDesc" placeholder="Ghi chú (ví dụ: Wi-Fi tầng 2 / Dự phòng)">
            <button onclick="addNewIp()" style="background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">Thêm IP</button>
        </div>

        <table class="table-ips">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Địa chỉ IP</th>
                    <th>Ghi chú</th>
                    <th>Người thêm</th>
                    <th>Thời gian</th>
                    <th>Thao tác</th>
                </tr>
            </thead>
            <tbody id="dbIpsBody">
                <tr><td colspan="6" style="text-align: center;">Đang tải...</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        async function loadData() {{
            const res = await fetch('/api/admin/ip-whitelist');
            if (!res.ok) return;
            const data = await res.json();
            
            // Env list
            const envDiv = document.getElementById('envIpsList');
            if (data.env_allowed_ips && data.env_allowed_ips.length > 0) {{
                envDiv.innerHTML = data.env_allowed_ips.map(ip => `<span class="badge-ip" style="margin-right: 8px;">${{ip}}</span>`).join(' ');
            }} else {{
                envDiv.innerHTML = '<span style="color: #94a3b8;">Chưa cấu hình biến ALLOWED_OFFICE_IPS (Mặc định cho phép tất cả nếu rỗng)</span>';
            }}

            // DB list
            const tbody = document.getElementById('dbIpsBody');
            if (data.db_allowed_ips && data.db_allowed_ips.length > 0) {{
                tbody.innerHTML = data.db_allowed_ips.map(item => `
                    <tr>
                        <td>${{item.id}}</td>
                        <td><span class="badge-ip">${{item.ip_address}}</span></td>
                        <td>${{item.description || ''}}</td>
                        <td>${{item.added_by || ''}}</td>
                        <td>${{item.created_at || ''}}</td>
                        <td>
                            <button onclick="deleteIp(${{item.id}})" style="background: #ef4444; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 11px;">Xóa</button>
                        </td>
                    </tr>
                `).join('');
            }} else {{
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #94a3b8;">Chưa có IP nào thêm trong database.</td></tr>';
            }}
        }}

        async function addCurrentIp() {{
            const ip = document.getElementById('currentIpSpan').innerText.trim();
            const res = await fetch('/api/admin/ip-whitelist', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ ip_address: ip, description: 'IP máy hiện tại (Thêm tự động)' }})
            }});
            const data = await res.json();
            if (res.ok) {{
                alert(data.message);
                loadData();
            }} else {{
                alert(data.detail || 'Lỗi thêm IP');
            }}
        }}

        async function addNewIp() {{
            const ip = document.getElementById('newIpInput').value.trim();
            const desc = document.getElementById('newIpDesc').value.trim();
            if (!ip) return alert('Vui lòng nhập IP');

            const res = await fetch('/api/admin/ip-whitelist', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ ip_address: ip, description: desc }})
            }});
            const data = await res.json();
            if (res.ok) {{
                document.getElementById('newIpInput').value = '';
                document.getElementById('newIpDesc').value = '';
                loadData();
            }} else {{
                alert(data.detail || 'Lỗi thêm IP');
            }}
        }}

        async function deleteIp(id) {{
            if (!confirm('Bạn có chắc chắn muốn xóa IP này?')) return;
            const res = await fetch(`/api/admin/ip-whitelist/${{id}}`, {{ method: 'DELETE' }});
            if (res.ok) {{
                loadData();
            }}
        }}

        loadData();
    </script>
</body>
</html>
""")
