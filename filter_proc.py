with open(r"C:\Users\TP.KHOAXETNGHIEM\.gemini\antigravity\scratch\khoa_xet_nghiem_app\proc_dump.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    low = line.lower()
    if any(k in low for k in ["cmd.exe", "powershell.exe", "conhost.exe", "wscript.exe", "cscript.exe", ".bat", ".cmd", "cloudflared"]):
        print(line.strip())
