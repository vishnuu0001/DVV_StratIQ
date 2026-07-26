// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: Modernization — vscode-extension (extension.js)
// Date: 2026-07-11
// ---------------------------------------------------------------------------
const vscode = require("vscode");

// Function: getConfig
function getConfig() {
  const cfg = vscode.workspace.getConfiguration("modernization");
  return {
    apiBaseUrl: String(cfg.get("apiBaseUrl", "http://127.0.0.1:8084")).replace(/\/$/, ""),
    authToken: String(cfg.get("authToken", "")).trim(),
    targetStack: String(cfg.get("targetStack", "aveva_mes")).trim() || "aveva_mes",
    outputMode: String(cfg.get("outputMode", "single_file")).trim() || "single_file",
    pollIntervalMs: Math.max(500, Number(cfg.get("pollIntervalMs", 1500))),
    requestTimeoutSec: Math.max(30, Number(cfg.get("requestTimeoutSec", 300))),
  };
}

// Function: buildHeaders
function buildHeaders(authToken, extraHeaders = {}) {
  const headers = {
    ...extraHeaders,
  };
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }
  return headers;
}

// Function: getFullDocumentRange
function getFullDocumentRange(document) {
  const start = new vscode.Position(0, 0);
  const end = document.lineAt(document.lineCount - 1).range.end;
  return new vscode.Range(start, end);
}

// Function: sleep
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Function: createPromptJob
async function createPromptJob(config, promptText) {
  const payload = new URLSearchParams();
  payload.set("prompt", promptText);
  payload.set("target_stack", config.targetStack);
  payload.set("output_mode", config.outputMode);

  const response = await fetch(`${config.apiBaseUrl}/api/modernize/analyze-prompt`, {
    method: "POST",
    headers: buildHeaders(config.authToken, {
      "Content-Type": "application/x-www-form-urlencoded",
    }),
    body: payload,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Failed to create modernization job (${response.status}): ${body}`);
  }

  const json = await response.json();
  if (!json.job_id) {
    throw new Error("Modernization API returned no job_id.");
  }
  return json.job_id;
}

// Function: getJob
async function getJob(config, jobId) {
  const response = await fetch(`${config.apiBaseUrl}/api/modernize/jobs/${encodeURIComponent(jobId)}`, {
    headers: buildHeaders(config.authToken),
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Failed to fetch job ${jobId} (${response.status}): ${body}`);
  }
  return response.json();
}

// Function: waitForCompletion
async function waitForCompletion(config, jobId, progress) {
  const deadline = Date.now() + config.requestTimeoutSec * 1000;

  while (Date.now() < deadline) {
    const job = await getJob(config, jobId);
    const pct = Number(job.progress || 0);
    const phase = job.phase || "processing";
    progress.report({ message: `${phase} (${pct}%)`, increment: 0 });

    if (job.status === "completed") {
      return job;
    }
    if (job.status === "failed") {
      throw new Error(job.error || "Modernization job failed.");
    }

    await sleep(config.pollIntervalMs);
  }

  throw new Error("Modernization timed out before completion.");
}

// Function: applyModernizedOutput
async function applyModernizedOutput(editor, output, modeName, targetRange, options = {}) {
  const requireConfirmation = options.requireConfirmation !== false;
  const singleFile = output && output.__single_file__;
  if (!singleFile) {
    throw new Error(
      `No __single_file__ output found. Current mode may be project mode (${modeName}). ` +
        "Set modernization.outputMode to single_file for direct replacement."
    );
  }

  if (requireConfirmation) {
    const action = await vscode.window.showWarningMessage(
      "Modernized code is ready.",
      "Replace Current File",
      "Open Preview"
    );

    if (!action) {
      return false;
    }

    if (action === "Open Preview") {
      const doc = await vscode.workspace.openTextDocument({
        language: editor.document.languageId,
        content: singleFile,
      });
      await vscode.window.showTextDocument(doc, { preview: true });
      return false;
    }
  }

  const rangeToReplace = targetRange || getFullDocumentRange(editor.document);
  const ok = await editor.edit((editBuilder) => {
    editBuilder.replace(rangeToReplace, singleFile);
  });
  return ok;
}

