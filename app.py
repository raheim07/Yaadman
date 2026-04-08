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
from Yaadman.Parser import parse, ASTNode, YaadmanSyntaxError
from Yaadman.Interpreter import Interpreter
from Yaadman.Lexer import YaadmanLexer
from Yaadman.Interpreter import SemanticAnalyzer

# ─────────────────────────────────────────────


def run_yaadman(source: str):
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr

    try:
        sys.stdout, sys.stderr = stdout_capture, stderr_capture

        interp = Interpreter()
        result = interp.run(source)

        printed = stdout_capture.getvalue()
        output = printed if printed else (result or "")

        return {"success": True, "output": output, "error": ""}

    except Exception:
        err = traceback.format_exc()
        return {"success": False, "output": "", "error": err}

    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


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
    data = request.get_json(force=True)
    source = data.get("code", "")

    try:
        lexer = YaadmanLexer(source)
        tokens = lexer.tokenize()

        formatted = []
        for i, token in enumerate(tokens):
            formatted.append({
                "index": i,
                "type": token.type,
                "value": str(token.value)
            })

        return jsonify({"tokens": formatted})

    except Exception:
        return jsonify({"tokens": [], "error": traceback.format_exc()})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
