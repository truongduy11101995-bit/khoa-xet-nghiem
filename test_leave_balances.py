import urllib.request
import http.cookiejar
import json

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

login_payload = json.dumps({'username': 'le_dinh_tu', 'password': '123456'}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/auth/login', data=login_payload, headers={'Content-Type': 'application/json'})
res = opener.open(req)
print('Login status:', res.status)

bal_res = opener.open('http://localhost:8000/api/leave/balances')
bal_data = json.loads(bal_res.read().decode('utf-8'))
print('Balances success:', bal_data['success'], 'Year:', bal_data['year'])
for b in bal_data['balances']:
    print(f"- {b['full_name']} ({b['title']}): Dinh muc={b['total_entitled']} ngay, Da nghi={b['used_approved']} ngay, Con lai={b['remaining_days']} ngay")

cal_res = opener.open('http://localhost:8000/api/leave/calendar?year=2026&month=11')
cal_data = json.loads(cal_res.read().decode('utf-8'))
print('Calendar balances present:', 'balances' in cal_data)
if 'my_balance' in cal_data and cal_data['my_balance']:
    print('My balance remaining:', cal_data['my_balance']['remaining_days'], 'days')
