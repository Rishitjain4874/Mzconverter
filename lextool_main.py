import re
from nltk.tokenize import RegexpTokenizer
from flask import Flask, request, jsonify


file = 'sampleUltraFormat.txt'
with open(file, 'r') as f:
    content = f.read()
def check_Ext_int(tokens, key):
    print(f'Checking for {key} keyword in the file\n')
    block = []
    block_value = []
    preview_list = []
    in_block = False
    skip_next_close_brace = False
    for i in tokens:
        if i in ['external', 'internal', 'in_map', 'out_map', 'session'] and i != key:
            in_block = False
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
    | \w+(?:-\w+)*       
    | \$?\d+(?:\.\d+)?%?  
    | \.\.\.              
    |  [{}.,;"'?():\-_<>\[\]]   
    '''
    token1 = []
    word_tokenizer = RegexpTokenizer(word_tokenizer_pattern)
    for sentence in sent_tokens:
        tokens = word_tokenizer.tokenize(sentence)
        token1.extend(tokens)
        token1.append('\n')
    return token1



app = Flask(__name__)

@app.route('/external', methods=['POST'])
def receive_tokens_ext():
    cont = request.data.decode('utf-8')
    block_value_ext = check_Ext_int(getcontentfile(cont), 'external')
    return block_value_ext

@app.route('/internal', methods=['POST'])
def receive_tokens_int():
    cont = request.data.decode('utf-8')
    block_value_ext = check_Ext_int(getcontentfile(cont), 'internal')
    return block_value_ext

@app.route('/test', methods=['GET'])
def hosttoken():
    try:
        block_value_ext = check_Ext_int(getcontentfile(content), 'external')
        return jsonify(block_value_ext)                               
    except Exception as e:
        return {'error': str(e)}
    

if __name__ == '__main__':
    app.run(port=5000)

