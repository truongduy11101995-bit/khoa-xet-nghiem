from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from backend.database import get_db
from backend.auth import (
    verify_password, hash_password, create_token, get_current_user
)
from backend.models import LoginRequest, ChangePasswordRequest

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login")
def login(req: LoginRequest, response: Response):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE username = ? AND status = 'active'
    """, (req.username.strip(),))
    user = cursor.fetchone()

    if not user or not verify_password(req.password, user["password_hash"]):
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác."
        )

    user_dict = dict(user)
    token = create_token(user_dict)

    # Set HTTP-only session cookie for smooth browser experience
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=7 * 24 * 3600,
        samesite="lax"
    )

    # Log action
    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'LOGIN', 'Đăng nhập hệ thống thành công')
    """, (user_dict["id"],))
    conn.commit()
    conn.close()

    # Don't send back password_hash
    del user_dict["password_hash"]
    return {
        "success": True,
        "token": token,
        "user": user_dict,
        "message": f"Chào mừng {user_dict['full_name']} đăng nhập thành công!"
    }

@router.post("/logout")
def logout(response: Response, user: dict = Depends(get_current_user)):
    conn = get_db()
    conn.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'LOGOUT', 'Đăng xuất khỏi hệ thống')
    """, (user["id"],))
    conn.commit()
    conn.close()

    response.delete_cookie("access_token")
    return {"success": True, "message": "Đã đăng xuất thành công."}

@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, full_name, title, role, folder_name,
               dob, phone, email, cchn, cchn_date, cchn_scope,
               education, specialty, status
        FROM users WHERE id = ?
    """, (user["id"],))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin tài khoản.")
    return {"success": True, "user": dict(db_user)}

@router.post("/change-password")
def change_password(req: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user["id"],))
    row = cursor.fetchone()

    if not row or not verify_password(req.old_password, row["password_hash"]):
        conn.close()
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không chính xác.")

    if len(req.new_password) < 4:
        conn.close()
        raise HTTPException(status_code=400, detail="Mật khẩu mới phải có ít nhất 4 ký tự.")

    new_hash = hash_password(req.new_password)
    cursor.execute("""
        UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    """, (new_hash, user["id"]))
    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'CHANGE_PASSWORD', 'Thay đổi mật khẩu thành công')
    """, (user["id"],))
    conn.commit()
    conn.close()

    return {"success": True, "message": "Đổi mật khẩu thành công!"}
