import subprocess

ps = """
Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, Name, CommandLine | Sort-Object Name | Format-Table -AutoSize | Out-String -Width 300
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
with open(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\proc_dump.txt", "w", encoding="utf-8") as f:
    f.write(res.stdout)
print("Dumped", len(res.stdout), "bytes")
