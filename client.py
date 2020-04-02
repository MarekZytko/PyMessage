import socket
import atexit
import argparse
import traceback
import string
import secrets
import hashlib
import json


@atexit.register
def godbye():
    print("\n\n")
    print("cleaning...")

ID = secrets.token_hex(128) #256 chars
SIMPLE_ID = secrets.token_hex(2) #4 chars
SERVER = ''
PORT = ''
HEADERSIZE = 10

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Simple python communicator.',\
                                        usage='%(prog)s [server] [port]')

        parser.add_argument('server', help='IPv4 server adress')
        parser.add_argument('port', help='server\'s port')

        args = parser.parse_args()
        
        SERVER = args.server
        PORT = args.port

        print(SERVER, PORT)
    except Exception:
        print('+++++++++++++++++++++++++++++++++')
        print(traceback.print_exc())


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
    PORT = 2137 # >1024
    # ==========================================================================

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER, PORT))

    while True:
        full_msg = ''
        new_msg = True
        while True:
            msg = s.recv(16)
            if new_msg:
                print("new msg len:", msg[:HEADERSIZE], '\n')
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            print(f"full message length: {msglen}\n")

            full_msg += msg.decode("utf-8")

            print(len(full_msg))

            if len(full_msg) - HEADERSIZE == msglen:
                print("full msg recvd")
                print(full_msg[HEADERSIZE:])
                new_msg = True
                break


