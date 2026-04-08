from flask import Flask, request, jsonify, render_template
import sys
import io
import traceback

app = Flask(__name__)

# ──────────────────────────────────────────────
# Paste your YaadmanLang Lexer, Parser,
# Semantic Analyzer, and Interpreter below.
# ──────────────────────────────────────────────

# ── PLACEHOLDER INTERPRETER ──────────────────
# Replace this section with your actual code.

class YaadmanInterpreter:
    """
    Drop-in placeholder.  Replace with your real
    Lexer → Parser → Semantic Analyzer → Interpreter pipeline.
    """
    def run(self, source: str) -> str:
        lines = source.strip().splitlines()
        output_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            # Tiny demo: echo recognised keywords
            if line.startswith("print "):
                value = line[6:].strip().strip('"').strip("'")
                output_lines.append(value)
            elif line.startswith("var "):
                output_lines.append(f"[declared] {line[4:]}")
            else:
                output_lines.append(f"[exec] {line}")
        return "\n".join(output_lines) if output_lines else "(no output)"

# ─────────────────────────────────────────────


def run_yaadman(source: str):
    """Run source through the interpreter, capture output + errors."""
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    try:
        interp = YaadmanInterpreter()
        # If your interpreter prints to stdout, redirect it:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = stdout_capture, stderr_capture
        result = interp.run(source)
        sys.stdout, sys.stderr = old_stdout, old_stderr

        printed = stdout_capture.getvalue()
        output  = printed if printed else (result or "")
        return {"success": True, "output": output, "error": ""}
    except Exception:
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__
        err = traceback.format_exc()
        return {"success": False, "output": "", "error": err}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run", methods=["POST"])
def run_code():
    data   = request.get_json(force=True)
    source = data.get("code", "")
    if not source.strip():
        return jsonify({"success": False, "output": "", "error": "No code provided."})
    result = run_yaadman(source)
    return jsonify(result)


@app.route("/analyze", methods=["POST"])
def analyze_tokens():
    """Return token stream for the lexer-view panel."""
    data   = request.get_json(force=True)
    source = data.get("code", "")
    # ── Replace with your actual Lexer call ──
    # e.g.  tokens = Lexer(source).tokenize()
    # For now, return a simple word-level mock:
    tokens = []
    for i, word in enumerate(source.split()):
        tokens.append({"index": i, "type": "TOKEN", "value": word})
    return jsonify({"tokens": tokens})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
