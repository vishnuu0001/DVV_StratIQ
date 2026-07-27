# ---------------------------------------------------------------------------
# Author: Vishnuu A
# Scope: watchdog_all_backends.ps1 â€” watchdog_all_backends (watchdog_all_backends.ps1)
# Date: 2026-05-11
# ---------------------------------------------------------------------------
# Strat-Aqorynth Master Backend Watchdog
# Monitors all backend services and restarts any that die.
# Launched via scheduled task at logon.

$bootstrapRestartRequest = Join-Path $PSScriptRoot '.runtime\restart-requests\Modernization.request'
if (Test-Path -LiteralPath $bootstrapRestartRequest) {
    $modernizationListener = Get-NetTCPConnection -LocalPort 8084 -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    $restartSucceeded = $true
    if ($modernizationListener) {
        Stop-Process -Id $modernizationListener.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        $unchangedListener = Get-NetTCPConnection -LocalPort 8084 -State Listen -ErrorAction SilentlyContinue |
            Where-Object { $_.OwningProcess -eq $modernizationListener.OwningProcess } |
            Select-Object -First 1
        $restartSucceeded = -not $unchangedListener
    }
    if ($restartSucceeded) {
        Remove-Item -LiteralPath $bootstrapRestartRequest -Force -ErrorAction SilentlyContinue
    } else {
        Write-Warning (
            "Modernization restart request retained: process $($modernizationListener.OwningProcess) " +
            "could not be stopped by this watchdog identity."
        )
    }
}

$createdNew = $false
$watchdogMutex = New-Object System.Threading.Mutex($true, 'Global\Strat-Aqorynth-Master-Watchdog', [ref]$createdNew)
if (-not $createdNew) {
    Write-Host 'Another Strat-Aqorynth master watchdog instance is already running.'
    exit 0
}

$Root   = $PSScriptRoot
$LogDir = Join-Path $Root 'Data\logs'
$null = New-Item -ItemType Directory -Path $LogDir -Force
$CheckSecs = 30
$SharedSecret = 'SCu0Fo2HIFWWHyfqrRtRqNaNmRj0NY-C3mfEMcqSRSeBCOG7'
$SharedCors   = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000,https://aqorynthapp.org,https://www.aqorynthapp.org'
$TraceForgeDatabaseUrl = [Environment]::GetEnvironmentVariable('TRACEFORGE_DATABASE_URL', 'Machine')
if (-not $TraceForgeDatabaseUrl) {
    $TraceForgeDatabaseUrl = [Environment]::GetEnvironmentVariable('TRACEFORGE_DATABASE_URL', 'User')
}
if (-not $TraceForgeDatabaseUrl) {
    $TraceForgeDatabaseUrl = 'postgresql+asyncpg://tf_admin:tf_secret@localhost:5432/traceforge'
}