// Function: buildPrompt
function buildPrompt(userInstruction, contextLabel, sourceCode, languageId) {
  return [
    "You are modernizing code for production readiness.",
    `Instruction: ${userInstruction}`,
    `Context: ${contextLabel}`,
    `Language: ${languageId}`,
    "Return complete improved code.",
    "SOURCE CODE:",
    sourceCode,
  ].join("\n\n");
}

// Function: getModernizationInput
function getModernizationInput(editor, selectionOnly) {
  const doc = editor.document;
  const hasSelection = editor.selection && !editor.selection.isEmpty;
  const selectedText = hasSelection ? doc.getText(editor.selection) : "";
  const sourceText = selectionOnly ? selectedText : doc.getText();
  const contextLabel = selectionOnly
    ? `${doc.fileName} (selected region)`
    : `${doc.fileName} (entire file)`;
  const targetRange = selectionOnly && hasSelection ? editor.selection : undefined;

  return {
    doc,
    hasSelection,
    sourceText,
    contextLabel,
    targetRange,
  };
}

// Function: runModernizationRequest
async function runModernizationRequest({
  editor,
  selectionOnly,
  instruction,
  onProgress,
  requireConfirmation,
  cancellationToken,
}) {
  const config = getConfig();
  const { doc, hasSelection, sourceText, contextLabel, targetRange } = getModernizationInput(editor, selectionOnly);

  if (selectionOnly && !hasSelection) {
    throw new Error("No selection found. Select code first or use /modernizeFile.");
  }

  if (!sourceText.trim()) {
    throw new Error("No source code found to modernize.");
  }

  const prompt = buildPrompt(instruction.trim(), contextLabel, sourceText, doc.languageId);

  // Function: report
  const report = (message) => {
    if (onProgress) {
      onProgress(message);
    }
  };

  report("Submitting request...");
  const jobId = await createPromptJob(config, prompt);

  const progressShim = {
    report: ({ message }) => {
      if (cancellationToken && cancellationToken.isCancellationRequested) {
        throw new Error("Modernization was cancelled.");
      }
      report(message || "Processing...");
    },
  };

  const job = await waitForCompletion(config, jobId, progressShim);
  const applied = await applyModernizedOutput(
    editor,
    job.output,
    config.outputMode,
    targetRange,
    { requireConfirmation }
  );

  return {
    jobId,
    applied,
    fileName: doc.fileName,
    selectionOnly,
  };
}

// Function: runModernization
async function runModernization({ selectionOnly }) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage("No active editor found.");
    return;
  }

  const input = getModernizationInput(editor, selectionOnly);
  const sourceText = input.sourceText;

  if (!sourceText.trim()) {
    vscode.window.showErrorMessage("No source code found to modernize.");
    return;
  }

  const instruction = await vscode.window.showInputBox({
    title: selectionOnly ? "Modernize Selected Code" : "Modernize Active File",
    prompt: "Describe how you want the code modernized.",
    placeHolder: "Example: Refactor to async patterns, improve error handling, and optimize performance",
    ignoreFocusOut: true,
    validateInput: (value) => (value && value.trim() ? null : "Instruction is required."),
  });

  if (!instruction) {
    return;
  }

  await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title: "Modernization in progress",
      cancellable: false,
    },
    async (progress) => {
      const result = await runModernizationRequest({
        editor,
        selectionOnly,
        instruction,
        onProgress: (message) => progress.report({ message, increment: 0 }),
        requireConfirmation: true,
      });
      const jobId = result.jobId;
      vscode.window.showInformationMessage(`Modernization completed (job ${jobId}).`);
    }
  );
}

