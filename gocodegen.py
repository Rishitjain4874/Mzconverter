import re
from flask import Flask
import requests

class AsciiDeclaration:
    def __init__(self, name, terminator):
        self.name = name
        self.terminator = terminator

class Terminator:
    def __init__(self, value):
        self.value = value

class GenericDeclaration:
    def __init__(self, type_name, name):
        self.type_name = type_name
        self.name = name

class ExternalDeclaration:
    def __init__(self, name, declarations):
        self.name = name
        self.declarations = declarations

def generate_go_code(external_declarations):
    go_code = "package main\n\n"
    for external_declaration in external_declarations:
        go_code += f"type {external_declaration.name} struct " + "{\n"
        for declaration in external_declaration.declarations:
            if isinstance(declaration, AsciiDeclaration):
                terminator_value = declaration.terminator.value
                if terminator_value:
                    terminator_value_str = terminator_value if terminator_value.startswith('0x') else f"'{terminator_value}'"
                else:
                    terminator_value_str = "''"
                go_code += f"\t{declaration.name} string `mzConverter: terminated_by({terminator_value_str})\"`\n"
            elif isinstance(declaration, GenericDeclaration):
                go_code += f"\t{declaration.name} {declaration.type_name}\n"
        go_code += "}\n\n"
    return go_code

def parse_ast(ast_str):
    # Define regex patterns to match the AST representation
    external_declaration_pattern = r"ExternalDeclaration\(name=(\w+), declarations=\[(.*?)\]\)"
    ascii_declaration_pattern = r"AsciiDeclaration\(name=(\w+), terminator=Terminator\(value=([:,0xA-Fa-f0-9]*)\)\)"
    generic_declaration_pattern = r"GenericDeclaration\(type_name=(\w+), name=(\w+)\)"

    # Extract individual ASTs from the provided string
    ast_matches = re.findall(external_declaration_pattern, ast_str, re.DOTALL)
    if not ast_matches:
        raise ValueError("Invalid AST format")
    
    external_declarations = []
    for match in ast_matches:
        name = match[0]
        declarations_str = match[1]
        
        declarations = []
        for declaration_match in re.finditer(ascii_declaration_pattern, declarations_str):
            declaration_name = declaration_match.group(1)
            terminator_value = declaration_match.group(2).strip()
            declaration = AsciiDeclaration(name=declaration_name, terminator=Terminator(value=terminator_value))
            declarations.append(declaration)
            
        for declaration_match in re.finditer(generic_declaration_pattern, declarations_str):
            type_name = declaration_match.group(1)
            declaration_name = declaration_match.group(2)
            declaration = GenericDeclaration(type_name=type_name, name=declaration_name)
            declarations.append(declaration)

        external_declarations.append(ExternalDeclaration(name=name, declarations=declarations))

    return external_declarations


url = 'http://127.0.0.1:5001/'
response = requests.get(url)
if response.status_code == 200:
    ast_str = response.text
    ast1 = parse_ast(ast_str)
    go_code = generate_go_code(ast1)

app = Flask(__name__)
@app.route('/', methods=['GET'])
def hostgocode():
    return go_code
if __name__ == '__main__':
    app.run(port=5002, debug=True)
