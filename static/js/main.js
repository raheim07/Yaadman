/* ── YaadmanLang IDE · main.js (Monaco edition) ─── */

// ── EXAMPLE SNIPPETS ─────────────────────────────────
const SNIPPETS = {
  hello: `Start{\nShow "Hello, Yaadman!";\nShow "Welcome to the IDE";\n}Done;`,
  vars: `Start{\n//Declare vairables\nMek name Text;\nMek version Number;\nMek active Boolean;
  //Initialize variables\nSet name To "Yaadman";\nSet version To 1.0;\nSet active To True;
  //Print variables\nShow name,version,"Active: ",active;\n}Done;`,
  loop: `Start{\nFor (Mek i Number: i < 3: Set i To i + 1) {\nShow "Step: ", i;\n}\n}Done;`,
  func: `Start{\nFunction add(a Number, b Number) {\nMek result Number;\nSet result To a + b;\nShow "Result is: ",result;\nReturn result;\n}\nadd(5,5);\n}Done;`,
};

// ── SHARED ELEMENTS ───────────────────────────────────
const outputContent = document.getElementById("outputContent");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");
const execTimeEl = document.getElementById("execTime");
const tokenGrid = document.getElementById("tokenGrid");
const toast = document.getElementById("toast");
const astGrid = document.getElementById("astGrid");
const analyzeAstBtn = document.getElementById("analyzeAstBtn");

// ── STATUS ────────────────────────────────────────────
function setStatus(state, text) {
  statusDot.className = `status-dot ${state}`;
  statusText.textContent = text;
}

// ── TOAST ─────────────────────────────────────────────
let toastTimer;
function showToast(msg) {
  clearTimeout(toastTimer);
  toast.textContent = msg;
  toast.classList.add("show");
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
}

// ── HELPERS ───────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── PANEL SWITCHING ───────────────────────────────────
function switchPanel(id) {
  document
    .querySelectorAll(".panel")
    .forEach((p) => p.classList.remove("active"));
  document
    .querySelectorAll(".nav-btn")
    .forEach((b) => b.classList.remove("active"));
  const panel = document.getElementById(`panel-${id}`);
  const btn = document.querySelector(`[data-panel="${id}"]`);
  if (panel) panel.classList.add("active");
  if (btn) btn.classList.add("active");
}
document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => switchPanel(btn.dataset.panel));
});

// ── RUN CODE ──────────────────────────────────────────
async function runCode(editor) {
  if (!editor) {
    showToast("Editor not ready");
    return;
  }
  const code = editor.getValue().trim();
  if (!code) {
    showToast("Nothing to run!");
    return;
  }

  setStatus("running", "Running…");
  outputContent.innerHTML = `<span style="color:var(--text-muted)">// Running…</span>`;

  const t0 = performance.now();
  try {
    const res = await fetch("/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await res.json();
    const ms = (performance.now() - t0).toFixed(1);
    execTimeEl.textContent = `${ms} ms`;

    if (data.success) {
      outputContent.innerHTML = `<span class="output-success">${escHtml(data.output || "(no output)")}</span>`;
      setStatus("success", "Done");
    } else {
      outputContent.innerHTML = `<span class="output-error">── Error ──\n${escHtml(data.error)}</span>`;
      setStatus("error", "Error");
    }
  } catch (err) {
    outputContent.innerHTML = `<span class="output-error">Network error: ${escHtml(err.message)}</span>`;
    setStatus("error", "Network error");
  }
}

// ── TOKEN ANALYSIS ────────────────────────────────────
const TOKEN_COLORS = {
  KEYWORD: "#c8f75e",
  IDENTIFIER: "#6ee7ff",
  NUMBER: "#ffb347",
  STRING: "#ff8fa3",
  OPERATOR: "#d0a0ff",
  TOKEN: "#8890b0",
};

async function analyzeTokens(editor) {
  if (!editor) {
    showToast("Editor not ready");
    return;
  }
  const code = editor.getValue().trim();
  if (!code) {
    showToast("No code to analyze");
    return;
  }

  tokenGrid.innerHTML = `<span class="token-placeholder">Analyzing…</span>`;
  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await res.json();
    renderTokens(data.tokens || []);
  } catch (err) {
    tokenGrid.innerHTML = `<span class="output-error">Error: ${escHtml(err.message)}</span>`;
  }
}

