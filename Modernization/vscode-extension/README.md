# Strat-Aqorynth Modernization VS Code Extension

Modernize code directly inside VS Code by calling the existing Modernization API.

## Features

- Modernize full active file from Command Palette.
- Modernize selected code from editor context menu.
- Replace current file directly or open generated result in preview.
- Trigger modernization from Copilot Chat through a dedicated participant.
- Use a dedicated Strat-Aqorynth Chat sidebar inside VS Code for a branded assistant workflow.

## Commands

- `Modernization: Modernize Active File`
- `Modernization: Modernize Selected Code`
- `Modernization: Open Strat-Aqorynth Chat`
- `Modernization: Open Extension Settings`

## Copilot Chat Integration

- Mention `@modernizer` in Copilot Chat.
- Use slash commands:
   - `/modernizeFile` to modernize and rewrite the active file.
   - `/modernizeSelection` to modernize and rewrite only the current selection.
- Then provide your instruction in natural language.

Examples:

- `@modernizer /modernizeFile Refactor to async patterns and add robust error handling`
- `@modernizer /modernizeSelection Optimize this block for performance and readability`

## Strat-Aqorynth Chat Sidebar

- Open `Modernization: Open Strat-Aqorynth Chat` from the Command Palette.
- The sidebar appears under the `Strat-Aqorynth` activity bar icon.
- Choose `Auto`, `Selection`, or `File` scope before sending your instruction.
- The sidebar reuses the same modernization backend and applies results directly to the active editor.
- Use `Open Native Chat` to jump from the sidebar into the built-in VS Code chat surface with `@modernizer`.

## Settings

- `modernization.apiBaseUrl` (default: `http://127.0.0.1:8084`)
- `modernization.authToken` (optional bearer token)
- `modernization.targetStack` (default: `aveva_mes`)
- `modernization.outputMode` (`single_file` or `project`, default `single_file`)
- `modernization.pollIntervalMs` (default: `1500`)
- `modernization.requestTimeoutSec` (default: `300`)

## Run and Debug the Extension

1. Open this folder in VS Code:
   - `Modernization/vscode-extension`
2. Press `F5` to launch the Extension Development Host.
3. In the host window, run a command from Command Palette:
   - `Modernization: Modernize Active File`
4. Ensure your backend is running:
   - `Modernization/api/server.py` on port `8084`

## Notes

- For direct in-editor replacement, keep `modernization.outputMode = single_file`.
- If API auth is enabled, set `modernization.authToken`.
- Chat edits apply directly to the active editor content when the modernization job completes.
