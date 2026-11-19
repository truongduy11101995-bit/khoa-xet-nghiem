import json
import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import io

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from fastapi.responses import Response, FileResponse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from backend.database import get_db, is_cloud_db
from backend.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/inventory", tags=["Kho Hóa Chất & Vật Tư"])

@router.get("/items")
def list_inventory_items(
    category: Optional[str] = Query("all", description="Filter category: hoa_chat, sinh_pham, vat_tu, all"),
    status_filter: Optional[str] = Query("all", description="Filter: all, low_stock, near_expiry, safe"),
    q: Optional[str] = Query(None, description="Search keyword"),
    user: dict = Depends(get_current_user)
):
    """
    Get inventory items with real-time stock levels, low-stock warnings, and expiry alerts.
    """
    conn = get_db()
    cursor = conn.cursor()

    sql = "SELECT * FROM inventory_items WHERE 1=1"
    params = []

    if category and category != "all":
        sql += " AND category = ?"
        params.append(category)

    if q and q.strip():
        search_term = f"%{q.strip().lower()}%"
        sql += " AND (VN_LOWER(code) LIKE ? OR VN_LOWER(name) LIKE ? OR VN_LOWER(manufacturer) LIKE ? OR VN_LOWER(lot_number) LIKE ? OR VN_LOWER(location) LIKE ?)"
        params.extend([search_term, search_term, search_term, search_term, search_term])

    sql += " ORDER BY category ASC, name ASC"

    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    today = datetime.date.today()
    low_stock_count = 0
    near_expiry_count = 0
    expired_count = 0

    enriched_items = []
    for item in rows:
        qty = float(item.get("quantity") or 0)
        min_s = float(item.get("min_stock") or 0)
        usage = float(item.get("monthly_usage") or 0)

        # Low stock check
        is_low_stock = qty <= min_s
        if is_low_stock:
            low_stock_count += 1

        # Expiry check
        exp_str = item.get("expiry_date")
        days_left = 9999
        expiry_status = "safe"

        if exp_str:
            try:
                exp_date = datetime.date.fromisoformat(exp_str)
                days_left = (exp_date - today).days
                if days_left < 0:
                    expiry_status = "expired"
                    expired_count += 1
                elif days_left <= 45:
                    expiry_status = "warning_30"
                    near_expiry_count += 1
                elif days_left <= 90:
                    expiry_status = "warning_60"
            except Exception:
                pass

        # Suggested order
        # Target stock = 1.5 months usage; suggested = target - current
        target_stock = usage * 1.5
        suggested = max(0, round(target_stock - qty, 1))

        item_enriched = {
            **item,
            "is_low_stock": is_low_stock,
            "days_left": days_left,
            "expiry_status": expiry_status,
            "suggested_order": suggested
        }

        # Status filtering
        if status_filter == "low_stock" and not is_low_stock:
            continue
        if status_filter == "near_expiry" and days_left > 45:
            continue
        if status_filter == "safe" and (is_low_stock or days_left <= 45):
            continue

        enriched_items.append(item_enriched)

    return {
        "success": True,
        "total": len(enriched_items),
        "total_unfiltered": len(rows),
        "low_stock_count": low_stock_count,
        "near_expiry_count": near_expiry_count,
        "expired_count": expired_count,
        "items": enriched_items
    }

