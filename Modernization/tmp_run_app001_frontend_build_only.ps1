Set-Location 'E:\stratIQ_VA-main\stratIQ_VA-main\Modernization\data\projects\APP-001\outputs\v001\CreateAFullStackSolutionForABank\frontend'
$sw = [System.Diagnostics.Stopwatch]::StartNew()
if (-not (Test-Path node_modules)) {
  npm install
  Write-Host ('npm_install_exit=' + $LASTEXITCODE)
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
npm run build
$code = $LASTEXITCODE
$sw.Stop()
Write-Host ('elapsed_seconds=' + [math]::Round($sw.Elapsed.TotalSeconds, 1))
exit $code
