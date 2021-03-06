#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 14:45:58 2021

@author: hernangoldenberg
"""

# Modulo 2 - Crear una cryptomoneda
# Flask==0.12.2 : pip install Flask==0.12.2
# Cliente HTTP Postman: hhtps://www.getpostman.com/
# Versiones
# Python 3.8.8
# Flask 1.1.2
# requests 2.18.4 pip install requests==2.18.4

# Importar las librerias

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Parte 1 - Crear la Blockchain

class Blockchain:
    
    def __init__(self):
        
        self.chain = []
        self.transactions = []
        self.create_block (proof = 1, previous_hash = '0')
        self.nodes = set()
        
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation [:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain [0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block ['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
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
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

# Parte 2 - Minado de un Blockchain

# Crear una web app
app = Flask(__name__)
app.config['JSONIFY_PRETTY_REGULAR'] = False

# Crear la direcci??n del nodo en el puerto 5000
node_address = str(uuid4()).replace('-',' ')

# Crear una blockchain
blockchain = Blockchain()

# Minar un nuevo bloque
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = "El Cholo", amount = 10)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Buen??simo, has minado un nuevo bloque',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous-hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# Obtener la cadena de bloques completa
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Comprobar si la cadena de bloques es v??lida
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : 'Todo correcto. La cadena de bloques es v??lida.'}
    else:
        response = {'message' : 'Houston, tenemos un problema. La cadena de bloques no es v??lida.'}
    return jsonify(response), 200  

# A??adir una nueva transacci??n a la cadena de bloques
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all(key in json for key in transaction_keys):
        return 'Faltan algunos elementos de la transacci??n', 400
    index = blockchain.add_transaction(json['sender'],['receiver'],['amount'])
    response = {'message':f'La transacci??n ser?? a??adida al bloque {index}'}
    return jsonify(response), 201

# Parte 3 - Descentralizar Cadena de Bloques
    
# Conectar nuevos nodos
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None: 
        return 'No hay nodos para a??adir', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'Todos los nodos han sido conectados. La cadena de Jbcoins contiene ahora los nodos siguientes: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Reemplazar la cadena por la m??s larga (si es necesario)
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message' : 'Los nodos ten??an diferentes cadenas, que han sido todas reemplazadas por la m??s larga.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message' : 'Todo correcto. La cadena en todos los nodos ya es la m??s larga.',
                    'actual_chain' : blockchain.chain}
    return jsonify(response), 200  


# Ejecutar la app
app.run(host = '0.0.0.0', port = 5000)

