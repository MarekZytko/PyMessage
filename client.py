import socket
import atexit
import argparse
import traceback
import string
import secrets
import hashlib
import json


ID = secrets.token_hex(128) #256 chars
SIMPLE_ID = secrets.token_hex(2) #4 chars
SERVER = ''
PORT = ''
HEADERSIZE = 10

class Client(socket.socket):
    HEADER_SIZE = 10

    def __init__(self, server:str, port:int):
        
        # Parameters init:
        self.server = server
        self.port = port

    def start(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 tcp
            print(self.server, self.port)
            print("waiting for connection...")
            self.s.connect((self.server, self.port))
        except:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(traceback.print_exc())

    def sendMsg(self, receipent:str, msg:str):
        if len(msg) >= (10 * self.HEADER_SIZE):
            raise Exception
        msg = f"{len(msg):<{self.HEADER_SIZE}}" + msg
        self.s.sendall(bytes(msg, "utf-8"))

    @staticmethod
    def closeAll(self):
        self.s.close()



parser = argparse.ArgumentParser(description='Simple python communicator.',\
                                usage='%(prog)s [server] [port]')

parser.add_argument('server', help='IPv4 server adress')
parser.add_argument('port', help='server\'s port')

args = parser.parse_args()

SERVER = args.server
PORT = args.port

print('Please provide receipent\'s ID to make connection:')
receipentSimpleID = input('Receipent\'s ID: ')
receipentSimpleID = receipentSimpleID[:4]
receipentSimpleID = str(receipentSimpleID)

for i in range(len(receipentSimpleID)):
    if receipentSimpleID[i] not in string.hexdigits:
        print('incorrect ID')
        exit()

#msg = SIMPLE_ID + ' ' + hashlib.sha3_512(b'').hexdigest()

msg = SIMPLE_ID + '|' + receipentSimpleID

print(f'\n[*] Searching for {receipentSimpleID} ...')


# ==========================================================================
SERVER = '127.0.0.1'
PORT = 55555 # >1024
# ==========================================================================

clientSocket = Client(SERVER, PORT)
clientSocket.start()

while True:
    fullMsg = ''
    new_msg = True
    while True:
        msg = clientSocket.recv(16)
        if new_msg:
            print("new msg len:", msg[:HEADERSIZE], '\n')
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        print(f"full message length: {msglen}\n")

        fullMsg += msg.decode("utf-8")

        print(len(fullMsg))

        if len(fullMsg) - HEADERSIZE == msglen:
            print("full msg recvd")
            print(fullMsg[HEADERSIZE:])
            new_msg = True
            break


