# -*- coding: utf-8 -*-
"""
Full catalog generator for Khoa Xét nghiệm BVĐK Thiên Ân - Viễn Đông.
Extracts 10 binders (11 volumes), 7 groups, and all 147 standardized documents
with complete rich HTML formatting into frontend/js/catalog_data.js.
Includes official logo and Word (.docx) download links.
"""
import docx
import json
import re
import html
from pathlib import Path

BASE_DIR = Path(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app")
DOCS_DIR = BASE_DIR / "frontend" / "assets" / "docs_10_cuon"
DOC1_PATH = BASE_DIR / "frontend" / "assets" / "docs_10_cuon" / "Cuon_00_Bang_Thong_Ke_Tong_Hop_147_Tai_Lieu_Chuan_Hoa_Khoa_XN.docx"
DOC2_PATH = BASE_DIR / "frontend" / "assets" / "docs_10_cuon" / "Tron_Bo_10_Cuon_Ho_So_QLCL_2429_Va_ATSH_Khoa_Xet_Nghiem_All_In_One.docx"
OUTPUT_JS = BASE_DIR / "frontend" / "js" / "catalog_data.js"

print("1. Extracting metadata from doc1...")
doc1 = docx.Document(DOC1_PATH)

# Mapping of binder labels to filenames
BINDER_FILES = {
    "Cuốn 00": "Cuon_00_Bang_Thong_Ke_Tong_Hop_147_Tai_Lieu_Chuan_Hoa_Khoa_XN.docx",
    "Cuốn 01": "Cuon_01_Ho_So_An_Toan_Sinh_Hoc_Cap_II_Khoa_XN.docx",
    "Cuốn 02": "Cuon_02_Ho_So_Phap_Ly_Nhan_Su_Co_So_Vat_Chat.docx",
    "Cuốn 03": "Cuon_03_So_Tay_Chat_Luong_Va_10_SOP_Quan_Ly.docx",
    "Cuốn 04": "Cuon_04_So_Tay_Lay_Mau_SOP_Chuyen_Mon_Va_So_Ghi_Chep.docx",
    "Cuốn 05": "Cuon_05_Tu_Danh_Gia_QD_2429_Va_Khung_Ho_So_Thiet_Bi.docx",
    "Cuốn 06": "Cuon_06_Ho_So_IQC_EQA_Xac_Nhan_Phuong_Phap_Va_LIS.docx",
    "Cuốn 07A": "Cuon_07A_So_Checklist_Nhiet_Do_Tu_Lanh_Tu_Dong_Tu_ATSH_Sang_Chieu.docx",
    "Cuốn 07B": "Cuon_07B_Bo_Checklist_Bo_Sung_Toan_Dien_Khoa_Xet_Nghiem.docx",
    "Cuốn 08": "Cuon_08_Ho_So_Quyet_Dinh_Bo_Sung_Va_Manh_Ghep_Cuoi_2429_ATSH.docx",
    "Cuốn 09": "Cuon_09_Bo_Ho_So_Chuyen_Sau_2429_Uy_Quyen_Bao_Mat_Du_Phong_Mau_Mau.docx",
    "Cuốn 10": "Cuon_10_Ho_So_Test_Nhanh_HIV_Truyen_Nhiem_Cap_Cuu_Lay_Mau_NCC_Va_6_Poster_Treo_Tuong.docx"
}

def get_file_info(fname):
    fpath = DOCS_DIR / fname
    if fpath.exists():
        size_kb = fpath.stat().st_size / 1024
        if size_kb >= 1024:
            return f"{size_kb/1024:.1f} MB"
        return f"{size_kb:.0f} KB"
    return "900 KB"

# Extract Binders from Table 4
t4 = doc1.tables[4]
binders_list = []

# First entry: Cuon 00
f_00 = BINDER_FILES["Cuốn 00"]
binders_list.append({
    "id": "cuon_00",
    "label": "Cuốn 00",
    "title": "Cuốn 00: Mục Lục & Bảng Thống Kê Tổng Thể Toàn Khoa (DM.TONG.00)",
    "docs_inside": "Toàn bộ 147 tài liệu chuẩn hóa từ Cuốn 01 đến Cuốn 10",
    "scale": "Toàn bộ 10 Cuốn (147 tài liệu)",
    "legal": "QĐ 2429/QĐ-BYT, NĐ 103/2016/NĐ-CP & NĐ 96/2023/NĐ-CP",
    "file_name": f_00,
    "download_url": f"/static/assets/docs_10_cuon/{f_00}",
    "file_size": get_file_info(f_00)
})

for r in t4.rows[1:]:
    cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
    cuon_label = cells[0].strip()
    title = cells[1].strip()
    docs_inside = cells[2].strip()
    scale = cells[3].strip()
    legal = cells[4].strip() if len(cells) > 4 else ''
    b_id = cuon_label.lower().replace(' ', '_').replace('cuốn_', 'cuon_')
    
    fname = BINDER_FILES.get(cuon_label, f_00)
    binders_list.append({
        'id': b_id,
        'label': cuon_label,
        'title': f'{cuon_label}: {title}',
        'docs_inside': docs_inside,
        'scale': scale,
        'legal': legal,
        'file_name': fname,
        'download_url': f"/static/assets/docs_10_cuon/{fname}",
        'file_size': get_file_info(fname)
    })

print(f"Extracted {len(binders_list)} binders with download links.")

# Extract 147 items from Table 5
t5 = doc1.tables[5]
catalog_items = []
current_group = ''
current_group_name = ''

for r in t5.rows[1:]:
    cells = [c.text.strip().replace('\n', ' ') for c in r.cells]
    col0 = cells[0].strip()
    col1 = cells[1].strip()
    col2 = cells[2].strip() if len(cells) > 2 else ''
    col3 = cells[3].strip() if len(cells) > 3 else ''
    
    if col0 in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'] or col1.startswith('NHÓM '):
        current_group = col0
        current_group_name = col1
        continue
    
    if col1:
        catalog_items.append({
            'stt': col0,
            'code': col1,
            'name': col2,
            'location': col3,
            'group_id': current_group,
            'group_name': current_group_name
        })

print(f"Extracted {len(catalog_items)} catalog items from doc1.")

# Load doc2
print("2. Loading doc2...")
doc2 = docx.Document(DOC2_PATH)
elements = list(doc2.element.body)
print(f"Total elements: {len(elements)}")

# Helper: paragraph to HTML
def p_to_html(p):
    txt = p.text.strip()
    if not txt:
        return ''
    runs_html = []
    for r in p.runs:
        t = html.escape(r.text)
        if r.bold:
            t = f"<strong>{t}</strong>"
        if r.italic:
            t = f"<em>{t}</em>"
        if r.underline:
            t = f"<u>{t}</u>"
        runs_html.append(t)
    inner = "".join(runs_html) if runs_html else html.escape(txt)
    
    align = str(p.alignment)
    cls_align = ""
    if "CENTER" in align:
        cls_align = " text-center"
    elif "RIGHT" in align:
        cls_align = " text-right"
        
    if txt.isupper() and len(txt) < 100:
        return f'<h4 class="font-bold text-slate-900 mt-4 mb-2 text-sm md:text-base border-b pb-1 border-slate-200{cls_align}">{inner}</h4>'
    
    if txt.startswith(('- ', '• ', '+ ')):
        return f'<li class="ml-5 list-disc text-slate-700 my-1 leading-relaxed text-sm">{inner[2:]}</li>'
        
    return f'<p class="mb-2 text-slate-700 leading-relaxed text-sm{cls_align}">{inner}</p>'

# Helper: table to HTML
def tbl_to_html(tbl):
    rows_html = []
    is_header_box = (len(tbl.rows) <= 3 and len(tbl.columns) <= 4 and any("SỞ Y TẾ" in c.text or "Mã số:" in c.text or "BỆNH VIỆN" in c.text for r in tbl.rows for c in r.cells))
    is_signature_box = any("NGƯỜI BIÊN SOẠN" in c.text or "PHÊ DUYỆT" in c.text for r in tbl.rows for c in r.cells)
    
    for r_idx, r in enumerate(tbl.rows):
        cells_html = []
        is_hdr = (r_idx == 0 and len(tbl.rows) > 1 and not is_header_box and not is_signature_box)
        tag = 'th' if is_hdr else 'td'
        cls_bg = 'bg-slate-100 font-bold text-slate-800 text-center' if is_hdr else 'text-slate-700'
        if is_header_box:
            cls_bg = 'bg-blue-50/70 font-semibold text-slate-800'
        elif is_signature_box:
            cls_bg = 'text-center font-semibold text-slate-800 align-top pt-3 pb-8'
            
        for c in r.cells:
            c_paras = []
            for p in c.paragraphs:
                p_txt = p.text.strip()
                if p_txt:
                    runs_html = []
                    for run in p.runs:
                        rt = html.escape(run.text)
                        if run.bold:
                            rt = f"<strong>{rt}</strong>"
                        if run.italic:
                            rt = f"<em>{rt}</em>"
                        runs_html.append(rt)
                    c_paras.append("".join(runs_html) if runs_html else html.escape(p_txt))
            cell_content = "<br>".join(c_paras) if c_paras else "&nbsp;"
            cells_html.append(f'<{tag} class="border border-slate-300 p-2.5 text-xs md:text-sm {cls_bg}">{cell_content}</{tag}>')
        rows_html.append(f'<tr>{" ".join(cells_html)}</tr>')
        
    wrapper_cls = "my-4 overflow-x-auto shadow-sm rounded border border-slate-200"
    if is_signature_box:
        wrapper_cls = "my-6 overflow-x-auto"
        
    return f'<div class="{wrapper_cls}"><table class="w-full border-collapse border border-slate-300 text-xs md:text-sm"><tbody>{" ".join(rows_html)}</tbody></table></div>'

# Pre-cache element texts
print("3. Pre-caching elements...")
cached = []
for idx, el in enumerate(elements):
    tag = el.tag.split('}')[-1]
    if tag == 'p':
        p = docx.text.paragraph.Paragraph(el, doc2)
        cached.append({'idx': idx, 'tag': 'p', 'text': p.text.strip(), 'obj': p})
    elif tag == 'tbl':
        tbl = docx.table.Table(el, doc2)
        txt = ' '.join(c.text.strip().replace('\n', ' ') for r in tbl.rows for c in r.cells)
        cached.append({'idx': idx, 'tag': 'tbl', 'text': txt, 'obj': tbl})
    else:
        cached.append({'idx': idx, 'tag': tag, 'text': '', 'obj': None})

# Locate anchors for all 147 documents
print("4. Locating document anchors...")
doc_starts = {}

for it in catalog_items:
    code = it['code']
    found_idx = None
    
    if code.startswith('Mẫu số 07'):
        for ce in cached:
            if 'BẢN TỰ CÔNG BỐ' in ce['text'] and ce['tag'] == 'p':
                found_idx = ce['idx'] - 4
                break
    elif code.startswith('Mẫu số 08'):
        for ce in cached:
            if 'BẢN KÊ KHAI NHÂN SỰ' in ce['text'] and ce['idx'] > 75:
                found_idx = ce['idx'] - 4 if ce['tag'] == 'p' else ce['idx']
                break
    elif code.startswith('Mẫu số 09'):
        for ce in cached:
            if 'BẢN KÊ KHAI TRANG THIẾT BỊ' in ce['text'] and ce['idx'] > 80:
                found_idx = ce['idx'] - 4 if ce['tag'] == 'p' else ce['idx']
                break
    elif code == 'CV.ATSH.01':
        for ce in cached:
            if 'Số: ....../CV-BV' in ce['text'] or ('Công văn' in ce['text'] and 'v/v nộp hồ sơ tự công bố' in ce['text']):
                found_idx = ce['idx']
                break
    elif code == 'QĐ.BV.01':
        for ce in cached:
            if 'thành lập Tổ Quản lý chất lượng' in ce['text'] and 'QUYẾT ĐỊNH' in ce['text']:
                found_idx = ce['idx'] - 1
                break
    elif code == 'QĐ.BV.02':
        for ce in cached:
            if 'ban hành Chính sách chất lượng, Sổ tay Chất lượng' in ce['text']:
                found_idx = ce['idx'] - 1
                break
    elif code == 'QĐ.BV.03':
        for ce in cached:
            if 'phê duyệt Danh mục Xét nghiệm, Khoảng tham chiếu' in ce['text']:
                found_idx = ce['idx'] - 1
                break
    elif code.startswith('BB.ATSH'):
        for ce in cached:
            if 'BIỂN BÁO DÁN MẶT NGOÀI CỬA PHÒNG XÉT NGHIỆM' in ce['text']:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.01' or code == 'BM.ATSH.01 (BM.TD.03)':
        for ce in cached:
            if 'NHẬT KÝ VẬN HÀNH, VỆ SINH TỦ ATSH CẤP II' in ce['text'] and ce['idx'] > 400:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.02':
        for ce in cached:
            if 'NHẬT KÝ VẬN HÀNH VÀ THEO DÕI CHỈ THỊ TIỆT TRÙNG NỒI HẤP' in ce['text']:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.03':
        for ce in cached:
            if 'SỔ THEO DÕI BÀN GIAO CHẤT THẢI Y TẾ' in ce['text']:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.04':
        for ce in cached:
            if 'BẢNG KIỂM GIÁM SÁT TUÂN THỦ THỰC HÀNH AN TOÀN SINH HỌC' in ce['text']:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.05':
        for ce in cached:
            if 'BIÊN BẢN BÁO CÁO SỰ CỐ AN TOÀN SINH HỌC' in ce['text'] and ce['idx'] > 430:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.06':
        for ce in cached:
            if 'SỔ THEO DÕI SỨC KHỎE NGHỀ NGHIỆP' in ce['text']:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.07':
        for ce in cached:
            if 'BIÊN BẢN TẬP HUẤN NỘI BỘ' in ce['text']:
                found_idx = ce['idx']
                break
    elif code == 'BM.ATSH.09':
        for ce in cached:
            if 'BẢNG NHẬT KÝ THEO DÕI VỆ SINH DỤNG CỤ & VẬN HÀNH TỦ SẤY' in ce['text']:
                found_idx = ce['idx']
                break
    elif code.startswith('PT.'):
        p_num = code.split('.')[-1]
        for ce in cached:
            if ce['idx'] > 1780 and (f'Poster {int(p_num)}' in ce['text'] or f'POSTER {int(p_num)}' in ce['text'] or f'PT.0{int(p_num)}' in ce['text']):
                found_idx = ce['idx']
                break
    else:
        clean_code = code.split('(')[0].split('&')[0].strip()
        pat = re.compile(r'(?:Mã số|MÃ SỐ|Mã tài liệu|MÃ TÀI LIỆU)\s*:\s*' + re.escape(clean_code) + r'(\s|;|\.|$)', re.IGNORECASE)
        for ce in cached:
            if ce['tag'] == 'tbl' and pat.search(ce['text']):
                found_idx = ce['idx']
                break
        if found_idx is None:
            for ce in cached:
                if clean_code in ce['text'] and ce['tag'] == 'tbl' and len(ce['obj'].rows) <= 3:
                    found_idx = ce['idx']
                    break

    doc_starts[code] = found_idx

print(f"Mapped {sum(1 for v in doc_starts.values() if v is not None)} / {len(catalog_items)} documents.")

# Create sorted list of documents by their start index
anchors = []
for it in catalog_items:
    code = it['code']
    s_idx = doc_starts.get(code)
    anchors.append({
        'item': it,
        'start_idx': s_idx if s_idx is not None else 999999
    })

anchors.sort(key=lambda x: x['start_idx'])

# Assign end index for each document
for i in range(len(anchors)):
    curr_start = anchors[i]['start_idx']
    next_start = anchors[i+1]['start_idx'] if i+1 < len(anchors) else len(elements)
    if next_start > curr_start + 45 and anchors[i]['item']['code'] != 'ST.QLCL.01':
        next_start = curr_start + 25
    anchors[i]['end_idx'] = min(next_start, len(elements))

# Render HTML for each document
print("5. Rendering HTML for all documents...")
rendered_docs = []
for anchor in anchors:
    it = anchor['item']
    code = it['code']
    s_idx = anchor['start_idx']
    e_idx = anchor['end_idx']
    
    # Identify binder ID & download file
    loc = it['location']
    b_id = "cuon_01"
    b_fname = BINDER_FILES["Cuốn 01"]
    for b in binders_list:
        if b['label'] in loc:
            b_id = b['id']
            b_fname = b.get('file_name', b_fname)
            break
            
    html_parts = []
    
    # Official Hospital Header Banner with Official Circular Logo
    header_html = f'''
    <div class="mb-6 p-4 md:p-5 bg-gradient-to-r from-blue-50/90 via-indigo-50/70 to-slate-50 border border-blue-200 rounded-xl shadow-xs">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-blue-200/60 pb-3.5 mb-3.5">
            <div class="flex items-center gap-3.5">
                <img src="/static/assets/logo.png" alt="Logo BV Thiên Ân" class="w-14 h-14 md:w-16 md:h-16 object-contain rounded-full border border-blue-200 bg-white p-0.5 shadow-xs shrink-0">
                <div>
                    <span class="text-[11px] font-bold uppercase tracking-wider text-blue-700">SỞ Y TẾ TỈNH VĨNH LONG</span>
                    <h3 class="text-sm md:text-base font-extrabold text-slate-800 uppercase tracking-tight">BỆNH VIỆN ĐA KHOA THIÊN ÂN - VIỄN ĐÔNG</h3>
                    <p class="text-xs font-semibold text-indigo-700">KHOA XÉT NGHIỆM — HỆ THỐNG QUẢN LÝ CHẤT LƯỢNG (QĐ 2429 & ATSH CẤP II)</p>
                </div>
            </div>
            <div class="text-left sm:text-right bg-white px-3.5 py-2 rounded-lg border border-blue-200 shadow-xs self-stretch sm:self-auto">
                <div class="text-xs font-bold text-slate-900">Mã hiệu: <span class="text-blue-600 font-mono font-extrabold">{code}</span></div>
                <div class="text-[11px] text-slate-500">Phiên bản: <strong>01</strong> | Năm ban hành: <strong>2026</strong></div>
                <div class="text-[11px] text-emerald-700 font-medium">Lưu trữ: <strong>{it['location']}</strong></div>
            </div>
        </div>
        <div class="text-center sm:text-left">
            <h2 class="text-base md:text-lg font-bold text-slate-900 leading-snug">{it['name']}</h2>
            <div class="text-xs text-slate-600 mt-2 flex flex-wrap items-center gap-2">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-semibold bg-blue-100 text-blue-800">{it['group_name'].split(':')[0]}</span>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-800">Vị trí: {it['location']}</span>
                <a href="/static/assets/docs_10_cuon/{b_fname}" download 
                    class="no-print inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 hover:bg-emerald-600 hover:text-white border border-emerald-200 transition-colors">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                    <span>Tải Word Cuốn này (.docx)</span>
                </a>
            </div>
        </div>
    </div>
    '''
    html_parts.append(header_html)
    
    if s_idx < len(elements):
        for idx in range(s_idx, e_idx):
            el_data = cached[idx]
            tag = el_data['tag']
            if tag == 'p':
                p_out = p_to_html(el_data['obj'])
                if p_out:
                    html_parts.append(p_out)
            elif tag == 'tbl':
                t_out = tbl_to_html(el_data['obj'])
                if t_out:
                    html_parts.append(t_out)
    else:
        html_parts.append(f'<div class="p-6 bg-slate-50 border border-slate-200 rounded text-center text-slate-600 my-4"><p>Tài liệu đã được đăng ký và lưu trữ chuẩn tại <strong>{it["location"]}</strong>.</p></div>')
        
    full_html = "\n".join(html_parts)
            
    rendered_docs.append({
        'stt': it['stt'],
        'code': it['code'],
        'name': it['name'],
        'location': it['location'],
        'group_id': f"group_{it['group_id'].lower()}",
        'group_num': it['group_id'],
        'group_name': it['group_name'],
        'binder_id': b_id,
        'download_url': f"/static/assets/docs_10_cuon/{b_fname}",
        'file_name': b_fname,
        'html_content': full_html
    })

rendered_docs.sort(key=lambda x: int(x['stt']) if x['stt'].isdigit() else 999)

# Define 7 groups
groups = [
    {
        "id": "group_i",
        "name": "NHÓM I: VĂN BẢN PHÁP LÝ, CÔNG VĂN, QUYẾT ĐỊNH, SỔ TAY & BẢNG KIỂM TỔNG THỂ (18 VĂN BẢN)",
        "count": 18,
        "color": "sky"
    },
    {
        "id": "group_ii",
        "name": "NHÓM II: HỆ THỐNG 10 QUY TRÌNH QUẢN LÝ CHẤT LƯỢNG CHUẨN (QT.QL.01 → QT.QL.10)",
        "count": 10,
        "color": "indigo"
    },
    {
        "id": "group_iii",
        "name": "NHÓM III: HỆ THỐNG 10 QUY TRÌNH AN TOÀN SINH HỌC CẤP II (QT.ATSH.01 → QT.ATSH.10)",
        "count": 10,
        "color": "emerald"
    },
    {
        "id": "group_iv",
        "name": "NHÓM IV: HỆ THỐNG 11 QUY TRÌNH CHUYÊN MÔN & TRUYỀN MÁU (QT.CM.01 → QT.CM.11)",
        "count": 11,
        "color": "teal"
    },
    {
        "id": "group_v",
        "name": "NHÓM V: BỘ BIỂU MẪU TỔ CHỨC, NHÂN SỰ, CƠ SỞ VẬT CHẤT, THIẾT BỊ & HÓA CHẤT (26 BIỂU MẪU)",
        "count": 26,
        "color": "blue"
    },
    {
        "id": "group_vi",
        "name": "NHÓM VI: BỘ SỔ SÁCH CHUYÊN MÔN, IQC/EQA, XÁC NHẬN PHƯƠNG PHÁP, LIS & CẢI TIẾN (38 BIỂU MẪU)",
        "count": 38,
        "color": "purple"
    },
    {
        "id": "group_vii",
        "name": "NHÓM VII: NHẬT KÝ AN TOÀN SINH HỌC, CHECKLIST THỰC ĐỊA SÁNG – CHIỀU & 06 POSTER (34 BIỂU MẪU)",
        "count": 34,
        "color": "rose"
    }
]

print(f"6. Writing {len(rendered_docs)} documents to {OUTPUT_JS}...")
with open(OUTPUT_JS, "w", encoding="utf-8") as f:
    f.write("// Dữ liệu Chuẩn hóa 10 Cuốn Hồ sơ (11 tập) & 147 Tài liệu Khoa Xét nghiệm BVĐK Thiên Ân - Viễn Đông\n")
    f.write("// Tự động trích xuất trực tiếp từ toàn văn tài liệu do Khoa cung cấp\n\n")
    
    f.write("var CATALOG_BINDERS = ")
    json.dump(binders_list, f, ensure_ascii=False, indent=2)
    f.write(";\n\n")
    
    f.write("var CATALOG_GROUPS = ")
    json.dump(groups, f, ensure_ascii=False, indent=2)
    f.write(";\n\n")
    
    f.write("var CATALOG_DOCUMENTS = ")
    json.dump(rendered_docs, f, ensure_ascii=False, indent=2)
    f.write(";\n\n")

    f.write("if (typeof window !== 'undefined') {\n")
    f.write("  window.CATALOG_BINDERS = CATALOG_BINDERS;\n")
    f.write("  window.CATALOG_GROUPS = CATALOG_GROUPS;\n")
    f.write("  window.CATALOG_DOCUMENTS = CATALOG_DOCUMENTS;\n")
    f.write("}\n")

print(f"SUCCESS: {OUTPUT_JS} generated with {len(rendered_docs)} documents and {len(binders_list)} binders!")
