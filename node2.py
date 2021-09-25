# Creating a decentralized Blockchain for Dexter's Coffee House

# importing libraries

# to obtain the timestamp
import datetime

# importing flask for creating the web app
from flask import Flask, jsonify, request

import requests
import json

# to calculate hash using SHA256 function
import hashlib

# to make connections between nodes
from uuid import uuid4
from urllib.parse import urlparse

# create Blockchain blueprint
class Blockchain:

    # initializing the genesis block and setting the initial values
    def __init__(self):
        self.chain = []
        self.transactions_pool = []
        self.create_block(prev_hash='0')
        self.nodes = set()

    # creating a new block before mining by storing appropriate values
    def create_block(self, prev_hash):

        # storing all the available transactions to the block before mining
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': 1,
                 'prev_hash': prev_hash,
                 'transactions': self.transactions_pool}

        # emptying the transaction pool after adding to the block
        self.transactions_pool = []

        if len(self.chain) == 0:
            self.chain.append(block)
        return block

    # get the last block from the blockchain
    def fetch_previous_block(self):
        return self.chain[-1]

    # retrieve complete information of the block as requested by the user using block id
    def get_block(self, block_index):
        block = []
        if block_index > len(self.chain):
            return block
        block.append(self.chain[block_index - 1])
        return block

    # retrieve timestamp of the block as requested by the user using block id
    def get_timestamp(self, block_index):
        if block_index > len(self.chain):
            return -1
        return self.chain[block_index - 1]['timestamp']

    # generating proof of work by finding a valid nonce
    # a valid nonce is a nonce value which when added to the block provides a hash with 4 leading 0s (0000)
    def proof_of_work(self, block):
        nonce = 1
        check = False
        while check is False:
            block['nonce'] = nonce
            encoded_block = json.dumps(block, sort_keys=True).encode()
            cur_hash = hashlib.sha256(encoded_block).hexdigest()
            if cur_hash[:4] == '0000':
                check = True
            else:
                nonce += 1
        return [block, cur_hash]

    # finding the hash of a block by giving a complete block as a parameter
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # checking the validity of a chain by traversing through the chain
    # the prev_hash value for the current block should be equal to the hash value of the previous block
    # checking if the hash value of all the blocks has 4 leading zeros except the genesis block
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(previous_block):
                return False
            encoded_block = json.dumps(block, sort_keys=True).encode()
            cur_hash = hashlib.sha256(encoded_block).hexdigest()
            if cur_hash[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    # adding a transaction into the current pool of transactions before adding them into a block
    def add_transaction(self, customer, receiver, order, amount):
        self.transactions_pool.append({'Customer': customer,
                                       'Receiver': receiver,
                                       'Order Details': order,
                                       'Order Amount': amount})

    # adding a node into the network of connected nodes maintaining blockchain
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # updating the chain of a node by comparing with chains in other nodes
    # the chain with the maximum length among all nodes is considered the latest chain
    # with this function we find the latest chain among all nodes
    def update_chain(self):
        connections = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in connections:
            response = requests.get(f'http://{node}/get_node_chain')
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


# creating a web app using flask
app = Flask(__name__)

# creating an address for the node on the mentioned port number
node_address = str(uuid4()).replace('-', '')

# creating an object of the Blockchain class
blockchain = Blockchain()

# making connections between the nodes
# the nodes to be connected are provided in JSON format during API call
@app.route('/make_connections', methods=['POST'])
def make_connections():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Connections made.',
                'connected_nodes': list(blockchain.nodes)}
    return jsonify(response), 201


# adding a new transaction into the current pool of transactions
# transaction details are provided in JSON format during API call
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['Customer', 'Receiver', 'Order Details', 'Order Amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    blockchain.add_transaction(json['Customer'], json['Receiver'], json['Order Details'], json['Order Amount'])
    response = {'message': 'This transaction is successfully added to the Transaction Pool. It will be mined where there are atleast 3 transactions in the Pool.'}

    # a block can store a maximum of 3 transactions
    # as soon as there are 3 unverified transactions in the pool, the transaction pool is emptied into the block and the block is mined
    if len(blockchain.transactions_pool) == 3:
        return mine_block()
    return jsonify(response), 201


# mining a block and displaying the information on the current block with its hash value
# before mining a block, it is checked whether the chain of the node is updated or not
# a hash value is generated using all the information on the block by calling the proof_of_work function
@app.route('/mine_block', methods=['GET'])
def mine_block():
    flag = blockchain.update_chain()
    prev_block = blockchain.fetch_previous_block()
    prev_hash = blockchain.hash(prev_block)
    block = blockchain.create_block(prev_hash)
    [block, cur_hash] = blockchain.proof_of_work(block)
    blockchain.chain.append(block)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'nonce': block['nonce'],
                'previous_hash': block['prev_hash'],
                'transactions': block['transactions'],
                'current_hash': cur_hash}
    return jsonify(response), 200


# retrieving the complete chain details of the node provided
@app.route('/get_node_chain', methods=['GET'])

def get_node_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# display the complete chain details along with corresponding hash values for all blocks
@app.route('/get_chain', methods=['GET'])
def get_chain():
    output = []
    for block in blockchain.chain:
        cur_hash = blockchain.hash(block)
        output.append({'block': block, 'cur_hash': cur_hash})
    response = {'Chain': output, 'Length': len(output)}
    return jsonify(response), 200


# checking the validity of the blockchain
@app.route('/is_valid', methods=['GET'])
def is_valid():
    flag = blockchain.is_chain_valid(blockchain.chain)
    if flag:
        response = {'message': 'Valid Blockchain'}
    else:
        response = {'message': 'Invalid Blockchain'}
    return jsonify(response), 200

# displaying the details of a specific block
# block index is provided in JSON format during API call
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


# displaying the timestamp of the creation of a specific block
# block index is provided in JSON format during API call
@app.route('/get_timestamp', methods=['POST'])
def get_timestamp():
    json = request.get_json()
    block_index = json.get('index')
    block_timestamp = blockchain.get_timestamp(block_index)
    if block_timestamp == -1:
        response = {'message': 'Invalid block index'}
    else:
        response = {'Block timestamp': block_timestamp}
    return jsonify(response), 201

# updating the chain to the latest chain in the network and displaying the updated chain
@app.route('/update_chain', methods=['GET'])
def update_chain():
    is_chain_updated = blockchain.update_chain()
    if is_chain_updated:
        response = {'message': 'The chain of the current node has been updated',
                    'updated_chain': blockchain.chain}
    else:
        response = {'message': 'No updates needed. The chain is the latest one.',
                    'updated_chain': blockchain.chain}
    return jsonify(response), 200


# running the app on mentioned host and port
app.run(host='127.0.0.1', port=5002)
