# YaadmanLang IDE

A web-based IDE for the YaadmanLang interpreter.

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:5000** in your browser.

## Plugging in your interpreter

Open `app.py` and replace the `YaadmanInterpreter` placeholder class with your
real pipeline:

```python
# Replace the placeholder class with your actual imports, e.g.:
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from interpreter import Interpreter

class YaadmanInterpreter:
    def run(self, source: str) -> str:
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        SemanticAnalyzer(ast).analyze()
        return Interpreter(ast).run()
```

For the **Token View** panel, update the `/analyze` route in `app.py`:

```python
@app.route("/analyze", methods=["POST"])
def analyze_tokens():
    source = request.get_json()["code"]
    tokens = Lexer(source).tokenize()          # ← your real Lexer
    result = [{"index": i, "type": t.type, "value": t.value}
              for i, t in enumerate(tokens)]
    return jsonify({"tokens": result})
```

## Project structure

```
yaadmanlang/
├── app.py               ← Flask backend (plug your interpreter here)
├── requirements.txt
├── templates/
│   └── index.html       ← Main IDE page
└── static/
    ├── css/style.css    ← All styling
    └── js/main.js       ← Editor, run, token view logic
```

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + Enter | Run code |
| Ctrl + L | Clear editor |
| Ctrl + T | Switch to Token View |
