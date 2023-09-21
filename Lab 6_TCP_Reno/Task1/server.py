import socket
import random
import time
import os

cwnd = 1 
ssthresh = 8 
dup_ack_count = 0 
last_ack_number = -1 
last_sequence_number = -1 
tim_out=5
est_rtt = 0.5
sample_rtt = 0.5
alpha = 0.125
beta = 0.25
dev_rtt = 0.5



def congestion_avoidance(curr_cwnd):
    return curr_cwnd + 1

def slow_start(curr_cwnd):
    return curr_cwnd * 2

def fast_retransmit(curr_cwnd):
    return curr_cwnd // 2


def trans_layer_decode(packet):
    seq=packet[:6]
    ack=packet[6:12]
    win=packet[12:16]
    check=packet[16:20]
    return (int(seq.decode('utf-8')),int(ack.decode('utf-8')),int(win.decode('utf-8')),int(check.decode('utf-8')))

def make_packet(seq,ack,window,checksum,payload):
    seq = int(seq)
    ack = int(ack)
    window = int(window)
    checksum = int(checksum)
    transport_header = f'{seq:06d}{ack:06d}{window:04d}{checksum:04d}'.encode('utf-8')[:20].ljust(20)
    
    # Build network layer header
    network_header = b'\x45\x00\x05\xdc'  # IP version 4, header length 20 bytes, total length 1500 bytes
    network_header += b'\x00\x00\x00\x00'  # Identification
    network_header += b'\x40\x06\x00\x00'  # TTL=64, protocol=TCP, checksum=0 (will be filled in by kernel)
    network_header += b'\x0a\x00\x00\x02'  # Source IP address
    network_header += b'\x0a\x00\x00\x01'  # Destination IP address
    
    # Build packet by concatenating headers and payload
    packet = network_header + transport_header + payload
    return packet

# Set up server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8882))
server_socket.listen(1)

print('Server is listening for incoming connections')

# Accept a client connection
client_socket, address = server_socket.accept()
client_socket.settimeout(5)

print(f'Accepted connection from {address}')

# Set receive window size (in bytes)
receive_window_size = 1460
rwnd=5
mss=1460
# Open file to be sent
file = open('file_to_send.txt', 'rb')
timeout=0.4
# Send packet with transport and network layer headers
sequence_number = random.randint(0,0)
ack_number=0
starting_time=time.time()
file_size= os.path.getsize('file_to_send.txt')
last_time=time.time()
while True:
    
    curr_sent=0
    stime=time.time()
    # while time.time()-stime<timeout and rwnd>curr_sent:
    max_cap=min(cwnd,rwnd)
    print(f'max_cap {cwnd} {rwnd}')
    while max_cap>curr_sent:
        curr_sent+=1
        payload = file.read(1460)
        payload_size=len(payload)
        ack_number+=payload_size
        if payload_size==0:
            break
        # Check if all file data has been read
        
        checksum=50
        
        packet=make_packet(ack_number,ack_number,max_cap,checksum,payload)
        sequence_number+=len(payload)
        client_socket.send(packet)
       # print(f'Sent packet {ack_number} currsent {curr_sent}\n')
        last_time=time.time()
    print(f'window currsent {curr_sent}\n')

    try:
        acknowledgment = client_socket.recv(1500)
    except socket.timeout:
        print('No acknowledgment received within 5 seconds')
        break
    if acknowledgment:
        # Parse acknowledgment

        network_header = acknowledgment[:20]
        transport_header = acknowledgment[20:40]

        
        client_seq,acknowledgment_sequence_number,rwnd,checksum=trans_layer_decode(transport_header)
        print(client_seq,acknowledgment_sequence_number,rwnd,checksum)
        
        if last_ack_number==client_seq:
            dup_ack_count+=1
        else:
            dup_ack_count=0
        if client_seq == ack_number:
            print(f'Received acknowledgment for packet {client_seq}')
            sequence_number += payload_size
            if cwnd<ssthresh:
                cwnd=slow_start(cwnd)
            else:
                cwnd=congestion_avoidance(cwnd)

            if dup_ack_count==3:
                dup_ack_count=0
                ssthresh=fast_retransmit(cwnd)
                cwnd=cwnd/2
                cwnd+=3
            
            if (time.time()-last_time>tim_out):
                print('tout')
                sthresh=fast_retransmit(cwnd)
                cwnd=1
                last_time=time.time()
            if(rwnd<2*cwnd):
                cwnd=1
            print(f'cwnd ={cwnd}')
            
        else:
            print(f'Received acknowledgment for packet {client_seq}, but expected {ack_number}')
    else:
        print('Did not receive acknowledgment')
    if not payload:
        break
    
    

# Close file
file.close()
print(f'Throughput: {(file_size/ (time.time()-starting_time))/1000.0} B/s')
    
# Close sockets
client_socket.close()
server_socket.close()
print('Done')