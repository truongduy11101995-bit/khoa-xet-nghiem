# -*- coding: utf-8 -*-
"""
Script to map each of the 147 items in catalog_items.json to its start index in doc2.
"""
import docx
import json
import re

doc2_path = r'C:/Users/TP.KHOAXETNGHIEM/.gemini/antigravity/brain/ec858f40-8ee4-4084-9f9c-133ae0c4cb71/.user_uploaded/media_1794810464243_47657a91.docx'
doc2 = docx.Document(doc2_path)
elements = list(doc2.element.body)

with open('catalog_items.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

# Pre-extract text of all elements
cached_elements = []
for idx, el in enumerate(elements):
    tag = el.tag.split('}')[-1]
    if tag == 'p':
        p = docx.text.paragraph.Paragraph(el, doc2)
        cached_elements.append({
            'idx': idx,
            'tag': 'p',
            'text': p.text.strip(),
            'obj': p
        })
    elif tag == 'tbl':
        tbl = docx.table.Table(el, doc2)
        txt = ' '.join(c.text.strip().replace('\n', ' ') for r in tbl.rows for c in r.cells)
        cached_elements.append({
            'idx': idx,
            'tag': 'tbl',
            'text': txt,
            'rows': len(tbl.rows),
            'cols': len(tbl.columns),
            'obj': tbl
        })
    else:
        cached_elements.append({'idx': idx, 'tag': tag, 'text': '', 'obj': None})

print(f"Pre-extracted {len(cached_elements)} elements.")

# Mapping logic
doc_starts = {}

for it in items:
    code = it['code']
    name = it['name']
    
    # Clean code variants for searching
    search_codes = [code]
    if '(' in code:
        # e.g., 'BM.ATSH.01 (BM.TD.03)' -> ['BM.ATSH.01', 'BM.TD.03']
        parts = re.findall(r'[A-Za-z0-9\._\-]+', code)
        search_codes.extend(parts)
    if '&' in code:
        # e.g., 'BM.TD.04-1 & 04-2' -> ['BM.TD.04-1', 'BM.TD.04-2']
        search_codes.extend(['BM.TD.04-1', 'BM.TD.04-2'])
        
    found_idx = None
    
    # Priority 1: Table with 'Mã số: <code>' or 'Mã tài liệu: <code>'
    for sc in search_codes:
        pat = re.compile(r'(?:Mã số|MÃ SỐ|Mã tài liệu|MÃ TÀI LIỆU)\s*:\s*' + re.escape(sc) + r'(\s|;|\.|$)', re.IGNORECASE)
        for ce in cached_elements:
            if ce['tag'] == 'tbl' and pat.search(ce['text']):
                found_idx = ce['idx']
                break
        if found_idx is not None:
            break
            
    # Priority 2: Mẫu số or Decision or Poster
    if found_idx is None:
        if code.startswith('Mẫu số 07'):
            # Look for 'BẢN TỰ CÔNG BỐ'
            for ce in cached_elements:
                if 'BẢN TỰ CÔNG BỐ' in ce['text'] and ce['tag'] == 'p':
                    found_idx = ce['idx'] - 4 # start at CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
                    break
        elif code.startswith('Mẫu số 08'):
            for ce in cached_elements:
                if 'BẢN KÊ KHAI NHÂN SỰ' in ce['text'] or 'Mẫu số 08' in ce['text']:
                    if ce['idx'] > 75 and ce['tag'] in ['p', 'tbl']:
                        found_idx = ce['idx']
                        break
        elif code.startswith('Mẫu số 09'):
            for ce in cached_elements:
                if ('BẢN KÊ KHAI TRANG THIẾT BỊ' in ce['text'] or 'Mẫu số 09' in ce['text']) and ce['idx'] > 80:
                    found_idx = ce['idx']
                    break
        elif code == 'CV.ATSH.01':
            for ce in cached_elements:
                if 'Số: ....../CV-BV' in ce['text'] or 'v/v nộp hồ sơ tự công bố' in ce['text']:
                    found_idx = ce['idx']
                    break
        elif code == 'QĐ.BV.01':
            for ce in cached_elements:
                if 'thành lập Tổ Quản lý chất lượng' in ce['text'] and 'QUYẾT ĐỊNH' in ce['text']:
                    found_idx = ce['idx'] - 1 if ce['idx'] > 0 else ce['idx']
                    break
        elif code == 'QĐ.BV.02':
            for ce in cached_elements:
                if 'ban hành Chính sách chất lượng, Sổ tay Chất lượng' in ce['text']:
                    found_idx = ce['idx'] - 1 if ce['idx'] > 0 else ce['idx']
                    break
        elif code == 'QĐ.BV.03':
            for ce in cached_elements:
                if 'phê duyệt Danh mục Xét nghiệm, Khoảng tham chiếu' in ce['text']:
                    found_idx = ce['idx'] - 1 if ce['idx'] > 0 else ce['idx']
                    break
        elif code.startswith('PT.'):
            # Posters PT.01 -> PT.06
            poster_num = code.split('.')[-1]
            for ce in cached_elements:
                if f'PT.{poster_num}' in ce['text'] or f'Poster {int(poster_num)}' in ce['text'] or (f'POSTER {int(poster_num)}' in ce['text']):
                    if ce['idx'] > 1780:
                        found_idx = ce['idx']
                        break
        elif code.startswith('BB.ATSH'):
            for ce in cached_elements:
                if 'BIỂN BÁO' in ce['text'] and 'NGUY HIỂM SINH HỌC' in ce['text'] and ce['idx'] > 150:
                    found_idx = ce['idx']
                    break
        elif code == 'BM.BS.10':
            for ce in cached_elements:
                if 'BM.BS.10' in ce['text'] and ce['idx'] > 1250:
                    found_idx = ce['idx']
                    break

    doc_starts[code] = found_idx

print(f"\nResults: {sum(1 for v in doc_starts.values() if v is not None)} / {len(items)} found.")
missing = [c for c, v in doc_starts.items() if v is None]
print("Missing:", missing)

with open('detected_starts.json', 'w', encoding='utf-8') as f:
    json.dump(doc_starts, f, ensure_ascii=False, indent=2)
