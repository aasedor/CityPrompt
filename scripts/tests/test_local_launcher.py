"""Exercise launcher functions with controlled process/CLI doubles; never start services."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
POWERSHELL = shutil.which('pwsh') or shutil.which('powershell')


@unittest.skipUnless(POWERSHELL, 'PowerShell is required for launcher lifecycle tests')
class LocalLauncherTests(unittest.TestCase):
    def run_launcher(self, body):
        with tempfile.TemporaryDirectory() as directory:
            quote = lambda value: str(value).replace("'", "''")
            setup = f"""
$ErrorActionPreference='Stop'
$source='{quote(ROOT / 'scripts/start-local-city-prompt.ps1')}'
$ast=[System.Management.Automation.Language.Parser]::ParseFile($source,[ref]$null,[ref]$null)
$ast.FindAll({{param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst]}},$false) |
 ForEach-Object {{Invoke-Expression $_.Extent.Text}}
$repoRoot='{quote(ROOT)}'
$backendRoot=Join-Path $repoRoot 'backend'
$artifactRoot='{quote(directory)}'
$celeryPidPath=Join-Path $artifactRoot 'celery-worker.pid'
$celeryBeatPidPath=Join-Path $artifactRoot 'celery-beat.pid'
$celerySchedulePath=Join-Path $artifactRoot 'celerybeat-schedule'
$queueDeclaration=$ast.EndBlock.Statements | Where-Object {{
 $_ -is [System.Management.Automation.Language.AssignmentStatementAst] -and $_.Left.VariablePath.UserPath -eq 'requiredCeleryQueues'
}}
if($queueDeclaration) {{Invoke-Expression $queueDeclaration.Extent.Text}}
$KeepBackend=$false
"""
            result = subprocess.run([POWERSHELL, '-NoProfile', '-NonInteractive', '-Command', setup + body],
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout.strip())

    def test_worker_launch_subscribes_every_routed_queue_hidden_and_owned(self):
        launch = self.run_launcher("""
function Get-Command { [pscustomobject]@{Source='fake-python'} }
function Get-LocalCeleryWorkerPid { return $null }
function Get-CimInstance { return @() }
function Write-Host {}
function Wait-Until {}
function Start-Process {param($FilePath,$ArgumentList,$WorkingDirectory,$RedirectStandardOutput,$RedirectStandardError,$WindowStyle)
 $script:launch=[pscustomobject]@{arguments=$ArgumentList;directory=$WorkingDirectory;window=$WindowStyle}}
Ensure-CeleryWorker
$script:launch|ConvertTo-Json -Compress
""")
        arguments = launch['arguments']
        self.assertIn('--queues=celery,direct3d,direct3d-maintenance,classroom-documents', arguments)
        self.assertEqual(launch['window'], 'Hidden')
        self.assertEqual(Path(launch['directory']), ROOT / 'backend')
        self.assertTrue(any('celery-worker.pid' in argument for argument in arguments))

    def test_ping_from_an_unrelated_worker_cannot_qualify_missing_queues(self):
        for reported_pid, queues, expected in [
            (101, ['celery'], False), (202, ['celery','direct3d','direct3d-maintenance','classroom-documents'], False),
            (101, ['celery','direct3d','direct3d-maintenance','classroom-documents'], True),
        ]:
            with self.subTest(pid=reported_pid, queues=queues):
                report = json.dumps({'owned@machine': [{'name': name} for name in queues]})
                stats = json.dumps({'owned@machine': {'pid': reported_pid}})
                ready = self.run_launcher(f"""
function Get-Process {{[pscustomobject]@{{Id=101}}}}
function Invoke-FakePython {{
 $global:LASTEXITCODE=0
 if($args -contains 'stats') {{'{stats}'}}
 elseif($args -contains 'active_queues') {{'{report}'}}
 else {{'pong'}}
}}
Test-CeleryWorkerReady -WorkerPid 101 -PythonPath 'Invoke-FakePython' | ConvertTo-Json -Compress
""")
                self.assertIs(ready, expected)

    def test_stale_pid_file_cannot_claim_another_checkouts_worker(self):
        pid = self.run_launcher("""
Set-Content -LiteralPath $celeryPidPath -Value '101'
function Get-CimInstance {[pscustomobject]@{Name='python.exe';CommandLine='python -m celery -A app.tasks.worker worker --pidfile=C:/unrelated/celery-worker.pid';ProcessId=101}}
Get-LocalCeleryWorkerPid | ConvertTo-Json -Compress
""")
        self.assertIsNone(pid)

    def test_keep_backend_refuses_unowned_worker_or_scheduler_before_reuse(self):
        for role, entrypoint, pid_function in [('worker', 'Ensure-CeleryWorker', 'Get-LocalCeleryWorkerPid'),
                                              ('beat', 'Ensure-CeleryBeat', 'Get-LocalCeleryBeatPid')]:
            with self.subTest(role=role):
                result = self.run_launcher(f"""
