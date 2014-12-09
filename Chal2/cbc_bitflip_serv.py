'''
This server is a modified version of the previous one.

CBC mode is used instead of ECB mode. 
You must supply a ciphertext that will contain the string ;admin=true.

Ciphertexts are sent back and forth as ASCII Encoded Hex Strings. 0xFF will be sent as 
"FF" (2 Bytes), not as "\xff" (1 Byte).

You can use python's string.encode('hex') and string.decode('hex') to quickly convert between
raw data and string representation if you need/want to.

Email biernp@rpi.edu with questions/comments :)

-Patrick Biernat
'''

from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
import os
import random

PORT = 9001

KEYSIZE = 16
KEY = "AAA" + "BBB" + "CCC" + '\x01' + "\x80" * 6
IV = "\x00" * KEYSIZE
SECRET = "but_3y3_th0ugh7_CBC_wuz_r1y_g00d?"


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

def xor_block(first,second):
        '''
        Return a string containing a XOR of bytes in first with second
        '''
        if(len(first) != len(second)):
                print "Blocks need to be the same length!"
                return -1

        first = list(first)
        second = list(second)
        for i in range(0,len(first)):
                first[i] = chr(ord(first[i]) ^ ord(second[i]))
        return ''.join(first)

def encrypt_cbc(key,IV, plaintext):
        '''
        High Level Function to encrypt things in AES CBC Mode.
        1: Pad plaintext if necessary. 
        2: Split plaintext into blocks of length <keysize>
        3: XOR Block 1 w/ IV
        4: Encrypt Blocks, XOR-ing them w/ the previous block. 
        '''
        if(len(plaintext) % len(key) != 0):
                plaintext = pad(plaintext,len(key))
        blocks = [plaintext[x:x+len(key)] for x in range(0,len(plaintext),len(key))]
        for i in range(0,len(blocks)):
                if (i == 0):
                        ctxt = xor_block(blocks[i],IV)
                        ctxt = encrypt_block(key,ctxt)
                        #print "First Block Encrypted."
                        #print ctxt.decode('hex')[-16:].encode('hex')
                else:
                        #print len(blocks[i])
                        #print len(ctxt[-32:].decode('hex'))
                        tmp = xor_block(blocks[i],ctxt[-1 * (len(key) * 2):].decode('hex'))     #len(key) * 2 because ctxt is an ASCII string that we convert to "raw" binary.          

                        ctxt = ctxt + encrypt_block(key,tmp)
        return ctxt

def decrypt_cbc(key,IV,ctxt):
        '''High Level function to decrypt thins in AES CBC mode.
        1: Split Ciphertext into blocks of len(Key)
        2: Decrypt block.
        3: For the first block, xor w/ IV. For the others, xor with last ciphertext block.
        '''
        ctxt = ctxt.decode('hex')
        if(len(ctxt) % len(key) != 0):
                print "Invalid Key."
                return -1
        blocks = [ctxt[x:x+len(key)] for x in range(0,len(ctxt),len(key))]
        for i in range(0,len(blocks)):
                #print blocks[0].encode('hex')
                if (i == 0):
                        ptxt = decrypt_block(key,blocks[i])
                        ptxt = xor_block(ptxt.decode('hex'),IV)
                        #print ptxt.encode('hex')
                else:
                        tmp = decrypt_block(key,blocks[i])
                        tmp = xor_block(tmp.decode('hex'),blocks[i-1])
                        ptxt = ptxt + tmp
        return ptxt


def mkprofile(email):
	if((";" in email)):
		return -1
	prefix = "comment1=wowsuch%20CBC;userdata="
	suffix = ";coment2=%20suchsafe%20very%20encryptwowww"
	
	ptxt = prefix + email + suffix
	print ptxt
	return encrypt_cbc(KEY,IV,ptxt)	


def parse_profile(data):
	print "DATA:"
	print data	
	ptxt = decrypt_cbc(KEY,IV,data.encode('hex'))
	ptxt = ptxt.replace("\x04","")
	print ptxt
	if ";admin=true" in ptxt:
		return 1
	return 0


class MyServer(protocol.Protocol):
    def dataReceived(self,data):
	if(len(data) > 512):
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
	
	else:
		self.transport.write("Syntax Error")
		self.transport.loseConnection()


class MyServerFactory(protocol.Factory):
    protocol = MyServer



factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
