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
    def __init__(self, name, declarations, external_terminator=None):
        self.name = name
        self.declarations = declarations
        self.external_terminator = external_terminator
    def __repr__(self):
        return f"ExternalDeclaration(name={self.name}, declarations={self.declarations})"

class InternalDeclaration(ASTNode):
    def __init__(self, name, declarations):
        self.name = name
        self.declarations = declarations

    def __repr__(self):
        return f"InternalDeclaration(name={self.name}, declarations={self.declarations})"

class AsciiDeclaration(ASTNode):
    def __init__(self, name, terminator, attri_type='str', encoded_value= None , externalonly= None, align_value=None, padded_value=None, static_size_value=0, additional_attributes=None):
        self.name = name
        self.terminator = terminator
        self.attri_type = attri_type
        self.encoded_value = encoded_value
        self.externalonly = externalonly  
        self.align_value = align_value
        self.padded_value = padded_value
        self.static_size_value = static_size_value
        self.additional_attributes = additional_attributes or []
        
    def __repr__(self):
        if self.align_value and self.padded_value and self.static_size_value:
            return f"AsciiDeclaration(name={self.name}, attri_type={self.attri_type}, align_value={self.align_value}, padded_value={self.padded_value}, static_size_value={self.static_size_value})"
        elif self.encoded_value and not self.externalonly and not self.align_value and not self.padded_value and not self.static_size_value and self.terminator != None:
           return f"AsciiDeclaration(name={self.name}, terminator={self.terminator}, attri_type={self.attri_type}, encoded_value={self.encoded_value})"
        elif self.externalonly and not self.encoded_value and not self.align_value and not self.padded_value and not self.static_size_value and self.terminator != None:
            return f"AsciiDeclaration(name={self.name}, terminator={self.terminator}, attri_type={self.attri_type}, externalonly={self.externalonly})"
        elif self.encoded_value and self.externalonly and not self.align_value and not self.padded_value and not self.static_size_value and self.terminator != None:
            return f"AsciiDeclaration(name={self.name}, terminator={self.terminator}, attri_type={self.attri_type}, encoded_value={self.encoded_value}, externalonly={self.externalonly})"
        elif self.additional_attributes and self.externalonly and self.encoded_value and self.terminator != None:
            return f"AsciiDeclaration(name={self.name}, terminator={self.terminator}, attri_type={self.attri_type}, encoded_value={self.encoded_value}, externalonly={self.externalonly}, additional_attributes={self.additional_attributes})"
        elif not self.additional_attributes or self.additional_attributes == [','] or self.encoded_value == None or self.externalonly == None or self.align_value == None or self.padded_value == None or self.static_size_value == None and self.terminator != None:
            return f"AsciiDeclaration(name={self.name}, terminator={self.terminator}, attri_type={self.attri_type})"

class GenericDeclaration(ASTNode):
    def __init__(self, type_name, name):
        self.type_name = type_name
        self.name = name

    def __repr__(self):
        return f"GenericDeclaration(type_name={self.type_name}, name={self.name})"

class Identifier(ASTNode):
    def __init__(self, tag, tag2= None, AsciiDeclaration=None, SetDeclaration=None):
        self.tag = tag
        self.tag2 = tag2
        self.AsciiDeclaration = AsciiDeclaration
        self.SetDeclaration = SetDeclaration
    def __repr__(self):
        if self.tag2 != None:
            return f"Identified_by(tag={self.tag}, tag2 = {self.tag2})"
        else:
            return f"Identified_by(tag={self.tag})"

