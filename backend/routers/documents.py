import os
import io
import json
import shutil
import zipfile
from pathlib import Path
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse, Response
from backend.database import get_db
from backend.auth import get_current_user, require_admin
from backend.config import (
    BIEU_MAU_DIR, BIEU_MAU_PHIEU_KQ, BIEU_MAU_2429, BIEU_MAU_HANH_CHINH, HO_SO_10_CUON_DIR, FRONTEND_DIR
)

router = APIRouter(prefix="/api/documents", tags=["Document Hub"])

def extract_from_cloud_bins(rel_path: str) -> Optional[bytes]:
    """Extract exact file bytes from cloud_docs_part1..3.bin and restore shared logo if needed."""
    norm_rel = rel_path.replace("\\", "/").lstrip("/")
    backend_dir = Path(__file__).resolve().parent.parent
    raw_bytes = None
    for idx in (1, 2, 3):
        bin_path = backend_dir / f"cloud_docs_part{idx}.bin"
        if bin_path.exists():
            try:
                with zipfile.ZipFile(bin_path, "r") as z:
                    if norm_rel in z.namelist():
                        raw_bytes = z.read(norm_rel)
                        break
                    # Fallback match by filename
                    target_name = Path(norm_rel).name.lower()
                    for name in z.namelist():
                        if Path(name).name.lower() == target_name:
                            raw_bytes = z.read(name)
                            break
                    if raw_bytes is not None:
                        break
            except Exception:
                pass

    if raw_bytes is None:
        return None

    if norm_rel.lower().endswith(".docx"):
        try:
            with zipfile.ZipFile(io.BytesIO(raw_bytes), "r") as in_z:
                needs_logo = any(
                    info.filename.startswith("word/media/") and info.file_size == 15
                    for info in in_z.infolist()
                )
                if needs_logo:
                    logo_path = FRONTEND_DIR / "img" / "logo_thien_an.png"
                    logo_bytes = logo_path.read_bytes() if logo_path.exists() else b""
                    out_buf = io.BytesIO()
                    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out_z:
                        for info in in_z.infolist():
                            data = in_z.read(info.filename)
                            if data == b"__SHARED_LOGO__" and logo_bytes:
                                data = logo_bytes
                            out_z.writestr(info.filename, data)
                    return out_buf.getvalue()
        except Exception:
            pass

    return raw_bytes

def resolve_cloud_document_path(raw_path: str, file_name: str) -> Path:
    """Resolve document file across local D: drive and Cloud bundled frontend/assets."""
    if raw_path:
        p = Path(raw_path)
        if p.exists() and p.is_file():
            return p
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists() and file_name:
        for fp in assets_dir.rglob("*"):
            if fp.is_file() and fp.name.lower() == file_name.lower():
                return fp
        # Fallback to stem match
        stem = Path(file_name).stem.lower()
        for fp in assets_dir.rglob("*"):
            if fp.is_file() and fp.stem.lower() == stem:
                return fp
    # Ultimate fallback on Cloud: All-in-One 10 Cuốn docx
    all_in_one = assets_dir / "docs_10_cuon" / "Tron_Bo_10_Cuon_Ho_So_QLCL_2429_Va_ATSH_Khoa_Xet_Nghiem_All_In_One.docx"
    if all_in_one.exists():
        return all_in_one
    return Path(raw_path or file_name)

CATEGORY_FOLDERS = {
    "phieu_kq_hen": BIEU_MAU_PHIEU_KQ,
    "so_sach_2429": BIEU_MAU_2429,
    "bia_hanh_chinh": BIEU_MAU_HANH_CHINH,
    "ho_so_10_cuon": HO_SO_10_CUON_DIR
}

