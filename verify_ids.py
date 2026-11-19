# -*- coding: utf-8 -*-
with open(r'C:/Users/TP.KHOAXETNGHIEM/.gemini/antigravity/scratch/khoa_xet_nghiem_app/frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

ids = [
    'tab-catalog',
    'view-catalog',
    'catalog-search-input',
    'catalog-binder-select',
    'btn-view-catalog-table',
    'btn-view-binders-grid',
    'catalog-table-container',
    'catalog-binders-container',
    'stat-total-docs',
    'stat-total-binders',
    'stat-total-groups',
    'catalog-group-pills',
    'catalog-binders-grid',
    'catalog-docs-tbody',
    'catalog-results-count',
    'catalog-doc-modal',
    'catalog-modal-title',
    'catalog-modal-subtitle',
    'catalog-modal-content',
    'catalog-modal-download-btn',
    'doc-tab-ho-so-10-cuon'
]

print("Checking all IDs in index.html:")
all_ok = True
for id_name in ids:
    found = f'id="{id_name}"' in html
    if not found:
        print(f"MISSING: {id_name}")
        all_ok = False
    else:
        print(f"OK: {id_name}")

print("FINAL RESULT: ALL OK?", all_ok)
