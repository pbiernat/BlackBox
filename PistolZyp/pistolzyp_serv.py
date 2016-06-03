#!/usr/bin/python2

"""This server implements a message compression and sending scheme.

Users submit a commandto the server by connecting over tcp to PORT. If
a command requires an argument, it is taken parsed starting one
character after the end of the command. New messages are taken
verbatim, and the session ID is given in its origonal base64 form. The
special base64 characters '+' and '/' may appear in the session ID.

Email freema@rpi.edu with questions/comments

- Adam Freeman

"""

from twisted.internet import reactor, protocol
from Crypto.Cipher import AES
import os
import zlib
import base64

PORT = 9008

SECRET = "flag{d1sr3g4rd_3ncrypt10n_4qu1r3_f14g}"

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
  +-------------------------------+
 /         Pistol Zypper           \\
+-----------------------------------+"""+bcolors.ENDC+"""
|                                   |
| """+bcolors.BOLD+"set <new_message>"+bcolors.ENDC+"""                 |
|    Set body of message to be sent |
|                                   |
| """+bcolors.BOLD+"send"+bcolors.ENDC+"""                              |
|   encrypt and send message.       |
|   This allows you to see          |
|   the encrypted message           |
|                                   |
| """+bcolors.BOLD+"get_flag <session_id>"+bcolors.ENDC+"""             |
|   submit the stolen session id    |
|   (still in base64) for the flag  |
|                                   |
+-----------------------------------+
> """

MESSAGE="""POST / HTTP/1.1
Host: hapless.com
Cookie: sessionid=%s
Content-Length: %d
%s"""

def format_message(sessionID, s):
    iv = os.urandom(16)
    key = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    
    message = MESSAGE % (base64.b64encode(sessionID), len(s), s)
    compressed_message = zlib.compress(message, 9)
    encrypted_message = cipher.encrypt(compressed_message)

    return encrypted_message
    
class MyServer(protocol.Protocol):
    def printMenu(self):
        self.transport.write(BANNER)
        

    def dataReceived(self, data):
        if len(data) > 256:
            self.transport.write("Data too long\n")
            self.transport.loseConnection()
            return

        if data.startswith("set "):
            self.message = data[4:]
            self.transport.write("Message set")
            
        if data.startswith("send"):
            m = format_message(self.sessionID, self.message)
            self.transport.write(m.encode('hex'))
            
        if data.startswith("get_flag"):
            sID = data[9:]
            if sID == base64.b64encode(self.sessionID):
                self.transport.write(SECRET)
                self.transport.loseConnection()
                
        else:
            self.printMenu()

    def connectionMade(self):
        self.message = "beep boop im a robot"
        self.sessionID = os.urandom(16)
        print("Generated session ID %s"% base64.b64encode(self.sessionID))
        self.printMenu()

class MyServerFactory(protocol.Factory):
    protocol = MyServer


factory = MyServerFactory()
reactor.listenTCP(PORT, factory)
reactor.run()
