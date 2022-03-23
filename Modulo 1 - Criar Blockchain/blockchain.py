import datetime
import hashlib
import json
from flask import Flask,jsonify

# Parte 1, criar um Blockchain

class Blockchain:
    #definição da class
    def __init__(self):
        #artributo incializado com lista
        self.chain = []
        #função com inicialização
        self.create_block(proof = 1, previous_hash = '0')
    
    #função de criação
    def create_block(self, proof, previous_hash):
        #declaração do dicionário
        block = {
            'index': len(self.chain) + 1, 
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash':previous_hash
        }
        
        self.chain.append(block)
    
        return block
    
    #retorna bloco anterior
    def get_previous_block(self):
        return self.chain[-1]
    
    #criar prova de trabalho
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            #aqui está o nível de dificuldade do hash
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            #confere 4 primeiros posições da string
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                
        return new_proof
    
    #criando hash
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        
        return hashlib.sha256(encoded_block).hexdigest()
    
    #valida chain
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
            
        return True
    
#cria uma app web
app = Flask(__name__)

#cria objeto
blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])

#mineração
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response =  {
        'message': 'Parabêns voce minerou um bloco!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    
    return jsonify(response), 200
    
@app.route('/get_chain', methods = ['GET'])

#busca a blockchain
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])

#def
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {
        'message': 'Tudo certo, o Blockchain é valido',
        }
    else:
        response = {
        'message': 'O Blockchain não é valido',
        }
    
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)