class Terminator(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Terminator(value={self.value})"

class SetDeclaration(ASTNode):
    def __init__(self, name, varname, fields, queries):
        self.name = name
        self.varname = varname
        self.fields = fields
        self.queries = queries

    def __repr__(self):
        return f"SetDeclaration(name={self.name}, varname={self.varname}, query_B1={self.fields}, query_B2={self.queries})"

class Asn_LengthDeclaration(ASTNode):
    def __init__(self, name, terminator, options=None):
        self.name = name
        self.terminator = terminator
        self.options = options

    def __repr__(self):
        if self.options:
            return f"Asn_LengthDeclaration(name={self.name}, terminator={self.terminator}, options={self.options})"
        else:
            return f"Asn_LengthDeclaration(name={self.name}, terminator={self.terminator})"

class BcdDeclaration(ASTNode):
    def __init__(self, name, terminator, order):
        self.name = name
        self.terminator = terminator
        self.order = order

    def __repr__(self):
        return f"BcdDeclaration(name={self.name}, terminator={self.terminator}, order={self.order})"

class EbcdicDeclaration(ASTNode):
    def __init__(self, name, terminator, additional_attributes=None):
        self.name = name
        self.terminator = terminator
        self.additional_attributes = additional_attributes or []

    def __repr__(self):
        if self.additional_attributes:
            return f"EbcdicDeclaration(name={self.name}, terminator={self.terminator}, additional_attributes={self.additional_attributes})"
        else:
            return f"EbcdicDeclaration(name={self.name}, terminator={self.terminator})"

class Msp_LengthDeclaration(ASTNode):
    def __init__(self, name, externalonly):
        self.name = name
        self.externalonly = externalonly

    def __repr__(self):
        return f"Msp_LengthDeclaration(name={self.name}, externalonly={self.externalonly})"

class ListDeclaration(ASTNode):
    def __init__(self, name, terminator, element_type, element_count):
        self.name = name
        self.terminator = terminator
        self.element_type = element_type
        self.element_count = element_count

    def __repr__(self):
        return f"ListDeclaration(name={self.name}, terminator={self.terminator}, element_type={self.element_type}, element_count={self.element_count})"

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
            raise SyntaxError(f"Expected {expected_value}")
        return token    
    
    def parse_external_declaration(self):
        name = self.consume()
        if self.tokens[self.pos] == '\n':
            self.consume('\n')
            self.consume("{")
            declarations = self.parse_declaration_list()
            self.consume('}')
            self.consume(';')
        elif self.tokens[self.pos] == '{':
            self.consume('{')
            declarations = self.parse_declaration_list()
            self.consume('}')
            self.consume(';')
        elif self.tokens[self.pos] == ':':
            self.consume(':')
            declarations = self.parse_declaration_list()
            self.consume('}')
            self.consume(';')
        return ExternalDeclaration(name, declarations)
    
    def parse_declaration_list(self):
        declarations = []
        if 'set' in self.tokens:
            if self.tokens[self.pos] == 'identified_by':
                declarations.append(self.parse_identified_by())
            declarations.append(self.parse_set())
        while self.pos < len(self.tokens) and self.tokens[self.pos] != '}':
            if self.tokens[self.pos] in ['\n', '']:
                self.pos += 1
                continue
            elif self.tokens[self.pos] == 'terminated_by':
                declarations.append(self.parse_terminator())
                self.consume('{')
            elif self.tokens[self.pos] == 'ascii':
                declarations.append(self.parse_ascii_declaration())
            elif self.tokens[self.pos] == 'identified_by':
                declarations.append(self.parse_identified_by())
            elif self.tokens[self.pos] == 'asn_length':
                declarations.append(self.parse_asn_length_declaration())
            elif self.tokens[self.pos] == 'bcd':
                declarations.append(self.parse_bcd_declaration())
            elif self.tokens[self.pos] == 'ebcdic':
                declarations.append(self.parse_ebcdic_declaration())
            elif self.tokens[self.pos] == 'msp_length':
                declarations.append(self.parse_msp_length_declaration())
            elif self.tokens[self.pos] == 'list':
                declarations.append(self.parse_list_declaration())
            else:
                declarations.append(self.parse_generic_declaration())
        return declarations

    def parse_asn_length_declaration(self):
        self.consume('asn_length')
        name = self.consume()
        self.consume(':')
        terminator = self.parse_terminator()
        options = None
        if self.tokens[self.pos] == 'content_only':
            self.consume('content_only')
            options = 'content_only'
        return Asn_LengthDeclaration(name, terminator, options)

    def parse_bcd_declaration(self):
        self.consume('bcd')
        name = self.consume()
        self.consume(':')
        terminator = self.parse_terminator()
        order = None
        if self.tokens[self.pos] == 'msn_fd':
            self.consume('msn_fd')
            order = 'msn_fd'
        elif self.tokens[self.pos] == 'lsn_fd':
            self.consume('lsn_fd')
            order = 'lsn_fd'
        return BcdDeclaration(name, terminator, order)

    def parse_ebcdic_declaration(self):
        self.consume('ebcdic')
        name = self.consume()
        self.consume(':')
        terminator = self.parse_terminator()
        additional_attributes = []
        while self.pos < len(self.tokens) and self.tokens[self.pos] != ';':
            token = self.tokens[self.pos]
            if token in ['character_encoding']:
                additional_attributes.append(self.parse_additional_attribute())
            else:
                self.consume()
        if self.pos < len(self.tokens) and self.tokens[self.pos] == ';':
            self.consume(';')
        return EbcdicDeclaration(name, terminator, additional_attributes)

    def parse_msp_length_declaration(self):
        self.consume('msp_length')
        name = self.consume()
        self.consume(':')
        externalonly = self.consume('external_only')
        self.consume(';')
        return Msp_LengthDeclaration(name, externalonly)

    def parse_list_declaration(self):
        self.consume('list')
        self.consume('<')
        element_type = self.consume()
        self.consume('>')
        name = self.consume()
        self.consume(':')
        terminator = self.parse_terminator()
        self.consume('element_count')
        self.consume('(')
        element_count = self.consume()
        self.consume(')')
        self.consume(';')
        return ListDeclaration(name, terminator, element_type, element_count)

    def parse_additional_attribute(self):
        attribute_name = self.consume()
        self.consume('(')
        attribute_value = self.consume('"')
        self.consume('"')
        self.consume(')')
        return f"{attribute_name}({attribute_value})"
    
    def parse_set(self):
        self.consume('\n')
        self.consume('set')
        self.consume('{')
        self.consume('\n')
        fields = []
        while self.tokens[self.pos] != '}':
            name = self.consume()
            varname = self.consume()
            if self.tokens[self.pos]== ':':
                self.consume(':')
            else:
                pass
            field = self.consume()
            fields.append((name, varname, field))
            self.consume(';')
            self.consume('\n')
        self.consume('}')
        self.consume(';')
        self.consume('\n')
        self.consume(';')
        self.consume('\n')
        queries = []
        while self.pos < len(self.tokens) and self.tokens[self.pos] != '}' and self.tokens[self.pos + 1] != ';' and self.tokens[self.pos + 2] != '\n':
            if self.tokens[self.pos] == 'ascii':
                queries.append(self.parse_ascii_declaration())
            else:
                query = self.consume()
                if self.tokens[self.pos]== ':':
                    self.consume(':')
                else:
                    pass
                query_nxt = self.consume()
                queries.append((query, query_nxt))
                self.consume(';')
            if self.tokens[self.pos]== '\n':
                self.consume('\n')
            else:
                pass
        return SetDeclaration(name, varname, fields, queries)

    def parse_identified_by(self):
        identifier1 = None
        self.consume('identified_by')
        if self.tokens[self.pos] == '(' and self.tokens[self.pos +1] == '(':
            self.consume('(')
            self.consume('(')
            identifier = self.parse_items_identified_by()
            self.consume(')')
            if self.tokens[self.pos] == "|":
                self.consume('|')
                self.consume('|')
                self.consume('(')
                identifier1 = self.parse_items_identified_by()
                self.consume(')')
            self.consume(')')
        else:
            self.consume('(')
            identifier = self.parse_items_identified_by()
            self.consume(')')
        self.consume('{')
        ascii_declaration1 = []
        if self.pos < len(self.tokens) and self.tokens[self.pos] == 'ascii':
            ascii_declaration1.append(self.parse_ascii_declaration())
            if self.pos < len(self.tokens) and self.tokens[self.pos] == 'ascii':
                ascii_declaration1.append(self.parse_ascii_declaration())
        return Identifier(identifier, identifier1)

    def parse_items_identified_by(self):
        if self.tokens[self.pos] == 'tag':
            self.consume('tag')
            self.consume('=')
            self.consume('=')
            self.consume('"')
            identifier = self.consume()
            self.consume('"')
        elif self.tokens[self.pos] == 'strStartsWith':
            self.consume('strStartsWith')
            self.consume('(')
            self.consume()
            self.consume(',')
            self.consume('"')
            identifier = self.consume()
            self.consume('"')
            self.consume(')')
        elif self.tokens[self.pos] == 'strContains':
            self.consume('strContains')
            self.consume('(')
            self.consume()
            self.consume(',')
            self.consume('"')
            identifier = self.consume()
            self.consume('"')
            self.consume(')')
        else: 
            name = self.consume()
            self.consume('=')
            self.consume('=')
            self.consume('"')
            idn = []
            idn.append(name)
            idn.append(" ")
            while self.tokens[self.pos] != '"':
                idn.append(self.consume())
            identifier = "".join(idn)
            self.consume('"')
        return identifier
    
    def parse_ascii_declaration(self):
        self.consume('ascii')
        name = self.consume()
        self.consume(':')
        terminator = None
        encoded_value = None
        externalonly = None
        attri_type = 'str'
        align_value = None
        padded_value = None
        static_size_value = 0
        additional_attributes = []
        
        while self.pos < len(self.tokens) and self.tokens[self.pos] != ';':
            token = self.tokens[self.pos]
            if token == 'align':
                self.consume('align')
                self.consume('(')
                align_value = self.consume()
                self.consume(')')
            elif token == 'padded_with':
                self.consume('padded_with')
                self.consume('(')
                if self.pos < len(self.tokens) and self.tokens[self.pos] == '"':
                    self.consume('"')
                    padded_value = self.consume()
                    padded_value = symbol_to_hex(padded_value)
                    self.consume('"')
                else:
                    padded_value = self.consume()
                self.consume(')')
            elif token == 'static_size':
                self.consume('static_size')
                self.consume('(')
                static_size_value = self.consume()
                self.consume(')')
            elif token == 'terminated_by':
                terminator = self.parse_terminator()
            elif token in ['int', 'str', 'long', 'byte', 'short', 'bigint']:
                attri_type = self.parse_attri_type()
                if self.pos < len(self.tokens) and self.tokens[self.pos] == ',':
                    self.consume(',')
            elif token == 'encode_value':
                self.consume('encode_value')
                self.consume('(')
                self.consume('"')
                encoded_value = self.consume()
                self.consume('"')
                self.consume(')')
            elif token == 'external_only':
                externalonly = self.consume('external_only')
            else:
                additional_attributes.append(token)
                self.consume()
        if self.pos < len(self.tokens) and self.tokens[self.pos] == ';':
            self.consume(';')  
        elif self.pos < len(self.tokens) and self.tokens[self.pos] == '}':
            self.consume('}')
        
        ascii_decl = AsciiDeclaration(name, terminator, attri_type, encoded_value, externalonly, align_value, padded_value, static_size_value)
        ascii_decl.additional_attributes = additional_attributes
        return ascii_decl

    def parse_generic_declaration(self):
        type_name = self.consume()
        name = self.consume()
        self.consume(';')
        return GenericDeclaration(type_name, name)

    def parse_attri_type(self):
        attri_type = self.consume()
        base = None
        if self.pos < len(self.tokens) and self.tokens[self.pos] == '(':
            self.consume('(')
            base = self.consume()
            self.consume(')')
        return attri_type if not base else (attri_type, base)

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
            print(f"Error parsing AST: {ascii(e).replace("'", " ")}, \t at {parser.tokens[parser.pos]}, positing {parser.pos} in \n {tokens}")
            continue
    return asts
# Text parsing functions
def check_Ext_int(tokens, key):
    block = []
    block_value = []
    preview_list = []
    in_block = False
    skip_next_close_brace = False
    prev_token = None
    for i in tokens:
        if i in ['external', 'internal', 'in_map', 'out_map', 'session'] and i != key:
            in_block = False
        if i == key:
            if prev_token == '\n' or prev_token == None:
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
            else:
                block.append(i)
        prev_token = i
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

def generate_go_code(external_declarations):
    go_code = "package main\n\n"
    for external_declaration in external_declarations:
        go_code += f"type {external_declaration.name} struct " + "{\n"
        for declaration in external_declaration.declarations:
            if isinstance(declaration, AsciiDeclaration):
                if declaration.terminator:
                    terminator_value = declaration.terminator.value
                else:
                    terminator_value = None
                attri_value = declaration.attri_type
                encoded_value = declaration.encoded_value
                externalonly = declaration.externalonly
                align_value = declaration.align_value
                padded_value = declaration.padded_value
                static_size_value = declaration.static_size_value
                if declaration.name == None:
                    continue
                if encoded_value and externalonly:
                    go_code += f"\t{declaration.name} string `mzConverter: terminated_by({terminator_value}), encoded_by({encoded_value}), {externalonly}\"`\n"
                elif static_size_value and align_value and padded_value:
                    go_code += f"\t{declaration.name} string `mzConverter: static_size({static_size_value}), align({align_value}), padded_with({padded_value})\"`\n"
                elif attri_value == 'str' or attri_value == None and terminator_value:
                    go_code += f"\t{declaration.name} string `mzConverter: terminated_by({terminator_value})\"`\n"
                elif 'int' in attri_value and terminator_value:
                    go_code += f"\t{declaration.name} Int64 `mzConverter: terminated_by({terminator_value}), base({(eval(attri_value))[1]})\"`\n"
                elif 'long' in attri_value and terminator_value:
                    go_code += f"\t{declaration.name} Decimal.decimal `mzConverter: terminated_by({terminator_value}), base({eval((attri_value))[1]})\"`\n"
                elif 'byte' in attri_value and terminator_value:
                    go_code += f"\t{declaration.name} byte `mzConverter: terminated_by({terminator_value})\"`\n"
                elif 'short' in attri_value and terminator_value:
                    go_code += f"\t{declaration.name} int16 `mzConverter: terminated_by({terminator_value}), base({eval((attri_value))[1]})\"`\n"
                elif 'bigint' in attri_value and terminator_value:
                    go_code += f"\t{declaration.name} big.Int `mzConverter: terminated_by({terminator_value}), base({eval((attri_value))[1]})\"`\n"
            elif isinstance(declaration, SetDeclaration):
                set_Dec = declaration.name
                set_field = declaration.fields
                go_code += f"\t{set_Dec} struct " + "{\n"
                go_code += f"\t{set_field[0]} {set_field[1]} {set_field[2]}\n"
                go_code += "}{\n"
            elif isinstance(declaration, GenericDeclaration):
                go_code += f"\t{declaration.name} {declaration.type_name}\n"
            elif isinstance(declaration, Identifier):
                go_code += f"\t_metadata string `mzConverter: Identified_by({declaration.tag})\"`\n"
        if external_declaration.external_terminator:
            go_code += f"\t_endRecord string `mzConverter: terminated_by({external_declaration.external_terminator})\"`\n"
        else:
            pass
        go_code += "}\n\n"
    return go_code

def symbol_to_hex(symbol):
    if isinstance(symbol, str) and symbol.startswith("0x"):
        return symbol
    return hex_map.get(symbol, None)

def parse_ast(ast_str):
    external_declaration_pattern = r"ExternalDeclaration\(name=(\w+), declarations=\[(.*?)\]\)"
    ascii_declaration_pattern = r"AsciiDeclaration\(name=([^,]+), terminator=Terminator\(value=([^)]+)\), \s*attri_type=(str|\('int', 'base(\d+)'\)|\('long', 'base(\d+)'\)|\('short', 'base(\d+)'\)|\('bigint', 'base(\d+)'\))"
    ascii_declaration_pattern1 = r"AsciiDeclaration\(name=([^,]+), \s*attri_type=(str|\('int', 'base\d+'\)|\('long', 'base\d+'\)), \s*align_value=([^,]+), \s*padded_value=([^,]+), \s*static_size_value=(\d+)\)"
    generic_declaration_pattern = r"GenericDeclaration\(type_name=(\w+), name=(\w+)\)"
    identified_by_pattern = r"Identified_by\(tag=([^,]+)(?:,\s*AsciiDeclaration\(name=([^,]+),\s*terminator=Terminator\(value=([^)]+)\),\s*attri_type=(str|\('int', 'base(\d+)'\)|\('long', 'base(\d+)'\))(?:,\s*align_value=([^,]+))?(?:,\s*padded_value=([^,]+))?(?:,\s*static_size_value=(\d+))?(?:,\s*encoded_value=([^,]+))?(?:,\s*externalonly=([^,]+))?(?:,\s*additional_attributes=\[(.*?)\])?)?(?:,\s*SetDeclaration\(name=([^,]+), varname=([^,]+), query_B1=\[(.*?)\], query_B2=\[(.*?)\]\))?\)"
    set_declaration_pattern = r"SetDeclaration\(\s*name=([^,]*),?\s*varname=([^,]*),?\s*query_B1\s*=\s*\[\s*\(\s*'(\w+)'\s*,\s*'(\w+)'\s*,\s*'(\w+)'\s*\)\s*\],\s*query_B2\s*=\s*\["
    ast_matches = re.findall(external_declaration_pattern, ast_str, re.DOTALL)
    if not ast_matches:
        raise ValueError("Invalid AST format")
    external_declarations = []
    for match in ast_matches:
        name = match[0]
        declarations_str = match[1]
        if 'Terminator' in match[1].split("AsciiDeclaration")[0]:
            external_terminator = match[1].split("AsciiDeclaration")[0].replace(",","").replace("Terminator(value=","").replace(")","").replace(" ","")
        else:
            external_terminator = None 
        declarations = []
        for declaration_match in re.finditer(set_declaration_pattern, match[1]):
            set_declaration_name = declaration_match.group(1)
            varname = declaration_match.group(2)
            fields = (declaration_match.group(3), declaration_match.group(4), declaration_match.group(5))
            queries = None
            declaration = SetDeclaration(name=set_declaration_name, varname=varname, fields=fields, queries=queries)
            declarations.append(declaration)

        for declaration_match in re.finditer(identified_by_pattern, declarations_str):
            tag = declaration_match.group(1)
            ascii_declaration_name = declaration_match.group(2)
            terminator_value = declaration_match.group(3)
            attri_type = declaration_match.group(4)
            encoded_value = declaration_match.group(10)
            externalonly = declaration_match.group(11)
            ascii_declaration = AsciiDeclaration(name=ascii_declaration_name, terminator=Terminator(value=terminator_value), attri_type=attri_type, encoded_value=encoded_value, externalonly=externalonly)
            identifier = Identifier(tag=tag.rstrip(")"))
            declarations.append(identifier)
            declarations.append(ascii_declaration)
        for declaration_match in re.finditer(ascii_declaration_pattern, declarations_str):
            declaration_name = declaration_match.group(1)
            terminator_value = declaration_match.group(2).strip()
            attri_type = declaration_match.group(3)
            if declaration_name == 'tag':
                continue
            else:
                declaration = AsciiDeclaration(name=declaration_name, terminator=Terminator(value=terminator_value), attri_type=attri_type)
            declarations.append(declaration)

        for declaration_match in re.finditer(ascii_declaration_pattern1, declarations_str):
            declaration_name = declaration_match.group(1)
            attri_type = declaration_match.group(2)
            align_value = declaration_match.group(3)
            padded_value = declaration_match.group(4)
            static_size_value = int(declaration_match.group(5))
            declaration = AsciiDeclaration(name=declaration_name, terminator=None, attri_type=attri_type, align_value=align_value, padded_value=padded_value, static_size_value=static_size_value)
            declarations.append(declaration)
        
        
        for declaration_match in re.finditer(generic_declaration_pattern, declarations_str):
            type_name = declaration_match.group(1)
            declaration_name = declaration_match.group(2)
            declaration = GenericDeclaration(type_name=type_name, name=declaration_name)
            declarations.append(declaration)
        external_declarations.append(ExternalDeclaration(name=name, declarations=declarations, external_terminator=external_terminator))
    return external_declarations

def main_check_code(q, maxfile):
    failed_Cases = 0
    failed_Cases_list = []
    passed_Cases = 0
    while q != maxfile:
        try:
            print(f"\n FOR FILE {q}\n")
            file = f'UDLF files/Test{q}.udlf'
            with open(file, 'r') as f:
                content = f.read()
            block_value_ext = check_Ext_int(getcontentfile(content), 'external')
            asts = parse_multiple_lists(block_value_ext)
            ast1 = ""
            for ast in asts:
                ast1 = ast1 + str(ast) + "\n"
            ast2 = parse_ast(ast1)
            go_code = generate_go_code(ast2)
            print(go_code)
            passed_Cases += 1
        except Exception as e:
            failed_Cases += 1
            failed_Cases_list.append(q)
            print(f"\n\nError: {e}\n\n")
            
            pass
        q += 1
    if failed_Cases == 0:
        print(f"Total Passed Cases: {passed_Cases}")
    else:
        print(f"Total Passed Cases: {passed_Cases}, Total Failed Cases: {failed_Cases}", f"Failed Cases: {failed_Cases_list}")

def flask_app():
    app = Flask(__name__)
    @app.route('/', methods=['POST'])
    def receive_tokens_ext():
        cont = request.data.decode('utf-8')
        blocks = {'external':  check_Ext_int(getcontentfile(cont), 'external'),
            'internal': check_Ext_int(getcontentfile(cont), 'internal'), 
            'in_map':  check_Ext_int(getcontentfile(cont), 'in_map'), 
            'out_map':  check_Ext_int(getcontentfile(cont), 'out_map'), 
            'session':  check_Ext_int(getcontentfile(cont), 'session')}
        asts = parse_multiple_lists(blocks['external'])
        ast1 = ""
        for ast in asts:
            ast1 = ast1 + str(ast) + "\n"
        ast2 = parse_ast(ast1)
        go_code = generate_go_code(ast2)
        return go_code
    if __name__ == '__main__':
        app.run(host="0.0.0.0", port=5011, debug=True) 

def main_check_test(q, maxfile):
    passed_Cases = 0
    failed_Cases = 0
    failed_Cases_list = []
    while q != maxfile:
        try:
            file = f'UDLF files/Test{q}.udlf'
            with open(file, 'r') as f:
                content = f.read()
            block_value_ext = check_Ext_int(getcontentfile(content), 'external')
            asts = parse_multiple_lists(block_value_ext)
            ast1 = ""
            for ast in asts:
                ast1 = ast1 + str(ast) + "\n"
            ast2 = parse_ast(ast1)
            go_code = generate_go_code(ast2)
            print(f'test {q} passed')
            passed_Cases += 1
        except:
            print(f'test {q} failed')
            failed_Cases += 1
            failed_Cases_list.append(q)
            pass
        q += 1
    print(f"Total Passed Cases: {passed_Cases}, Total Failed Cases: {failed_Cases}")
    print(f"Failed Cases: {failed_Cases_list}")

main_check_code(84, 85)