'''
This server is a modified version of the previous one.

This server will send you some data encrypted in CBC mode.
You can request decryptions of ciphertexts. The server will tell you if your ciphertext
decrypts to something with valid padding, but you won't get the plaintext back.

This is one of those obscure crypto implementation details that you can use to completely 
defeat the cryptosystem.


The Secret is in the decrypted ciphertext. 

Good luck!

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

PORT = 9004

KEYSIZE = 16
KEY = "AAA" + "BBB" + "CCC" + '\x01' + "\x80" * 6
IV = os.urandom(16)
SECRET = "A" * 16 + "d4t_!nf0_l34k_y0"


def pad(instr, length):
        '''
	Generate valid PKCS#7 Padding
	'''
	if(length == None):
                print "Supply a length to pad to"
        elif(len(instr) < length):
                return instr + chr((length - len(instr))) * (length - len(instr))
        elif(len(instr) % length == 0):
                #Add a block-length worth of padding. 
                return instr + (chr(length) * length)
        else:
                return instr + chr((length - (len(instr) % length ))) * (length - (len(instr) % length ))


def valid_padding(instr):
        '''
        Determine if valid PKCS#7 Padding is present in instr.
        '''
        #Grab the last byte of instr.
        length = instr[-1]
#       print length.encode('hex')
        test = instr[-1 * int(length.encode('hex'),16):]
        test = test.replace(length,"")
        if (test != ""):
                return False
        return True

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
                        ctxt = xor_block(blocks[i],"\x00"* 16)
                        ctxt = encrypt_block(key,ctxt)
                else:
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
                if (i == 0):
                        ptxt = decrypt_block(key,blocks[i])
                        ptxt = xor_block(ptxt.decode('hex'),IV)
                else:
                        tmp = decrypt_block(key,blocks[i])
                        tmp = xor_block(tmp.decode('hex'),blocks[i-1])
                        ptxt = ptxt + tmp
        return ptxt


def padding_check(data):
	print "DATA:"
	print data	
	print decrypt_cbc(KEY,IV,data)
	return valid_padding(decrypt_cbc(KEY,IV,data))

def get_your_ctxt():
	'''
	This will return the Secret String that you need to decrypt.
	'''
	return encrypt_cbc(KEY,IV,pad(SECRET,len(KEY)))

class MyServer(protocol.Protocol):
    def dataReceived(self,data):
	if(len(data) > 512):
		self.transport.write("Data too long.\n")
		self.transport.loseConnection()
		return
#Make Profile From "Email"
	if(data.startswith("get:")):
		resp = get_your_ctxt()
		if (resp == -1):
			self.transport.write("No Cheating!\n")
		else:
			self.transport.write(resp)

#Decrypt Ciphertext and "parse" into Profile
	elif(data.startswith("parse:")):
		print "PARSING"
		data = data[6:]
		if (len(data) % KEYSIZE != 0):
			print "BAD CIPHERTEXT"
			self.transport.write("Invalid Ciphertext <length>\n")
			self.transport.loseConnection()
			return
		
		if(padding_check(data) == True):
			self.transport.write("VALID PADDING")
		
		else:
			self.transport.write("INVALID PADDING")
	
	else:
		self.transport.write("Syntax Error")
		self.transport.loseConnection()


class MyServerFactory(protocol.Factory):
    protocol = MyServer



factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
