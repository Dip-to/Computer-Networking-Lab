import socket
import random
import time
import os

cwnd = 1 
ssthresh = 10 
dup_ack_count = 0 
last_ack_number = -1 
last_sequence_number = -1 
tim_out=0.5
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
    
    packet = network_header + transport_header + payload
    return packet

# Set up server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8882))
server_socket.listen(1)

print('Server is listening for incoming connections')

client_socket, address = server_socket.accept()
client_socket.settimeout(1)

print(f'Accepted connection from {address}')

receive_window_size = 1460
rwnd=5

file = open('file_to_send.txt', 'rb')
fsize=os.stat('file_to_send.txt')
file_size=fsize.st_size
timeout=0.4
sequence_number = random.randint(0,0)
ack_number=0
last_time=time.time()
starting_time=time.time()
max_cap=5
while True:
    curr_sent=0
    stime=time.time()
    max_cap=min(rwnd,rwnd)

    while time.time()-stime<timeout and max_cap>curr_sent:
        print(f'{curr_sent} + currs')
        payload = file.read(1460)
        payload_size=len(payload)
        ack_number+=payload_size
        # Check if all file data has been read
        if not payload:
            break
        checksum=50
        packet=make_packet(sequence_number,ack_number,rwnd,checksum,payload)
        sequence_number+=len(payload)

        print(sequence_number,ack_number,rwnd,checksum)
        print()
        client_socket.send(packet)
        curr_sent+=1
        print(f'Sent packet {sequence_number} currsent {curr_sent}')
        last_time=time.time()
    

    sample_rtt=time.time()-last_time
    est_rtt = alpha * sample_rtt + (1 - alpha) * est_rtt
    dev_rtt = beta * abs(sample_rtt - est_rtt) + (1 - beta) * dev_rtt
    tim_out = est_rtt + 4 * dev_rtt




    # Wait for acknowledgment from client
    try:
        acknowledgment = client_socket.recv(1024)
    except socket.timeout:
        print('No acknowledgment received within 5 seconds')
        break
    if acknowledgment:
        # Parse acknowledgment

        network_header = acknowledgment[:20]
        transport_header = acknowledgment[20:40]
        # print(acknowledgment_header)
        # acknowledgment_sequence_number = int(acknowledgment_header.split(b'=')[1])
        
        seq,acknowledgment_sequence_number,rwnd,checksum=trans_layer_decode(transport_header)
        print(seq,acknowledgment_sequence_number,rwnd,checksum)
        if last_ack_number==acknowledgment_sequence_number:
            dup_ack_count+=1
        else:
            dup_ack_count=0
        if acknowledgment_sequence_number == sequence_number+payload_size:
            print(f'Received acknowledgment for packet {sequence_number}')
            sequence_number += payload_size
            if cwnd<ssthresh:
                cwnd=congestion_avoidance(cwnd)
            else:
                cwnd=slow_start(cwnd)
            if dup_ack_count==3:
                dup_ack_count=0
                ssthresh=fast_retransmit(cwnd)
                cwnd=1
            
            if (time.time()-last_time>tim_out):
                sthresh=fast_retransmit(cwnd)
                cwnd=1
                last_time=time.time()

                print(f'cwnd ={cwnd}')

        else:
            print(f'Received acknowledgment for packet {acknowledgment_sequence_number}')
    else:
        print('Did not receive acknowledgment')

# Close file
file.close()
    
# Close sockets
client_socket.close()
server_socket.close()
print('Done')
print(f'upload: {(file_size/ (time.time()-starting_time))/1000.0} B/s')