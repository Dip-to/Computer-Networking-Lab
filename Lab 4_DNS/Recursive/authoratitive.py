import os
import socket
import threading
import struct

IP = ''
PORT = 4489
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
dic={
    "www.google.com":('100.20.8.1','A',86400),
    "www.cse.du.ac.bd": ('192.0.2.3','A',86400),
    "www.yahoo.com":('1.2.3.9999',"A",86400)
}

def handle_client(data, addr,server):

    try:
        print(f"[RECEIVED MESSAGE] {data} from {addr}.")
        if dic[data][1]=='A' or dic[data][1]=='AAAA':
            print('sending')
            server.sendto(str(data+' '+dic[data][0]+' '+dic[data][1]+' '+str(dic[data][2])).encode(FORMAT),addr)
    except Exception as e:
        print("ERROR: ",str(e))
            

    

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
   
    print("[STARTING] auth Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)
    print(f"[LISTENING] auth Server is listening on {IP}:{PORT}.")

    while True:
        data, addr = server.recvfrom(SIZE)
        data = data.decode(FORMAT)
        # thread = threading.Thread(target=handle_client, args=(data, addr,server))
        # thread.start()
        handle_client(data,addr,server)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()