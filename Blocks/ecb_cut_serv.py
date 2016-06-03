'''
Blocks
Fairgame, Fall 2015

Patrick Biernat
RPISEC
'''
from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
import os
import base64
import random

PORT = 9001

FLAG = "flag{Sw@pp!n_Bl0x_liek_l3g0z}"
KEY = os.urandom(32) 

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
|+ NSANET - User Configuration Panel       - |
'--------------------------------------------'""" + bcolors.ENDC
DEBUGMODE = bcolors.WARNING + """
| !!!!      DEBUG MODE ACTIVATED        !!!! |
'--------------------------------------------'
""" 

META = """|        *** DATABASE SETTINGS ***           |
'--------------------------------------------'
|ALGORITHM: AES-ECB                          |
|KEY[BITS]: 128                              |
|KEY[STAT]: STATIC                           |
'--------------------------------------------'
""" 

CONT = bcolors.OKBLUE + """
[+] Press Enter To Activate Application...""" + bcolors.ENDC


OPTS = bcolors.WARNING + """
| !!!!       DEBUG OPTIONS MENU         !!!! |
'--------------------------------------------'
|[1] CHANGE CURRENT USER                     |
|[2] MODIFY CURRENT ATTRIBUTES               | 
|[3] VIEW CURRENT ATTRIBUTES                 |
'--------------------------------------------'
""" + bcolors.ENDC

CHOICE = bcolors.OKBLUE + "[+] CHOICE: " + bcolors.ENDC
CHANGE = bcolors.OKGREEN + "[+] USER: " + bcolors.ENDC
UPDATE = bcolors.OKGREEN + "[+] UPDATE ATTRIBUTE STRING: " + bcolors.ENDC
RAWDATA = bcolors.OKGREEN + "[+] ENCRYPTED ATTRIBUTE STRING [+]" + bcolors.ENDC

BEGIN= """|BEGIN:                                      |
"""
END = """|:END                                        |
'--------------------------------------------'
"""

ATTR = bcolors.FAIL + """
.----------------------------------------------.
|+           CURRENT USER ATTRIBUTES           |
'----------------------------------------------'
""" + bcolors.ENDC

ENCATTR = bcolors.OKBLUE + "[+] Raw Attribute Data [+]" + bcolors.ENDC

RAWMSG = "[+] Press Enter For Raw Ciphertext Data"

def chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def encrypt_block(key, plaintext):
        encobj = AES.new(key, AES.MODE_ECB)
        return encobj.encrypt(plaintext).encode('hex')

def decrypt_block(key, ctxt):
        decobj = AES.new(key, AES.MODE_ECB)
        return decobj.decrypt(ctxt).encode('hex')

def encrypt(key, ptxt):
    if (len(ptxt) % 16 != 0):
        ptxt = ptxt + " " * (16 - (len(ptxt) % 16))
    return encrypt_block(key, ptxt)

def decrypt(key, ctxt):
    return decrypt_block(key, ctxt.decode('hex')).decode('hex')

class MyServer(protocol.Protocol):

    def change_user(self):
        self.state = "CHANGE"
        self.transport.write(CHANGE)

    def print_main_menu(self):
        self.transport.write(bcolors.CLEAR)
        self.transport.write(BANNER)
        self.transport.write(OPTS)
        self.transport.write(CHOICE)

    def get_attr(self):
        return decrypt(self.key, self.attr)

    def update_attr(self):
        self.state = "UPDATE"
        self.transport.write(UPDATE)

    def view_attributes(self):
        self.transport.write(bcolors.CLEAR)
        self.transport.write(ATTR)
        self.transport.write(decrypt(self.key, self.attr) + "\n") 
        self.transport.write(RAWDATA + "\n")
        self.transport.write(self.attr) 
   
    def check_admin(self):
        attr = decrypt(self.key,self.attr)
        if "role=admin" in attr:
            self.transport.write(FLAG)
            self.transport.loseConnection()
    
    def dataReceived(self, data):
        # Menu Selection Options
        if (self.state == "MENU"):
            if (data == "\n" or data == "\r\n"):
                self.print_main_menu()
            elif (data == "1\n" or data == "1\r\n"):
                self.change_user()
            elif (data == "2\n" or data == "2\r\n"):
                self.update_attr()
            # View Attributes
            elif (data == "3\n" or data == "3\r\n"):
                self.view_attributes()
       
       # Username Change 
        elif (self.state == "CHANGE"):
            if (data.startswith("admin") or "role" in data):
                self.transport.write(bcolors.FAIL + "[!!] NOT PERMITTED [!!]" + bcolors.ENDC)
            else:
                self.transport.write(bcolors.OKGREEN + "[+] Changed User" + bcolors.ENDC)
                self.user = data.strip()
                self.attr = encrypt(self.key, self.user + ";role=unpriv")
            self.state = "MENU"
        
        # Attribute Update
        elif (self.state == "UPDATE"):
            data = data.strip()
            if (len(data) % 32 != 0):
                self.transport.write("Invalid Attribute Length")
                self.transport.loseConnection()
            else:
                self.attr = data
                self.state = "MENU"
                self.transport.write(bcolors.OKGREEN + "[+] Updated Attributes [+]\n" + bcolors.ENDC) 
                self.check_admin() 
 
    def connectionMade(self):
        self.key = os.urandom(32) 
        self.user = "A. Nobody"
        self.attr = encrypt(self.key, self.user + ";role=unpriv")
        self.state = "MENU" 
        self.transport.write(BANNER)
        self.transport.write(DEBUGMODE)
        self.transport.write(META)
        self.transport.write(CONT)

class MyServerFactory(protocol.Factory):
    protocol = MyServer


factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