// Function: registerChatParticipant
function registerChatParticipant(context) {
  if (!vscode.chat || typeof vscode.chat.createChatParticipant !== "function") {
    return;
  }

  const participant = vscode.chat.createChatParticipant(
    "strat-aqorynth-modernization-extension.modernizer",
    async (request, chatContext, stream, token) => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        stream.markdown("Open a file in the editor, then try again.");
        return { metadata: { status: "no_editor" } };
      }

      const hasSelection = editor.selection && !editor.selection.isEmpty;
      const selectionOnly = request.command === "modernizeSelection"
        ? true
        : request.command === "modernizeFile"
          ? false
          : hasSelection;

      const instruction = String(request.prompt || "").trim();
      if (!instruction) {
        stream.markdown("Provide a modernization instruction. Example: optimize this logic, improve error handling, and modernize patterns.");
        return { metadata: { status: "missing_instruction" } };
      }

      try {
        const result = await runModernizationRequest({
          editor,
          selectionOnly,
          instruction,
          onProgress: (message) => stream.progress(message),
          requireConfirmation: false,
          cancellationToken: token,
        });

        const scopeText = result.selectionOnly ? "selection" : "file";
        stream.markdown(`Modernization applied to the active ${scopeText}. Job ID: ${result.jobId}.`);
        stream.reference(editor.document.uri);
        return {
          metadata: {
            status: "completed",
            jobId: result.jobId,
            command: request.command || "auto",
          },
        };
      } catch (err) {
        stream.markdown(`Modernization failed: ${err.message || String(err)}`);
        return {
          metadata: {
            status: "failed",
            error: err.message || String(err),
          },
        };
      }
    }
  );

  participant.followupProvider = {
    provideFollowups(result) {
      if (!result || !result.metadata || result.metadata.status !== "completed") {
        return [];
      }
      return [
        {
          prompt: "Apply one more pass focused on performance",
          label: "Optimize performance",
        },
        {
          prompt: "Apply one more pass focused on readability and naming",
          label: "Improve readability",
        },
      ];
    },
  };

  context.subscriptions.push(participant);
}

class Strat-AqorynthChatSidebarProvider {
  static viewType = "modernization.chatSidebar";
  static stateKey = "modernization.chatSidebar.messages";

  constructor(context) {
    this.context = context;
    this.view = undefined;
    this.messages = Array.isArray(context.workspaceState.get(Strat-AqorynthChatSidebarProvider.stateKey))
      ? context.workspaceState.get(Strat-AqorynthChatSidebarProvider.stateKey)
      : [];
  }

  resolveWebviewView(webviewView) {
    this.view = webviewView;
    webviewView.webview.options = {
      enableScripts: true,
    };
    webviewView.webview.html = this.getHtml(webviewView.webview);

    webviewView.onDidDispose(() => {
      if (this.view === webviewView) {
        this.view = undefined;
      }
    });

    webviewView.webview.onDidReceiveMessage(async (message) => {
      if (!message || typeof message !== "object") {
        return;
      }

      if (message.type === "ready") {
        this.syncState();
        return;
      }

      if (message.type === "openSettings") {
        await vscode.commands.executeCommand("modernization.openSettings");
        return;
      }

      if (message.type === "openNativeChat") {
        await vscode.commands.executeCommand("workbench.action.chat.open", "@modernizer ");
        return;
      }

      if (message.type === "clearHistory") {
        this.messages = [];
        await this.persistMessages();
        this.syncState();
        return;
      }

      if (message.type === "submitPrompt") {
        await this.handlePromptSubmission(message);
      }
    });

    this.syncState();
  }

  async handlePromptSubmission(message) {
    const instruction = String(message.prompt || "").trim();
    if (!instruction) {
      this.postMessage({
        type: "requestValidation",
        error: "Instruction is required.",
      });
      return;
    }

    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      this.appendMessage("assistant", "Open a file in the editor before sending a modernization request.");
      return;
    }

