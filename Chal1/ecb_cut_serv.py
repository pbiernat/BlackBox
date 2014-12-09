'''
A server intentionally showcasing a AES-ECB Cut-And-Paste vulnerability.

Ciphertexts are sent back and forth as ASCII Encoded Hex Strings. 0xFF will be sent as 
"FF" (2 Bytes), not as "\xff" (1 Byte).

You can use python's string.encode('hex') and string.decode('hex') to quickly convert between
raw data and string representation if you need/want to.



-Patrick Biernat
'''

from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
import os
import random

PORT = 9000

KEYSIZE = 32
KEY = os.urandom(32)
SECRET = "Y0uR_Alg0ri7Hm_iZ_g00d. Y0ur_impl3m3ntation_iZ_b4d"


def pad(instr, length):
        if(length == None):
                print "Supply a length to pad to"
        elif(len(instr) % length == 0):
                print "No Padding Needed"
                return instr
        else:
                return instr + '\x04' * (length - (len(instr) % length ))

def encrypt_block(key, plaintext):
        encobj = AES.new(key, AES.MODE_ECB)
        return encobj.encrypt(plaintext).encode('hex')

def decrypt_block(key, ctxt):
        decobj = AES.new(key, AES.MODE_ECB)
        return decobj.decrypt(ctxt).encode('hex')

def mkprofile(email):
	if( ("&" in email) or ("=" in email)):
		return -1
	return encrypt_block(KEY,pad("email="+email+"&uid="+str(random.randint(1,100))+"&role=user",KEYSIZE))

def parse_profile(data):
	
	ptxt = decrypt_block(KEY,data).decode('hex')
	ptxt = ptxt.replace("\x04","")
	ptxt = ptxt.split("&")
	if "role=admin" in ptxt:
		return 1
	return 0


class MyServer(protocol.Protocol):
    def dataReceived(self,data):
	if(len(data) > 256):
		self.transport.write("Data too long.\n")
		self.transport.loseConnection()
		return
#Make Profile From "Email"
	if(data.startswith("mkprof:")):
		data = data[7:]
		resp = mkprofile(data)
		if (resp == -1):
			self.transport.write("No Cheating!\n")
		else:
			self.transport.write(resp)

#Decrypt Ciphertext and "parse" into Profile
	elif(data.startswith("parse:")):
		self.transport.write("Parsing Profile...")
		data = data[6:].decode('hex')
		if (len(data) % KEYSIZE != 0):
			self.transport.write("Invalid Ciphertext <length>\n")
			self.transport.loseConnection()
			return
		
		if(parse_profile(data) == 1):
			self.transport.write("Congratulations!\nThe Secret is: ")
			self.transport.write(SECRET)
			self.transport.loseConnection()
		
		else:
			self.transport.write("You are a normal user.\n")
			self.transport.loseConnection()
	
	else:
		self.transport.write("Syntax Error")
		self.transport.loseConnection()


class MyServerFactory(protocol.Factory):
    protocol = MyServer



factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
