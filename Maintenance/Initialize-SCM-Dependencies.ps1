[CmdletBinding()]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$RedisExe = 'C:\Users\Vishnuu\AppData\Local\Microsoft\WinGet\Packages\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe\Redis-8.8.0-Windows-x64-msys2\redis-server.exe'
)

$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Administrator privileges are required.'
}

$psql = 'C:\Program Files\PostgreSQL\16\bin\psql.exe'
if (-not (Test-Path -LiteralPath $psql)) { throw "psql not found: $psql" }
$env:PGPASSWORD = 'sc_secret'
$env:PGOPTIONS = '--client-min-messages=warning'

$roleExists = & $psql -U postgres -h localhost -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='sc_admin'"
if (-not $roleExists) {
    & $psql -U postgres -h localhost -d postgres -v ON_ERROR_STOP=1 -c "CREATE ROLE sc_admin LOGIN PASSWORD 'sc_secret'"
}
$dbExists = & $psql -U postgres -h localhost -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='disruption_mgr'"
if (-not $dbExists) {
    & 'C:\Program Files\PostgreSQL\16\bin\createdb.exe' -U postgres -h localhost -O sc_admin disruption_mgr
}
& $psql -U postgres -h localhost -d disruption_mgr -v ON_ERROR_STOP=1 -f (Join-Path $RepoRoot 'supply-chain-disruption-manager\infra\postgres\init.sql')

if (-not (Test-Path -LiteralPath $RedisExe)) { throw "Redis executable not found: $RedisExe" }
$redisSourceDir = Split-Path -Parent $RedisExe
$redisDir = 'C:\ProgramData\SCM\Redis'
$null = New-Item -ItemType Directory -Path $redisDir -Force
Copy-Item -Path (Join-Path $redisSourceDir '*') -Destination $redisDir -Recurse -Force
$redisExeInstalled = Join-Path $redisDir 'redis-server.exe'
$redisConfig = Join-Path $redisDir 'redis.conf'
if (-not (Test-Path -LiteralPath $redisConfig)) { throw "Redis configuration not found in $redisDir" }

# redis-server.exe is a console application and does not implement the
# Windows Service Control Manager protocol. watchdog_all_backends.ps1 owns it.
$staleService = Get-Service -Name 'SCM-Redis' -ErrorAction SilentlyContinue
if ($staleService) {
    if ($staleService.Status -ne 'Stopped') { Stop-Service $staleService -Force }
    & sc.exe delete 'SCM-Redis' | Out-Null
}
