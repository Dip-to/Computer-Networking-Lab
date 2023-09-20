import socket
import random
import time

# Define variables for congestion control
cwnd = 1 # congestion window size
ssthresh = 10 # slow start threshold
dup_ack_count = 0 # count of duplicate acknowledgments
last_ack_number = -1 # last acknowledged packet number
last_sequence_number = -1 # last sequence number

# Function to calculate new congestion window size using congestion avoidance algorithm
def congestion_avoidance(curr_cwnd):
    return curr_cwnd + 1

# Function to calculate new congestion window size using slow start algorithm
def slow_start(curr_cwnd):
    return curr_cwnd * 2

# Function to calculate new congestion window size after detecting congestion using fast retransmit algorithm
def fast_retransmit(curr_cwnd):
    return curr_cwnd // 2

def trans_layer_decode(packet):
    seq = packet[:6]
    ack = packet[6:12]
    win = packet[12:16]
    check = packet[16:20]
    return (int(seq.decode('utf-8')), int(ack.decode('utf-8')), int(win.decode('utf-8')), int(check.decode('utf-8')))

def make_packet(seq, ack, window, checksum, payload):
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
server_socket.bind(('localhost', 8881))
server_socket.listen(1)

print('Server is listening for incoming connections')

# Accept a client connection
client_socket, address = server_socket.accept()
client_socket.settimeout(5)

print(f'Accepted connection from {address}')

# Set receive window size (in bytes)
receive_window_size = 1460
rwnd = 5

# Open file to be sent
file = open('file_to_send.txt', 'rb')
timeout = 0.4

# Send packet with transport and network layer headers
sequence_number = random.randint(0, 0)
ack_number = 0
while True:
    curr_sent = 0
    stime = time.time()
    while time.time() - stime < timeout and rwnd > curr_sent:
        payload = file.read(1460)
        payload_size = len(payload)
        ack_number += payload_size
        
        # Check if all file data has been read
        if not payload:
            break
            
        # Calculate checksum
        checksum = 50
        
        # Build packet
        packet = make_packet(sequence_number, ack_number, rwnd, checksum, payload)
         # Send packet
    client_socket.send(packet)
    print(f'Sent packet with sequence number {sequence_number}')
    
    # Update variables
    curr_sent += payload_size
    sequence_number += payload_size
    
    # Wait for acknowledgment
    try:
        ack_packet = client_socket.recv(1024)
        ack_sequence_number, ack_ack_number, ack_rwnd, ack_checksum = trans_layer_decode(ack_packet)
        
        # Check if acknowledgment is duplicate
        if ack_ack_number == last_ack_number:
            dup_ack_count += 1
        else:
            last_ack_number = ack_ack_number
            dup_ack_count = 0
        
        # Check if acknowledgment is out of order
        if ack_ack_number > last_sequence_number:
            # Update congestion window size based on congestion control algorithm
            if cwnd < ssthresh:
                cwnd = slow_start(cwnd)
            else:
                cwnd = congestion_avoidance(cwnd)
            
            # Update variables
            last_sequence_number = ack_ack_number
            rwnd = ack_rwnd
            
        # Check if congestion has been detected
        if dup_ack_count == 3:
            # Perform fast retransmit
            cwnd = fast_retransmit(cwnd)
            ssthresh = cwnd
            dup_ack_count = 0
            
            # Resend missing packet
            payload = file.read(last_ack_number - sequence_number)
            payload_size = len(payload)
            ack_number += payload_size
            checksum = 50
            packet = make_packet(sequence_number, ack_number, rwnd, checksum, payload)
            client_socket.send(packet)
            print(f'Resent packet with sequence number {sequence_number}')
            
            # Update variables
            curr_sent = payload_size
            sequence_number += payload_size
            
    except socket.timeout:
        # Handle timeout
        cwnd = 1
        ssthresh = max(rwnd // 2, 2)
        dup_ack_count = 0
        last_sequence_number = -1
        last_ack_number = -1
        print('Timeout occurred. Resetting congestion control variables')
        continue
        
    # Check if all file data has been sent
    if not payload:
        break
client_socket.close()
server_socket.close()
file.close()

print('File transfer completed')
