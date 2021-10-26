import datetime
import requests
import json
import hashlib

class Blockchain():

    def __init__(self):
        self.chain = []
        self.genesis()

    #Creating genesis Block
    def genesis(self):
        genesisBlock = self.create_block('genesisHash', [],'Genesis Mined')
        genesisBlock['timestamp'] = 0

    def create_block(self, prev_hash, transactions, miner):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'prev_hash': prev_hash,
                 'transactions': transactions,
                 'Miner': miner}
        self.add_block_to_chain(block)
        return block

    def add_block_to_chain(self, block):
        self.chain.append(block)

    def fetch_previous_block(self):
        return self.chain[-1]

    # Hash method ; static method to encode the block using SHA-256 Hash
    @staticmethod
    def hash(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

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






