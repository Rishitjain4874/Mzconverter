import re
from nltk.tokenize import RegexpTokenizer
from flask import Flask, request
import string

hex_map = {c: hex(ord(c)) for c in string.printable}


# AST Generator
class ASTNode:
    def __str__(self):
        return self.__repr__()

class ExternalDeclaration(ASTNode):
    def __init__(self, name, declarations):
        self.name = name
        self.declarations = declarations

    def __repr__(self):
        return f"ExternalDeclaration(name={self.name}, declarations={self.declarations})"

class InternalDeclaration(ASTNode):
    def __init__(self, name, declarations):
        self.name = name
        self.declarations = declarations

    def __repr__(self):
        return f"InternalDeclaration(name={self.name}, declarations={self.declarations})"

class AsciiDeclaration(ASTNode):
    def __init__(self, name, terminator, attri_type='str'):
        self.name = name
        self.terminator = terminator
        self.attri_type = attri_type
    def __repr__(self):
        return f"AsciiDeclaration(name={self.name}, terminator={self.terminator}, attri_type={self.attri_type})"
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
        while self.pos < len(self.tokens) and self.tokens[self.pos] != '}':
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
        terminator = None
        attri_type = 'str'
        
        while self.pos < len(self.tokens) and self.tokens[self.pos] != ';':
            token = self.tokens[self.pos]
            if token == 'terminated_by':
                terminator = self.parse_terminator()
            elif token in ['int', 'str', 'long']:
                attri_type = self.parse_attri_type()
                if self.pos < len(self.tokens) and self.tokens[self.pos] == ',':
                    self.consume(',')
            else:
                self.consume()  
        
        self.consume(';')
        return AsciiDeclaration(name, terminator, attri_type)

    def parse_generic_declaration(self):
        type_name = self.consume()
        name = self.consume()
        self.consume(';')
        return GenericDeclaration(type_name, name)
    
    def parse_attri_type(self):
        attri_type = self.consume()
        if self.pos < len(self.tokens) and self.tokens[self.pos] == '(':
            self.consume('(')
            base = self.consume()
            self.consume(')')
        return (attri_type, base)
    
    def parse_terminator(self):
        self.consume('terminated_by')
        self.consume('(')
        if self.tokens[self.pos] == '"':
            self.consume('"')
            value = self.consume()
            value = symbol_to_hex(value)
            self.consume('"')
        else:
            value = self.consume()
            value = symbol_to_hex(value)
        self.consume(')')
        return Terminator(value)
    
def symbol_to_hex(symbol):
    return symbol.encode('utf-8').hex()

def parse_multiple_lists(token_lists):
    asts = []
    for tokens in token_lists:
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            asts.append(ast)
        except Exception as e:
            print(f"Error parsing AST: {e}")
            continue
    return asts

# Text parsing functions
def check_Ext_int(tokens, key):
    print(f'Checking for {key} keyword in the file\n')
    block = []
    block_value = []
    preview_list = []
    in_block = False
    skip_next_close_brace = False
    for i in tokens:
        if i == key:    
            in_block = True
        elif i == '}':
            if in_block:
                if skip_next_close_brace:
                    block.append("}")
                    block.append(";")
                    block.append("\n")
                    skip_next_close_brace = False
                    continue
                block.append(i)
                block.pop()
                block.append('}')
                block.append(';')
                block.append('\n')
                block_value.append(block)
                preview = " ".join(block)
                preview_list.append(preview)
                in_block = False
                block = []
        elif in_block:
            if i == 'set':
                skip_next_close_brace = True
            block.append(i)
    return block_value

def getcontentfile(content):
    pattern = r'\n+'
    tokenizer = RegexpTokenizer(pattern, gaps=True)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    content = re.sub(r'//.*|--.*', '', content)
    sent_tokens = tokenizer.tokenize(content)
    word_tokenizer_pattern = r'''(?x)    
        (?:[A-Z]\.)+                   
    |   \w+(?:-\w+)*                   
    |   \$?\d+(?:\.\d+)?%?             
    |   \.\.\.                         
    |   [{}.,;"'?():\-_<>\[\]@#&*+=/|~] 
    |   [€£¥]                          
    |   [\u00A0-\u00FF]                
    |   \n                            
    |   \S                            
    '''
    token1 = []
    word_tokenizer = RegexpTokenizer(word_tokenizer_pattern)
    for sentence in sent_tokens:
        tokens = word_tokenizer.tokenize(sentence)
        token1.extend(tokens)
        token1.append('\n')
    return token1

# Go code generator
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


def symbol_to_hex(symbol):
    if isinstance(symbol, str) and symbol.startswith("0x"):
        return symbol
    return hex_map.get(symbol, None)
def parse_ast(ast_str):
    # Define regex patterns to match the AST representation
    external_declaration_pattern = r"ExternalDeclaration\(name=(\w+), declarations=\[(.*?)\]\)"
    ascii_declaration_pattern = r"AsciiDeclaration\(name=(\w+), terminator=Terminator\(value=([a-fA-F0-9]*)\)\)"
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

# Read the file and process

file = 'sampleUltraFormat.txt'
with open(file, 'r') as f:
    content = f.read()
block_value_ext = check_Ext_int(getcontentfile(content), 'external')
asts = parse_multiple_lists(block_value_ext)
ast1 = ""
for ast in asts:
    ast1 = ast1 + str(ast) + "\n"
print(ast1)
ast2 = parse_ast(ast1)
go_code = generate_go_code(ast2)
print(go_code)

'''
app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_tokens_ext():
    cont = request.data.decode('utf-8')
    block_value_ext = check_Ext_int(getcontentfile(cont), 'external')
    asts = parse_multiple_lists(block_value_ext)
    print(block_value_ext)
    ast1 = ""
    for ast in asts:
        ast1 = ast1 + str(ast) + "\n"
    print(ast1)
    ast2 = parse_ast(ast1)
    go_code = generate_go_code(ast2)
    return go_code

if __name__ == '__main__':
    app.run(port=5011)'''