function renderTokens(tokens) {
  if (!tokens.length) {
    tokenGrid.innerHTML = `<span class="token-placeholder">No tokens found.</span>`;
    return;
  }
  tokenGrid.innerHTML = tokens
    .map((t, i) => {
      const color = TOKEN_COLORS[t.type] || TOKEN_COLORS.TOKEN;
      return `<div class="token-chip" style="animation-delay:${i * 0.02}s">
      <span class="token-type" style="color:${color}">${escHtml(t.type)}</span>
      <span class="token-value">${escHtml(String(t.value))}</span>
      <span class="token-index">#${t.index}</span>
    </div>`;
    })
    .join("");
}

// ── COPY OUTPUT ───────────────────────────────────────
document.getElementById("copyBtn").addEventListener("click", () => {
  navigator.clipboard
    .writeText(outputContent.textContent)
    .then(() => showToast("Copied!"));
});

// ── MONACO SETUP ─────────────────────────────────────
require.config({
  paths: {
    vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs",
  },
});

require(["vs/editor/editor.main"], function () {
  // Register YaadmanLang as a custom language
  monaco.languages.register({ id: "yaadman" });

  monaco.languages.setMonarchTokensProvider("yaadman", {
    keywords: [
      "Start",
      "Done",
      "Mek",
      "Set",
      "To",
      "Show",
      "Tek",
      "if",
      "Else",
      "While",
      "For",
      "Function",
      "Return",
      "Try",
      "Ketch",
      "Number",
      "Text",
      "Boolean",
      "True",
      "False",
    ],
    tokenizer: {
      root: [
        [/\/\/.*$/, "comment"],
        [/"[^"]*"/, "string"],
        [/'[^']*'/, "string"],
        [/\b\d+(\.\d+)?\b/, "number"],
        [
          /\b(Start|Done|Mek|Set|To|Show|Tek|if|Else|While|For|Function|Return|Try|Ketch|Number|Text|Boolean|True|False)\b/,
          "keyword",
        ],
        [/[a-zA-Z_]\w*/, "identifier"],
        [/[=+\-*/<>!&|]+/, "operator"],
      ],
    },
  });

  monaco.editor.defineTheme("yaadman-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "c8f75e", fontStyle: "bold" },
      { token: "string", foreground: "ff8fa3" },
      { token: "number", foreground: "ffb347" },
      { token: "comment", foreground: "454d6a", fontStyle: "italic" },
      { token: "identifier", foreground: "6ee7ff" },
      { token: "operator", foreground: "d0a0ff" },
    ],
    colors: {
      "editor.background": "#0a0b0e",
      "editor.foreground": "#e8eaf2",
      "editorLineNumber.foreground": "#454d6a",
      "editorLineNumber.activeForeground": "#c8f75e",
      "editorCursor.foreground": "#c8f75e",
      "editor.selectionBackground": "#1f2235",
      "editorIndentGuide.background": "#1e2236",
      "editor.lineHighlightBackground": "#0f1117",
    },
  });

  const editor = monaco.editor.create(document.getElementById("monacoEditor"), {
    language: "yaadman",
    theme: "yaadman-dark",
    fontSize: 13.5,
    fontFamily: "'JetBrains Mono', monospace",
    fontLigatures: true,
    lineHeight: 24,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    padding: { top: 14, bottom: 14 },
    value: `Start{\n//Write your YaadmanLang code here\nShow "Hello, Yaadman!";\n}Done;`,
  });

  // ── Ctrl+Enter to run (inside Monaco) ──
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () =>
    runCode(editor),
  );

  // ── Button: Run ──
  document
    .getElementById("runBtn")
    .addEventListener("click", () => runCode(editor));