@router.post("/items")
def add_inventory_item(
    payload: dict = Body(...),
    admin: dict = Depends(require_admin)
):
    """Add a new inventory item (Admin/Trưởng khoa/KTV trưởng)."""
    code = payload.get("code", "").strip().upper()
    name = payload.get("name", "").strip()
    category = payload.get("category", "hoa_chat")
    unit = payload.get("unit", "Hộp").strip()
    spec = payload.get("spec", "").strip()
    manufacturer = payload.get("manufacturer", "").strip()
    lot_number = payload.get("lot_number", "").strip()
    expiry_date = payload.get("expiry_date", "").strip() or None
    storage_temp = payload.get("storage_temp", "2-8°C").strip()
    quantity = float(payload.get("quantity") or 0)
    min_stock = float(payload.get("min_stock") or 0)
    monthly_usage = float(payload.get("monthly_usage") or 0)
    unit_price = float(payload.get("unit_price") or 0)
    location = payload.get("location", "").strip()
    notes = payload.get("notes", "").strip()

    if not code or not name:
        raise HTTPException(status_code=400, detail="Mã hàng và Tên mặt hàng không được để trống.")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inventory_items (
            code, name, category, unit, spec, manufacturer, lot_number,
            expiry_date, storage_temp, quantity, min_stock, monthly_usage,
            unit_price, location, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        code, name, category, unit, spec, manufacturer, lot_number,
        expiry_date, storage_temp, quantity, min_stock, monthly_usage,
        unit_price, location, notes
    ))

    conn.commit()
    conn.close()

    return {"success": True, "message": f"Đã thêm thành công mặt hàng '{name}' vào kho."}

@router.put("/items/{item_id}")
def update_inventory_item(
    item_id: int,
    payload: dict = Body(...),
    admin: dict = Depends(require_admin)
):
    """Update item details or stock count (Admin only)."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy mặt hàng này.")

    fields = [
        "name", "category", "unit", "spec", "manufacturer", "lot_number",
        "expiry_date", "storage_temp", "quantity", "min_stock", "monthly_usage",
        "unit_price", "open_date", "open_expiry_days", "location", "notes"
    ]

    set_clauses = []
    params = []
    for f in fields:
        if f in payload:
            set_clauses.append(f"{f} = ?")
            val = payload[f]
            if f in ["quantity", "min_stock", "monthly_usage", "unit_price"]:
                val = float(val or 0)
            elif f == "open_expiry_days":
                val = int(val or 0)
            elif val == "":
                val = None
            params.append(val)

    if not set_clauses:
        conn.close()
        return {"success": True, "message": "Không có thông tin thay đổi."}

    sql = f"UPDATE inventory_items SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    params.append(item_id)

    cursor.execute(sql, params)
    conn.commit()
    conn.close()

    return {"success": True, "message": "Cập nhật thông tin mặt hàng thành công."}

@router.delete("/items/{item_id}")
def delete_inventory_item(
    item_id: int,
    admin: dict = Depends(require_admin)
):
    """Delete an item from inventory (Admin only)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Đã xóa mặt hàng khỏi kho thành công."}

