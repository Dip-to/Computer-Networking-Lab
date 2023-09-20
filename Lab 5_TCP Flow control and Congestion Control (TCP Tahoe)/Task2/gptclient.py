import socket
import time
def trans_layer_decode(packet):
    seq=packet[:6]
    ack=packet[6:12]
    win=packet[12:16]
    check=packet[16:20]
    return (int(seq.decode('utf-8')),int(ack.decode('utf-8')),int(win.decode('utf-8')),int(check.decode('utf-8')))
def make_packet(seq,ack,window,checksum):
    transport_header = f'{seq:06d}{ack:06d}{window:04d}{checksum:04d}'.encode('utf-8')[:20].ljust(20)
    
    # Build network layer header
    network_header = b'\x45\x00\x05\xdc'  # IP version 4, header length 20 bytes, total length 1500 bytes
    network_header += b'\x00\x00\x00\x00'  # Identification
    network_header += b'\x40\x06\x00\x00'  # TTL=64, protocol=TCP, checksum=0 (will be filled in by kernel)
    network_header += b'\x0a\x00\x00\x02'  # Source IP address
    network_header += b'\x0a\x00\x00\x01'  # Destination IP address
    
    # Build packet by concatenating headers and payload
    packet = network_header + transport_header
    return packet
rcvtim=0.6
mss=1460
# Set up client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8881))
client_socket.settimeout(1)

print('Connected to server')

#buffer
max_buffer_size = 1465*20  # 10 MB buffer size
data_buffer = b''
curr_buffer_size=0
total_received = 0
start_time = time.time()
tot_time=start_time

# Slow start algorithm variables
congestion_window = mss
threshold = 14600  # initial threshold value
slow_start = True  # start in slow start mode

try:
    # Receive packets and write to file
    with open('received_file.txt', 'wb') as file:
        expected_sequence_number = 0
        while True:
            start_time = time.time()
            curr_rcv=0
            # Receive packet from server
            while time.time()-start_time<rcvtim:

                try:
                    packet = client_socket.recv(1500)
                except socket.timeout:
                    print('No data received within 5 seconds')
                    continue

                print(f'rcvd {curr_rcv}')
                curr_rcv+=1
                # print(packet)
                if not packet:
                    break
                #parsing packet
                network_header = packet[:20]
                transport_header = packet[20:40]
                payload = packet[40:]
                payload_size=len(payload)
                sequence_number,ack,window,checksum=trans_layer_decode(transport_header)
                print(sequence_number,ack,window,checksum)
                if sequence_number == expected_sequence_number:
                    print(f'dhukse {sequence_number} {expected_sequence_number}')
                    data_buffer += payload 
                    curr_buffer_size+=payload_size
                    total_received += payload_size
                    expected_sequence_number += 1
                else:
                    print(f'Invalid sequence number. Expected {expected_sequence_number}, but received {sequence_number}')
                
                # check if buffer has reached max size, if yes, write to file and reset buffer
                if curr_buffer_size >= max_buffer_size:
                    file.write(data_buffer)
                    data_buffer = b''
                    curr_buffer_size = 0
                    print('Buffer flushed to file')
                    
                # congestion control algorithm
                if slow_start:
                    congestion_window += mss
                    if congestion_window >= threshold:
                        slow_start = False
                        print('Exited slow start mode')
                else:
                    congestion_window += mss * (mss / congestion_window)
                
                # send acknowledgement packet to server
                ack_packet = make_packet(0, expected_sequence_number, congestion_window, 0)
                client_socket.sendall(ack_packet)
                
                # print stats
                print(f'Total received: {total_received} bytes')
                print(f'Current buffer size: {curr_buffer_size} bytes')
                print(f'Congestion window size: {congestion_window} bytes')
                
                # sleep for some time before receiving next packet
                time.sleep(0.01)
            
    # write any remaining data in buffer to file
    file.write(data_buffer)
    data_buffer = b''
    curr_buffer_size = 0
    
    # print stats
    tot_time = time.time() - tot_time
    print(f'Total received: {total_received} bytes')
    print(f'Time taken: {tot_time:.2f} seconds')
    print(f'Average download speed: {(total_received / tot_time) / 1000:.2f} KB/s')
except KeyboardInterrupt:
    print('Keyboard interrupt received. Closing socket and exiting...')
    client_socket.close()
    
