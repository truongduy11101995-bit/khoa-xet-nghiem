import os
import shutil
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from backend.database import get_db
from backend.auth import get_current_user, require_admin
from backend.config import HO_SO_DIR
from backend.models import ProfileUpdateRequest

router = APIRouter(prefix="/api/profiles", tags=["Employee Profiles"])

def check_profile_access(target_user_id: int, current_user: dict):
    """Enforce rule: Only target employee or Trưởng khoa / KTV Trưởng can access."""
    is_owner = target_user_id == current_user["id"]
    is_admin = current_user.get("role") in ("truong_khoa", "ktv_truong")
    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="BẢO MẬT: Chỉ nhân viên này hoặc Trưởng khoa / KTV Trưởng mới có quyền xem và tải hồ sơ cá nhân."
        )

@router.get("/list")
def list_profiles(user: dict = Depends(get_current_user)):
    """List 8 staff members."""
    conn = get_db()
    cursor = conn.cursor()

    is_admin = user.get("role") in ("truong_khoa", "ktv_truong")
    cursor.execute("""
        SELECT u.id, u.username, u.full_name, u.title, u.role, u.folder_name,
               u.dob, u.phone, u.email, u.cchn, u.cchn_date, u.cchn_scope,
               u.education, u.specialty, u.status,
               (SELECT COUNT(*) FROM employee_files ef WHERE ef.user_id = u.id) as file_count
        FROM users u
        ORDER BY u.id ASC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Redact sensitive contact/CCHN data of colleagues if the viewer is a regular KTV
    if not is_admin:
        for r in rows:
            if r["id"] != user["id"]:
                r["cchn"] = "***"
                r["cchn_date"] = "***"
                r["cchn_scope"] = "***"
                r["phone"] = "***"
                r["email"] = "***"

    return {
        "success": True,
        "profiles": rows,
        "current_user_id": user["id"],
        "is_admin": is_admin
    }

@router.get("/{user_id}")
def get_profile_detail(user_id: int, user: dict = Depends(get_current_user)):
    """Get full profile details and file list for employee (strictly checked)."""
    check_profile_access(user_id, user)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    target_user = cursor.fetchone()

    if not target_user:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên.")

    user_data = dict(target_user)
    del user_data["password_hash"]

    # Get employee files
    cursor.execute("""
        SELECT * FROM employee_files WHERE user_id = ? ORDER BY uploaded_at DESC
    """, (user_id,))
    files = [dict(f) for f in cursor.fetchall()]
    conn.close()

    return {
        "success": True,
        "profile": user_data,
        "files": files,
        "can_edit": user_id == user["id"] or user.get("role") in ("truong_khoa", "ktv_truong")
    }

@router.put("/{user_id}")
def update_profile(
    user_id: int,
    req: ProfileUpdateRequest,
    user: dict = Depends(get_current_user)
):
    """Update profile information."""
    check_profile_access(user_id, user)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users SET
            phone = COALESCE(?, phone),
            email = COALESCE(?, email),
            dob = COALESCE(?, dob),
            cchn = COALESCE(?, cchn),
            cchn_date = COALESCE(?, cchn_date),
            cchn_scope = COALESCE(?, cchn_scope),
            education = COALESCE(?, education),
            specialty = COALESCE(?, specialty),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        req.phone, req.email, req.dob, req.cchn,
        req.cchn_date, req.cchn_scope, req.education,
        req.specialty, user_id
    ))

    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'PROFILE_UPDATE', ?)
    """, (user["id"], f"Cập nhật thông tin hồ sơ nhân sự #{user_id}"))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Cập nhật thông tin hồ sơ nhân viên thành công!"}

@router.post("/{user_id}/upload-file")
async def upload_employee_file(
    user_id: int,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    title: str = Form(...),
    user: dict = Depends(get_current_user)
):
    r"""
    Upload scan or document to employee personal folder on D: drive:
    D:\KHOA_XET_NGHIEM_DATA\HO_SO_NHAN_SU\[folder_name]\
    """
    check_profile_access(user_id, user)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT folder_name, full_name FROM users WHERE id = ?", (user_id,))
    target = cursor.fetchone()
    if not target:
        conn.close()
        raise HTTPException(status_code=404, detail="Nhân viên không tồn tại.")

    folder_name = target["folder_name"]
    emp_dir = HO_SO_DIR / folder_name
    emp_dir.mkdir(parents=True, exist_ok=True)

    orig_name = file.filename or "tep_dinh_kem"
    dest_path = emp_dir / orig_name

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = dest_path.stat().st_size

    cursor.execute("""
        INSERT INTO employee_files (
            user_id, doc_type, title, file_name, file_path, file_size, uploaded_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, doc_type, title, orig_name, str(dest_path), file_size, user["id"]))

    file_id = cursor.lastrowid
    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'PROFILE_FILE_UPLOAD', ?)
    """, (user["id"], f"Tải lên tệp '{orig_name}' cho hồ sơ {target['full_name']}"))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "file_id": file_id,
        "message": f"Tải lên và lưu trữ thành công: {orig_name}"
    }

@router.get("/{user_id}/file/{file_id}/download")
def download_employee_file(
    user_id: int,
    file_id: int,
    user: dict = Depends(get_current_user)
):
    """Download scan document with strict authorization."""
    check_profile_access(user_id, user)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employee_files WHERE id = ? AND user_id = ?", (file_id, user_id))
    f = cursor.fetchone()
    conn.close()

    if not f:
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp hồ sơ này.")

    file_path = Path(f["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Tệp tin không tồn tại trên ổ D.")

    return FileResponse(
        path=str(file_path),
        filename=f["file_name"],
        media_type="application/octet-stream"
    )

@router.get("/{user_id}/file/{file_id}/preview")
def preview_employee_file(
    user_id: int,
    file_id: int,
    user: dict = Depends(get_current_user)
):
    """Preview scan document (PDF or image)."""
    check_profile_access(user_id, user)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employee_files WHERE id = ? AND user_id = ?", (file_id, user_id))
    f = cursor.fetchone()
    conn.close()

    if not f:
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp hồ sơ này.")

    file_path = Path(f["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Tệp tin không tồn tại trên ổ D.")

    ext = file_path.suffix.lstrip(".").lower()
    media_types = {
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg"
    }
    m_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        media_type=m_type,
        headers={"Content-Disposition": f"inline; filename={f['file_name']}"}
    )

@router.delete("/{user_id}/file/{file_id}")
def delete_employee_file(
    user_id: int,
    file_id: int,
    user: dict = Depends(get_current_user)
):
    """Delete an employee file."""
    check_profile_access(user_id, user)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employee_files WHERE id = ? AND user_id = ?", (file_id, user_id))
    f = cursor.fetchone()

    if not f:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp hồ sơ này.")

    cursor.execute("DELETE FROM employee_files WHERE id = ?", (file_id,))
    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'PROFILE_FILE_DELETE', ?)
    """, (user["id"], f"Xóa tệp hồ sơ #{file_id} của nhân sự #{user_id}"))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Đã xóa tệp hồ sơ thành công."}
