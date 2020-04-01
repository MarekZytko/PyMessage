import socket
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple python communicator.', usage='%(prog)s [server] [port]')

    parser.add_argument('server', help='IPv4 server adress')
    parser.add_argument('port', help='port to connect to')

    args = parser.parse_args()

    


"""
def main(argv):
    HOST = ''
    PORT = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError as err:
        print(err)
        print('use --help or -h to show help.')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print('Usage: \n\
            \t client.py [server_IPv4] [port]\n\n\
            \t -p  \n\
            \t -p  \n\
            \t -p  \n\
            \t -p  \n')
        sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
"""