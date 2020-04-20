import argparse
import atexit
import hashlib
import json
import math
import os
import secrets
import socket
import string
import sys
import time
import traceback
import threading
import _thread
import sqlite3
import colorama

from keyExchange import DiffieHellman


ID = secrets.token_hex(128) #256 chars
USER_ID = secrets.token_hex(5) #10 chars

lock = threading.Lock()


class Client(socket.socket):
    HEADER_SIZE = 10

    def __init__(self, server:str, port:int):
        
        # Parameters init:
        self.server = server
        self.port = port

        self.free = True

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
                for i in range(sleepTime,-1,-1):
                    sys.stdout.write("\r")
                    if i != 0:
                        sys.stdout.write("[{}] Reconnecting in {:1d}...".format(n, i))
                    else:
                        sys.stdout.write("                             ")
                        sys.stdout.write("\r[{}] Reconnecting...".format(n))
                    sys.stdout.flush()
                    time.sleep(1)
                
                print('')
                if n == 5:
                    sleepTime = 10
                if n == 10:
                    print("Unable to connect to the server :(")
                    exit()
                n += 1

    def sendMsg(self, msg:str):
        if len(msg) >= math.pow(10, self.HEADER_SIZE):
            print('message is to big!')
            return
        msg = f"{len(msg):<{self.HEADER_SIZE}}" + msg
        self.s.sendall(bytes(msg, "utf-8"))
        return


    def recvMsg(self):
        while True:
            fullMsg = ''
            newMsg = True
            while True:
                msg = self.s.recv(self.HEADER_SIZE * 2) #ALLWAYS HAS TO BE GRATER THAN HEADER
                if newMsg:
                    msgLen = int(msg[:self.HEADER_SIZE])
                    #print(f"Message arrived! [len: {msgLen}]")
                    newMsg = False

                fullMsg += msg.decode("utf-8")
                #print(f"full message length: {len(fullMsg)}")

                if len(fullMsg) - self.HEADER_SIZE == msgLen:
                    #print(fullMsg[self.HEADER_SIZE:])
                    newMsg = False
                    break
            #Removing header
            fullMsg = fullMsg[self.HEADER_SIZE:]
            return fullMsg

    @staticmethod
    def closeAll(self):
        self.s.shutdown(2) #"SHUT_RDWR"
        self.s.close()

class Database(object):
    def __init__(self, createReq:str):
        self.database = sqlite3.connect(':memory:', check_same_thread=False)
        self.c = self.database.cursor()
        # Create table and columns:
        self.c.execute(createReq)

        # Save (commit) the changes
        self.database.commit()
        return

    def insert(self, data, request:str):
        with lock:
            self.c.execute(request, data)
            self.database.commit()
    
    def delete(self, data, request:str):
        with lock:
            self.c.execute(request, data)
            self.database.commit()

    def getRecord(self, data, reqeust:str):
        with lock:
            self.c.execute(reqeust, data)
            result = self.c.fetchone()
        return result

    def dump(self):
        self.c.execute("SELECT * FROM messages")
        print(self.c.fetchall())

class Chat():
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket

        self.messages = Database("CREATE TABLE messages (userID text, msg text)")
        print("database created")

        _thread.start_new_thread(self.receiveMessages, (self.clientSocket,))
        _thread.start_new_thread(self.startChat, (self.clientSocket,))


    def addMessageToSend(self, msg):
        self.messages.insert((USER_ID, msg), f"INSERT INTO messages VALUES (?,?)")


    def startChat(self, client):
        while True:
            msg = self.messages.getRecord((USER_ID,), "SELECT msg FROM messages where userID=?")
            if msg != None:
                msg = msg[0]
                while True:
                    #Generating new pair of keys each time
                    self.df = DiffieHellman()

                    #TODO
                    #How to serialize DiffieHellman object not using Pickle?

                    #publicKey = self.df.public_key.public_bytes
                    #print(publicKey)




                    client.sendMsg(msg)
                    self.messages.delete((msg,), "DELETE FROM messages where msg=?")
                    time.sleep(1)
                    break
            time.sleep(1)

    
    def receiveMessages(self, client):
        while True:
            msg = client.recvMsg()
            msg = json.loads(msg)
            
            #TODO
            #Add exception if first sent message is not key exchange protocol
            #msg['key']
            print(colorama.Fore.GREEN + msg['msg'] + colorama.Fore.RESET)
            time.sleep(1)

    def clearChat(self):
        clear = lambda: os.system('cls') #on Windows System
        clear()


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
    #print(msg)

    clientSocket.sendMsg(msg)
    print("\n[*] Request sent")
    print(f'[*] Waiting for receipent to connect to the server ...')


    msg = clientSocket.recvMsg()
    msg = json.loads(msg)
    print(msg)

    if msg['server'] == 'chatCreated':
        chat = Chat(clientSocket)
        chat.clearChat()
        print("[*] Chat created !\n")

    while True:
        msg = input("")
        msg = str(msg)
        msg = {"userID": USER_ID, "msg": msg}
        msg = json.dumps(msg)
        chat.addMessageToSend(msg)

    #clear = lambda: os.system('cls') #on Windows System
    #clear()
    #======================================================================