    const scope = message.scope === "selection" || message.scope === "file" ? message.scope : "auto";
    const selectionOnly = scope === "selection"
      ? true
      : scope === "file"
        ? false
        : !!(editor.selection && !editor.selection.isEmpty);

    const requestId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
    const scopeLabel = selectionOnly ? "selection" : "file";

    this.appendMessage("user", instruction, { scope: scopeLabel, fileName: editor.document.fileName });
    this.postMessage({ type: "requestStarted", requestId });
    this.upsertPendingAssistantMessage(requestId, `Submitting modernization request for the active ${scopeLabel}...`);

    try {
      const result = await runModernizationRequest({
        editor,
        selectionOnly,
        instruction,
        onProgress: (progressMessage) => {
          this.upsertPendingAssistantMessage(requestId, progressMessage);
        },
        requireConfirmation: false,
      });

      const completionText = `Applied modernization to the active ${result.selectionOnly ? "selection" : "file"}. Job ID: ${result.jobId}.`;
      this.resolvePendingAssistantMessage(requestId, completionText, {
        jobId: result.jobId,
        fileName: result.fileName,
      });
      vscode.window.setStatusBarMessage("Strat-Aqorynth modernization applied.", 3000);
    } catch (err) {
      this.resolvePendingAssistantMessage(
        requestId,
        `Modernization failed: ${err.message || String(err)}`,
        { isError: true }
      );
    } finally {
      this.postMessage({ type: "requestFinished", requestId });
      this.syncContext();
    }
  }

  appendMessage(role, text, extra = {}) {
    const entry = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
      role,
      text,
      timestamp: new Date().toISOString(),
      ...extra,
    };
    this.messages = [...this.messages, entry].slice(-50);
    this.persistAndSync();
    return entry;
  }

  upsertPendingAssistantMessage(requestId, text) {
    const existingIndex = this.messages.findIndex((entry) => entry.pending && entry.requestId === requestId);
    if (existingIndex >= 0) {
      const nextMessages = [...this.messages];
      nextMessages[existingIndex] = {
        ...nextMessages[existingIndex],
        text,
        timestamp: new Date().toISOString(),
      };
      this.messages = nextMessages;
    } else {
      this.messages = [
        ...this.messages,
        {
          id: `${requestId}-assistant`,
          requestId,
          role: "assistant",
          text,
          pending: true,
          timestamp: new Date().toISOString(),
        },
      ].slice(-50);
    }
    this.persistAndSync();
  }

  resolvePendingAssistantMessage(requestId, text, extra = {}) {
    const existingIndex = this.messages.findIndex((entry) => entry.pending && entry.requestId === requestId);
    if (existingIndex >= 0) {
      const nextMessages = [...this.messages];
      nextMessages[existingIndex] = {
        ...nextMessages[existingIndex],
        ...extra,
        text,
        pending: false,
        timestamp: new Date().toISOString(),
      };
      this.messages = nextMessages;
    } else {
      this.messages = [
        ...this.messages,
        {
          id: `${requestId}-assistant-final`,
          requestId,
          role: "assistant",
          text,
          pending: false,
          timestamp: new Date().toISOString(),
          ...extra,
        },
      ].slice(-50);
    }
    this.persistAndSync();
  }

  async persistMessages() {
    await this.context.workspaceState.update(Strat-AqorynthChatSidebarProvider.stateKey, this.messages);
  }

  persistAndSync() {
    this.persistMessages();
    this.syncState();
  }

  syncState() {
    this.postMessage({ type: "state", messages: this.messages });
    this.syncContext();
  }

  syncContext() {
    const editor = vscode.window.activeTextEditor;
    this.postMessage({
      type: "editorContext",
      editor: editor
        ? {
            fileName: editor.document.fileName,
            languageId: editor.document.languageId,
            hasSelection: !!(editor.selection && !editor.selection.isEmpty),
          }
        : null,
    });
  }

  postMessage(message) {
    if (this.view) {
      this.view.webview.postMessage(message);
    }
  }

  getHtml(webview) {
    const nonce = String(Date.now());
    return `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${webview.cspSource} https:; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Strat-Aqorynth Chat</title>
    <style>
      :root {
        color-scheme: light dark;
        --bg: var(--vscode-sideBar-background);
        --fg: var(--vscode-foreground);
        --muted: var(--vscode-descriptionForeground);
        --panel: var(--vscode-editorWidget-background);
        --border: var(--vscode-panel-border);
        --accent: var(--vscode-button-background);
        --accent-fg: var(--vscode-button-foreground);
        --accent-hover: var(--vscode-button-hoverBackground);
        --input-bg: var(--vscode-input-background);
        --input-fg: var(--vscode-input-foreground);
        --user-bg: color-mix(in srgb, var(--accent) 16%, transparent);
        --assistant-bg: color-mix(in srgb, var(--panel) 88%, white 12%);
        --error: var(--vscode-errorForeground);
        font-family: var(--vscode-font-family);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        background: radial-gradient(circle at top, color-mix(in srgb, var(--accent) 18%, var(--bg)) 0%, var(--bg) 52%);
        color: var(--fg);
      }

      .layout {
        display: grid;
        grid-template-rows: auto auto 1fr auto;
        min-height: 100vh;
      }

      .hero {
        padding: 16px 16px 10px;
        border-bottom: 1px solid var(--border);
        background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 15%, transparent), transparent);
      }

      .eyebrow {
        margin: 0 0 4px;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted);
      }

      h1 {
        margin: 0;
        font-size: 18px;
        line-height: 1.2;
      }

      .subcopy {
        margin: 6px 0 0;
        color: var(--muted);
        font-size: 12px;
        line-height: 1.45;
      }

      .context {
        margin: 12px 16px 0;
        padding: 10px 12px;
        border: 1px solid var(--border);
        border-radius: 12px;
        background: color-mix(in srgb, var(--panel) 92%, transparent);
        font-size: 12px;
      }

      .context strong {
        display: block;
        margin-bottom: 4px;
      }

      .messages {
        padding: 12px 16px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        overflow-y: auto;
      }

      .empty {
        padding: 14px;
        border: 1px dashed var(--border);
        border-radius: 12px;
        color: var(--muted);
        background: color-mix(in srgb, var(--panel) 75%, transparent);
        font-size: 12px;
        line-height: 1.5;
      }

      .message {
        padding: 12px;
        border-radius: 14px;
        border: 1px solid transparent;
        white-space: pre-wrap;
        word-break: break-word;
      }

      .message.user {
        background: var(--user-bg);
        border-color: color-mix(in srgb, var(--accent) 26%, transparent);
      }

      .message.assistant {
        background: var(--assistant-bg);
        border-color: var(--border);
      }

      .message.error {
        border-color: color-mix(in srgb, var(--error) 55%, transparent);
      }

      .meta {
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        gap: 8px;
        font-size: 11px;
        color: var(--muted);
      }

      .composer {
        padding: 12px 16px 16px;
        border-top: 1px solid var(--border);
        display: grid;
        gap: 10px;
        background: color-mix(in srgb, var(--bg) 85%, black 15%);
      }

      .scope-row,
      .button-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }

      button {
        border: 1px solid var(--border);
        background: transparent;
        color: var(--fg);
        border-radius: 999px;
        padding: 7px 12px;
        cursor: pointer;
        font: inherit;
      }

      button.primary {
        background: var(--accent);
        color: var(--accent-fg);
        border-color: transparent;
      }

      button.primary:hover {
        background: var(--accent-hover);
      }

      button.active {
        border-color: var(--accent);
        box-shadow: inset 0 0 0 1px var(--accent);
      }

      button:disabled {
        opacity: 0.6;
        cursor: default;
      }

      textarea {
        width: 100%;
        min-height: 110px;
        resize: vertical;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: var(--input-bg);
        color: var(--input-fg);
        padding: 12px;
        font: inherit;
      }

      .hint,
      .error-text {
        font-size: 12px;
        color: var(--muted);
      }

      .error-text {
        color: var(--error);
      }
    </style>
  </head>
  <body>
    <div class="layout">
      <section class="hero">
        <p class="eyebrow">Strat-Aqorynth Assistant</p>
        <h1>Modernization Chat</h1>
        <p class="subcopy">Use the active file or selection as working context and apply the modernization result directly in the editor.</p>
      </section>
      <section class="context" id="contextPanel">
        <strong>No active editor</strong>
        Open a file to start a modernization request.
      </section>
      <main class="messages" id="messages"></main>
      <section class="composer">
        <div class="scope-row">
          <button type="button" class="active" data-scope="auto">Auto</button>
          <button type="button" data-scope="selection">Selection</button>
          <button type="button" data-scope="file">File</button>
        </div>
        <textarea id="promptInput" placeholder="Example: Refactor this code to async patterns, improve resilience, and simplify control flow."></textarea>
        <div class="error-text" id="errorText"></div>
        <div class="button-row">
          <button type="button" class="primary" id="sendButton">Send</button>
          <button type="button" id="nativeChatButton">Open Native Chat</button>
          <button type="button" id="settingsButton">Settings</button>
          <button type="button" id="clearButton">Clear</button>
        </div>
        <div class="hint">Auto uses the current selection when one exists, otherwise the full active file.</div>
      </section>
    </div>
    <script nonce="${nonce}">
      const vscode = acquireVsCodeApi();
      const state = {
        scope: 'auto',
        messages: [],
        busy: false,
      };

      const messagesEl = document.getElementById('messages');
      const promptInput = document.getElementById('promptInput');
      const errorText = document.getElementById('errorText');
      const sendButton = document.getElementById('sendButton');
      const contextPanel = document.getElementById('contextPanel');

      // Function: escapeHtml
      function escapeHtml(value) {
        return String(value)
          .replace(/&/g, '&amp;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;');
      }

      // Function: renderMessages
      function renderMessages() {
        if (!state.messages.length) {
          messagesEl.innerHTML = '<div class="empty">Ask Strat-Aqorynth to modernize the active file or the current selection. The result is applied directly in the editor using the same workflow as the existing chat participant.</div>';
          return;
        }

        messagesEl.innerHTML = state.messages.map((message) => {
          const roleLabel = message.role === 'user' ? 'You' : 'Strat-Aqorynth';
          const extra = [];
          if (message.scope) extra.push(message.scope);
          if (message.jobId) extra.push('job ' + message.jobId);
          const metaRight = extra.length ? escapeHtml(extra.join(' | ')) : '&nbsp;';
          const classes = ['message', message.role];
          if (message.isError) classes.push('error');
          return '<article class="' + classes.join(' ') + '">' +
            '<div class="meta"><span>' + roleLabel + '</span><span>' + metaRight + '</span></div>' +
            '<div>' + escapeHtml(message.text) + '</div>' +
          '</article>';
        }).join('');
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }

      // Function: renderContext
      function renderContext(editor) {
        if (!editor) {
          contextPanel.innerHTML = '<strong>No active editor</strong>Open a file to start a modernization request.';
          return;
        }
        const modeText = editor.hasSelection ? 'Selection available' : 'No selection, file scope available';
        contextPanel.innerHTML = '<strong>' + escapeHtml(editor.fileName) + '</strong>' +
          '<div>Language: ' + escapeHtml(editor.languageId) + '</div>' +
          '<div>' + escapeHtml(modeText) + '</div>';
      }

      // Function: renderScopeButtons
      function renderScopeButtons() {
        document.querySelectorAll('[data-scope]').forEach((button) => {
          button.classList.toggle('active', button.dataset.scope === state.scope);
        });
      }

      // Function: renderBusy
      function renderBusy() {
        sendButton.disabled = state.busy;
        sendButton.textContent = state.busy ? 'Sending...' : 'Send';
      }

      // Function: submitPrompt
      function submitPrompt() {
        const prompt = promptInput.value.trim();
        errorText.textContent = '';
        vscode.postMessage({
          type: 'submitPrompt',
          prompt,
          scope: state.scope,
        });
      }

      document.querySelectorAll('[data-scope]').forEach((button) => {
        button.addEventListener('click', () => {
          state.scope = button.dataset.scope;
          renderScopeButtons();
        });
      });

      sendButton.addEventListener('click', submitPrompt);
      document.getElementById('settingsButton').addEventListener('click', () => vscode.postMessage({ type: 'openSettings' }));
      document.getElementById('nativeChatButton').addEventListener('click', () => vscode.postMessage({ type: 'openNativeChat' }));
      document.getElementById('clearButton').addEventListener('click', () => vscode.postMessage({ type: 'clearHistory' }));
      promptInput.addEventListener('keydown', (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
          submitPrompt();
        }
      });

      window.addEventListener('message', (event) => {
        const message = event.data;
        if (!message || typeof message !== 'object') {
          return;
        }

        if (message.type === 'state') {
          state.messages = Array.isArray(message.messages) ? message.messages : [];
          renderMessages();
          return;
        }

        if (message.type === 'editorContext') {
          renderContext(message.editor || null);
          return;
        }

        if (message.type === 'requestValidation') {
          errorText.textContent = message.error || 'Unable to send request.';
          return;
        }

        if (message.type === 'requestStarted') {
          state.busy = true;
          renderBusy();
          return;
        }

        if (message.type === 'requestFinished') {
          state.busy = false;
          promptInput.value = '';
          renderBusy();
        }
      });

      renderMessages();
      renderScopeButtons();
      renderBusy();
      vscode.postMessage({ type: 'ready' });
    </script>
  </body>
</html>`;
  }
}

