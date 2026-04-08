/* ── YaadmanLang IDE · main.js ─────────────────────── */

// ── EXAMPLE SNIPPETS ────────────────────────────────
const SNIPPETS = {
  hello: `// Hello World in YaadmanLang
print "Hello, Yaadman!"
print "Welcome to the IDE"`,

  vars: `// Variable declarations
var name = "Yaadman"
var version = 1
var active = true
print name`,

  loop: `// Loop example
var i = 0
// Replace with your loop syntax
print "Loop start"
print "Iteration 1"
print "Iteration 2"
print "Loop end"`,

  func: `// Function example
// Define and call a function
var result = 42
print "Function result:"
print result`
};

// ── ELEMENTS ─────────────────────────────────────────
const codeEditor   = document.getElementById("codeEditor");
const outputContent= document.getElementById("outputContent");
const lineNumbers  = document.getElementById("lineNumbers");
const statusDot    = document.getElementById("statusDot");
const statusText   = document.getElementById("statusText");
const execTimeEl   = document.getElementById("execTime");
const tokenGrid    = document.getElementById("tokenGrid");
const toast        = document.getElementById("toast");

// ── LINE NUMBERS ─────────────────────────────────────
function updateLineNumbers() {
  const lines = codeEditor.value.split("\n").length;
  lineNumbers.textContent = Array.from({length: lines}, (_, i) => i + 1).join("\n");
}
codeEditor.addEventListener("input", updateLineNumbers);
codeEditor.addEventListener("scroll", () => {
  lineNumbers.scrollTop = codeEditor.scrollTop;
});
updateLineNumbers();

// ── TAB KEY ──────────────────────────────────────────
codeEditor.addEventListener("keydown", e => {
  if (e.key === "Tab") {
    e.preventDefault();
    const s = codeEditor.selectionStart;
    const v = codeEditor.value;
    codeEditor.value = v.slice(0, s) + "  " + v.slice(codeEditor.selectionEnd);
    codeEditor.selectionStart = codeEditor.selectionEnd = s + 2;
    updateLineNumbers();
  }
});

// ── STATUS ───────────────────────────────────────────
function setStatus(state, text) {
  statusDot.className  = `status-dot ${state}`;
  statusText.textContent = text;
}

// ── TOAST ────────────────────────────────────────────
let toastTimer;
function showToast(msg) {
  clearTimeout(toastTimer);
  toast.textContent = msg;
  toast.classList.add("show");
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
}

// ── RUN CODE ─────────────────────────────────────────
async function runCode() {
  const code = codeEditor.value.trim();
  if (!code) { showToast("Nothing to run!"); return; }

  setStatus("running", "Running…");
  outputContent.innerHTML = `<span style="color:var(--text-muted)">// Running…</span>`;

  const t0 = performance.now();
  try {
    const res  = await fetch("/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({code})
    });
    const data = await res.json();
    const ms   = (performance.now() - t0).toFixed(1);
    execTimeEl.textContent = `${ms} ms`;

    if (data.success) {
      outputContent.innerHTML =
        `<span class="output-success">${escHtml(data.output || "(no output)")}</span>`;
      setStatus("success", "Done");
    } else {
      outputContent.innerHTML =
        `<span class="output-error">── Error ──\n${escHtml(data.error)}</span>`;
      setStatus("error", "Error");
    }
  } catch (err) {
    outputContent.innerHTML =
      `<span class="output-error">Network error: ${escHtml(err.message)}</span>`;
    setStatus("error", "Network error");
  }
}

document.getElementById("runBtn").addEventListener("click", runCode);

// ── CLEAR ─────────────────────────────────────────────
document.getElementById("clearBtn").addEventListener("click", () => {
  codeEditor.value = "";
  outputContent.innerHTML = `<span class="output-placeholder">// Output will appear here...</span>`;
  execTimeEl.textContent  = "";
  updateLineNumbers();
  setStatus("", "Ready");
  showToast("Editor cleared");
});

// ── COPY OUTPUT ───────────────────────────────────────
document.getElementById("copyBtn").addEventListener("click", () => {
  const text = outputContent.textContent;
  navigator.clipboard.writeText(text).then(() => showToast("Copied!"));
});

// ── KEYBOARD SHORTCUTS ────────────────────────────────
document.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); runCode(); }
  if ((e.ctrlKey || e.metaKey) && e.key === "l")     { e.preventDefault(); document.getElementById("clearBtn").click(); }
  if ((e.ctrlKey || e.metaKey) && e.key === "t")     { e.preventDefault(); switchPanel("tokens"); }
});

// ── PANEL SWITCHING ───────────────────────────────────
function switchPanel(id) {
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  const panel = document.getElementById(`panel-${id}`);
  const btn   = document.querySelector(`[data-panel="${id}"]`);
  if (panel) panel.classList.add("active");
  if (btn)   btn.classList.add("active");
}
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => switchPanel(btn.dataset.panel));
});

// ── EXAMPLE SNIPPETS ──────────────────────────────────
document.querySelectorAll(".example-item").forEach(item => {
  item.addEventListener("click", () => {
    const snippet = SNIPPETS[item.dataset.snippet];
    if (snippet) {
      codeEditor.value = snippet;
      updateLineNumbers();
      switchPanel("editor");
      showToast(`Loaded: ${item.textContent}`);
    }
  });
});

// ── TOKEN ANALYSIS ────────────────────────────────────
const TOKEN_COLORS = {
  KEYWORD:    "#c8f75e",
  IDENTIFIER: "#6ee7ff",
  NUMBER:     "#ffb347",
  STRING:     "#ff8fa3",
  OPERATOR:   "#d0a0ff",
  TOKEN:      "#8890b0",
};

document.getElementById("analyzeBtn").addEventListener("click", async () => {
  const code = codeEditor.value.trim();
  if (!code) { showToast("No code to analyze"); return; }

  tokenGrid.innerHTML = `<span class="token-placeholder">Analyzing…</span>`;
  try {
    const res  = await fetch("/analyze", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({code})
    });
    const data = await res.json();
    renderTokens(data.tokens || []);
  } catch (err) {
    tokenGrid.innerHTML = `<span class="output-error">Error: ${escHtml(err.message)}</span>`;
  }
});

function renderTokens(tokens) {
  if (!tokens.length) {
    tokenGrid.innerHTML = `<span class="token-placeholder">No tokens found.</span>`;
    return;
  }
  tokenGrid.innerHTML = tokens.map((t, i) => {
    const color = TOKEN_COLORS[t.type] || TOKEN_COLORS.TOKEN;
    return `<div class="token-chip" style="animation-delay:${i * 0.02}s">
      <span class="token-type" style="color:${color}">${escHtml(t.type)}</span>
      <span class="token-value">${escHtml(String(t.value))}</span>
      <span class="token-index">#${t.index}</span>
    </div>`;
  }).join("");
}

// ── HELPERS ───────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;");
}
