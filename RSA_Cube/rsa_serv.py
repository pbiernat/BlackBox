'''This server implements a RSA signatre checking scheme.

Users submit a command to a server. If an action requires privildeged
access, then the user must submit a signature proving that they are
the admin. The algorithm is modified version of the RSA signature
algorithm, and the signature should be submitted as a string of hex.

Users can either push the button, which increments a counter (does
nothing) or attempt to get the flag, which requires authentication.

Email freema@rpi.edu with questions/comments

- Adam Freeman

'''

from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
import random

PORT = 9007

SECRET = "flag{f1nd_th4t_cub3_r00t}"

SAFEPRIME = 156889488273028743973050898439146834066306803266194526990335127425357098805016602379889715733931500413745989225679309665133656355406361171050469938154960096172905128087101102290516244866061873567569226845874460892029543150008926384103922539976142167037167434270556062239833399615952408699661016765061638806267L
# generated with gensafeprime.generate(1024)
# https://pypi.python.org/pypi/gensafeprime

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
 /----------------------------------/
/  [ BLACKBOX ] RSA Cube v.3.14    /"""+bcolors.ENDC+'|'+bcolors.OKBLUE+"""
+----------------------------------+""" + bcolors.ENDC + "|"

BODY = """
|                                  ||
|  push: push the button           ||
|  get_flag: get the flag.         ||
|         requires authentication  ||
|                                  ||
|  Button has been pushed          ||
|      %4d times                  ||
|                                  |/
+----------------------------------+
> """
def rsa_verify(data, signature, prime):
    '''
    Returns a boolian showing if the passed signature is valid
    '''
    decsig = pow(signature, 3)

    print(hex(signature))

    decstrh = hex(decsig)[2:]
    if decstrh[-1] == 'L':
        decstrh = decstrh[:-1]

    decstr = ('0'*(2048-len(decstrh))+decstrh).decode('hex')
    print(decstr.encode('hex'))
    # check the beginning and end to make sure the signature is valid
    return decstr.startswith("\x00\x01\xff") and ("\xff\xff\x00ASN.1"+data in decstr)

class MyServer(protocol.Protocol):
    def printMenu(self):
        self.transport.write(BANNER)
        self.transport.write(BODY%self.buttonPresses)

    def dataReceived(self, data):
        if(len(data) > 20148):
            self.transport.write("Data too long\n")
            self.transport.loseConnection()
            return

        if data.startswith("push"):
            self.buttonPresses += 1
            self.printMenu()

        elif data.startswith("get_flag"):
            try:
                signature = int(data[9:], 16)
            except ValueError:
                self.transport.write("Could not decode signature\n")
                return

            if rsa_verify("get_flag", signature, SAFEPRIME):
                self.transport.write(SECRET)
		self.transport.loseConnection()

            else:
                self.transport.write("Signature was invalid\n")

        else:
            self.transport.write(bcolors.CLEAR)
            self.printMenu()


    def connectionMade(self):
        self.buttonPresses = 0
        self.printMenu()

class MyServerFactory(protocol.Factory):
    protocol = MyServer

factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
