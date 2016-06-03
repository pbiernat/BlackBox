'''
This server is a modified version of the previous one.

CTR mode is used instead of CBC or ECB mode.
You must discover the initial cipher text.

Ciphertexts will be given to the user as ascii encoded hex
strings. 0xFF will be sent as "FF" (2 Bytes), not as "\xff" (1 Byte).

You can use python's string.encode('hex') and string.decode('hex') to quickly convert between
raw data and string representation if you need/want to.

Email freema@rpi.edu with questions/comments (:

- Adam Freeman

'''

from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
import os
import random
import struct

PORT = 9003

KEYSIZE = 16
SECRET = "flag{Ed1t_A11_Teh_Blokz_D0ubl3_N0nce_G1ves_F1ag}"
INITIAL_SECRET = "HURRY Crack The bricks HIT IT WITH A HAMMER" + SECRET + "EAT THE BLOCKS nom nom nom nom nom nom nom nom nom"

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


BANNER = bcolors.OKBLUE + """
.--------------------------------------------.
|+ [ BLACKBOX ]  PUBLIC API DOCS v1.33.7   + |
'--------------------------------------------'""" + bcolors.ENDC

DOCS = """
|                                            |
|                                            |
|view:                 View the secret store |
|edit:<index>,<text>   Edit the store        |
|                                            |
|                                            |
'--------------------------------------------'
"""
def pad(instr, length):
        if(length == None):
                print "Supply a length to pad to"
        elif(len(instr) % length == 0):
                print "No Padding Needed"
                return instr
        else:
                return instr + ' ' * (length - (len(instr) % length ))

def encrypt_block(key, plaintext):
        encobj = AES.new(key, AES.MODE_ECB)
        return encobj.encrypt(plaintext)

def decrypt_block(key, ctxt):
        decobj = AES.new(key, AES.MODE_ECB)
        return decobj.decrypt(ctxt)

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

def encrypt_ctr(key, nonce, plaintext):
        '''
        High Level Function to encrypt things in AES CBC Mode.
        1: Pad plaintext if necessary.
        2: Split plaintext into blocks of length <keysize>
        3: Encrypt nonce + block number
        4: Xor encrypted nonce with cipher text
        '''
        if(len(plaintext) % len(key) != 0):
                plaintext = pad(plaintext,len(key))
        blocks = [plaintext[x:x+len(key)] for x in range(0,len(plaintext),len(key))]
        ctxt = ''
        for i in range(0,len(blocks)):
                keypad = encrypt_block(key, nonce[:-4]+struct.pack("I",i))
                ctxt = ctxt + xor_block(blocks[i], keypad)

        return ctxt

def decrypt_ctr(key, nonce, ctxt):
        '''
        High Level function to decrypt thins in AES CTR mode.
        1: Split Ciphertext into blocks of len(Key)
        2: Encrypt nonce + block number
        3: Xor encrypted nonce with cipher text
        '''
        ctxt = ctxt.decode('hex')
        if(len(ctxt) % len(key) != 0):
                print "Invalid Key."
                return -1
        blocks = [ctxt[x:x+len(key)] for x in range(0,len(ctxt),len(key))]
        for i in range(0,len(blocks)):
                keypad = encrypt_block(key, nonce[:-4]+struct.pack("I",i))
                ctxt = ctxt + xor_block(blocks[i], keypad)

        return ptxt

def edit_ctr(key, nonce, index, newblock, ctxt):
        '''
        High Level function to change a single block of cipher text in
        AES CTR mode.
        1: Encrypt nonce + block number
        2: Xor encrypted nonce with plaintext
        3: Replace old cipher text with new
        '''
        # Bounds checking
        if len(newblock) != KEYSIZE:
                return -2
        if index >= len(ctxt)/KEYSIZE:
                return -1

        pad = encrypt_block(key, nonce[:-4]+struct.pack("I",index))
        ctxt_block = xor_block(pad, newblock)
        ctxt = ctxt[:index*KEYSIZE] + ctxt_block + ctxt[(index+1)*KEYSIZE:]

        return ctxt


class MyServer(protocol.Protocol):
        def parse_profile(self, data):
	        ptxt = decrypt_cbc(self.key,self.iv, data.encode('hex'))
	        ptxt = ptxt.replace(" ","")
	        print ptxt
	        if ";admin=true" in ptxt:
		        return 1
	        return 0

        def print_docs(self):
                self.transport.write(BANNER)
                self.transport.write(DOCS)

        def dataReceived(self,data):
	        if(len(data) > 512):
		        self.transport.write("Data too long.\n")
		        self.transport.loseConnection()
		        return

                # Let the user see the encrypted secret store
                if(data.startswith("view:")):
                        self.transport.write("Encrypted secret store is:\n")
                        self.transport.write(self.store.encode('hex'))

                # Overwrite a single block of the secret store with new text
	        elif(data.startswith("edit:")):
		        self.transport.write("Changing secret store...\n")
                        if len(data.split(',')) != 2:
                                self.transport.write("Invalid Syntax\n")
                                return
		        index = int(data[5:].split(',')[0])
                        newblock = data[5:].split(',')[1]
                        if len(newblock) < KEYSIZE:
                                self.transport.write("given block too small\n")

                        newblock = newblock[:16]

                        ctxt = edit_ctr(self.key, self.nonce, index, newblock, self.store)

                        if ctxt == -2:
                                self.transport.write("given block not the correct size\n")
                        elif ctxt == -1:
                                self.transport.write("given index is too large\n")
                        else:
                                self.transport.write("Done!\n")
                                self.store = ctxt

	        else:
		        self.print_docs()


        def connectionMade(self):
                self.key = os.urandom(16)
                self.nonce = os.urandom(16)
                self.store = encrypt_ctr(self.key, self.nonce, INITIAL_SECRET)
                self.print_docs()

class MyServerFactory(protocol.Factory):
    protocol = MyServer



factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
