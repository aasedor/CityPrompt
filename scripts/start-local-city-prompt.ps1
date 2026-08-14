[CmdletBinding()]
param(
    [switch]$SkipFrontend,
    [switch]$KeepBackend,
    [int]$StartupTimeoutSeconds = 90
)

$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$artifactRoot = Join-Path $repoRoot 'artifacts\local-dev'
$backendRoot = Join-Path $repoRoot 'backend'
$frontendRoot = Join-Path $repoRoot 'frontend'

New-Item -ItemType Directory -Force -Path $artifactRoot | Out-Null

function Test-HttpEndpoint {
    param([Parameter(Mandatory)][string]$Uri)

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Uri -TimeoutSec 3
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

function Wait-Until {
    param(
        [Parameter(Mandatory)][scriptblock]$Condition,
        [Parameter(Mandatory)][string]$Description
    )

    $deadline = (Get-Date).AddSeconds($StartupTimeoutSeconds)
    do {
        if (& $Condition) {
            return
        }
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)

    throw "Timed out waiting for $Description after $StartupTimeoutSeconds seconds."
}

function Test-DockerReady {
    docker version --format '{{.Server.Version}}' 2>$null | Out-Null
    return $LASTEXITCODE -eq 0
}

function Ensure-DockerDesktop {
    if (Test-DockerReady) {
        return
    }

    $dockerDesktop = 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
    if (-not (Test-Path -LiteralPath $dockerDesktop)) {
        throw 'Docker Desktop is not running and its standard executable was not found.'
    }

    Write-Host 'Starting Docker Desktop...'
    Start-Process -FilePath $dockerDesktop -WindowStyle Hidden
    Wait-Until -Description 'Docker Desktop' -Condition { Test-DockerReady }
}

function Get-ContainerName {
    param([Parameter(Mandatory)][string]$Name)

    return docker ps -a --filter "name=^/$Name$" --format '{{.Names}}'
}

function Test-ContainerRunning {
    param([Parameter(Mandatory)][string]$Name)

    $running = docker inspect $Name --format '{{.State.Running}}' 2>$null
    return $LASTEXITCODE -eq 0 -and $running -eq 'true'
}

function Ensure-Infrastructure {
    $required = @('devplatform-db', 'devplatform-redis', 'devplatform-minio')
    $missing = @($required | Where-Object { -not (Get-ContainerName -Name $_) })

    if ($missing.Count -gt 0) {
        Write-Host "Creating missing local infrastructure: $($missing -join ', ')"
        Push-Location $repoRoot
        try {
            docker compose up -d db redis minio
            if ($LASTEXITCODE -ne 0) {
                throw 'Docker Compose could not create the local infrastructure.'
            }
        }
        finally {
            Pop-Location
        }
    }

    foreach ($name in $required) {
        if (-not (Test-ContainerRunning -Name $name)) {
            Write-Host "Starting $name..."
            docker start $name | Out-Null
        }
    }

    Wait-Until -Description 'PostgreSQL health' -Condition {
        (docker inspect devplatform-db --format '{{.State.Health.Status}}' 2>$null) -eq 'healthy'
    }
    Wait-Until -Description 'Redis health' -Condition {
        (docker inspect devplatform-redis --format '{{.State.Health.Status}}' 2>$null) -eq 'healthy'
    }
}

function Stop-KnownDockerApiPortConflicts {
    # OAuth providers return through localhost:8000. A backend container from
    # another checkout can therefore intercept the callback even while this
    # worktree's API is healthy on 127.0.0.1. Keep the stateful infrastructure
    # running, but stop known stateless API containers before binding the port.
    $knownApiContainers = @('cityprompt-backend', 'devplatform-backend')
    $publishedOwners = @(docker ps --filter 'publish=8000' --format '{{.Names}}' |
        Where-Object { $_ })

    $unexpected = @($publishedOwners | Where-Object { $_ -notin $knownApiContainers })
    if ($unexpected.Count -gt 0) {
        throw "Port 8000 is published by an unexpected Docker container: $($unexpected -join ', ')."
    }

    foreach ($name in $publishedOwners) {
        Write-Host "Stopping stale Docker API container $name (stateful services remain running)..."
        docker stop $name | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Could not stop Docker API container $name."
        }
    }
}

