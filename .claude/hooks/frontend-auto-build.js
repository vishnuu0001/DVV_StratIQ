#!/usr/bin/env node
// PostToolUse hook (Edit|Write): when a change lands under a "src/**" path
// belonging to some frontend project, kick off `npm run build` for that
// project in the background so its build/dist output (served directly by
// IIS) stays current. Fire-and-forget: does not block the tool call, and
// no-ops silently for any path that isn't under a recognized project's src.
//
// The project root is found by walking up from the edited file looking for
// the nearest ancestor with a package.json exposing a "build" script — this
// covers every naming convention used in this monorepo (.../frontend/src/,
// .../ui/src/, etc.) rather than hardcoding a single folder name.
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
  const srcMatch = normalized.match(/^(.*)\/src\//i);
  if (!srcMatch) process.exit(0);

  // Walk up from the "src" parent looking for the nearest package.json with
  // a build script — bounded so an edit deep in node_modules or similar
  // can't walk all the way to a monorepo root and build something huge.
  let dir = srcMatch[1].split('/').join(path.sep);
  let frontendDir = null;
  let pkg = null;
  for (let i = 0; i < 4 && dir; i++) {
    const pkgPath = path.join(dir, 'package.json');
    if (fs.existsSync(pkgPath)) {
      try {
        pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      } catch {
        process.exit(0);
      }
      frontendDir = dir;
      break;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  if (!frontendDir || !pkg) process.exit(0);
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
