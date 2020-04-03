import socket
import time
import traceback
import abc
import atexit
import sqlite3


#TODO
'''
- Check for headersize
- Create adress table (ID)


for now:
    - two clients at the time (receipent and receiver)
    - no crypto (for now)


sock = ssl.wrap_socket(sock)


'''





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
            print("waiting for connection...")
            self.s.listen(2)

            self.conn, self.addr = self.s.accept()

            # BRAK OBSŁUGI POŁĄCZENIA
            # po wyjściu z tej funkcji zostanie prawdopodobnie zerwane, naprawić

            with self.conn:
                print('Connection from: ', self.addr)
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


SERVER = '127.0.0.1'
PORT = 55555 # >1024

if __name__ == "__main__":
    @atexit.register
    def godbye():
        print("\n\n")
        print("cleaning...")
        Server.closeAll(s)
        database.close()
        

    #Creating database in memory
    database = sqlite3.connect(':memory:')

    c = database.cursor()
    # Create table
    c.execute('''CREATE TABLE adresses
                (userId text, ipAdress text, port text)''')

    # Save (commit) the changes
    database.commit()
    
    #Starting server
    s = Server(SERVER, PORT)
    s.start()
    
    data = ('test1', s.addr[0], s.addr[1])

    c.execute(f"INSERT INTO adresses VALUES {data}")
    database.commit()

    c.execute('SELECT * FROM adresses')
    print(c.fetchone())