import socket
import time
import traceback
import abc
import atexit
import sqlite3
import json
import os

class Server(socket.socket):
    HEADER_SIZE = 10

    def __init__(self, server:str, port:int):
        # Parameters init:
        self.server = server
        self.port = port

    def start(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ipv4 tcp
            print(self.server, self.port)

            self.s.bind((self.server, self.port))
            print("[*] waiting for connection...")
            self.s.listen(2)
            self.conn, self.addr = self.s.accept()

            print('Connection from: ', self.addr)
        except:
            print("++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(traceback.print_exc())

    def sendMsg(self, msg:str):
        if len(msg) >= (10 * self.HEADER_SIZE):
            print('message is to big!')
            return
        msg = f"{len(msg):<{self.HEADER_SIZE}}" + msg
        self.conn.send(bytes(msg, "utf-8"))

    def recvMsg(self):
        while True:
            fullMsg = ''
            newMsg = True
            while True:
                msg = self.conn.recv(self.HEADER_SIZE * 2) #ALLWAYS HAS TO BE GRATER THAN HEADER
                if newMsg:
                    #print("new msg len:",msg[:self.HEADER_SIZE])
                    msgLen = int(msg[:self.HEADER_SIZE])
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
        self.s.close()


SERVER = '127.0.0.1'
PORT = 55555 # >1024

if __name__ == "__main__":

    #Creating database in memory
    database = sqlite3.connect(':memory:')

    c = database.cursor()
    # Create table
    c.execute('''CREATE TABLE adresses
                (userId text, ipAdress text, port text)''')

    # Save (commit) the changes
    database.commit()
    
    #Starting server
    server = Server(SERVER, PORT)
    server.start()

    #Information exchange:
    testMessage = server.recvMsg()
    testMessage = json.loads(testMessage)
    
    data = (testMessage['userID'], server.addr[0], server.addr[1])

    c.execute(f"INSERT INTO adresses VALUES {data}")
    database.commit()

    c.execute('SELECT * FROM adresses')
    print(c.fetchone())

    #clear = lambda: os.system('cls') #on Windows System
    #clear()

    @atexit.register
    def godbye():
        print("\n\n")
        print("cleaning...")
        Server.closeAll(server)
        database.close()