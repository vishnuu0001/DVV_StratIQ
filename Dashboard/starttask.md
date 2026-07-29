$ollama = 'C:\Users\Vishnuu\AppData\Local\Programs\Ollama\ollama.exe'
$models = 'C:\Users\Vishnuu\.ollama\models'

$action = New-ScheduledTaskAction `
  -Execute 'powershell.exe' `
  -Argument "-NoProfile -WindowStyle Hidden -Command `"`$env:OLLAMA_MODELS='$models'; & '$ollama' serve`""

$trigger = New-ScheduledTaskTrigger -AtStartup

$principal = New-ScheduledTaskPrincipal `
  -UserId 'SYSTEM' `
  -LogonType ServiceAccount `
  -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
  -RestartCount 10 `
  -RestartInterval (New-TimeSpan -Minutes 1) `
  -ExecutionTimeLimit ([TimeSpan]::Zero)

Register-ScheduledTask `
  -TaskName 'StratIQ-Ollama' `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Force

Start-ScheduledTask -TaskName 'StratIQ-Ollama'