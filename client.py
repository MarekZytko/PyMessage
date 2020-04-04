import socket
import atexit
import argparse
import traceback
import string
import secrets
import hashlib
import json
import os
import time
import sys

ID = secrets.token_hex(128) #256 chars
USER_ID = secrets.token_hex(5) #10 chars
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
        print(self.server, self.port)
        n = 1
        sleepTime = 3
        while True:
            try:
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 tcp
                if n == 1:
                    print("[*] Connecting...")
                self.s.connect((self.server, self.port))
                print(f"[*] Connected to the server ({self.server}:{self.port})")
                return
            except:
                for i in range(sleepTime,0,-1):
                    sys.stdout.write("\r")
                    sys.stdout.write("[*] Reconnecting in [{:1d}]...".format(i))
                    sys.stdout.flush()
                    time.sleep(1)
                n += 1
                
                if n == 5:
                    sleepTime = 10
                if n == 10:
                    print("Unable to connect to the server")
                    exit()
                #print("++++++++++++++++++++++++++++++++++++++++++++++++++")
                #print(traceback.print_exc())
                #exit()

    def sendMsg(self, msg:str):
        if len(msg) >= (10 * self.HEADER_SIZE):
            print('message is to big!')
            return
        msg = f"{len(msg):<{self.HEADER_SIZE}}" + msg
        self.s.send(bytes(msg, "utf-8"))

    @staticmethod
    def closeAll(self):
        self.s.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simple python communicator.',\
                                    usage='%(prog)s [server] [port]')

    parser.add_argument('server', help='IPv4 server adress')
    parser.add_argument('port', help='server\'s port')

    args = parser.parse_args()

    SERVER = args.server
    PORT = int(args.port)

    print("-----------------------------")
    print(f"|     Your ID: {USER_ID}   |")
    print("-----------------------------")

    clientSocket = Client(SERVER, PORT)
    clientSocket.start()

    print('Please provide receipent\'s ID to make connection:')
    receipentUserID = input('Receipent\'s ID: ')
    if len(receipentUserID) != len(USER_ID):
        print("incorrect UserID length")
        exit()
    receipentUserID = str(receipentUserID)

    for i in range(len(receipentUserID)):
        if receipentUserID[i] not in string.hexdigits:
            print('incorrect ID')
            exit()

    msg = {
        "userID": USER_ID,
        "receipentID": receipentUserID
    }

    msg = json.dumps(msg)
    print(msg)

    print(f'\n[*] Searching for {receipentUserID} ...')

    clientSocket.sendMsg(msg)

    #clear = lambda: os.system('cls') #on Windows System
    #clear()
