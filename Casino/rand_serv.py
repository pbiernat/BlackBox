'''
Can you predict the numbers?
This is a pretty well known weakness of MT19937. Recreate the internal state of the generator '''

from twisted.internet import reactor, protocol
from mersenne import mtwister
import random
PORT = 9005

SECRET = "flag{M0re_r3liable_th@n_f0rtun3_c00kiez}"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CLEAR = '\x1b[2J\x1b[1;1H'
BANNER = bcolors.WARNING + """
.--------------------------------------------. 
| [$]       BLACKBOX FLAG CASINO         [$] |
'--------------------------------------------'""" + bcolors.ENDC

GAMES = """
| 1: Slots - Unlimited Plays!                |
| 2 <num>: Lucky Numbers - Guess the next    | 
|                        Slot to get a flag! |
|  _______________________________________   |
|                                            |
|""" + bcolors.WARNING + """     [ $$$$$ ]   [ $$$$$ ]   [ $$$$$ ] """ + bcolors.ENDC + """     |
|                                            |
'--------------------------------------------'
"""

SLOT = bcolors.OKBLUE + "[- %s -]\n" + bcolors.ENDC 

CHOICE = bcolors.OKGREEN + "[$] Choice: " + bcolors.ENDC
FAIL = bcolors.FAIL + "[ X_X ] ~ Not Your Lucky Day ~ \n" + bcolors.ENDC

class MyServer(protocol.Protocol):
	def __init__(self):
		self.mt = mtwister(random.randint(0,2 **32))

        def print_menu(self):
            self.transport.write(BANNER)
            self.transport.write(GAMES)
            self.transport.write(CHOICE)

        def slots(self):
           self.transport.write(SLOT % str(self.mt.extract_number()))

        def lucky(self, guess):
            if (self.mt.extract_number() == guess):
                self.transport.write(SECRET)
            else:
                self.transport.write(FAIL)
                self.transport.write(CHOICE)

	def dataReceived(self,data):
                data = data.strip()
		if(data.startswith("1")):
		    self.slots()	

		elif(data.startswith("2")):
                    try:
                        guess = int(data[2:])
                        self.lucky(guess)
                    except:
                        self.transport.write(FAIL)
                        self.transport.write(CHOICE)
                    
                else:
                    self.print_menu()
	def connectionMade(self):
                self.print_menu()
		self.mt = mtwister(random.randint(0,2**32))
	
		
class MyServerFactory(protocol.Factory):
    protocol = MyServer


factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
