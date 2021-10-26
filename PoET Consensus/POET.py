import time
import random


class POET():

    # Initialising the wait time to 0 and stop to False
    # Stop is a flag variable which tells whether to stop waiting for the remaining time alloted by PoET consensus
    def __init__(self):
        self.waittime = 0
        self.stop = False

    def mine(self):
        flag = self.timer()
        return flag

    def timer(self):
        # Initialising a random time to wait
        self.waittime = random.randrange(1, 20, 1)
        flag = self.run()
        if flag:
            # Completed wait time and now can mine
            return True
        else:
            # Returned False signifies it does not have the right to mine
            self.waittime = 0
            return False


    def run(self):
        starttime = time.time()
        # Loop to wait for specified waittime
        # exit either on elapsed time == wait time
        # or some other node has already mined and brodcasted 'MINED' message which in turn flipped the stop flag to True
        while True:
            curtime = time.time()
            elapsedtime = curtime - starttime
            if self.stop:
                # Returned False signifies it does not have the right to mine
                return False
            if elapsedtime >= self.waittime:
                # Completed wait time and now can mine
                return True




