import socket
import struct

IP = ''
PORT = 4487
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

def encode_msg(message):
    data = message.split()
    name = data[0]
    type = data[1]
    
    flag = 0
    q = 0
    a = 1
    auth_rr = 0
    add_rr = 0

    ms = (name + ' ' + type).encode('utf-8')
    packed_data = struct.pack(f"6H{len(ms)}s", 50, flag, q, a, auth_rr, add_rr, ms)
    return packed_data
                
def decode_msg(msg):
    header = struct.unpack("6H", msg[:12])
    ms = msg[12:].decode('utf-8')

    print('\n Before Decoding')
    print(msg)
    
    print('\n After Decoding')
    print({header},{ms})
 
    return ms

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = input("Enter an address: ")
    client.sendto(message.encode(FORMAT), ADDR)
    msg,addr=client.recvfrom(SIZE)
    msg1=decode_msg(msg)
    print(msg1)
    data=msg1.split()
    while data[2]=="NS":
        # print(data[1])
        new_adr=('',int(data[1]))
        print('Connecting to port', data[1])
        client.sendto(message.encode(FORMAT),new_adr)
        msg,addr=client.recvfrom(SIZE)
        msg1=decode_msg(msg)
        print(msg1)
        data=msg1.split()
        
    # print(struct.unpack("6H",msg))
    # msg,addr=client.recvfrom(SIZE)
    

if __name__ == "__main__":
    main()