@router.get("/list")
def list_documents(
    category: Optional[str] = Query(None, description="Category filter or 'all'"),
    q: Optional[str] = Query(None, description="Search keyword for name, code or description"),
    user: dict = Depends(get_current_user)
):
    """
    List documents with fast search by code or name and optional category tab filter.
    """
    conn = get_db()
    cursor = conn.cursor()

    sql = """
        SELECT d.*, u.full_name as uploader_name
        FROM documents d
        LEFT JOIN users u ON d.uploaded_by = u.id
        WHERE 1=1
    """
    params = []

    if category and category != "all":
        sql += " AND d.category = ?"
        params.append(category)

    if q and q.strip():
        search_term = f"%{q.strip().lower()}%"
        sql += " AND (VN_LOWER(d.code) LIKE ? OR VN_LOWER(d.title) LIKE ? OR VN_LOWER(d.file_name) LIKE ? OR VN_LOWER(d.description) LIKE ? OR VN_LOWER(d.category) LIKE ?)"
        params.extend([search_term, search_term, search_term, search_term, search_term])

    sql += " ORDER BY d.category ASC, d.title ASC"

    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]

    # Category counts for tabs
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM documents
        GROUP BY category
    """)
    cat_counts = {r["category"]: r["count"] for r in cursor.fetchall()}
    conn.close()

    return {
        "success": True,
        "total": len(rows),
        "documents": rows,
        "category_counts": cat_counts
    }

@router.get("/{doc_id}/download")
def download_document(
    doc_id: int,
    user: dict = Depends(get_current_user)
):
    """Download document file directly from D: drive."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    conn.close()

    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu này.")

    file_path = resolve_cloud_document_path(doc["file_path"], doc["file_name"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Tệp tin không tồn tại trên hệ thống: ({doc['file_name']})")

    # Determine media type
    media_types = {
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg"
    }
    m_type = media_types.get(doc["file_ext"].lower(), "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        filename=doc["file_name"],
        media_type=m_type
    )

@router.get("/{doc_id}/preview")
def preview_document(
    doc_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Preview document in browser (PDF, images) with inline Content-Disposition.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    conn.close()

    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")

    file_path = resolve_cloud_document_path(doc["file_path"], doc["file_name"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Tệp tin không tồn tại trên máy chủ.")

    ext = doc["file_ext"].lower()
    if ext == "pdf":
        media_type = "application/pdf"
    elif ext in ("png", "jpg", "jpeg", "webp"):
        media_type = f"image/{ext}"
    else:
        # Word or Excel can't be rendered natively in standard browsers without plugins, so trigger download
        return download_document(doc_id, user)

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={"Content-Disposition": f"inline; filename={doc['file_name']}"}
    )

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    code: Optional[str] = Form(""),
    title: str = Form(...),
    version: Optional[str] = Form("1.0"),
    description: Optional[str] = Form(""),
    admin: dict = Depends(require_admin)
):
    r"""
    Upload a new form or document version (Admin/KTV Trưởng).
    File is saved directly to D:\KHOA_XET_NGHIEM_DATA\BIEU_MAU\[category]\.
    """
    if category not in CATEGORY_FOLDERS:
        raise HTTPException(status_code=400, detail="Danh mục biểu mẫu không hợp lệ.")

    target_dir = CATEGORY_FOLDERS[category]
    target_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize file name
    orig_name = file.filename or "bieu_mau_moi"
    ext = orig_name.split(".")[-1].lower() if "." in orig_name else ""
    target_path = target_dir / orig_name

    # Write file to D: drive
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = target_path.stat().st_size

    conn = get_db()
    cursor = conn.cursor()

    # Check if a document with same filename exists in this category
    cursor.execute("""
        SELECT id FROM documents WHERE category = ? AND file_name = ?
    """, (category, orig_name))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE documents SET
                code = ?, title = ?, file_ext = ?, file_path = ?,
                file_size = ?, version = ?, description = ?,
                uploaded_by = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (code, title, ext, str(target_path), file_size, version, description, admin["id"], existing["id"]))
        doc_id = existing["id"]
        msg = f"Đã cập nhật phiên bản mới cho biểu mẫu: {title}"
    else:
        cursor.execute("""
            INSERT INTO documents (
                category, code, title, file_name, file_ext, file_path,
                file_size, version, description, uploaded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (category, code, title, orig_name, ext, str(target_path), file_size, version, description, admin["id"]))
        doc_id = cursor.lastrowid
        msg = f"Đã tải lên và lưu trữ thành công biểu mẫu: {title}"

    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'DOCUMENT_UPLOAD', ?)
    """, (admin["id"], f"Tải lên biểu mẫu #{doc_id}: {title} ({orig_name})"))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "document_id": doc_id,
        "message": msg
    }

@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    admin: dict = Depends(require_admin)
):
    """Delete a document record (Admin only)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    if not doc:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu.")

    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    cursor.execute("""
        INSERT INTO system_logs (user_id, action, details)
        VALUES (?, 'DOCUMENT_DELETE', ?)
    """, (admin["id"], f"Xóa tài liệu #{doc_id}: {doc['title']}"))

    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã xóa biểu mẫu khỏi danh mục."}

@router.post("/sync-disk")
def sync_disk_documents(admin: dict = Depends(require_admin)):
    """Re-scan D: drive folders and register any manually copied files."""
    conn = get_db()
    cursor = conn.cursor()

    added_count = 0
    for cat, folder in CATEGORY_FOLDERS.items():
        if folder.exists():
            for f in folder.iterdir():
                if f.is_file():
                    ext = f.suffix.lstrip(".").lower()
                    cursor.execute("""
                        SELECT id FROM documents WHERE category = ? AND file_name = ?
                    """, (cat, f.name))
                    if not cursor.fetchone():
                        title = f.stem.replace("_", " ")
                        cursor.execute("""
                            INSERT INTO documents (
                                category, code, title, file_name, file_ext,
                                file_path, file_size, version, description, uploaded_by
                            ) VALUES (?, '', ?, ?, ?, ?, ?, '1.0', 'Tự động quét từ ổ đĩa D', ?)
                        """, (cat, title, f.name, ext, str(f), f.stat().st_size, admin["id"]))
                        added_count += 1

    conn.commit()
    conn.close()
    return {"success": True, "message": f"Đã quét và đồng bộ thành công {added_count} tệp tin mới từ ổ D."}

from urllib.parse import quote

# Primary path on D drive (with fallbacks if user renamed or organized)
FULL_ROOT = Path(r"D:/01_TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026").resolve()
if not FULL_ROOT.exists():
    FULL_ROOT = Path(r"D:/TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026").resolve()

CATEGORIES_META = {
    "root": {
        "title": "Mục Lục & File Tổng Hợp Toàn Diện 2026",
        "badge": "00-Tổng hợp",
        "color": "sky"
    },
    "00_HUONG_DAN_VA_MUC_LUC_TRA_CUU": {
        "title": "00. Hướng Dẫn & Bảng Tra Cứu Toàn Diện",
        "badge": "00-Hướng dẫn",
        "color": "blue"
    },
    "01_HO_SO_HAT_NHAN_10_CUON_ALL_IN_ONE": {
        "title": "01. Hồ Sơ Hạt Nhân 10 Cuốn (All-in-One & Từng Cuốn)",
        "badge": "01-Hạt nhân",
        "color": "indigo"
    },
    "02_HO_SO_PHAP_LY_VA_AN_TOAN_SINH_HOC_CAP_II": {
        "title": "02. Hồ Sơ Pháp Lý & An Toàn Sinh Học Cấp II",
        "badge": "02-ATSH Cấp II",
        "color": "emerald"
    },
    "03_SO_TAY_CHAT_LUONG_VA_37_SOP_QUAN_LY_2429_ISO": {
        "title": "03. Sổ Tay Chất Lượng & 37 SOP Quản Lý (2429 & ISO)",
        "badge": "03-SOP Quản lý",
        "color": "purple"
    },
    "04_QUY_TRINH_KY_THUAT_CHUYEN_MON_117_SOP": {
        "title": "04. Hệ Thống 117 SOP Quy Trình Kỹ Thuật Chuyên Môn",
        "badge": "04-SOP Kỹ thuật",
        "color": "teal"
    },
    "05_QUAN_LY_TRANG_THIET_BI_MAY_MOC": {
        "title": "05. Quản Lý Trang Thiết Bị & Máy Móc Xét Nghiệm",
        "badge": "05-Thiết bị",
        "color": "cyan"
    },
    "06_QUAN_LY_HOA_CHAT_VAT_TU_SINH_PHAM": {
        "title": "06. Quản Lý Hóa Chất, Vật Tư Tiêu Hao & Sinh Phẩm",
        "badge": "06-Hóa chất",
        "color": "amber"
    },
    "07_KIEM_TRA_CHAT_LUONG_IQC_EQA_VERIFICATION": {
        "title": "07. Kiểm Tra Chất Lượng IQC, EQA & Xác Nhận Phương Pháp",
        "badge": "07-IQC/EQA",
        "color": "violet"
    },
    "08_SO_GHI_CHEP_VA_CHECKLIST_VAN_HANH_HANG_NGAY": {
        "title": "08. Sổ Ghi Chép & Checklist Thực Địa Hằng Ngày",
        "badge": "08-Sổ sách",
        "color": "orange"
    },
    "09_HO_SO_NHAN_SU_VA_DAO_TAO_4_CAN_BO": {
        "title": "09. Hồ Sơ Nhân Sự & Đào Tạo Cán Bộ Y Tế",
        "badge": "09-Nhân sự",
        "color": "rose"
    },
    "10_DANH_GIA_NOI_BO_XEM_XET_LANH_DAO_VA_CAPA": {
        "title": "10. Đánh Giá Nội Bộ, Xem Xét Lãnh Đạo & Báo Cáo CAPA",
        "badge": "10-CAPA",
        "color": "red"
    },
    "11_BO_BIA_MAT_BIA_GAY_CONG_VA_NHAN_DECAL_IN_SAN": {
        "title": "11. Bộ Bìa Mặt, Bìa Gáy Còng & Nhãn Decal In Sẵn",
        "badge": "11-Bìa nhãn",
        "color": "slate"
    }
}

@router.get("/full-tree")
def get_full_tree(user: dict = Depends(get_current_user)):
    """Return categorized files from D:\TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026 or Cloud manifest fallback."""
    if not FULL_ROOT.exists():
        manifest_path = Path(__file__).resolve().parent.parent / "full_tree_manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as mf:
                    return json.load(mf)
            except Exception:
                pass
        return {"success": False, "categories": [], "total_files": 0}

    tree = {}
    total_files = 0
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(FULL_ROOT):
        rel = Path(dirpath).relative_to(FULL_ROOT)
        top_cat = rel.parts[0] if rel.parts else "root"
        sub_dir = "/".join(rel.parts[1:]) if len(rel.parts) > 1 else ""

        if top_cat not in tree:
            meta = CATEGORIES_META.get(top_cat, {
                "title": top_cat.replace("_", " "),
                "badge": top_cat[:10],
                "color": "blue"
            })
            tree[top_cat] = {
                "key": top_cat,
                "title": meta["title"],
                "badge": meta["badge"],
                "color": meta["color"],
                "files": []
            }

        for fn in filenames:
            fp = Path(dirpath) / fn
            ext = fp.suffix.lower().lstrip(".")
            sz = fp.stat().st_size
            rel_file_path = str(fp.relative_to(FULL_ROOT)).replace("\\", "/")

            tree[top_cat]["files"].append({
                "name": fn,
                "sub_dir": sub_dir,
                "rel_path": rel_file_path,
                "size_kb": round(sz / 1024, 1),
                "ext": ext,
                "download_url": f"/api/documents/download-file?rel_path={quote(rel_file_path)}"
            })
            total_files += 1
            total_size += sz

    categories_list = []
    for cat_key in CATEGORIES_META.keys():
        if cat_key in tree and tree[cat_key]["files"]:
            tree[cat_key]["files"].sort(key=lambda x: x["name"])
            tree[cat_key]["count"] = len(tree[cat_key]["files"])
            categories_list.append(tree[cat_key])

    for cat_key, cat_val in tree.items():
        if cat_key not in CATEGORIES_META and cat_val["files"]:
            cat_val["files"].sort(key=lambda x: x["name"])
            cat_val["count"] = len(cat_val["files"])
            categories_list.append(cat_val)

    return {
        "success": True,
        "categories": categories_list,
        "total_files": total_files,
        "total_size_mb": round(total_size / (1024 * 1024), 1)
    }

@router.get("/download-file")
def download_full_file(rel_path: str = Query(...), user: dict = Depends(get_current_user)):
    """Safely download any file from D:\TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026 or Cloud bundled archive."""
    media_types = {
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".pdf": "application/pdf",
        ".zip": "application/zip",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg"
    }
    file_name = Path(rel_path).name
    m_type = media_types.get(Path(file_name).suffix.lower(), "application/octet-stream")

    if FULL_ROOT.exists():
        safe_path = (FULL_ROOT / rel_path).resolve()
        if str(safe_path).startswith(str(FULL_ROOT)) and safe_path.exists() and safe_path.is_file():
            return FileResponse(path=str(safe_path), filename=file_name, media_type=m_type)

    # Cloud archive extraction (all 603 files from D: drive)
    bin_bytes = extract_from_cloud_bins(rel_path)
    if bin_bytes is not None:
        encoded_name = quote(file_name)
        return Response(
            content=bin_bytes,
            media_type=m_type,
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}"}
        )

    target_path = resolve_cloud_document_path("", file_name)
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp tin")

    return FileResponse(
        path=str(target_path),
        filename=file_name,
        media_type=m_type
    )

@router.get("/preview-file")
def preview_full_file(rel_path: str = Query(...), user: dict = Depends(get_current_user)):
    """Preview PDF or text files inline from D:\TRON_BO_HO_SO_KHOA_XET_NGHIEM_TOAN_DIEN_2026 or Cloud bundled archive."""
    file_name = Path(rel_path).name
    ext = Path(file_name).suffix.lower()
    media_type = "application/pdf" if ext == ".pdf" else "text/plain; charset=utf-8"

    if FULL_ROOT.exists():
        safe_path = (FULL_ROOT / rel_path).resolve()
        if str(safe_path).startswith(str(FULL_ROOT)) and safe_path.exists() and safe_path.is_file():
            return FileResponse(path=str(safe_path), media_type=media_type)

    bin_bytes = extract_from_cloud_bins(rel_path)
    if bin_bytes is not None:
        encoded_name = quote(file_name)
        return Response(
            content=bin_bytes,
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename*=UTF-8''{encoded_name}"}
        )

    target_path = resolve_cloud_document_path("", file_name)
    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="Không tìm thấy tệp tin")

    return FileResponse(
        path=str(target_path),
        media_type=media_type
    )