@router.post("/adjust-stock")
def adjust_stock(
    payload: dict = Body(...),
    admin: dict = Depends(require_admin)
):
    """
    Quick stock adjustment: Nhập kho (+) hoặc Xuất kho (-) (Admin only).
    """
    item_id = payload.get("item_id")
    action_type = payload.get("type", "xuat") # "nhap" or "xuat"
    qty_change = float(payload.get("quantity") or 0)
    reason = payload.get("reason", "").strip()

    if not item_id or qty_change <= 0:
        raise HTTPException(status_code=400, detail="Dữ liệu nhập/xuất kho không hợp lệ.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    if not item:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy mặt hàng.")

    current_qty = float(item["quantity"] or 0)
    if action_type == "xuat":
        if current_qty < qty_change:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Số lượng xuất ({qty_change}) vượt quá số lượng tồn kho hiện có ({current_qty}).")
        new_qty = current_qty - qty_change
    else:
        new_qty = current_qty + qty_change

    cursor.execute("""
        UPDATE inventory_items
        SET quantity = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_qty, item_id))

    conn.commit()
    conn.close()

    action_label = "Nhập kho" if action_type == "nhap" else "Xuất kho"
    return {
        "success": True,
        "message": f"Đã {action_label} {qty_change} {item['unit']} '{item['name']}'. Tồn mới: {new_qty} {item['unit']}."
    }

# -------------------------------------------------------------
# FORECASTS (DỰ TRÙ HÓA CHẤT, SINH PHẨM & VẬT TƯ)
# -------------------------------------------------------------
@router.get("/forecasts")
def list_forecasts(user: dict = Depends(get_current_user)):
    """List all forecast records."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, u.full_name as creator_name
        FROM inventory_forecasts f
        LEFT JOIN users u ON f.created_by = u.id
        ORDER BY f.id DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    for r in rows:
        try:
            r["items"] = json.loads(r.get("items_json") or "[]")
        except Exception:
            r["items"] = []

    return {"success": True, "forecasts": rows}

@router.post("/forecasts")
def save_forecast(
    payload: dict = Body(...),
    admin: dict = Depends(require_admin)
):
    """Save or create a new forecast plan (Admin only)."""
    period = payload.get("period", "").strip()
    title = payload.get("title", "").strip()
    items = payload.get("items", [])
    notes = payload.get("notes", "").strip()
    forecast_id = payload.get("id")

    if not period or not items:
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp kỳ dự trù và danh mục các mặt hàng.")

    if not title:
        title = f"Bảng Dự Trù Hóa Chất & Vật Tư - {period}"

    # Calculate debt for each item if provided
    for it in items:
        ord_q = float(it.get("order_qty") or 0)
        rec_q = float(it.get("received_qty") if it.get("received_qty") is not None else ord_q)
        it["received_qty"] = rec_q
        it["debt_qty"] = max(0.0, ord_q - rec_q)

    total_cost = sum(float(i.get("total_cost") or 0) for i in items)
    items_json = json.dumps(items, ensure_ascii=False)

    conn = get_db()
    cursor = conn.cursor()

    if forecast_id:
        cursor.execute("""
            UPDATE inventory_forecasts
            SET period = ?, title = ?, total_cost = ?, items_json = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (period, title, total_cost, items_json, notes, forecast_id))
    else:
        cursor.execute("""
            INSERT INTO inventory_forecasts (
                period, title, status, created_by, total_cost, items_json, notes
            ) VALUES (?, ?, 'submitted', ?, ?, ?, ?)
        """, (period, title, admin["id"], total_cost, items_json, notes))

    conn.commit()
    conn.close()

    return {"success": True, "message": f"Đã lưu thành công kế hoạch dự trù '{title}'."}

@router.post("/forecasts/resolve-debt")
def resolve_forecast_debt(
    payload: dict = Body(...),
    admin: dict = Depends(require_admin)
):
    """
    Kho Dược trả nợ hàng / phát bù sau cho Khoa Xét Nghiệm.
    Tự động cập nhật số lượng nợ trong kế hoạch dự trù và cộng trực tiếp vào tồn kho thực tế của Khoa.
    """
    forecast_id = payload.get("forecast_id")
    item_code = payload.get("item_code", "").strip()
    return_qty = float(payload.get("return_qty") or 0)
    notes = payload.get("notes", "").strip()

    if not forecast_id or not item_code or return_qty <= 0:
        raise HTTPException(status_code=400, detail="Thông tin nhận hàng bù từ Dược không hợp lệ.")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inventory_forecasts WHERE id = ?", (forecast_id,))
    fc = cursor.fetchone()
    if not fc:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy kế hoạch dự trù.")

    d_fc = dict(fc)
    try:
        items = json.loads(d_fc.get("items_json") or "[]")
    except Exception:
        items = []

    matched_item = None
    for it in items:
        if it.get("code") == item_code:
            matched_item = it
            break

    if not matched_item:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Không tìm thấy mặt hàng mã '{item_code}' trong kỳ dự trù này.")

    current_received = float(matched_item.get("received_qty") or 0)
    order_qty = float(matched_item.get("order_qty") or 0)
    new_received = current_received + return_qty
    new_debt = max(0.0, order_qty - new_received)

    matched_item["received_qty"] = new_received
    matched_item["debt_qty"] = new_debt
    today_str = datetime.date.today().strftime("%d/%m/%Y")
    new_note_entry = f"[{today_str}] Dược phát bù +{return_qty} {matched_item.get('unit', '')}"
    if notes:
        new_note_entry += f" ({notes})"
    if matched_item.get("debt_notes"):
        matched_item["debt_notes"] += " • " + new_note_entry
    else:
        matched_item["debt_notes"] = new_note_entry

    # 1. Update items_json in inventory_forecasts
    updated_items_json = json.dumps(items, ensure_ascii=False)
    cursor.execute("""
        UPDATE inventory_forecasts
        SET items_json = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (updated_items_json, forecast_id))

    # 2. Automatically add return_qty to inventory_items (Tồn kho thực tế của Khoa)
    cursor.execute("SELECT id, quantity, name, unit FROM inventory_items WHERE code = ?", (item_code,))
    stock_item = cursor.fetchone()
    if stock_item:
        new_stock_qty = float(stock_item["quantity"] or 0) + return_qty
        cursor.execute("""
            UPDATE inventory_items
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_stock_qty, stock_item["id"]))

    conn.commit()
    conn.close()

    unit_name = matched_item.get('unit', 'đơn vị')
    debt_msg = f"Còn nợ lại: {new_debt} {unit_name}" if new_debt > 0 else "ĐÃ TRẢ HẾT NỢ (ĐỦ HÀNG)"
    return {
        "success": True,
        "message": f"Đã nhận bù +{return_qty} {unit_name} '{matched_item.get('name', '')}'. {debt_msg}. Tồn kho thực tế đã tự động cộng thêm.",
        "item": matched_item
    }

@router.get("/export-excel")
def export_inventory_excel(
    category: Optional[str] = Query("all"),
    user: dict = Depends(get_current_user)
):
    """Export current inventory stock to official Excel file."""
    conn = get_db()
    cursor = conn.cursor()

    sql = "SELECT * FROM inventory_items WHERE 1=1"
    params = []
    if category and category != "all":
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY category ASC, name ASC"

    cursor.execute(sql, params)
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ton_Kho_Hien_Tai"
    ws.views.sheetView[0].showGridLines = True

    font_title = Font(name="Times New Roman", size=14, bold=True, color="1E3A8A")
    font_bold = Font(name="Times New Roman", size=10, bold=True)
    font_regular = Font(name="Times New Roman", size=10)
    font_th = Font(name="Times New Roman", size=10, bold=True, color="FFFFFF")
    fill_th = PatternFill(start_color="0369A1", end_color="0369A1", fill_type="solid")
    fill_warn = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    ws["A1"] = "BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG • KHOA XÉT NGHIỆM"
    ws["A1"].font = Font(name="Times New Roman", size=11, bold=True, color="0369A1")
    ws["A2"] = f"BÁO CÁO TỒN KHO HÓA CHẤT, SINH PHẨM & VẬT TƯ TIÊU HAO (Tính đến ngày {datetime.date.today().strftime('%d/%m/%Y')})"
    ws["A2"].font = font_title

    headers = [
        "STT", "Mã Hàng", "Tên Hóa Chất / Sinh Phẩm / Vật Tư", "Phân Loại", "Quy Cách", "ĐVT",
        "Số Lô", "Hạn Sử Dụng", "Nhiệt Độ", "Tồn Kho Hiện Có", "Định Mức Tối Thiểu", "Tiêu Hao TB", "Vị Trí Lưu Trữ", "Tình Trạng"
    ]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_idx, value=h)
        cell.font = font_th
        cell.fill = fill_th
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[4].height = 28

    today = datetime.date.today()
    cat_labels = {
        "hoa_chat": "Hóa chất",
        "sinh_pham": "Sinh phẩm/Kit",
        "vat_tu": "Vật tư tiêu hao",
        "qc_chuan": "Hóa chất QC"
    }

    cur_row = 5
    for idx, item in enumerate(items, 1):
        qty = float(item.get("quantity") or 0)
        min_s = float(item.get("min_stock") or 0)
        is_low = qty <= min_s

        exp_str = item.get("expiry_date") or ""
        status_text = "An toàn"
        if is_low:
            status_text = "Dưới định mức"

        if exp_str:
            try:
                days_left = (datetime.date.fromisoformat(exp_str) - today).days
                if days_left < 0:
                    status_text = "Đã hết hạn"
                elif days_left <= 45:
                    status_text = f"Cận date ({days_left} ngày)"
            except Exception:
                pass

        row_data = [
            idx, item["code"], item["name"], cat_labels.get(item["category"], item["category"]),
            item["spec"] or "", item["unit"], item["lot_number"] or "", exp_str,
            item["storage_temp"] or "", qty, min_s, item["monthly_usage"] or 0,
            item["location"] or "", status_text
        ]

        for col_idx, val in enumerate(row_data, 1):
            cell = ws.cell(row=cur_row, column=col_idx, value=val)
            cell.font = font_regular
            cell.border = thin_border
            if col_idx in [1, 2, 4, 6, 7, 8, 9, 14]:
                cell.alignment = Alignment(horizontal="center")
            elif col_idx in [10, 11, 12]:
                cell.alignment = Alignment(horizontal="right")
                if col_idx == 10 and is_low:
                    cell.font = Font(name="Times New Roman", size=10, bold=True, color="B91C1C")
                    cell.fill = fill_warn

        ws.row_dimensions[cur_row].height = 20
        cur_row += 1

    col_widths = {1: 6, 2: 13, 3: 36, 4: 15, 5: 14, 6: 8, 7: 12, 8: 14, 9: 14, 10: 14, 11: 15, 12: 13, 13: 20, 14: 18}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Bao_Cao_Ton_Kho_Khoa_Xet_Nghiem_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==============================================================================
# QUẢN LÝ HẠN MỞ NẮP LỌ HÓA CHẤT / SINH PHẨM (IN-USE STABILITY / OPEN-VIAL)
# ==============================================================================

@router.get("/open-vials")
def list_open_vials(
    status_filter: Optional[str] = Query("active", description="Filter: active, finished, discarded, all"),
    location: Optional[str] = Query(None, description="Filter location"),
    q: Optional[str] = Query(None, description="Search term"),
    user: dict = Depends(get_current_user)
):
    """
    Get open vials with countdown of in-use shelf life and expiry alerts.
    """
    conn = get_db()
    cursor = conn.cursor()

    sql = "SELECT * FROM open_vials WHERE 1=1"
    params = []

    if status_filter and status_filter != "all":
        sql += " AND status = ?"
        params.append(status_filter)

    if location and location.strip():
        sql += " AND location = ?"
        params.append(location.strip())

    if q and q.strip():
        search_term = f"%{q.strip().lower()}%"
        sql += " AND (VN_LOWER(item_code) LIKE ? OR VN_LOWER(item_name) LIKE ? OR VN_LOWER(lot_number) LIKE ? OR VN_LOWER(vial_label) LIKE ?)"
        params.extend([search_term, search_term, search_term, search_term])

    sql += " ORDER BY CASE WHEN status = 'active' THEN 0 ELSE 1 END, expiry_date ASC, id DESC"

    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    today = datetime.date.today()
    total_active = 0
    safe_count = 0
    warning_count = 0
    expired_count = 0

    enriched = []
    for vial in rows:
        exp_str = vial.get("expiry_date")
        open_str = vial.get("open_date")
        days_left = 999
        used_days = 0
        progress_pct = 0
        vial_status = "safe"

        stability_days = vial.get("stability_days") or 30

        try:
            exp_date = datetime.date.fromisoformat(exp_str)
            days_left = (exp_date - today).days
        except Exception:
            pass

        try:
            open_date = datetime.date.fromisoformat(open_str)
            used_days = max(0, (today - open_date).days)
            if stability_days > 0:
                progress_pct = min(100, max(0, round((used_days / stability_days) * 100)))
        except Exception:
            pass

        is_active = (vial.get("status") == "active")

        if days_left < 0:
            vial_status = "expired"
            if is_active:
                expired_count += 1
        elif days_left <= 5:
            vial_status = "warning"
            if is_active:
                warning_count += 1
        else:
            vial_status = "safe"
            if is_active:
                safe_count += 1

        if is_active:
            total_active += 1

        enriched.append({
            **vial,
            "days_left": days_left,
            "used_days": used_days,
            "progress_pct": progress_pct,
            "vial_status": vial_status
        })

    return {
        "stats": {
            "total_active": total_active,
            "safe_count": safe_count,
            "warning_count": warning_count,
            "expired_count": expired_count
        },
        "vials": enriched
    }


@router.post("/open-vials")
def create_open_vial(
    payload: Dict[str, Any] = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Register a newly opened reagent vial/kit.
    """
    item_code = payload.get("item_code", "").strip()
    item_name = payload.get("item_name", "").strip()
    lot_number = payload.get("lot_number", "").strip()
    vial_label = payload.get("vial_label", "Lọ 01").strip()
    open_date = payload.get("open_date") or datetime.date.today().strftime("%Y-%m-%d")
    open_time = payload.get("open_time") or datetime.datetime.now().strftime("%H:%M")
    location = payload.get("location", "Máy sinh hóa tự động").strip()
    notes = payload.get("notes", "").strip()

    try:
        stability_days = int(payload.get("stability_days", 30))
    except (TypeError, ValueError):
        stability_days = 30

    # Calculate in-use expiry date
    expiry_date = payload.get("expiry_date")
    if not expiry_date:
        try:
            o_date = datetime.date.fromisoformat(open_date)
            expiry_date = (o_date + datetime.timedelta(days=stability_days)).strftime("%Y-%m-%d")
        except Exception:
            expiry_date = (datetime.date.today() + datetime.timedelta(days=stability_days)).strftime("%Y-%m-%d")

    if not item_name:
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên hóa chất/sinh phẩm mở nắp!")

    opened_by = user.get("id")
    opened_by_name = user.get("full_name") or user.get("username")
    item_id = payload.get("item_id")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO open_vials (
        item_id, item_code, item_name, lot_number, vial_label,
        open_date, open_time, stability_days, expiry_date, location,
        opened_by, opened_by_name, status, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
    """, (
        item_id, item_code, item_name, lot_number, vial_label,
        open_date, open_time, stability_days, expiry_date, location,
        opened_by, opened_by_name, notes
    ))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Đã ghi nhận mở nắp lọ: {item_name} ({vial_label}) - Hạn dùng mở nắp: {expiry_date}"
    }


@router.post("/open-vials/{vial_id}/finish")
def finish_open_vial(
    vial_id: int,
    payload: Dict[str, Any] = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Mark an open vial as finished (used up) or discarded (hủy bỏ).
    """
    status_choice = payload.get("status", "finished")
    discard_reason = payload.get("discard_reason", "")

    if status_choice not in ["finished", "discarded"]:
        status_choice = "finished"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE open_vials
    SET status = ?, discard_reason = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (status_choice, discard_reason, vial_id))
    conn.commit()
    conn.close()

    action_name = "dùng hết" if status_choice == "finished" else "hủy bỏ"
    return {"success": True, "message": f"Đã chuyển trạng thái lọ sang '{action_name}'."}


@router.get("/open-vials/{vial_id}/label")
def get_vial_label(
    vial_id: int,
    user: dict = Depends(get_current_user)
):
    """
    Get printable mini sticker label data for a vial (Decision 2429/QD-BYT standard).
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM open_vials WHERE id = ?", (vial_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin lọ hóa chất!")

    vial = dict(row)
    return {
        "hospital": "BVĐK THIÊN ÂN - VIỄN ĐÔNG",
        "department": "KHOA XÉT NGHIỆM",
        "title": "TEM NHÃN MỞ NẮP HÓA CHẤT",
        "vial": vial,
        "print_date": datetime.date.today().strftime("%d/%m/%Y")
    }

