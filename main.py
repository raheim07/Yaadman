import sys
from Interpreter import run_program
from utils import print_tokens, show_ast

def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python main.py tokens file.ym")
        print("  python main.py ast file.ym")
        print("  python main.py run file.ym")
        print("  python main.py debug file.ym")
        return

    mode = sys.argv[1]
    filename = sys.argv[2]

    try:
        with open(filename, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    if mode == "tokens":
        print_tokens(code)

    elif mode == "ast":
        show_ast(code)

    elif mode == "run":
        run_program(code)

    elif mode == "debug":
        print_tokens(code)
        show_ast(code)
        print("\nExecuting...\n")
        run_program(code)

    else:
        print("Unknown mode.")


if __name__ == "__main__":
    main()