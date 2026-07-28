Set-Location 'E:\stratIQ_VA-main\stratIQ_VA-main\Modernization\data\projects\APP-001\outputs\v001\CreateAFullStackSolutionForABank\frontend'
if (-not (Test-Path node_modules)) {
    npm install
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
npm run build
exit $LASTEXITCODE
