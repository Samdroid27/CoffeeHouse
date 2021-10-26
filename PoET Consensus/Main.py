from Nodes import Nodes
import sys

if __name__ == '__main__':
    # receiving the IP , PORT , APIPORT
    ip = sys.argv[1]
    port = int(sys.argv[2])
    apiPort = int(sys.argv[3])

    # Starting the node and its operations
    node = Nodes(ip, port)
    node.startp2p()
    node.startAPI(apiPort)
    node.consensus()
    node.blockchain()
    node.txs()