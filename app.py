from flask import Flask, request, jsonify, render_template
import sys
import io
import traceback
from Parser import parse
from utils import tokenize   # your tokenize() function
from Parser import ASTNode
import os
import google.generativeai as genai

os.environ["GOOGLE_API_KEY"] = "AIzaSyBJsGfzvWWKJuvBcXvqS5LLVM596iI9bGM"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

# ──────────────────────────────────────────────
# Paste your YaadmanLang Lexer, Parser,
# Semantic Analyzer, and Interpreter below.
# ──────────────────────────────────────────────

# ── PLACEHOLDER INTERPRETER ──────────────────
# Replace this section with your actual code.
from Parser import parse, ASTNode, YaadmanSyntaxError
from Interpreter import Interpreter
from Lexer import YaadmanLexer
from Interpreter import SemanticAnalyzer

# ─────────────────────────────────────────────


def run_yaadman(source: str):
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr

    try:
        sys.stdout, sys.stderr = stdout_capture, stderr_capture

        interp = Interpreter()
        result = interp.run_program(source)

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


@app.route("/ast", methods=["POST"])
def get_ast():
    data = request.get_json()
    code = data.get("code", "")

    try:
        tree = parse(code)
        return jsonify({
            "ast": tree.to_dict()
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# LLM Integration for output
@app.route("/llm", methods=["POST"])
def llm_execute():
    data = request.get_json()
    code = data.get("code", "")

    prompt = f"""
    You are an interpreter for a programming language called YaadmanLang.

    Simulate execution step by step.

    Return in this format:

    [Execution Trace]
    - Step 1:
    - Step 2:

    [Output]

    [Final State]

    Code:
    {code}
    """

    try:
        response = model.generate_content(prompt)

        return jsonify({
            "output": response.text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    code = data.get("code", "")

    tokens = tokenize(code)

    # add index for frontend
    for i, t in enumerate(tokens):
        t["index"] = i+1

    return jsonify({
        "tokens": tokens
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
