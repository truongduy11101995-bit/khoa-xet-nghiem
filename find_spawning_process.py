import subprocess
import time
import json

# Use WMI or PowerShell to monitor process creation for 15 seconds
ps_script = """
$watcher = New-Object System.Management.ManagementEventWatcher
$query = New-Object System.Management.WqlEventQuery("__InstanceCreationEvent", [TimeSpan]::FromSeconds(1), "TargetInstance ISA 'Win32_Process'")
$watcher.Query = $query
$watcher.Start()

$events = @()
$timeout = (Get-Date).AddSeconds(12)

while ((Get-Date) -lt $timeout) {
    try {
        $event = $watcher.WaitForNextEvent([TimeSpan]::FromSeconds(2))
        $p = $event.TargetInstance
        if ($p.Name -in @('cmd.exe', 'powershell.exe', 'conhost.exe', 'python.exe', 'cloudflared.exe')) {
            $events += [PSCustomObject]@{
                Time = (Get-Date).ToString("HH:mm:ss")
                PID = $p.ProcessId
                ParentPID = $p.ParentProcessId
                Name = $p.Name
                CommandLine = $p.CommandLine
            }
        }
    } catch {}
}
$watcher.Stop()
$events | ConvertTo-Json -Depth 3
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
print("STDOUT:", res.stdout)
print("STDERR:", res.stderr)
