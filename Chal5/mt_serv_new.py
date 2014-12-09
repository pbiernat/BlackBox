'''
Can you predict the numbers?

This is a pretty well known weakness of MT19937. Recreate the internal state of the generator 
locally, and see if you can predict a value. 

Numbers are sent back as strings, and are expected to be received as strings. So, if you want to 
send up 1000, make sure to do client.send(str(1000)). 

Email biernp@rpi.edu with questions/comments :)

-Patrick Biernat
'''

from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
from mersenne import mtwister
import time
import os
import random
import struct
PORT = 9004

SECRET = "W4nn4_g0_t0_d4_KaS!n0_l83r?"

class MyServer(protocol.Protocol):
	def __init__(self):
		self.mt = mtwister(random.randint(0,2 **32))

	def dataReceived(self,data):
		if(len(data) > 512):
			self.transport.write("Data too long.\n")
			self.transport.loseConnection()
			return
#Make Profile From "Email"
		if(data.startswith("get:")):
			resp = self.mt.extract_number()
			if (resp == -1):
				self.transport.write("No Cheating!\n")
			else:
				self.transport.write(str(resp))

		elif(data.startswith("predict:")):
			if(self.mt.extract_number() == int(data[8:])):
				self.transport.write("Congratz!")
				self.transport.write(SECRET)
				self.transport.loseConnection()
		else:
			self.transport.write("Syntax Error")
			self.transport.loseConnection()

	def connectionMade(self):
		self.mt = mtwister(random.randint(0,2**32))
	
		
class MyServerFactory(protocol.Factory):
    protocol = MyServer


factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
