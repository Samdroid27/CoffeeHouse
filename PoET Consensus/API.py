from flask_classful import FlaskView, route
from flask import Flask, jsonify, request
from Blockchain import Blockchain
from POET import POET
import datetime
from Transactions import Transactions
from Connections import Connections
import requests
import json
import hashlib
from utils import Utils

node = None

class API(FlaskView):

    def __init__(self):
        self.app = Flask(__name__)

    def start(self, port):
        API.register(self.app, route_base='/')
        self.app.run(host='localhost', port=port)

    # Accessing the Node object
    def injectNode(self, injectedNode):
        global node
        node = injectedNode

    @route('/add_transaction', methods=['POST'])
    def add_transaction(self):
        json = request.get_json()
        transaction_keys = ['Customer']
        if not all(key in json for key in transaction_keys):
            return 'Some elements of the transaction are missing', 400

        # Creating a new transaction
        transaction = node.transactionPool.create_transaction(customer=json["Customer"], receiver=json['Receiver'], order= json['Order Details'], orderdatetime= str(datetime.datetime.now()), amount=json['Order Amount'])

        # Adding transaction to the Transaction Pool
        node.obj.sendtransaction(transaction)

        # Since the Limit of Pool is set to 1 transaction for easy demonstration purpose ,
        # every block is now ordered to requested to race for mining the block according the PoET consensus
        node.obj.makemine(transaction)
        response = {'message': 'This transaction is successfully added to the Transaction Pool.'}
        return jsonify(response), 201

    # Get the Latest Blockchain
    @route('/get_chain', methods=['GET'])
    def get_chain(self):
        output = []
        for block in node.blockchain.chain:
            cur_hash = Blockchain.hash(block)
            output.append({'block': block, 'cur_hash': cur_hash})
        response = {'Chain': output, 'Length': len(output)}
        return jsonify(response), 200

    # view the transaction Pool
    @route('/viewpool', methods=['GET'])
    def viewpool(self):
        transaction = node.transactionPool.currentpool();
        return jsonify(transaction), 200
