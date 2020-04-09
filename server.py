import socket
import time
import traceback
import abc
import atexit
import sqlite3
import json
import os
import _thread
import threading 
import math
import logging

CONNECTIONS = {}
CHATS = {}

lock = threading.Lock()

class ServerDatabase(object):
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

    def getRecord(self, data, reqeust:str):
        with lock:
            self.c.execute(reqeust, data)
            result = self.c.fetchone()
            print('======',result,'=======')

        return result

    def dump(self):
        self.c.execute("SELECT * FROM adresses")
        print(self.c.fetchall())


class Server():
    HEADER_SIZE = 10
    HELLOMSG_TIMEOUT = 10
    COMMUNICATION_TIMEOUT = 60*30   #0,5 hour

    def __init__(self, server:str, port:int):
        # Parameters init:
        self.server = server
        self.port = port
        self.database = ServerDatabase("CREATE TABLE adresses (userID text, receipentID text)")
        return

    def onNewClient(self, conn):
        print(f'new connection!')
        testMessage = self.recvMsg(conn)
        testMessage = json.loads(testMessage)

        userID = testMessage['userID']
        receipentID = testMessage['receipentID']

        client = Client(userID, conn)
        CONNECTIONS[userID] = client

        data = (userID, receipentID)
        self.database.insert(data, f"INSERT INTO adresses VALUES (?,?)")

        #If this request...

        #Searching receipent in database:
        while True:
            receipent = self.database.getRecord((receipentID,), 'SELECT receipentID FROM adresses WHERE userID=?')

            #returns client's userID, it means, that receipent want to connect to exactly him   
            if receipent != None:
                if receipent[0] == userID:
                    receipent = receipent[0]
                    #If receipent is still connected to server:
                    if receipent in CONNECTIONS.keys() and userID in CONNECTIONS.keys():
                        #Making chat:
                        #if it does not exist:
                        if f'{userID}:{receipentID}' in CHATS.keys() or f'{receipentID}:{userID}' in CHATS.keys():
                            print("CZAT ISTNIEJE")
                        else:
                            CHATS[f'{userID}:{receipentID}'] = Chat(CONNECTIONS[userID], CONNECTIONS[receipentID])
                        break
            else:
                print("receipent does not exist in database")
            while True:
                time.sleep(1000)

        #print("thread closed")
        #_thread.exit()


    def start(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 tcp
            self.s.bind((self.server, self.port))
            print("[*] waiting for connections...")
            self.s.listen(5) 

            while True:
                conn, _ = self.s.accept()     # Establish connection with client.
                _thread.start_new_thread(self.onNewClient,(conn,))
        except:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(traceback.print_exc())


    def sendMsg(self, msg:str, conn):
        if len(msg) >= math.pow(10, self.HEADER_SIZE):
            print('\nmessage is to big!')
            return
        msg = f"{len(msg):<{self.HEADER_SIZE}}" + msg
        conn.sendall(bytes(msg, "utf-8"))
        return


    def recvMsg(self, conn):
        while True:
            fullMsg = ''
            newMsg = True
            while True:
                msg = conn.recv(self.HEADER_SIZE * 2) #ALLWAYS HAS TO BE GRATER THAN HEADER
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

    
    @staticmethod
    def dump(self):
        return self.database.dump()


class Client(socket.socket):
    HEADER_SIZE = 10

    def __init__(self, userID:str, conn:socket.socket):
        self.conn = conn
        self.userID = userID
        self.free = True
        return

    def sendMsg(self, msg:str):
            if len(msg) >= math.pow(10, self.HEADER_SIZE):
                print('\nmessage is to big!')
                return
            msg = f"{len(msg):<{self.HEADER_SIZE}}" + msg
            self.conn.sendall(bytes(msg, "utf-8"))
            return


    def recvMsg(self):
        while True:
            fullMsg = ''
            newMsg = True
            msg = self.conn.recv(self.HEADER_SIZE * 2) #ALLWAYS HAS TO BE GRATER THAN HEADER
            while len(msg):
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
            print(fullMsg)
            return fullMsg


class Chat():
    def __init__(self, sender, receipent):
        self.client1 = sender
        self.client2 = receipent

        self.messages = ServerDatabase("CREATE TABLE messages (userID text, msg text)")
        print('chat created on new thread!')

        welcomeMsg = {"server": "chatCreated"}
        welcomeMsg = json.dumps(welcomeMsg)
        print(welcomeMsg)
        self.client1.sendMsg(welcomeMsg)
        self.client2.sendMsg(welcomeMsg)

        _thread.start_new_thread(self.messagesTable, (self.client1,))
        _thread.start_new_thread(self.messagesTable, (self.client2,))

        _thread.start_new_thread(self.startChat, (self.client1, self.client2))
        _thread.start_new_thread(self.startChat, (self.client2, self.client1))


    def startChat(self, client1, client2):
        while True:
            messages = self.messages.getRecord((client1.userID,), "SELECT msg FROM messages where userID=?")
            print("gotRecord, ", messages)
            if messages != None and messages[0]['userID'] == client1.userID:
                while True:
                    print("checking if client free")
                    if client2.free:
                        print("client is free!")
                        client2.sendMsg(messages[0]['msg'])
                        print("sending message: ", messages[0])
                    time.sleep(1)
                    break
            time.sleep(1)

    
    def messagesTable(self, client):
        print("messagesTable")
        while True:
            print("CHUJ 8============================================>")
            client.free = False
            msg = client.recvMsg()
            print("MESSAGE ARRIVED FROM: ", client.userID)
            msg = json.loads(msg)
            client.free = True
            msg = (msg['userID'], msg['msg'])
            self.messages.insert(msg, f"INSERT INTO messages VALUES (?,?)")
            time.sleep(1)

    def clearChat(self):
        clear = lambda: os.system('cls') #on Windows System
        clear()

    def chatRcvMsg(self):
        pass

    def chatSendMsg(self):
        pass



SERVER = '127.0.0.1'
PORT = 55555 #>1024

if __name__ == "__main__":
    #Starting server
    server = Server(SERVER, PORT)
    server.start()

    #Information exchange:

    @atexit.register
    def godbye():
        print("\n\n")
        print("cleaning...")
        Server.closeAll(server)
        Server.dump(server)
        print(CONNECTIONS)
        #clear = lambda: os.system('cls') #on Windows System
        #clear()
