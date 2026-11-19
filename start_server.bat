@echo off
chcp 65001 >nul
title KHOA XET NGHIEM - BVDK THIEN AN VIEN DONG - LOCAL SERVER

echo =========================================================================
echo   SO Y TE TINH VINH LONG - BENH VIEN DA KHOA THIEN AN - VIEN DONG
echo   HE THONG QUAN LY NOI BO KHOA XET NGHIEM (QD 2429/QD-BYT)
echo =========================================================================
echo.

:: 1. Kiem tra va tao thu muc tren o D:
echo [*] Kiem tra o dia D: va kho du lieu D:\KHOA_XET_NGHIEM_DATA\ ...
if exist D:\ (
    if not exist "D:\KHOA_XET_NGHIEM_DATA\DATABASE" mkdir "D:\KHOA_XET_NGHIEM_DATA\DATABASE"
    if not exist "D:\KHOA_XET_NGHIEM_DATA\BIEU_MAU\Phieu_KQ_Phieu_Hen" mkdir "D:\KHOA_XET_NGHIEM_DATA\BIEU_MAU\Phieu_KQ_Phieu_Hen"
    if not exist "D:\KHOA_XET_NGHIEM_DATA\BIEU_MAU\So_Sach_2429" mkdir "D:\KHOA_XET_NGHIEM_DATA\BIEU_MAU\So_Sach_2429"
    if not exist "D:\KHOA_XET_NGHIEM_DATA\BIEU_MAU\Bia_Ho_So_Hanh_Chinh" mkdir "D:\KHOA_XET_NGHIEM_DATA\BIEU_MAU\Bia_Ho_So_Hanh_Chinh"
    if not exist "D:\KHOA_XET_NGHIEM_DATA\HO_SO_NHAN_SU" mkdir "D:\KHOA_XET_NGHIEM_DATA\HO_SO_NHAN_SU"
    echo [OK] Thu muc luu tru tren o D: da san sang.
) else (
    echo [CANH BAO] Khong tim thay o dia D:! He thong se tu dong su dung thu muc du phong cuc bo.
)

:: 2. Tim Python
set PYTHON_CMD=python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else (
        py --version >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_CMD=py
        ) else (
            echo [LOI] Khong tim thay Python tren may! Vui long cai dat Python 3.10 tro len.
            pause
            exit /b 1
        )
    )
)

echo [*] Su dung trinh thuc thi: %PYTHON_CMD%

:: 3. Kiem tra thu vien phan mem
echo [*] Kiem tra cac thu vien FastAPI, Uvicorn, OpenPyXL...
%PYTHON_CMD% -c "import fastapi, uvicorn, openpyxl" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Dang cai dat cac goi thu vien can thiet...
    %PYTHON_CMD% -m pip install fastapi uvicorn python-multipart openpyxl
)

:: 4. Chuyen vao thu muc du an
cd /d "%~dp0"

:: 5. Mo trinh duyet sau 2 giay
echo [*] Dang khoi dong Web App tren cong 8000...
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000"

:: 6. Chay May chu Uvicorn (cho phep ket noi ca tren mang LAN noi bo)
echo.
echo =========================================================================
echo   MAY CHU DANG HOAT DONG SAN SANG!
echo   - Truy cap cuc bo tai may chu: http://localhost:8000
echo   - Cac may tinh khac trong mang LAN co the truy cap bang dia chi IP may nay:
echo     Vi du: http://192.168.x.x:8000
echo   - Nhan Ctrl + C de dung may chu.
echo =========================================================================
echo.

%PYTHON_CMD% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

pause
