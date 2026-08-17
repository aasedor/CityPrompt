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
$celeryPidPath = Join-Path $artifactRoot 'celery-worker.pid'

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

function Get-UnhydratedRuntimeLfsAssets {
    $publicRoot = Join-Path $frontendRoot 'public'
    $parkKitRoot = Join-Path $publicRoot 'park-kits'
    $candidateFiles = if (Test-Path -LiteralPath $parkKitRoot) {
        @(Get-ChildItem -LiteralPath $parkKitRoot -Recurse -File -Filter '*.glb')
    }
    else {
        @()
    }
    foreach ($relativeRoot in @(
        'archetypes\buildings',
        'archetypes\openspaces',
        'archetypes\streets'
    )) {
        $catalogueRoot = Join-Path $publicRoot $relativeRoot
        if (Test-Path -LiteralPath $catalogueRoot) {
            $candidateFiles += Get-ChildItem -LiteralPath $catalogueRoot -Recurse -File
        }
    }

    return @(
        $candidateFiles |
            Sort-Object -Property FullName -Unique |
            Where-Object {
                $_.Length -lt 300 -and
                (Get-Content -LiteralPath $_.FullName -First 1 -ErrorAction SilentlyContinue) -eq
                    'version https://git-lfs.github.com/spec/v1'
            }
    )
}

function Ensure-RuntimeLfsAssets {
    if ($SkipFrontend) {
        return
    }

    $pointers = @(Get-UnhydratedRuntimeLfsAssets)
    if ($pointers.Count -eq 0) {
        return
    }

    git lfs version 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Found $($pointers.Count) unhydrated runtime assets, but Git LFS is not installed."
    }

    # Runtime building modules are served from backend library storage. Pulling
    # every historical source-family GLB here adds roughly 8 GB and makes Vite
    # copy that archive into dist. The browser directly consumes park kits and
    # the three authoritative catalogue image roots, so hydrate only those.
    $include = 'frontend/public/park-kits/**/*.glb,frontend/public/archetypes/buildings/**,frontend/public/archetypes/openspaces/**,frontend/public/archetypes/streets/**'
    $upstream = ((git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>$null) | Out-String).Trim()
    Write-Host "Hydrating $($pointers.Count) Git LFS catalogue/model assets..."
    Push-Location $repoRoot
    try {
        if ($LASTEXITCODE -eq 0 -and $upstream.Contains('/')) {
            $slash = $upstream.IndexOf('/')
            $remote = $upstream.Substring(0, $slash)
            $branch = $upstream.Substring($slash + 1)
            git lfs pull $remote $branch "--include=$include"
        }
        else {
            git lfs pull "--include=$include"
        }
        $pullExitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    $remaining = @(Get-UnhydratedRuntimeLfsAssets)
    if ($remaining.Count -gt 0) {
        $examples = ($remaining | Select-Object -First 3 -ExpandProperty FullName) -join '; '
        throw "Git LFS left $($remaining.Count) runtime assets as pointer text. Examples: $examples"
    }
    if ($pullExitCode -ne 0) {
        Write-Warning 'Git LFS reported an index update warning, but all required runtime assets were hydrated successfully.'
    }
}

