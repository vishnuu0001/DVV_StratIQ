Set-Location 'E:\stratIQ_VA-main\stratIQ_VA-main\Modernization'
Write-Host '== FILE CHECK =='
.\.venv\Scripts\python.exe .\tmp_list_app001_frontend.py
Write-Host '== APP MODULE =='
.\.venv\Scripts\python.exe .\tmp_read_appmodule_issue.py
Write-Host '== DIRECT FRONTEND BUILD =='
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tmp_repro_app001_frontend_build.ps1
Write-Host ('direct_exit=' + $LASTEXITCODE)
Write-Host '== BUILD RUNNER =='
.\.venv\Scripts\python.exe .\tmp_build_runner_repro.py
