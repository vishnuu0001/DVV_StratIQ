[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$jobRoot = 'C:\Windows\Temp\modernization_jobs'
$reportPath = Join-Path $repoRoot 'Modernization\data\logs\build-failure-diagnostics.json'

$records = @()
if (Test-Path -LiteralPath $jobRoot) {
    foreach ($file in Get-ChildItem -LiteralPath $jobRoot -Filter '*.json' -File) {
        try {
            $job = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
            $build = $job.validation.build
            if ($build.checker -eq 'maven+npm-build' -and -not $build.passed) {
                $javaStructure = @()
                $frontendPaths = @()
                foreach ($property in $job.output.PSObject.Properties) {
                    $path = [string]$property.Name
                    $content = [string]$property.Value
                    if ($path.EndsWith('.java', [System.StringComparison]::OrdinalIgnoreCase)) {
                        $package = [regex]::Match($content, '(?m)^\s*package\s+([^;]+);').Groups[1].Value
                        $imports = @(
                            [regex]::Matches($content, '(?m)^\s*import\s+([^;]+);') |
                                ForEach-Object { $_.Groups[1].Value }
                        )
                        $declarations = @(
                            [regex]::Matches($content, '\b(?:class|interface|record|enum)\s+([A-Za-z_]\w*)') |
                                ForEach-Object { $_.Groups[1].Value }
                        )
                        $javaStructure += [pscustomobject]@{
                            path = $path
                            package = $package
                            imports = $imports
                            declarations = $declarations
                        }
                    } elseif ($path -match '/frontend/') {
                        $frontendPaths += $path
                    }
                }
                $records += [pscustomobject]@{
                    modified_at = $file.LastWriteTimeUtc.ToString('o')
                    job_id = $job.job_id
                    project_id = $job.project_id
                    status = $job.status
                    phase = $job.phase
                    created_at = $job.created_at
                    updated_at = $job.updated_at
                    target_stack = $job.target_stack
                    output_file_count = @($job.output.PSObject.Properties).Count
                    remaining_errors = $build.remaining_errors
                    java_structure = $javaStructure
                    frontend_paths = $frontendPaths
                }
            }
        } catch {
            continue
        }
    }
}
$records |
    Sort-Object modified_at -Descending |
    Select-Object -First 8 |
    ConvertTo-Json -Depth 12 |
    Set-Content -LiteralPath $reportPath -Encoding UTF8
