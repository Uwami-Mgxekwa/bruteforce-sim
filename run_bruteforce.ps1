Write-Host "========================================"
Write-Host "  Brute Force Simulator Launcher"
Write-Host "========================================"
Write-Host "Select mode to run:"
Write-Host "1. Server Mode"
Write-Host "2. Attack Mode"
Write-Host ""
$mode = Read-Host "Enter 1 or 2"

if ($mode -eq '1') {
    Write-Host "Starting Server..."
    python bruteforce.py --mode server
} elseif ($mode -eq '2') {
    Write-Host "Starting Attacker..."
    python bruteforce.py --mode attack --wordlist wordlist.txt
} else {
    Write-Host "Invalid choice. Showing help instead..."
    python bruteforce.py --help
}

Write-Host ""
Write-Host "Press any key to exit..."
$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
