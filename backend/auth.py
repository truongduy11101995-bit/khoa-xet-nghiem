import hashlib
import hmac
import base64
import json
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from backend.config import SECRET_KEY, TOKEN_EXPIRE_HOURS

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with salt."""
    if salt is None:
        salt = base64.b64encode(hashlib.sha256(str(time.time()).encode()).digest()[:16]).decode()
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    b64_hash = base64.b64encode(key).decode()
    return f"{salt}${b64_hash}"

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify password against stored salt$hash."""
    try:
        salt, b64_hash = stored_hash.split('$', 1)
        expected = hash_password(plain_password, salt)
        return hmac.compare_digest(expected, stored_hash)
    except Exception:
        return False

def create_token(user_data: Dict[str, Any]) -> str:
    """Create signed session token containing user payload and expiry."""
    payload = {
        "id": user_data["id"],
        "username": user_data["username"],
        "role": user_data["role"],
        "full_name": user_data["full_name"],
        "title": user_data.get("title", ""),
        "exp": int(time.time()) + (TOKEN_EXPIRE_HOURS * 3600)
    }
    payload_str = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
    return f"{payload_str}.{signature}"

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify signed token."""
    try:
        payload_str, signature = token.split('.', 1)
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_str.encode()).decode())
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Extract user from Authorization Bearer header or session cookie."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")
    elif "token" in request.query_params:
        token = request.query_params.get("token")

    if not token:
        return None
    return decode_token(token)

def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency for authenticated user."""
    user = get_current_user_optional(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên làm việc đã hết hạn hoặc chưa đăng nhập.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_admin(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Allow Trưởng khoa or KTV Trưởng (Management rights)."""
    if user.get("role") not in ("truong_khoa", "ktv_truong"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện thao tác quản lý này."
        )
    return user

def require_truong_khoa(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Allow only Trưởng khoa (Highest admin)."""
    if user.get("role") != "truong_khoa":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Trưởng khoa mới có quyền thực hiện thao tác này."
        )
    return user