$KeepBackend=$true
function Get-Command {{[pscustomobject]@{{Source='fake-python'}}}}
function {pid_function} {{return 101}}
function Test-CeleryWorkerReady {{return $true}}
function Get-CimInstance {{[pscustomobject]@{{Name='python.exe';ProcessId=202;CommandLine='python -m celery -A app.tasks.worker {role}'}}}}
function Start-Process {{throw 'Must not launch a competing process'}}
function Stop-Process {{throw 'Must not stop an unowned process'}}
try {{{entrypoint}; $blocked=$false}} catch {{$blocked=$_.Exception.Message -match 'not owned'}}
$blocked|ConvertTo-Json -Compress
""")
                self.assertTrue(result)

    def test_operational_readiness_rejects_a_live_but_unavailable_api(self):
        for status, expected in [('unavailable', False), ('ready', True)]:
            with self.subTest(status=status):
                result = self.run_launcher(f"""
function Invoke-RestMethod {{[pscustomobject]@{{status='{status}'}}}}
Test-ApplicationReady | ConvertTo-Json -Compress
""")
                self.assertIs(result, expected)

    def test_keep_backend_restarts_an_owned_worker_with_missing_queues(self):
        result = self.run_launcher("""
$KeepBackend=$true
function Get-Command {[pscustomobject]@{Source='fake-python'}}
function Get-LocalCeleryWorkerPid {return 101}
function Test-CeleryWorkerReady {return $false}
function Get-CimInstance {[pscustomobject]@{Name='python.exe';ProcessId=101;CommandLine='python -m celery -A app.tasks.worker worker'}}
function Stop-Process {param($Id,[switch]$Force) $script:stopped=$Id}
function Wait-Until {}
function Write-Host {}
function Start-Process {param($FilePath,$ArgumentList,$WorkingDirectory,$RedirectStandardOutput,$RedirectStandardError,$WindowStyle)
 $script:started=$true}
Ensure-CeleryWorker
[pscustomobject]@{stopped=$script:stopped;started=$script:started}|ConvertTo-Json -Compress
""")
        self.assertEqual(result, {'stopped': 101, 'started': True})

    def test_startup_orders_schema_workers_scheduler_and_readiness_before_frontend(self):
        order = self.run_launcher("""
$script:order=@()
function Ensure-DatabaseSchema {$script:order+='schema'}
function Ensure-Backend {$script:order+='api'}
function Ensure-CeleryWorker {$script:order+='worker'}
function Ensure-CeleryBeat {$script:order+='beat'}
function Ensure-Frontend {$script:order+='frontend'}
function Wait-Until {param($Description,$Condition) $script:order+='readiness'}
$names=@('Ensure-DatabaseSchema','Ensure-Backend','Ensure-CeleryWorker','Ensure-CeleryBeat','Ensure-Frontend','Wait-Until')
foreach($statement in $ast.EndBlock.Statements) {
 if($statement -is [System.Management.Automation.Language.PipelineAst] -and
    $statement.PipelineElements[0].GetCommandName() -in $names) {Invoke-Expression $statement.Extent.Text}
}
$script:order|ConvertTo-Json -Compress
""")
        self.assertEqual(order, ['schema', 'api', 'worker', 'beat', 'readiness', 'frontend'])

    def test_beat_launch_uses_its_own_managed_pid_schedule_and_hidden_window(self):
        launch = self.run_launcher("""
function Get-Command {[pscustomobject]@{Source='fake-python'}}
function Get-LocalCeleryBeatPid {return $null}
function Get-CimInstance {return @()}
function Write-Host {}
function Wait-Until {}
function Start-Process {param($FilePath,$ArgumentList,$WorkingDirectory,$RedirectStandardOutput,$RedirectStandardError,$WindowStyle)
 $script:launch=[pscustomobject]@{arguments=$ArgumentList;window=$WindowStyle}}
Ensure-CeleryBeat
$script:launch|ConvertTo-Json -Compress
""")
        self.assertIn('beat', launch['arguments'])
        self.assertEqual(launch['window'], 'Hidden')
        self.assertTrue(any('celery-beat.pid' in argument for argument in launch['arguments']))
        self.assertTrue(any('celerybeat-schedule' in argument for argument in launch['arguments']))

    def test_database_preparation_runs_the_real_migration_entrypoint_before_readiness(self):
        arguments = self.run_launcher("""
function Get-Command {[pscustomobject]@{Source='Invoke-FakePython'}}
function Write-Host {}
function Invoke-FakePython {$global:LASTEXITCODE=0;$script:arguments=@($args)}
Ensure-DatabaseSchema
$script:arguments|ConvertTo-Json -Compress
""")
        self.assertEqual(arguments, ['-m', 'scripts.prepare_database'])


if __name__ == '__main__':
    unittest.main()
