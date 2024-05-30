import re
from collections import namedtuple

# Define namedtuples for declarations
Terminator = namedtuple('Terminator', ['value'])
AsciiDeclaration = namedtuple('AsciiDeclaration', ['name', 'terminator', 'attri_type'])
GenericDeclaration = namedtuple('GenericDeclaration', ['type_name', 'name'])
ExternalDeclaration = namedtuple('ExternalDeclaration', ['name', 'declarations'])

def parse_ast(ast_str):
    # Define regex patterns to match the AST representation
    external_declaration_pattern = r"ExternalDeclaration\(name=(\w+), declarations=\[(.*?)\]\)"
    ascii_declaration_pattern = r"AsciiDeclaration\(name=(\w+), terminator=Terminator\(value=0x([a-fA-F0-9]+)\), attri_type=(\w+|(?:\('.*?'\)))\)"
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
        print('TEST -1')
        for declaration_match in re.finditer(ascii_declaration_pattern, declarations_str):
            print('TEST 0')
            declaration_name = declaration_match.group(1)
            print('TEST 1')
            terminator_value = declaration_match.group(2).strip()
            print('TEST 2')
            attri_type = declaration_match.group(3)
            print('TEST 3')
            declaration = AsciiDeclaration(name=declaration_name, terminator=Terminator(value=terminator_value), attri_type=attri_type)
            declarations.append(declaration)
            
        for declaration_match in re.finditer(generic_declaration_pattern, declarations_str):
            type_name = declaration_match.group(1)
            declaration_name = declaration_match.group(2)
            declaration = GenericDeclaration(type_name=type_name, name=declaration_name)
            declarations.append(declaration)

        external_declarations.append(ExternalDeclaration(name=name, declarations=declarations))

    return external_declarations

def generate_go_code(external_declarations):
    go_code = "package main\n\nimport (\n\t\"github.com/shopspring/decimal\"\n)\n\n"
    
    for external_declaration in external_declarations:
        go_code += f"type {external_declaration.name} struct {{\n"
        for declaration in external_declaration.declarations:
            if isinstance(declaration, AsciiDeclaration):
                go_code += f"\t{declaration.name} string\n"
            elif isinstance(declaration, GenericDeclaration):
                go_code += f"\t{declaration.name} {declaration.type_name}\n"
        go_code += "}\n\n"
    
    return go_code

# Example AST string
ast_str = """
ExternalDeclaration(name=File_Header_Ext, declarations=[GenericDeclaration(type_name=Filename, name=filename), GenericDeclaration(type_name=CreationTime, name=creationTime), GenericDeclaration(type_name=DctID, name=dctID), GenericDeclaration(type_name=DctVer, name=dctVer), GenericDeclaration(type_name=DctDef, name=dctDef)])
ExternalDeclaration(name=DctDefValue, declarations=[])
ExternalDeclaration(name=Rishit_jain, declarations=[])
ExternalDeclaration(name=VCDR_Ext, declarations=[])
ExternalDeclaration(name=VCDR_Ext, declarations=[])
ExternalDeclaration(name=File_Trailer_Ext, declarations=[GenericDeclaration(type_name=CloseTime, name=closeTime), GenericDeclaration(type_name=SeqnumFirst, name=seqnumFirst), GenericDeclaration(type_name=SeqnumLast, name=seqnumLast), GenericDeclaration(type_name=RecordCount, name=recordCount)])
ExternalDeclaration(name=NPO_Reporting, declarations=[])
ExternalDeclaration(name=ildContentFormat_GenBand, declarations=[])
ExternalDeclaration(name=BIExt, declarations=[AsciiDeclaration(name=CallingPartyNumber, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=CalledPartyNumber, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OutpulseDigits, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=DialedNumber, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=DigitsDialed, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=Cnumber, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OriginalCalledNumber, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigLineorTrunkType, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=TermLineorTrunkType, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=TermLRN, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=CallStartDate, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=CallstartTime, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=CallEndDate, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=CallEndTime, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=CallDuration, terminator=Terminator(value=0x2c), attri_type=('long', 'base10')), AsciiDeclaration(name=InTG, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OutTG, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=PCVOrigIOI, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=PCVTermIOI, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=ICID, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=InTGNumber, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=OutTGNumber, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=OrigSignalRelCause, terminator=Terminator(value=0x2c), attri_type=('long', 'base10')), AsciiDeclaration(name=TermSignalRelCause, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=OriginatingDateandTime, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=InternalReleaseCause, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=DisconnectDirection, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OriginatingMG, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=TerminatingMG, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=AnswerType, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=ORGREMRFACTOR, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=TRMRemRFACTOR, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigTrunkGroupCircuitID, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=TermTrunkGroupCircuitID, terminator=Terminator(value=0x2c), attri_type=('int', 'base10')), AsciiDeclaration(name=OriginatingTGRP, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigTransmitPlPercentage, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigTransmitJitterMax, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigTransmitJitterMean, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=TermTransmitPlPercentage, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=TermTransmitJitterMax, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=TermTransmitJitterMean, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigReceivingPlPercentage, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigReceivingJitterMax, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=OrigReceivingJitterMean, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=TermReceivingPlPercentage, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=TermReceivingJitterMax, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=TermReceivingJitterMean, terminator=Terminator(value=0x2c), attri_type=str), AsciiDeclaration(name=CallType, terminator=Terminator(value=0xA), attri_type=str)])
"""

# Parse the AST
parsed_ast = parse_ast(ast_str)

# Generate Go code
go_code = generate_go_code(parsed_ast)

# Print the generated Go code
print(go_code)