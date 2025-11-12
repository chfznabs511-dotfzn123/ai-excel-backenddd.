# validator.py - Validate code and request payloads

import ast

FORBIDDEN_BUILTINS = [
    'open', 'eval', 'exec', '__import__', 'globals', 'locals', 'getattr', 'setattr', 'delattr'
]

FORBIDDEN_IMPORTS = [
    'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'ftplib', 'telnetlib'
]

class CodeValidator(ast.NodeVisitor):
    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in FORBIDDEN_IMPORTS:
                self.errors.append(f"Forbidden module import: '{alias.name}' is not allowed.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module in FORBIDDEN_IMPORTS:
            self.errors.append(f"Forbidden module import: '{node.module}' is not allowed.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_BUILTINS:
            self.errors.append(f"Forbidden function call: '{node.func.id}()' is not allowed.")
        self.generic_visit(node)

def validate_code(code_string: str) -> list[str]:
    try:
        tree = ast.parse(code_string)
        validator = CodeValidator()
        validator.visit(tree)
        return validator.errors
    except SyntaxError as e:
        return [f"Syntax Error: {e.msg} on line {e.lineno}"]
    except Exception as e:
        return [f"Unexpected validation error: {str(e)}"]

def validate_request_payload(payload: dict) -> list[str]:
    errors = []
    if not isinstance(payload, dict):
        return ["Payload must be a JSON object."]
    if 'code' not in payload or not isinstance(payload['code'], str):
        errors.append("Missing or invalid 'code' field.")
    if 'data' not in payload or not isinstance(payload['data'], dict):
        errors.append("Missing or invalid 'data' field.")
    return errors
