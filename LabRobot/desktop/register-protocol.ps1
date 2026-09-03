param(
    [string]$ExecutablePath = "",
    [switch]$AllUsers
)

$ErrorActionPreference = "Stop"
$protocolRoot = if ($AllUsers) {
    "HKLM:\Software\Classes\labrobot"
} else {
    "HKCU:\Software\Classes\labrobot"
}
$commandKey = Join-Path $protocolRoot "shell\open\command"

New-Item -Path $commandKey -Force | Out-Null
Set-ItemProperty -Path $protocolRoot -Name "(Default)" -Value "URL:Lab Robot Windows App"
Set-ItemProperty -Path $protocolRoot -Name "URL Protocol" -Value ""

if ($ExecutablePath) {
    $resolvedExecutable = (Resolve-Path -LiteralPath $ExecutablePath).Path
    $command = "`"$resolvedExecutable`" `"%1`""
} else {
    $launcher = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "start.ps1")).Path
    $powershell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
    $command = "`"$powershell`" -NoProfile -ExecutionPolicy Bypass -File `"$launcher`" -ProtocolUri `"%1`""
}

Set-ItemProperty -Path $commandKey -Name "(Default)" -Value $command
$scope = if ($AllUsers) { "all Windows users" } else { "the current Windows user" }
Write-Host "Registered labrobot:// for $scope."