// Function: activate
function activate(context) {
  const sidebarProvider = new Strat-AqorynthChatSidebarProvider(context);
  const modernizeActiveFile = vscode.commands.registerCommand("modernization.modernizeActiveFile", async () => {
    try {
      await runModernization({ selectionOnly: false });
    } catch (err) {
      vscode.window.showErrorMessage(`Modernization failed: ${err.message || String(err)}`);
    }
  });

  const modernizeSelection = vscode.commands.registerCommand("modernization.modernizeSelection", async () => {
    try {
      await runModernization({ selectionOnly: true });
    } catch (err) {
      vscode.window.showErrorMessage(`Modernization failed: ${err.message || String(err)}`);
    }
  });

  const openSettings = vscode.commands.registerCommand("modernization.openSettings", async () => {
    await vscode.commands.executeCommand("workbench.action.openSettings", "modernization.");
  });

  const openChatSidebar = vscode.commands.registerCommand("modernization.openChatSidebar", async () => {
    await vscode.commands.executeCommand("workbench.view.extension.stratiqModernization");
    await vscode.commands.executeCommand("modernization.chatSidebar.focus");
  });

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(Strat-AqorynthChatSidebarProvider.viewType, sidebarProvider, {
      webviewOptions: {
        retainContextWhenHidden: true,
      },
    })
  );

  context.subscriptions.push(
    vscode.window.onDidChangeActiveTextEditor(() => {
      sidebarProvider.syncContext();
    }),
    vscode.window.onDidChangeTextEditorSelection(() => {
      sidebarProvider.syncContext();
    })
  );

  registerChatParticipant(context);

  context.subscriptions.push(modernizeActiveFile, modernizeSelection, openChatSidebar, openSettings);
}

// Function: deactivate
function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
