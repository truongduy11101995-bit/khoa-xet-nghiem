Set WshShell = CreateObject("WScript.Shell")
pythonw = "C:\Users\TP.KHOAXETNGHIEM\AppData\Local\Programs\Python\Python312\pythonw.exe"
watchdog = "C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\watchdog_service.py"

' Khoi dong che do giam sat tu dong 24/7 (An hoan toan khong hien cua so)
WshShell.Run """" & pythonw & """ """ & watchdog & """", 0, False