function Assert-PortAvailableOrHealthy {
    param(
        [Parameter(Mandatory)][int]$Port,
        [Parameter(Mandatory)][string]$HealthUri,
        [Parameter(Mandatory)][string]$ServiceName
    )

    if (Test-HttpEndpoint -Uri $HealthUri) {
        return $true
    }

    $listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($listener) {
        throw "$ServiceName is not healthy, but port $Port is already owned by PID $($listener.OwningProcess)."
    }

    return $false
}

function Ensure-Backend {
    Stop-KnownDockerApiPortConflicts

    # Restart by default so source edits cannot leave the browser talking to
    # stale code. Inspect every listener because wildcard and IPv6 listeners
    # can appear as multiple rows for one process.
    $listeners = @(Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue)
    $listenerPids = @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
    $uvicornPids = @()

    foreach ($listenerPid in $listenerPids) {
        $listenerProcess = Get-CimInstance Win32_Process -Filter "ProcessId=$listenerPid"
        $isUvicorn = $listenerProcess.Name -match '^python(?:\.exe)?$' -and
            $listenerProcess.CommandLine -match 'uvicorn(?:\.exe)?"?\s+app\.main:app'
        if (-not $isUvicorn) {
            throw "Port 8000 is owned by an unexpected process (PID $listenerPid)."
        }
        $uvicornPids += $listenerPid
    }

    $bothLoopbackRoutesHealthy =
        (Test-HttpEndpoint -Uri 'http://127.0.0.1:8000/health') -and
        (Test-HttpEndpoint -Uri 'http://localhost:8000/health')
    if ($KeepBackend -and $uvicornPids.Count -gt 0 -and $bothLoopbackRoutesHealthy) {
        return
    }

    if ($uvicornPids.Count -gt 0) {
        Write-Host 'Restarting City Prompt API for the current worktree...'
        foreach ($listenerPid in $uvicornPids) {
            Stop-Process -Id $listenerPid -Force
        }
        Wait-Until -Description 'the previous City Prompt API to stop' -Condition {
            -not (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue)
        }
    }

    $uvicorn = Get-Command uvicorn.exe -ErrorAction SilentlyContinue
    if (-not $uvicorn) {
        $uvicorn = Get-Command uvicorn -ErrorAction SilentlyContinue
    }
    if (-not $uvicorn) {
        throw 'uvicorn is not installed. Install backend/requirements.txt before starting City Prompt.'
    }

    Write-Host 'Starting City Prompt API...'
    Start-Process -FilePath $uvicorn.Source `
        -ArgumentList @('app.main:app', '--host', '0.0.0.0', '--port', '8000') `
        -WorkingDirectory $backendRoot `
        -RedirectStandardOutput (Join-Path $artifactRoot 'backend.out.log') `
        -RedirectStandardError (Join-Path $artifactRoot 'backend.err.log') `
        -WindowStyle Hidden

    Wait-Until -Description 'City Prompt API health on both OAuth loopback routes' -Condition {
        (Test-HttpEndpoint -Uri 'http://127.0.0.1:8000/health') -and
        (Test-HttpEndpoint -Uri 'http://localhost:8000/health')
    }
}

function Ensure-Frontend {
    if ($SkipFrontend) {
        return
    }

    if (Assert-PortAvailableOrHealthy -Port 5174 -HealthUri 'http://127.0.0.1:5174/' -ServiceName 'City Prompt frontend') {
        return
    }

    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (-not $npm) {
        throw 'npm.cmd is not installed or is not on PATH.'
    }

    Write-Host 'Starting City Prompt frontend...'
    Start-Process -FilePath $npm.Source `
        -ArgumentList @('run', 'dev', '--', '--host', '127.0.0.1', '--port', '5174') `
        -WorkingDirectory $frontendRoot `
        -RedirectStandardOutput (Join-Path $artifactRoot 'frontend.out.log') `
        -RedirectStandardError (Join-Path $artifactRoot 'frontend.err.log') `
        -WindowStyle Hidden

    Wait-Until -Description 'City Prompt frontend' -Condition {
        Test-HttpEndpoint -Uri 'http://127.0.0.1:5174/'
    }
}

Ensure-DockerDesktop
Ensure-Infrastructure
Ensure-Backend
Ensure-Frontend

Write-Host ''
Write-Host 'City Prompt local stack is ready.' -ForegroundColor Green
Write-Host 'Frontend: http://127.0.0.1:5174/'
Write-Host 'API:      http://127.0.0.1:8000/health (also localhost for OAuth callbacks)'
Write-Host "Logs:     $artifactRoot"
