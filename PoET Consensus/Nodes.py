from p2pnetwork.node import Node
from utils import Utils
import time
from Blockchain import Blockchain
from Connections import Connections
from Transactions import Transactions
from API import API
from POET import POET

class Nodes():

    def __init__(self, ip, port):
        self.p2p = None
        self.ip = ip
        self.port = port
        self.transactionPool = Transactions()
        self.blockchain = Blockchain()
        self.poet = POET()

    # Starting the connection with other nodes
    def startp2p(self):
        self.obj = Connections(self.ip, self.port)
        self.obj.startconnections()
        self.obj.injectNode(self)

    # Starting the rest API
    def startAPI(self, apiPort):
        self.api = API()
        self.api.injectNode(self)
        self.api.start(apiPort)

















