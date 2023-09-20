import os
import socket
import threading
import struct

IP = ''
PORT = 4487
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"
dic={}

def handle_client(data, addr, server):
    print(f"[RECEIVED MESSAGE] {data} from {addr}.")
    data = data.split()
    print(data[0])
    print(data[1])

    file1 = open('dns_records.txt', 'r')
    for line in file1:
        line = line.split()
        name = line[0]
        value = line[1]
        type = line[2]
        ttl = line[3]
        if name == data[0] and type == data[1]:
            print('hi')
            flag = 0
            q = 0
            a = 1
            auth_rr = 0
            add_rr = 0
            
            # Pack DNS header fields and message into the same buffer
            ms = (name + ' ' + value + ' ' + type + ' ' + ttl).encode('utf-8')
            packed_data = struct.pack(f"6H{len(ms)}s", 50, flag, q, a, auth_rr, add_rr, ms)
            
            server.sendto(packed_data, addr)
            break

def main():
   
    print("[STARTING] Server is starting")
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)
    print(f"[LISTENING] Server is listening on {IP}:{PORT}.")

    while True:
        data, addr = server.recvfrom(SIZE)
        data = data.decode(FORMAT)
        thread = threading.Thread(target=handle_client, args=(data, addr,server))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()