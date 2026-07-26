[CmdletBinding()]
param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$RedisExe = 'C:\Users\Vishnuu\AppData\Local\Microsoft\WinGet\Packages\taizod1024.redis-windows-fork_Microsoft.Winget.Source_8wekyb3d8bbwe\Redis-8.8.0-Windows-x64-msys2\redis-server.exe',
    [string]$Neo4jZip = (Join-Path $RepoRoot '.tmp\neo4j-community-2026.06.0-windows.zip')
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

$neo4jRoot = 'C:\ProgramData\SCM\Neo4j'
if (-not (Test-Path -LiteralPath (Join-Path $neo4jRoot 'bin\neo4j.bat'))) {
    if (-not (Test-Path -LiteralPath $Neo4jZip)) { throw "Neo4j ZIP not found: $Neo4jZip" }
    $extractRoot = 'C:\ProgramData\SCM\Neo4j-extract'
    if (Test-Path -LiteralPath $extractRoot) {
        Remove-Item -LiteralPath $extractRoot -Recurse -Force
    }
    Expand-Archive -LiteralPath $Neo4jZip -DestinationPath $extractRoot -Force
    $extracted = Get-ChildItem -LiteralPath $extractRoot -Directory |
        Where-Object { Test-Path (Join-Path $_.FullName 'bin\neo4j.bat') } |
        Select-Object -First 1
    if (-not $extracted) { throw 'Neo4j archive layout was not recognized.' }
    if (Test-Path -LiteralPath $neo4jRoot) {
        Remove-Item -LiteralPath $neo4jRoot -Recurse -Force
    }
    Move-Item -LiteralPath $extracted.FullName -Destination $neo4jRoot
    Remove-Item -LiteralPath $extractRoot -Recurse -Force
}

$javaHome = Split-Path -Parent (Split-Path -Parent (Get-Command java.exe).Source)
[Environment]::SetEnvironmentVariable('JAVA_HOME', $javaHome, 'Machine')
[Environment]::SetEnvironmentVariable('NEO4J_HOME', $neo4jRoot, 'Machine')
$env:JAVA_HOME = $javaHome
$env:NEO4J_HOME = $neo4jRoot

$neo4jAdmin = Join-Path $neo4jRoot 'bin\neo4j-admin.bat'
$neo4j = Join-Path $neo4jRoot 'bin\neo4j.bat'
$authFile = Join-Path $neo4jRoot 'data\dbms\auth.ini'
if (-not (Test-Path -LiteralPath $authFile)) {
    & $neo4jAdmin dbms set-initial-password 'disruption123'
    if ($LASTEXITCODE -ne 0) { throw "Neo4j initial-password setup failed with exit code $LASTEXITCODE" }
}

if (-not (Get-Service -Name 'neo4j' -ErrorAction SilentlyContinue)) {
    & $neo4j windows-service install
    if ($LASTEXITCODE -ne 0) { throw "Neo4j service installation failed with exit code $LASTEXITCODE" }
}
Set-Service -Name 'neo4j' -StartupType Automatic
Start-Service -Name 'neo4j'