$Services = @(
    @{
        Name       = 'AppRationalization'
        Port       = 5001
        Dir        = "$Root\AppRationalization\backend"
        Python     = "$Root\AppRationalization\backend\.venv\Scripts\python.exe"
        Exe        = "$Root\AppRationalization\backend\.venv\Scripts\waitress-serve.exe"
        UseWaitress= $true
        WaitressApp= 'run:app'
        FallbackArgs= "`"$Root\AppRationalization\backend\run.py`""
        Env        = @{
            FLASK_DEBUG                   = 'false'
            FLASK_ENV                     = 'production'
            FLASK_HOST                    = '0.0.0.0'
            FLASK_PORT                    = '5001'
            DATABASE_PROVIDER             = 'sqlite'
            # Migrated from SQLite 2026-07-14 â€” see AppRationalization/backend/scripts/
            # migrate_sqlite_to_postgres.py. Same local Postgres 16 instance as TraceForge.
            DATABASE_URL                  = 'postgresql+psycopg://ar_admin:yGox8k87NsE0aC4be5aeyKGM@localhost:5432/apprationalization'
            SECRET_KEY                    = $SharedSecret
            AUTH_TOKEN_SECRET             = $SharedSecret
            CORS_ORIGINS                  = $SharedCors
            INCLUDE_LOCALHOST_CORS_ORIGINS= 'true'
            ALLOW_INSECURE_AUTH_SECRET    = 'false'
        }
    },
    @{
        Name   = 'CodeAnalysis'
        Port   = 8082
        Dir    = "$Root\CodeAnalysis"
        Python = "$Root\CodeAnalysis\.venv\Scripts\python.exe"
        Args   = '-m uvicorn api.server:app --host 0.0.0.0 --port 8082 --log-level info'
        Env    = @{
            GIT_PYTHON_REFRESH= 'quiet'
            AUTH_REQUIRED     = 'true'
            AUTH_TOKEN_SECRET = $SharedSecret
            CORS_ORIGINS      = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
        }
    },
    @{
        Name   = 'InfraRationalization'
        Port   = 8083
        Dir    = "$Root\InfraRationalization"
        Python = "$Root\InfraRationalization\.venv\Scripts\python.exe"
        Args   = '-m uvicorn api.server:app --host 0.0.0.0 --port 8083 --log-level info'
        Env    = @{
            AUTH_REQUIRED     = 'true'
            AUTH_TOKEN_SECRET = $SharedSecret
            CORS_ORIGINS      = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
        }
    },
    @{
        Name   = 'Modernization'
        Port   = 8084
        Dir    = "$Root\Modernization"
        Python = "$Root\Modernization\.venv\Scripts\python.exe"
        Args   = '-m uvicorn api.server:app --host 0.0.0.0 --port 8084 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET     = $SharedSecret
            AUTH_TOKEN_TTL_SECONDS= '28800'
            AUTH_REQUIRED         = 'true'
            CORS_ORIGINS          = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
            # Code-generation LLM (see services/llm.py) â€” model is forced to
            # qwen3.5:9b in code and is NOT configurable via OLLAMA_MODEL.
            OLLAMA_BASE_URL       = 'http://localhost:11434'
        }
    },
    @{
        Name   = 'Novastra-ITSM'
        Port   = 8086
        Dir    = "$Root\Novastra-ITSM"
        Python = "$Root\Novastra-ITSM\.venv\Scripts\python.exe"
        Args   = '-m uvicorn backend.main:app --host 0.0.0.0 --port 8086 --log-level info'
        Env    = @{
            JWT_SECRET              = $SharedSecret
            AUTH_TOKEN_SECRET       = $SharedSecret
            ALLOW_LOCAL_AUTH_BYPASS = 'false'
            DB_BACKEND              = 'sqlite'
            VECTOR_BACKEND          = 'lancedb'
            SYNC_REQUIRE_DUAL_WRITE = 'false'
            CORS_ORIGINS            = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
            ALLOWED_ORIGINS         = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
            # 2026-07-24: previously unset and silently fell back to the
            # "admin_change_me_in_prod" default baked into config.py. That fallback
            # was removed (config.py now fails startup if this is unset).
            ADMIN_SECRET             = 'DXZrb85cVQSDAbVkZRWso32b559T2PCrYHOWEu3RTsg'
            # 2026-07-24: required so the Settings UI can persist LLM provider
            # config (Ollama URL, OpenAI key) to DB encrypted instead of in-memory only.
            SETTINGS_ENCRYPTION_KEY  = 'ZwW_2MxhFRIUZs6KAP9FudG7nsuWgo3Qm_CGOPGB10w='
        }
    },
    @{
        Name   = 'Dashboard'
        Port   = 8087
        Dir    = "$Root\Dashboard\backend"
        Python = "$Root\Dashboard\backend\.venv\Scripts\python.exe"
        Args   = '-m uvicorn main:app --host 0.0.0.0 --port 8087 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET          = $SharedSecret
            CORS_ORIGINS               = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
            # Default of 20s is too tight for this ServiceNow dev instance, whose paginated
            # table fetches routinely take 12-20s each; a slow page (e.g. sc_req_item) would
            # exceed it and fail the whole /api/sync call with a 500.
            SERVICENOW_TIMEOUT_SECONDS = '60'
            # TODO (2026-07-24): NEW â€” Dashboard previously had no database at all.
            # ServiceNow connection settings (URL/username/password) are meant to persist
            # here encrypted instead of being echoed to the UI straight from .env in
            # plaintext. Password below is a deliberate placeholder (real Postgres
            # password not supplied yet) â€” every DB read/write path in code is wrapped
            # to fail soft on a bad connection (logs a warning, falls back to the old
            # .env-sourced values), so this does NOT block Dashboard from starting or
            # from working exactly as it did before this feature â€” the DB-persistence
            # feature itself just stays inert until the real password replaces CHANGEME
            # below (same postgres/postgres role Novastra-ITSM connects to on this box).
            POSTGRES_DSN             = 'postgresql://postgres:CHANGEME@localhost:5432/postgres?connect_timeout=10&sslmode=prefer'
            SETTINGS_ENCRYPTION_KEY  = '0OeFHIKFaZpNOBYlpgN1brdu3mReFpQoDx2NAj5R4Y0='
        }
    },
    @{
        Name   = 'SSDLC'
        Port   = 8091
        Dir    = "$Root\SSDLC_Process_Assessment\backend"
        Python = "$Root\SSDLC_Process_Assessment\backend\.venv\Scripts\python.exe"
        Args   = '-m uvicorn app.main:app --host 0.0.0.0 --port 8091 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET       = $SharedSecret
            # IIS reverse-proxy requests arrive from loopback too, so a local
            # bypass here would also bypass authentication for public traffic.
            ALLOW_LOCAL_AUTH_BYPASS = 'false'
            CORS_ORIGINS            = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
        }
    },
    @{
        Name   = 'OpportunityTracker'
        Port   = 8092
        Dir    = "$Root\OpportunityTracker\backend"
        Python = "$Root\OpportunityTracker\backend\.venv\Scripts\python.exe"
        Args   = '-m uvicorn main:app --host 0.0.0.0 --port 8092 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET = $SharedSecret
            PORTAL_AUTH_TOKEN_SECRET = $SharedSecret
            CORS_ORIGINS      = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
            # Wave Planning feature â€” LLM-assisted migration wave-plan analysis (see wave_llm_service.py)
            OLLAMA_BASE_URL   = 'http://localhost:11434'
            OLLAMA_MODEL      = 'qwen3.5:9b'
        }
    },
    @{
        Name   = 'LabRobot'
        Port   = 8000
        Dir    = "$Root\LabRobot\backend"
        Python = "$Root\LabRobot\backend\.venv\Scripts\python.exe"
        Args   = '-m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET = $SharedSecret
            CORS_ORIGINS      = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
        }
    },
    @{
        # Local Aedes MQTT broker for the LabRobot 3D simulation â€” TCP :1883
        # (consumed by the LabRobot backend's paho-mqtt bridge) and
        # WebSocket :9001 (consumed by the browser's mqtt.js client).
        Name   = 'LabRobot-MqttBroker'
        Port   = 1883
        Dir    = "$Root\LabRobot\mqtt-broker"
        Python = 'C:\Program Files\nodejs\node.exe'
        Args   = 'broker.js'
        Env    = @{
            MQTT_TCP_PORT = '1883'
            MQTT_WS_PORT  = '9001'
        }
    },
    @{
        Name   = 'AI_Reman_Core'
        Port   = 8093
        Dir    = "$Root\AI_Reman_Core\backend"
        Python = "$Root\AI_Reman_Core\backend\.venv\Scripts\python.exe"
        Args   = '-m uvicorn main:app --host 0.0.0.0 --port 8093 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET = $SharedSecret
            CORS_ORIGINS      = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
        }
    },
    @{
        Name   = 'AI_Vehicle_Loan'
        Port   = 8094
        Dir    = "$Root\AI_Vehicle_Loan"
        Python = "$Root\AI_Vehicle_Loan\.venv\Scripts\python.exe"
        Args   = '-m uvicorn api.main:app --host 0.0.0.0 --port 8094 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET = $SharedSecret
            CORS_ORIGINS      = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:3000,http://127.0.0.1:3000'
        }
    },
    @{
        Name   = 'TraceForge-API'
        Port   = 8095
        Dir    = "$Root\TraceForge\api"
        Python = "$Root\TraceForge\api\.venv\Scripts\python.exe"
        Args   = '-m uvicorn traceforge.main:app --host 0.0.0.0 --port 8095 --log-level info'
        Env    = @{
            AUTH_TOKEN_SECRET       = $SharedSecret
            ALLOW_LOCAL_AUTH_BYPASS = 'false'
            CORS_ORIGINS            = 'http://localhost,http://127.0.0.1,http://localhost:8090,http://127.0.0.1:8090,http://localhost:5186,http://127.0.0.1:5186'
            DATABASE_URL            = $TraceForgeDatabaseUrl
            REDIS_URL               = 'redis://127.0.0.1:6379/3'
            OLLAMA_BASE_URL         = 'http://localhost:11434'
            OLLAMA_MODEL            = 'qwen3.5:9b'
            OLLAMA_EMBED_MODEL      = 'nomic-embed-text'
            OLLAMA_NUM_CTX          = '12288'
            OLLAMA_TIMEOUT_SECONDS  = '300'
            TRACEFORGE_PERFORMANCE_MODE = 'fast'
            GIT_PYTHON_REFRESH          = 'quiet'
        }
    },
    @{
        # Arq worker for TraceForge's long-lived agent runs. Requirements.MD Â§2 is explicit
        # that these must NOT live inside the IIS/uvicorn worker process â€” a run in progress
        # must survive an app-pool recycle of TraceForge-API. Binds no TCP port (it's a Redis
        # job-queue consumer, not a server), so Is-ServiceAlive falls back to PID liveness â€”
        # Port is intentionally omitted here, not set to $null explicitly.
        Name   = 'TraceForge-Worker'
        Dir    = "$Root\TraceForge\api"
        Python = "$Root\TraceForge\api\.venv\Scripts\python.exe"
        Args   = '-m arq traceforge.workers.arq_worker.WorkerSettings'
        Env    = @{
            AUTH_TOKEN_SECRET  = $SharedSecret
            DATABASE_URL       = $TraceForgeDatabaseUrl
            REDIS_URL          = 'redis://127.0.0.1:6379/3'
            OLLAMA_BASE_URL    = 'http://localhost:11434'
            OLLAMA_MODEL       = 'qwen3.5:9b'
            OLLAMA_EMBED_MODEL = 'nomic-embed-text'
            OLLAMA_NUM_CTX     = '12288'
            OLLAMA_TIMEOUT_SECONDS = '300'
            AGENT_WORKER_CONCURRENCY = '1'
            AGENT_JOB_TIMEOUT_SECONDS = '14400'
            TRACEFORGE_PERFORMANCE_MODE = 'fast'
            GIT_PYTHON_REFRESH          = 'quiet'
        }
    },
    @{
        # Native Redis-compatible process used by SCM. This Windows build is a
        # console application rather than a Service Control Manager binary, so
        # the master watchdog owns its lifecycle just like the API processes.
        Name   = 'SCM-Redis'
        Port   = 6379
        Dir    = 'C:\ProgramData\SCM\Redis'
        Python = 'C:\ProgramData\SCM\Redis\redis-server.exe'
        # MSYS2 Redis interprets a drive-letter argument as a POSIX-relative
        # path. WorkingDirectory is already Redis's directory, so keep this
        # configuration argument relative.
        Args   = 'redis.conf'
        Env    = @{}
    },
    # SCM (supply-chain-disruption-manager) microservices â€” previously not covered by this
    # watchdog at all, so they could silently crash with nothing to restart them (found when
    # they'd died with no trace in their own logs). Dir points directly at each service's
    # src/ so `-m uvicorn <pkg>.main:app` resolves without a separate PYTHONPATH entry.
    @{
        Name   = 'SCM-KG-Service'
        Port   = 8001
        Dir    = "$Root\supply-chain-disruption-manager\services\kg-service\src"
        Python = "$Root\supply-chain-disruption-manager\services\kg-service\.venv\Scripts\python.exe"
        Args   = '-m uvicorn kg.main:app --host 0.0.0.0 --port 8001 --log-level info'
        Env    = @{
            ENVIRONMENT              = 'development'
            DEBUG                    = 'true'
            LOG_JSON                 = 'false'
            NEO4J_URI                = 'bolt://localhost:7687'
            NEO4J_USER               = 'neo4j'
            NEO4J_PASSWORD           = 'disruption123'
            KG_API_KEY               = 'kg-dev-key-change-in-prod'
            KG_BASE_URL              = 'http://localhost:8001'
            POSTGRES_URL             = 'postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr'
            REDIS_URL                = 'redis://localhost:6379/0'
            AGENT_API_KEY            = 'agent-dev-key-change-in-prod'
            AGENT_BASE_URL           = 'http://localhost:8002'
            ORCHESTRATOR_MODEL       = 'qwen3.5:9b'
            SPECIALIST_MODEL         = 'qwen3.5:9b'
            INSPECTOR_ERP_HMAC_SECRET= 'erp-hmac-secret-change-in-prod'
            MOCK_AGENTS              = 'true'
        }
    },
    @{
        Name   = 'SCM-Agent-Service'
        Port   = 8002
        Dir    = "$Root\supply-chain-disruption-manager\services\agent-service\src"
        Python = "$Root\supply-chain-disruption-manager\services\agent-service\.venv\Scripts\python.exe"
        Args   = '-m uvicorn agents.main:app --host 0.0.0.0 --port 8002 --log-level info'
        Env    = @{
            ENVIRONMENT              = 'development'
            DEBUG                    = 'true'
            LOG_JSON                 = 'false'
            NEO4J_URI                = 'bolt://localhost:7687'
            NEO4J_USER               = 'neo4j'
            NEO4J_PASSWORD           = 'disruption123'
            KG_API_KEY               = 'kg-dev-key-change-in-prod'
            KG_BASE_URL              = 'http://localhost:8001'
            POSTGRES_URL             = 'postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr'
            REDIS_URL                = 'redis://localhost:6379/0'
            AGENT_API_KEY            = 'agent-dev-key-change-in-prod'
            AGENT_BASE_URL           = 'http://localhost:8002'
            INSPECTOR_ERP_HMAC_SECRET= 'erp-hmac-secret-change-in-prod'
            MOCK_AGENTS              = 'true'
        }
    },
    @{
        Name   = 'SCM-Signal-Inspector'
        Port   = 8003
        Dir    = "$Root\supply-chain-disruption-manager\services\signal-inspector\src"
        Python = "$Root\supply-chain-disruption-manager\services\signal-inspector\.venv\Scripts\python.exe"
        Args   = '-m uvicorn inspector.main:app --host 0.0.0.0 --port 8003 --log-level info'
        Env    = @{
            ENVIRONMENT              = 'development'
            DEBUG                    = 'true'
            LOG_JSON                 = 'false'
            NEO4J_URI                = 'bolt://localhost:7687'
            NEO4J_USER               = 'neo4j'
            NEO4J_PASSWORD           = 'disruption123'
            KG_API_KEY               = 'kg-dev-key-change-in-prod'
            KG_BASE_URL              = 'http://localhost:8001'
            POSTGRES_URL             = 'postgresql+asyncpg://sc_admin:sc_secret@localhost:5432/disruption_mgr'
            REDIS_URL                = 'redis://localhost:6379/0'
            AGENT_API_KEY            = 'agent-dev-key-change-in-prod'
            AGENT_BASE_URL           = 'http://localhost:8002'
            INSPECTOR_ERP_HMAC_SECRET= 'erp-hmac-secret-change-in-prod'
            MOCK_AGENTS              = 'true'
        }
    }
)

$ProcessMap = @{}

# Function: Write-Log
function Write-Log {
    param([string]$Svc, [string]$Msg)
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$ts][$Svc] $Msg"
    Add-Content "$LogDir\watchdog_master.log" -Value $line
    Write-Host $line
}

# Function: Is-PortListening
function Is-PortListening {
    param([int]$Port)
    $null -ne (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
}

# TraceForge-Worker (Arq) binds no TCP port â€” it's a job-queue consumer, not a server â€”
# so the usual port-based health check can't see it. Fall back to PID liveness for any
# service with Port = $null; every existing service still has a Port and is unaffected.
# Function: Is-ServiceAlive
function Is-ServiceAlive {
    param($Svc)
    if ($Svc.Port) { return Is-PortListening $Svc.Port }
    $proc = $ProcessMap[$Svc.Name]
    return ($null -ne $proc) -and (-not $proc.HasExited)
}

# Function: Ensure-Neo4jRunning
function Ensure-Neo4jRunning {
    if (Is-PortListening 7687) { return }

    $dbmsRoots = @(
        (Join-Path $env:USERPROFILE '.Neo4jDesktop\relate-data\dbmss'),
        (Join-Path $env:SystemDrive 'Users\stratdev\.Neo4jDesktop\relate-data\dbmss')
    ) | Select-Object -Unique
    $dbms = $dbmsRoots |
        Where-Object { Test-Path -LiteralPath $_ } |
        ForEach-Object { Get-ChildItem -LiteralPath $_ -Directory -ErrorAction SilentlyContinue } |
        Where-Object { Test-Path (Join-Path $_.FullName 'bin\neo4j.bat') } |
        Sort-Object CreationTime -Descending |
        Select-Object -First 1

    if (-not $dbms) {
        Write-Log 'Neo4j' 'No Neo4j Desktop DBMS installation was found'
        return
    }

    $neo4jBat = Join-Path $dbms.FullName 'bin\neo4j.bat'
    # Neo4j Enterprise defaults its internal discovery listener to localhost:5000,
    # which collides with the portal authentication API. Keep the internal-only
    # listener on a dedicated port. AppRationalization uses 5001 to avoid the
    # topology's persisted discovery binding on 5000.
    $env:NEO4J_server_discovery_listen__address = ':5100'
    $env:NEO4J_server_discovery_advertised__address = ':5100'
    Start-Process -FilePath $neo4jBat -ArgumentList 'console' -WorkingDirectory $dbms.FullName -WindowStyle Hidden | Out-Null
    Write-Log 'Neo4j' "Started DBMS from $($dbms.FullName)"
}

# Function: Start-Backend
function Start-Backend {
    param($Svc)

    if (-not (Test-Path $Svc.Python)) {
        Write-Log $Svc.Name "Python not found at $($Svc.Python) - skipping"
        return $null
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.UseShellExecute        = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError  = $true
    $psi.CreateNoWindow         = $true
    $psi.WorkingDirectory       = $Svc.Dir

    # Scheduled tasks retain the environment captured when they started.
    # Refresh PATH for every child so toolchains installed by an administrator
    # become available when a backend is restarted, without rebooting the host.
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $psi.EnvironmentVariables['Path'] = @($machinePath, $userPath) -join ';'

    foreach ($key in $Svc.Env.Keys) {
        $val = $Svc.Env[$key]
        if ($null -ne $psi.EnvironmentVariables[$key]) {
            $psi.EnvironmentVariables[$key] = $val
        } else {
            $psi.EnvironmentVariables.Add($key, $val)
        }
    }

    if ($Svc.UseWaitress -and (Test-Path $Svc.Exe)) {
        $psi.FileName  = $Svc.Exe
        $psi.Arguments = "--host=0.0.0.0 --port=$($Svc.Port) --threads=4 $($Svc.WaitressApp)"
    } elseif ($Svc.ContainsKey('Args')) {
        $psi.FileName  = $Svc.Python
        $psi.Arguments = $Svc.Args
    } else {
        $psi.FileName  = $Svc.Python
        $psi.Arguments = $Svc.FallbackArgs
    }

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    $logFile    = "$LogDir\$($Svc.Name)_stderr.log"
    $stdoutFile = "$LogDir\$($Svc.Name)_stdout.log"

    # -MessageData/$Event.MessageData is required here, not a closure over $stdoutFile/$logFile:
    # Register-ObjectEvent -Action script blocks run in the event subscriber's own scope, which
    # does NOT see this function's local variables. Referencing them directly silently resolved
    # to $null, so Add-Content wrote to no file at all - every service's stderr/stdout has been
    # discarded since this handler was added, including whatever explains TraceForge-Worker's
    # repeated restarts.
    Register-ObjectEvent -InputObject $proc -EventName OutputDataReceived -MessageData $stdoutFile -Action {
        if ($Event.SourceEventArgs.Data) { Add-Content -Path $Event.MessageData -Value $Event.SourceEventArgs.Data }
    } | Out-Null
    Register-ObjectEvent -InputObject $proc -EventName ErrorDataReceived -MessageData $logFile -Action {
        if ($Event.SourceEventArgs.Data) { Add-Content -Path $Event.MessageData -Value $Event.SourceEventArgs.Data }
    } | Out-Null

    $proc.Start()             | Out-Null
    $proc.BeginOutputReadLine()
    $proc.BeginErrorReadLine()

    Write-Log $Svc.Name "Started (PID $($proc.Id)) on port $($Svc.Port)"
    return $proc
}

Write-Log 'Master' "Watchdog starting - managing $($Services.Count) services"

Ensure-Neo4jRunning

$RestartRequestDir = Join-Path $Root '.runtime\restart-requests'
New-Item -ItemType Directory -Force -Path $RestartRequestDir | Out-Null
foreach ($svc in $Services) {
    $requestFile = Join-Path $RestartRequestDir "$($svc.Name).request"
    if (-not (Test-Path -LiteralPath $requestFile)) { continue }
    if ($svc.Port) {
        $listener = Get-NetTCPConnection -LocalPort $svc.Port -State Listen -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($listener) {
            Write-Log $svc.Name "Explicit restart requested; stopping PID $($listener.OwningProcess)"
            Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
    }
    Remove-Item -LiteralPath $requestFile -Force -ErrorAction SilentlyContinue
}

foreach ($svc in $Services) {
    if (-not (Is-ServiceAlive $svc)) {
        $proc = Start-Backend $svc
        if ($proc) { $ProcessMap[$svc.Name] = $proc }
        Start-Sleep -Seconds 3
    } else {
        Write-Log $svc.Name "Already running on port $($svc.Port)"
    }
}

Write-Log 'Master' "Initial startup complete - entering monitor loop"

while ($true) {
    Start-Sleep -Seconds $CheckSecs
    foreach ($svc in $Services) {
        if (-not (Is-ServiceAlive $svc)) {
            Write-Log $svc.Name "$(if ($svc.Port) { "Port $($svc.Port)" } else { 'Process' }) went down - restarting"
            $proc = Start-Backend $svc
            if ($proc) { $ProcessMap[$svc.Name] = $proc }
            Start-Sleep -Seconds 5
        }
    }
}
