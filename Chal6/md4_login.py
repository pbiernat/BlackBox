'''


Email biernp@rpi.edu with questions/comments :)

-Patrick Biernat
'''

from twisted.internet import reactor, protocol
import md4
import time
import os
import random
import struct
from decimal import Decimal
PORT = 9006

SECRET = "h@sh3z_r_n0t_p3rf3k7!"
KEY = "mykey0"
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

	def dataReceived(self,data):
		if(len(data) > 512):
			self.transport.write("Data too long.\n")
			self.transport.loseConnection()
			return
		
		if(data.startswith("getvalidmac:")):
			self.transport.write(md4mac("User",KEY))			


		elif(data.startswith("login:")):
			if (checklogin(data[6:])):
				self.transport.write("Congratulations!")
				self.transport.write(SECRET)
			else:
				self.transport.write("Invalid Login!")
			
		else:
			self.transport.write("Syntax Error")
			self.transport.loseConnection()

		
class MyServerFactory(protocol.Factory):
    protocol = MyServer

factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
