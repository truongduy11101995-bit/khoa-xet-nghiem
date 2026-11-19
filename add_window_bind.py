# -*- coding: utf-8 -*-
p = r'C:/Users/TP.KHOAXETNGHIEM/.gemini/antigravity/scratch/khoa_xet_nghiem_app/frontend/js/catalog_data.js'
with open(p, 'a', encoding='utf-8') as f:
    f.write('''
if (typeof window !== 'undefined') {
    window.CATALOG_BINDERS = CATALOG_BINDERS;
    window.CATALOG_GROUPS = CATALOG_GROUPS;
    window.CATALOG_DOCUMENTS = CATALOG_DOCUMENTS;
}
''')
print('Appended window bindings to catalog_data.js')
