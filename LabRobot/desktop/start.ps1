param(
    [string]$LabRobotUrl = "https://strat-iq.azurewebsites.net/lab/",
    [string]$PortalBaseUrl = "https://strat-iq.azurewebsites.net/",
    [string]$ProtocolUri = ""
)

$env:LAB_ROBOT_URL = $LabRobotUrl
$env:PORTAL_BASE_URL = $PortalBaseUrl
$projectPath = Join-Path $PSScriptRoot "LabRobot.WindowsApp.csproj"

if ($ProtocolUri) {
    dotnet run --project $projectPath -- $ProtocolUri
} else {
    dotnet run --project $projectPath
}
