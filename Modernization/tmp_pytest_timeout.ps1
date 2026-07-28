Set-Location 'E:\stratIQ_VA-main\stratIQ_VA-main\Modernization'
.\.venv\Scripts\python.exe -m pytest tests/test_build_runner_integrity.py::BuildRunnerIntegrityTests::test_npm_compile_uses_dedicated_frontend_build_timeout -vv --maxfail=1
exit $LASTEXITCODE
