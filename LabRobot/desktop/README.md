# Lab Robot Windows App

This project is a native Windows desktop shell built with WPF and Microsoft Edge WebView2. Claude, Google Flow (Veo), Microsoft Copilot, and Lab Robot load as top-level WebView2 documents inside the application window. They are not HTML iframes, so provider `frame-ancestors` restrictions do not apply.

## Prerequisites

- Windows 10 or Windows 11
- .NET 8 SDK
- Microsoft Edge WebView2 Runtime (included with current Windows/Edge installations)
- The Lab Robot frontend running locally, or the URL of a deployed Lab Robot frontend

## Run

For local development, register the `labrobot://` protocol for the current
Windows user once:

```powershell
./desktop/register-protocol.ps1
```

An administrator can register it for every user on the workstation:

```powershell
./desktop/register-protocol.ps1 -AllUsers
```

Then run the shell directly:

```powershell
./desktop/start.ps1
```

The deployed portal configuration is the default. It can also be supplied explicitly:

```powershell
./desktop/start.ps1 -LabRobotUrl "https://strat-iq.azurewebsites.net/lab/" -PortalBaseUrl "https://strat-iq.azurewebsites.net/"
```

Provider sign-in sessions are persisted in `%LOCALAPPDATA%\StratAqorynth\LabRobot\WebView2`.

## Authentication handoff

When an authenticated user selects Lab Robot in Launch Modules, the portal:

1. creates a random 60-second, single-use launch ticket bound to the user's current server session;
2. opens `labrobot://launch` with that ticket (never the access token);
3. lets the desktop shell redeem the ticket directly with the portal;
4. opens Lab Robot with a token tied to the same central session.

The desktop shell and Lab Robot backend revalidate the session and current
`LAB_ROBOT` permission with the portal. Logout, expiry, account disablement,
or removal of access sends the desktop window back to the portal login.

## Build

```powershell
dotnet build ./desktop/LabRobot.WindowsApp.csproj --configuration Release
```

## Publish

Create a 64-bit Windows package:

```powershell
dotnet publish ./desktop/LabRobot.WindowsApp.csproj --configuration Release --runtime win-x64 --self-contained false
```

The published executable is placed under `desktop/bin/Release/net8.0-windows10.0.19041.0/win-x64/publish/`.

Register the published executable instead of the development launcher:

```powershell
./desktop/register-protocol.ps1 -ExecutablePath "./desktop/bin/Release/net8.0-windows10.0.19041.0/win-x64/publish/LabRobot.WindowsApp.exe"
```
