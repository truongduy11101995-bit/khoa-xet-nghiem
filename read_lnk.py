import subprocess

ps = """
$wsh = New-Object -ComObject WScript.Shell
$sc = $wsh.CreateShortcut("$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\KhoaXetNghiem_Server.lnk")
Write-Output "Target: $($sc.TargetPath)"
Write-Output "Args: $($sc.Arguments)"
"""
res = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
print(res.stdout)