// Button: run LLM
const llmRunBtn = document.getElementById("llmRunBtn");

llmRunBtn.addEventListener("click", () => {
  runWithLLM(editor);
});


  // ── Button: Clear ──
  document.getElementById("clearBtn").addEventListener("click", () => {
    editor.setValue("");
    outputContent.innerHTML = `<span class="output-placeholder">// Output will appear here...</span>`;
    execTimeEl.textContent = "";
    setStatus("", "Ready");
    showToast("Editor cleared");
    editor.focus();
  });

  // ── Button: Analyze tokens ──
  document
    .getElementById("analyzeBtn")
    .addEventListener("click", () => analyzeTokens(editor));

  // ── Sidebar example snippets ──
  document.querySelectorAll(".example-item").forEach((item) => {
    item.addEventListener("click", () => {
      const snippet = SNIPPETS[item.dataset.snippet];
      if (snippet) {
        editor.setValue(snippet);
        switchPanel("editor");
        editor.focus();
        showToast(`Loaded: ${item.textContent}`);
      }
    });
  });

  // ── Global keyboard shortcuts (outside Monaco) ──
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "l") {
      e.preventDefault();
      document.getElementById("clearBtn").click();
    }
    if ((e.ctrlKey || e.metaKey) && e.key === "t") {
      e.preventDefault();
      switchPanel("tokens");
    }
  });

  // Generater AST
  async function analyzeAST(editor) {
    if (!editor) {
      showToast("Editor not ready");
      return;
    }

    const code = editor.getValue().trim();
    if (!code) {
      showToast("No code to analyze");
      return;
    }

    astGrid.innerHTML = `<span class="token-placeholder">Building AST…</span>`;

    try {
      const res = await fetch("/ast", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      const data = await res.json();

      if (data.error) {
        astGrid.innerHTML = `<span class="output-error">${escHtml(data.error)}</span>`;
        return;
      }

      renderAST(data.ast);
    } catch (err) {
      astGrid.innerHTML = `<span class="output-error">Error: ${escHtml(err.message)}</span>`;
    }
  }
  analyzeAstBtn.addEventListener("click", () => {
    analyzeAST(editor); // assuming you already have editor
  });

  // Render Tree

  function renderAST(ast) {
    if (!ast) {
      astGrid.innerHTML = `<span class="token-placeholder">No AST generated.</span>`;
      return;
    }

    astGrid.innerHTML = buildTree(ast);
  }
// Function to build tree
  function buildTree(node) {
  if (!node) return "";

  const value = node.value !== null && node.value !== undefined
    ? `: ${escHtml(JSON.stringify(node.value))}`
    : "";

  let childrenHTML = "";

  if (node.children && node.children.length > 0) {
    childrenHTML = `
      <div class="ast-children">
        ${node.children.map(child => buildTree(child)).join("")}
      </div>
    `;
  }

  return `
    <div class="ast-node">
      <div class="ast-label" onclick="this.nextElementSibling?.classList.toggle('hidden')">
        ${escHtml(node.type)}${value}
      </div>
      ${childrenHTML}
    </div>
  `;
}

// LLM Execution
async function runWithLLM(editor) {
  if (!editor) { showToast("Editor not ready"); return; }

  const code = editor.getValue().trim();
  if (!code) { showToast("No code to execute"); return; }

  outputContent.innerHTML = "🤖 Thinking...";

  try {
    const res = await fetch("/llm", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ code })
    });

    const data = await res.json();

    if (data.error) {
      outputContent.innerHTML = `<span class="output-error">${escHtml(data.error)}</span>`;
      return;
    }

    outputContent.innerHTML = `
      <div class="llm-output">
        ${formatLLMOutput(data.output)}
      </div>
    `;

  } catch (err) {
    outputContent.innerHTML = `<span class="output-error">${err.message}</span>`;
  }
}

function formatLLMOutput(text) {
  return escHtml(text).replace(/\n/g, "<br>");
}

  setStatus("", "Ready");
  editor.focus();
});
