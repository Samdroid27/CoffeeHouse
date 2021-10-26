# Custom Package installed for P2P networking
from p2pnetwork.node import Node

from utils import Utils
from Message import Message
from Socket import Socket
from Blockchain import Blockchain

import json

node = None

class Connections(Node):

    # Initialising blank peer group
    # Initialising the connector variable which contains the address
    def __init__(self, ip, port):
        super(Connections, self).__init__(ip, port, None)
        self.peers = []
        self.connector  = Socket(ip, port)

    def injectNode(self, injectedNode):
        global node
        node = injectedNode

    def startconnections(self):
        self.start()
        self.connecttofirst()

    #  Connecting to First node at port 5000
    def connecttofirst(self):
        if self.port != 5000:
            self.connect_with_node('localhost', 5000)

    # Overriding the inbuilt function in P2P library
    def outbound_node_connected(self, connected_node):
        message = Message(self.connector, 'INITIAL', '')
        encodedmessage = Utils.encode(message)
        self.send_to_node(connected_node, encodedmessage)

    # Overriding the inbuilt function in P2P library which handles message which are broadcasted by other nodes
    def node_message(self, connected_node, info):
        message = Utils.decode(json.dumps(info))

        # Handling Initial message from incoming nodes
        if message.type == 'INITIAL':
            peercon = message.connector
            print("Connected with: " + peercon.ip + " " + str(peercon.port))
            if self.port == 5000:
                self.senddata(connected_node)
            self.peers.append(peercon)

        # Updating the peerlist for the new node
        if message.type == 'PEERLIST':
            self.makeconnections(message.data)

        # Adding a transaction added by other node and broadcasted in P2P network
        if message.type == 'TRANSACTION':
            transaction = message.data
            node.transactionPool.addTransaction(transaction)

        # The node is ordered to participate in the mining competition and win a chance to mine a block
        # The order is brodcasted by the node which added last transaction in the pool
        if message.type == "TIMETOMINE":
            node.poet.stop = False
            # flag stores whether the node won the race of PoET consensus
            flag = node.transactionPool.timetomine(node.poet)
            transaction = message.data
            # If won the race of consensus, gets the right to mine
            if flag:
                # Creating a block and brodcasting the mined block in the P2P network and emptying the pool
                node.blockchain.create_block(Blockchain.hash(node.blockchain.chain[-1]), transaction, str(self.connector.ip) + str(self.connector.port))
                node.obj.minermessage(node.blockchain.chain[-1])
                node.transactionPool.emptyPool()

        # Receiving the message that some other node has already mined
        # and thus stop waiting for the rest of the time remaining according to consensus
        # and adding the already mined to its copy of blockchain
        if message.type == 'MINED':
            block = message.data
            node.blockchain.add_block_to_chain(block)
            node.poet.stop = True
            node.transactionPool.emptyPool()

    # Sending the peerlist from Node 5000 to new Node
    def senddata(self, connected_node):
        data = self.peers
        message = Message(self.connector, 'PEERLIST', data)
        encodedmessage = Utils.encode(message)
        # Builtin function to send message to connected node
        self.send_to_node(connected_node, encodedmessage)

    # Broadcasting the transaction
    def sendtransaction(self, transaction):
        data = transaction
        message = Message(self.connector, 'TRANSACTION', data)
        encodedmessage = Utils.encode(message)
        # Builtin function to broadcast transaction
        self.send_to_nodes(encodedmessage)

    # Broadcast message to network to race for mining
    def makemine(self, transaction):
        data = transaction
        message = Message(self.connector,'TIMETOMINE', transaction)
        encodedmessage = Utils.encode(message)

        # Broadcasting to the node's Peers
        self.send_to_nodes(encodedmessage)

        # Self running the consensus
        node.poet.stop = False
        flag = node.transactionPool.timetomine(node.poet)
        if flag:
            node.blockchain.create_block(Blockchain.hash(node.blockchain.chain[-1]), transaction,str(self.connector.ip) + str(self.connector.port))
            node.obj.minermessage(node.blockchain.chain[-1])
            node.transactionPool.emptyPool()

    # Connecting with nodes
    def makeconnections(self, peerlist):
        for peer in peerlist:
            # Builtin function to make connections
            self.connect_with_node(peer.ip, peer.port)
            print("connected to peer " + str(peer.port))

    # Node issuing that it has mined the block
    def minermessage(self, block):
        data = block
        message = Message(self.connector, 'MINED', data)
        encodedmessage = Utils.encode(message)
        self.send_to_nodes(encodedmessage)


