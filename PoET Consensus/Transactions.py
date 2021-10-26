from Blockchain import Blockchain
from POET import POET

class Transactions():

    def __init__(self):
        self.transactions = []

    #Creating a new Transaction
    def create_transaction(self, customer, receiver, order, orderdatetime, amount):
        transaction = {'Customer': customer, 'Receiver': receiver, 'Order Details': order, 'Order Amount': amount, 'Order DateTime': orderdatetime}
        self.addTransaction(transaction)
        return transaction

    def currentpool(self):
        return self.transactions

    def addTransaction(self, transaction):
        self.transactions.append(transaction)

    # Emptying the pool after mining the block
    def emptyPool(self):
        self.transactions = []

    # Time to mine executes PoET consensus for every node and gets a flag whether it has got the right to mine or not
    # True : Gained the right
    # False : Has to stop before wait time was over and does not have the right to mine
    def timetomine(self, poet):
        if len(self.transactions) >= 1:
            flag = poet.mine()
            return flag
