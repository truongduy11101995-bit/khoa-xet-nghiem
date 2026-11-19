@echo off
title Khoa Xet Nghiem - BV Thien An Vien Dong
cd /d "C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app"

:: Kiem tra neu cong 8000 chua chay thi bat server ngam
netstat -ano | findstr 8000 | findstr LISTENING >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    start "" "C:\Users\TP.KHOAXETNGHIEM\AppData\Local\Programs\Python\Python312\pythonw.exe" "C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\run_server_background.py"
    ping 127.0.0.1 -n 2 >nul
)

:: Mo trinh duyet
start http://localhost:8000
