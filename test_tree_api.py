# -*- coding: utf-8 -*-
import urllib.request
import json

# Login
req = urllib.request.Request('http://localhost:8000/api/auth/login', 
    data=json.dumps({'username': 'le_dinh_tu', 'password': '123456'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'})
res = urllib.request.urlopen(req)
cookie = res.headers.get('Set-Cookie')

# Query full-tree
req_tree = urllib.request.Request('http://localhost:8000/api/documents/full-tree', headers={'Cookie': cookie})
res_tree = urllib.request.urlopen(req_tree)
data = json.loads(res_tree.read().decode('utf-8'))
print('Success:', data['success'])
print('Total files:', data['total_files'], '| Total size:', data['total_size_mb'], 'MB')
print('Categories count:', len(data['categories']))
for c in data['categories']:
    print(f" - {c['title']}: {c['count']} tệp tin")
