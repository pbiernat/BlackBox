from twisted.internet import reactor, protocol
import md4
import time
import os
import random
import struct
from decimal import Decimal
PORT = 9006

SECRET = "flag{h0w_l0ng_is_ur_h@sh}"
KEY = os.urandom(8)

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
| [LAME] Legit Admin Management Experience   |
'--------------------------------------------'""" + bcolors.ENDC

MENU = """
|                                            |
| [1 <username>]: Register New Account       |
| [2 <mac+username>]: Get Flag (Admin only)  |
|                                            |
'--------------------------------------------'
"""

CHEATER = bcolors.FAIL + "[!!] HACKER DETECTED LOL [!!]\n" + bcolors.ENDC
def md4mac(message,secret):
	'''
	Simple MAC using MD4 as the underlying hash.
	'''
	hobj = md4.MD4()
	hobj.update(secret + message)
	print "MAC: " + secret + message
	return hobj.digest() + message

def checklogin(data):
	tsthash = data[:32]
	usrstr = data[32:]
	print tsthash
	print usrstr
	rhash = md4mac(usrstr,KEY)[:32]
	print rhash
	if( (rhash == tsthash) and (";admin=1" in usrstr) ) :
		return True
	return False

class MyServer(protocol.Protocol):

        def print_menu(self):
            self.transport.write(BANNER)
            self.transport.write(MENU)

        def register_account(self, username):
            if ";" in username or "admin" in username:
                self.transport.write(CHEATER)
                self.print_menu()
            else: 
                self.transport.write(md4mac(username,KEY)) 
                self.print_menu()
       
        def get_flag(self, userdata):
            tsthash = userdata[:32]
            usrstr = userdata[32:]
	    print tsthash
	    rhash = md4mac(usrstr,KEY)[:32]
	    if( (rhash == tsthash) and (";admin=1" in usrstr) ) :
	        self.transport.write("Nice MAC Dude\n")
                self.transport.write(SECRET)
            else:
                self.transport.write("What are you trying to pull?? :<")

	def dataReceived(self,data):
		if(data.startswith("1")):
                    self.register_account(data[2:])

		elif(data.startswith("2")):
		    self.get_flag(data[2:])	

		else:
		        self.print_menu()	
        
        def connectionMade(self):
            self.print_menu()
		
class MyServerFactory(protocol.Factory):
    protocol = MyServer

factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
