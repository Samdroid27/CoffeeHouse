# Module 2 - Create a Cryptocurrency

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/
# requests==2.18.4: pip install requests==2.18.4

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(previous_hash='0')
        self.nodes = set()

    def create_block(self, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': 1,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        if len(self.chain) == 0:
            self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def get_block(self, block_index):
        block = []
        if block_index > len(self.chain):
            return block
        block.append(self.chain[block_index - 1])
        return block

    def get_timestamp(self, block_index):
        if block_index > len(self.chain):
            return -1
        return self.chain[block_index - 1]['timestamp']

    def proof_of_work(self, block):
        new_proof = 1
        check_proof = False
        flag = 1
        while check_proof is False:
            block['proof'] = new_proof
            encoded_block = json.dumps(block, sort_keys=True).encode()
            hash_operation = hashlib.sha256(encoded_block).hexdigest()
            if hash_operation[:4] == '000000':
                check_proof = True
            else:
                new_proof += 1
        return [block, hash_operation, flag]

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # previous_proof = previous_block['proof']
            # proof = block['proof']
            encoded_block = json.dumps(block, sort_keys=True).encode()
            hash_operation = hashlib.sha256(encoded_block).hexdigest()
            if hash_operation[:4] != '000000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, customer, receiver, order, amount):
        self.transactions.append({'Customer': customer,
                                  'Receiver': receiver,
                                  'Order Details': order,
                                  'Order Amount': amount})
        previous_block = self.get_previous_block()
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


# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    flag = blockchain.replace_chain()
    previous_block = blockchain.get_previous_block()
    # previous_proof = previous_block['proof']
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(previous_hash)
    [block, cur_hash, flag] = blockchain.proof_of_work(block)
    if flag:
        blockchain.chain.append(block)
        response = {'message': 'Congratulations, you just mined a block!',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previous_hash': block['previous_hash'],
                    'transactions': block['transactions'],
                    'current_hash': cur_hash}
    else:
        response = {'message': 'Do not mined, but you could not mine'}
    return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Checking if the Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'We have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['Customer', 'Receiver', 'Order Details', 'Order Amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['Customer'], json['Receiver'], json['Order Details'], json['Order Amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/get_block', methods=['POST'])
def get_block():
    json = request.get_json()
    block_index = json.get('index')
    block = blockchain.get_block(block_index)
    if len(block) == 0:
        response = {'message': 'Invalid block index'}
    else:
        block_hash = blockchain.hash(block[0])
        response = {'Block': block[0],
                    'Block Hash': block_hash
                    }
    return jsonify(response), 201


@app.route('/get_timestamp', methods=['POST'])
def get_timestamp():
    json = request.get_json()
    block_index = json.get('index')
    block_timestamp = blockchain.get_timestamp(block_index)
    if block_timestamp == -1:
        response = {'message': 'Invalid block index'}
    else:
        response = {'Block timestamp': block_timestamp
                    }
    return jsonify(response), 201


# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Hadcoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


# Running the app
app.run(host='127.0.0.1', port=5002)
