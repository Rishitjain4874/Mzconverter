import requests
from flask import Flask

class ASTNode:
    def __str__(self):
        return self.__repr__()

class ExternalDeclaration(ASTNode):
    def __init__(self, name, declarations):
        self.name = name
        self.declarations = declarations

    def __repr__(self):
        return f"ExternalDeclaration(name={self.name}, declarations={self.declarations})"

class IntegerDeclaration(ASTNode):
    def __init__(self, name, terminator):
        self.name = name
        self.terminator = terminator

    def __repr__(self):
        return f"IntegerDeclaration(name={self.name}, terminator={self.terminator})"

class AsciiDeclaration(ASTNode):
    def __init__(self, name, terminator):
        self.name = name
        self.terminator = terminator

    def __repr__(self):
        return f"AsciiDeclaration(name={self.name}, terminator={self.terminator})"

class GenericDeclaration(ASTNode):
    def __init__(self, type_name, name):
        self.type_name = type_name
        self.name = name

    def __repr__(self):
        return f"GenericDeclaration(type_name={self.type_name}, name={self.name})"

class Identifier(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Identifier(value={self.value})"

class Terminator(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Terminator(value={self.value})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.parse_external_declaration()

    def consume(self, expected_value=None):
        if self.pos >= len(self.tokens):
            raise SyntaxError(f"Unexpected end of input, expected {expected_value}")
        token = self.tokens[self.pos]
        self.pos += 1
        if expected_value and token != expected_value:
            raise SyntaxError(f"Expected {expected_value}, got {token}")
        return token

    def parse_external_declaration(self):
        name = self.consume()
        self.consume('{')
        declarations = self.parse_declaration_list()
        self.consume('}')
        self.consume(';')
        return ExternalDeclaration(name, declarations)

    def parse_declaration_list(self):
        declarations = []
        while self.tokens[self.pos] != '}':
            if self.tokens[self.pos] in ['\n', '']:
                self.pos += 1
                continue
            if self.tokens[self.pos] == 'ascii':
                declarations.append(self.parse_ascii_declaration())
            else:
                declarations.append(self.parse_generic_declaration())
        return declarations

    def parse_ascii_declaration(self):
        self.consume('ascii')
        name = self.consume()
        self.consume(':')
        terminator = self.parse_terminator()
        self.consume(';')
        return AsciiDeclaration(name, terminator)

    def parse_generic_declaration(self):
        type_name = self.consume()
        name = self.consume()
        self.consume(';')
        return GenericDeclaration(type_name, name)

    def parse_terminator(self):
        self.consume('terminated_by')
        self.consume('(')
        if self.tokens[self.pos] == '"':
            self.consume('"')
            value = self.consume()
            self.consume('"')
        else:
            value = self.consume()
        self.consume(')')
        return Terminator(value)
    

url = 'http://127.0.0.1:5000/test'
response = requests.get(url)
if response.status_code == 200:
    tokens = response.json()
else:
    print("Failed to retrieve tokens. Status code:", response.status_code)

app = Flask(__name__)
@app.route('/', methods=['GET'])
def hostast():
    parser1 = Parser(tokens[0])
    ast1 = parser1.parse()
    parser2 = Parser(tokens[6])
    ast2 = parser2.parse()
    parser3 = Parser(tokens[10])
    ast3 = parser3.parse()
    parser4 = Parser(tokens[31])
    ast4 = parser4.parse()
    return f'({str(ast1)} \n {str(ast2)} \n {str(ast3)} \n {str(ast4)})'
if __name__ == '__main__':
    app.run(port=5001, debug=True)