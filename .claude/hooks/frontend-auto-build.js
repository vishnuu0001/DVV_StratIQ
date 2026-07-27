#!/usr/bin/env node
// PostToolUse hook (Edit|Write): when a change lands under any
// "<MicroApp>/frontend/src/**" path, kick off `npm run build` for that
// micro-app's frontend in the background so its build/dist output (served
// directly by IIS) stays current. Fire-and-forget: does not block the tool
// call, and no-ops silently for any path outside a recognized frontend/src.
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn, execFileSync } = require('child_process');

let raw = '';
process.stdin.on('data', (chunk) => {
  raw += chunk;
});
process.stdin.on('end', () => {
  let input;
  try {
    input = JSON.parse(raw || '{}');
  } catch {
    process.exit(0);
  }

  const filePath = input && input.tool_input && input.tool_input.file_path;
  if (!filePath) process.exit(0);

  const normalized = filePath.replace(/\\/g, '/');
  const match = normalized.match(/^(.*\/frontend)\/src\//i);
  if (!match) process.exit(0);

  const frontendDir = match[1].split('/').join(path.sep);
  const pkgPath = path.join(frontendDir, 'package.json');
  if (!fs.existsSync(pkgPath)) process.exit(0);

  let pkg;
  try {
    pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
  } catch {
    process.exit(0);
  }
  if (!pkg.scripts || !pkg.scripts.build) process.exit(0);

  const logDir = path.join(os.tmpdir(), 'claude-frontend-auto-build');
  fs.mkdirSync(logDir, { recursive: true });
  const logName = frontendDir.replace(/[:\\/]/g, '_');
  const logFile = path.join(logDir, `${logName}.log`);
  fs.appendFileSync(logFile, `\n[${new Date().toISOString()}] change: ${filePath}\n[${new Date().toISOString()}] running npm run build in ${frontendDir}\n`);

  if (process.platform === 'win32') {
    // This hook's own node.exe runs inside the calling harness's process
    // tree, which on Windows is tied to a job object that kills descendants
    // (however they're spawned — detached child_process, Start-Process, etc.)
    // the moment this process exits. A one-time Task Scheduler task runs via
    // a completely separate OS service, so the build survives independent of
    // this process's lifetime. The task deletes itself once the build ends.
    const taskName = `ClaudeAutoBuild_${logName}`;
    const batFile = path.join(logDir, `${logName}.bat`);
    fs.writeFileSync(
      batFile,
      // `call` is required: npm.cmd is itself a batch file, and invoking a
      // .cmd/.bat from another .bat without `call` transfers control into it
      // permanently — nothing after this line would ever run otherwise.
      `@echo off\r\ncd /d "${frontendDir}"\r\ncall npm run build >> "${logFile}" 2>&1\r\nschtasks /delete /tn "${taskName}" /f >nul 2>&1\r\n`
    );
    try {
      execFileSync('schtasks', ['/create', '/tn', taskName, '/tr', batFile, '/sc', 'once', '/st', '23:59', '/f'], {
        stdio: 'ignore',
      });
      execFileSync('schtasks', ['/run', '/tn', taskName], { stdio: 'ignore' });
    } catch {
      // best-effort automation; never fail the tool call over this
    }
  } else {
    const child = spawn('sh', ['-c', `npm run build >> "${logFile}" 2>&1`], {
      cwd: frontendDir,
      detached: true,
      stdio: 'ignore',
    });
    child.unref();
  }

  process.exit(0);
});
