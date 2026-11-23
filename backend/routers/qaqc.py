import json
import time
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Body

from backend.database import get_db, is_cloud_db
from backend.auth import get_current_user

router = APIRouter(prefix="/api/qaqc", tags=["Quản lý Hiệu chuẩn, Nội kiểm & Ngoại kiểm (QA/QC)"])

STORE_KEY = "main_2026"


def _ensure_qaqc_table(cursor) -> None:
    """Ensure qaqc_store table exists on both PostgreSQL (Supabase) and SQLite."""
    if is_cloud_db():
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS qaqc_store (
            id SERIAL PRIMARY KEY,
            store_key VARCHAR(100) UNIQUE NOT NULL,
            data_json TEXT NOT NULL,
            version VARCHAR(100) NOT NULL,
            updated_by VARCHAR(255),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
    else:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS qaqc_store (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_key TEXT UNIQUE NOT NULL,
            data_json TEXT NOT NULL,
            version TEXT NOT NULL,
            updated_by TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)


@router.get("/state")
def get_qaqc_state(user: dict = Depends(get_current_user)):
    """Retrieve shared QA/QC state for the entire department."""
    conn = get_db()
    try:
        cursor = conn.cursor()
        _ensure_qaqc_table(cursor)
        conn.commit()

        cursor.execute(
            "SELECT data_json, version, updated_by, updated_at FROM qaqc_store WHERE store_key = ?",
            (STORE_KEY,)
        )
        row = cursor.fetchone()
        if not row:
            return {"exists": False, "version": None, "updated_by": None, "updated_at": None, "data": None}

        row_dict = dict(row)
        data_raw = row_dict.get("data_json")
        try:
            parsed = json.loads(data_raw)
        except Exception:
            return {"exists": False, "version": None, "updated_by": None, "updated_at": None, "data": None}

        updated_at = row_dict.get("updated_at")
        return {
            "exists": True,
            "version": row_dict.get("version"),
            "updated_by": row_dict.get("updated_by"),
            "updated_at": str(updated_at) if updated_at is not None else None,
            "data": parsed,
        }
    finally:
        conn.close()


@router.post("/state")
def save_qaqc_state(
    payload: Dict[str, Any] = Body(...),
    user: dict = Depends(get_current_user)
):
    """Save shared QA/QC state to Cloud Supabase (or local SQLite)."""
    state_obj = payload.get("data") if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict) else payload
    if not isinstance(state_obj, dict) or "parameters" not in state_obj or "eqaPrograms" not in state_obj:
        raise HTTPException(status_code=400, detail="Dữ liệu QA/QC không hợp lệ.")

    raw_json = json.dumps(state_obj, ensure_ascii=False)
    version = str(time.time_ns())
    updated_by = user.get("full_name") or user.get("username") or "Nhân viên Khoa"

    conn = get_db()
    try:
        cursor = conn.cursor()
        _ensure_qaqc_table(cursor)

        cursor.execute("SELECT id FROM qaqc_store WHERE store_key = ?", (STORE_KEY,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute(
                """
                UPDATE qaqc_store
                SET data_json = ?, version = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP
                WHERE store_key = ?
                """,
                (raw_json, version, updated_by, STORE_KEY)
            )
        else:
            cursor.execute(
                """
                INSERT INTO qaqc_store (store_key, data_json, version, updated_by)
                VALUES (?, ?, ?, ?)
                """,
                (STORE_KEY, raw_json, version, updated_by)
            )

        conn.commit()
        return {"ok": True, "version": version, "updated_by": updated_by}
    finally:
        conn.close()
