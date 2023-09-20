import socket
import struct

ADDR = ('127.0.0.1', 4487)
SIZE = 1024
FORMAT = 'utf-8'

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = input("Enter a message to send to the server: ")
    client.sendto(message.encode(FORMAT), ADDR)
    
    msg, addr = client.recvfrom(SIZE)
    print('In bytes: ')
    print(msg)

    header = struct.unpack("6H", msg[:12])
    ms = msg[12:].decode('utf-8')
    print('\n After Decoding')
    print({header},{ms})
    

if __name__ == '__main__':
    main()