function Test-DockerReady {
    # PowerShell 7 can promote a non-zero native exit to a terminating error
    # when the script uses ErrorActionPreference=Stop. A stopped Docker daemon
    # is an expected probe result here; let Ensure-DockerDesktop start it.
    try {
        docker version --format '{{.Server.Version}}' 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
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

    # Optional application containers are commonly absent on a clean setup.
    # Treat docker inspect's non-zero exit as "not running" under PowerShell 7
    # instead of allowing ErrorActionPreference=Stop to abort the launcher.
    try {
        $running = docker inspect $Name --format '{{.State.Running}}' 2>$null
        return $LASTEXITCODE -eq 0 -and $running -eq 'true'
    }
    catch {
        return $false
    }
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

function Ensure-DatabaseSchema {
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        throw 'Python is not installed or is not on PATH.'
    }

    Write-Host 'Applying City Prompt database migrations...'
    Push-Location $backendRoot
    try {
        & $python.Source -m alembic upgrade head
        if ($LASTEXITCODE -ne 0) {
            throw 'Alembic could not upgrade the local City Prompt database.'
        }
    }
    finally {
        Pop-Location
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

    # A worker from the Docker checkout consumes the same default Redis queue
    # as this worktree. Leaving it alive makes background jobs nondeterministic:
    # Site DNA may execute against stale source even though the local API is
    # correct. The launcher owns the application processes; only the stateful
    # db/redis/minio containers stay shared.
    foreach ($name in @('cityprompt-celery', 'devplatform-celery')) {
        if (Test-ContainerRunning -Name $name) {
            Write-Host "Stopping stale Docker worker $name (stateful services remain running)..."
            docker stop $name | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "Could not stop Docker worker $name."
            }
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
    $uvicornArguments = @('app.main:app', '--host', '0.0.0.0', '--port', '8000')
    if ($uvicorn) {
        $uvicornExecutable = $uvicorn.Source
    }
    else {
        # Python's Windows app installer can expose installed console modules
        # without placing their generated .exe wrappers on PATH.
        $python = Get-Command python.exe -ErrorAction SilentlyContinue
        if (-not $python) {
            $python = Get-Command python -ErrorAction SilentlyContinue
        }
        try {
            if (-not $python) {
                throw 'Python is not installed.'
            }
            & $python.Source -c 'import uvicorn' 2>$null
            if ($LASTEXITCODE -ne 0) {
                throw 'The uvicorn Python module is not installed.'
            }
        }
        catch {
            throw 'uvicorn is not installed. Install backend/requirements.txt before starting City Prompt.'
        }
        $uvicornExecutable = $python.Source
        $uvicornArguments = @('-m', 'uvicorn') + $uvicornArguments
    }

    Write-Host 'Starting City Prompt API...'
    Start-Process -FilePath $uvicornExecutable `
        -ArgumentList $uvicornArguments `
        -WorkingDirectory $backendRoot `
        -RedirectStandardOutput (Join-Path $artifactRoot 'backend.out.log') `
        -RedirectStandardError (Join-Path $artifactRoot 'backend.err.log') `
        -WindowStyle Hidden

    Wait-Until -Description 'City Prompt API health on both OAuth loopback routes' -Condition {
        (Test-HttpEndpoint -Uri 'http://127.0.0.1:8000/health') -and
        (Test-HttpEndpoint -Uri 'http://localhost:8000/health')
    }
}

function Get-LocalCeleryWorkerPid {
    if (-not (Test-Path -LiteralPath $celeryPidPath)) {
        return $null
    }

    $rawPid = (Get-Content -LiteralPath $celeryPidPath -Raw).Trim()
    $workerPid = 0
    if (-not [int]::TryParse($rawPid, [ref]$workerPid)) {
        return $null
    }

    $worker = Get-CimInstance Win32_Process -Filter "ProcessId=$workerPid" -ErrorAction SilentlyContinue
    if (
        $worker -and
        $worker.Name -match '^python(?:\.exe)?$' -and
        $worker.CommandLine -match 'celery' -and
        $worker.CommandLine -match 'app\.tasks\.worker' -and
        $worker.CommandLine -match '\bworker\b'
    ) {
        return $workerPid
    }
    return $null
}

function Test-CeleryWorkerReady {
    param(
        [Parameter(Mandatory)][int]$WorkerPid,
        [Parameter(Mandatory)][string]$PythonPath
    )

    if (-not (Get-Process -Id $WorkerPid -ErrorAction SilentlyContinue)) {
        return $false
    }

    Push-Location $backendRoot
    try {
        $ping = & $PythonPath -m celery -A app.tasks.worker inspect ping --timeout 3 2>$null
        return $LASTEXITCODE -eq 0 -and ($ping -join "`n") -match '\bpong\b'
    }
    finally {
        Pop-Location
    }
}

function Ensure-CeleryWorker {
    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        throw 'Python is not installed or is not on PATH.'
    }

    $workerPid = Get-LocalCeleryWorkerPid
    if ($KeepBackend -and $workerPid -and (Test-CeleryWorkerReady -WorkerPid $workerPid -PythonPath $python.Source)) {
        return
    }

    if ($workerPid) {
        Write-Host 'Restarting City Prompt background worker for the current worktree...'
        Stop-Process -Id $workerPid -Force
        Wait-Until -Description 'the previous City Prompt background worker to stop' -Condition {
            -not (Get-Process -Id $workerPid -ErrorAction SilentlyContinue)
        }
    }

    if (Test-Path -LiteralPath $celeryPidPath) {
        Remove-Item -LiteralPath $celeryPidPath -Force
    }

    $otherWorkers = @(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^python(?:\.exe)?$' -and
        $_.CommandLine -match 'celery' -and
        $_.CommandLine -match 'app\.tasks\.worker' -and
        $_.CommandLine -match '\bworker\b'
    })
    if ($otherWorkers.Count -gt 0) {
        $owners = ($otherWorkers | Select-Object -ExpandProperty ProcessId) -join ', '
        throw "A Celery worker not owned by this launcher is already running (PID $owners). Stop it before starting this worktree."
    }

    Write-Host 'Starting City Prompt background worker...'
    Start-Process -FilePath $python.Source `
        -ArgumentList @(
            '-m', 'celery', '-A', 'app.tasks.worker', 'worker',
            '--loglevel=info', '--pool=solo',
            '--hostname=cityprompt-local@%h',
            "--pidfile=$celeryPidPath"
        ) `
        -WorkingDirectory $backendRoot `
        -RedirectStandardOutput (Join-Path $artifactRoot 'celery.out.log') `
        -RedirectStandardError (Join-Path $artifactRoot 'celery.err.log') `
        -WindowStyle Hidden

    Wait-Until -Description 'City Prompt background worker' -Condition {
        $startedPid = Get-LocalCeleryWorkerPid
        $startedPid -and (Test-CeleryWorkerReady -WorkerPid $startedPid -PythonPath $python.Source)
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

Ensure-RuntimeLfsAssets
Ensure-DockerDesktop
Ensure-Infrastructure
Ensure-DatabaseSchema
Ensure-Backend
Ensure-CeleryWorker
Ensure-Frontend

Write-Host ''
Write-Host 'City Prompt local stack is ready.' -ForegroundColor Green
Write-Host 'Frontend: http://127.0.0.1:5174/'
Write-Host 'API:      http://127.0.0.1:8000/health (also localhost for OAuth callbacks)'
Write-Host 'Worker:   Celery ready (Site DNA, AI Planner, renders, and processing)'
Write-Host "Logs:     $artifactRoot"
