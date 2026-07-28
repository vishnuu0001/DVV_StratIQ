@echo off
cd /d E:\stratIQ_VA-main\stratIQ_VA-main\Modernization
.venv\Scripts\python.exe tmp_list_app001_frontend.py
.venv\Scripts\python.exe tmp_read_appmodule_issue.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tmp_repro_app001_frontend_build.ps1
