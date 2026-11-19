# -*- coding: utf-8 -*-
with open(r'C:/Users/TP.KHOAXETNGHIEM/.gemini/antigravity/scratch/khoa_xet_nghiem_app/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

m3_ids = [
    'doc-search-input',
    'documents-list-container',
    'doc-tab-all', 'doc-count-all',
    'doc-tab-phieu-kq', 'doc-count-phieu-kq',
    'doc-tab-so-sach-2429', 'doc-count-so-sach-2429',
    'doc-tab-bia-hc', 'doc-count-bia-hc',
    'doc-tab-ho-so-10-cuon', 'doc-count-ho-so-10-cuon',
    'modal-upload-document',
    'modal-preview-document',
    'preview-iframe',
    'preview-doc-title',
    'preview-download-btn'
]

print("Checking Module 3 IDs in index.html:")
all_ok = True
for id_name in m3_ids:
    found = f'id="{id_name}"' in html
    if not found:
        print(f"MISSING: {id_name}")
        all_ok = False
    else:
        print(f"OK: {id_name}")

print("MODULE 3 ALL OK?", all_ok)
