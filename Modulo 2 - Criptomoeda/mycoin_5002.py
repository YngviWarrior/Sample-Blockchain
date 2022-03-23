import datetime
import hashlib
import json
from flask import Flask,jsonify,request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Parte 1, criar um Blockchain

class Blockchain:
    #definição da class
    def __init__(self):
        #artributo incializado com lista
        self.chain = []
        #atributo de transações
        self.transactions = []
        #função com inicialização
        self.create_block(proof = 1, previous_hash = '0')
        #atributo do tipo set para todos os nós da rede
        self.nodes = set()
    
    #função de criação
    def create_block(self, proof, previous_hash):
        #declaração do dicionário
        block = {
            'index': len(self.chain) + 1, 
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash':previous_hash,
            'transactions': self.transactions
        }
        
        #zerar a lista ao criar bloco
        self.transactions = []
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
    
    #método para criar transação
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            'sender': sender, 
            'receiver': receiver, 
            'amount': amount
        })
        
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    #método para adicionar nós
    def add_node(self, address):
        #não só adiciona o nós,
        parsed_url = urlparse(address)
        #mas vai extrair uma parte do endereço
        self.nodes.add(parsed_url.netloc)
        
    #método de substituição da cadeia, se achar um bloco maior
    #equivalente ao protocolo de consenso estudado
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        #verifica se variavel é diferente de None
        if longest_chain:
            self.chain = longest_chain
            return True
        return False 
    
#cria uma app web
app = Flask(__name__)

#cria endereço para os nós
node_address = str(uuid4()).replace('-', '')

#cria objeto
blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])

#mineração
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver='Sane', amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response =  {
        'message': 'Parabêns voce minerou um bloco!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transaction': block['transactions']
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

@app.route('/add_transaction', methods = ['POST'])

#post para adicionar transações
def add_transaction():
    #recebe obj json enviado pelo postman
    json = request.get_json()
    transactions_keys = ['sender', 'receiver', 'amount']
    
    #verifica se todas as chaves foram enviadas
    if not all(key in json for key in transactions_keys):
        return 'Alguns elementos estão faltando', 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'messege': f'Esta transação será adicionada ao bloco {index}'}
    return jsonify(response), 201

#requisição para conectar um nó a rede
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    #armazena a chave nodes
    nodes = json.get('nodes')
    if nodes is None:
        return "Vazio", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Todos nós conectados, blockchain contem os seguintes nós:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#substituição de blocos invalidos
@app.route('/replace_chain', methods= ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        response = {'message': 'Os nós tinham cadeias diferentes então foi substituida',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'Não houve subistituição',
                    'actual_chain': blockchain.chain}
        
    return jsonify(response), 201
    

app.run(host = '0.0.0.0', port = 5002)