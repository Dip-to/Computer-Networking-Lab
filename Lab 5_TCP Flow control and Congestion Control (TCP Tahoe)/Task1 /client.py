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
client_socket.connect(('localhost', 8882))
client_socket.settimeout(1)

print('Connected to server')

#buffer
max_buffer_size = 1465*20  # 10 MB buffer size
data_buffer = b''
curr_buffer_size=0
total_received = 0
start_time = time.time()
tot_time=start_time
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
                    total_received += len(payload)
                    expected_sequence_number += payload_size # ack


                else:
                    print(f'Received packet {sequence_number} out of order, expected {expected_sequence_number}')
                    break
                    #ack pathano lagbe
                # if  total_received + len(payload)>= max_buffer_size:
                #     break;
                print(time.time()-start_time)
            
            
            if curr_rcv!=0:
                rwnd=int((max_buffer_size-len(data_buffer))/mss)
                checksum=45
                packet = make_packet(ack,sequence_number+payload_size,rwnd,checksum)
                print('ack send')
                # acknowledgment = f'seq={ack}ack={sequence_number+payload_size}'.encode('utf-8')
                client_socket.send(packet)

                file.write(data_buffer)
                data_buffer = b''
                print(start_time,{sequence_number,ack})
                start_time = time.time()

        if data_buffer:
                file.write(data_buffer)
        client_socket.close()
        print('Done' )
        print(time.time()-tot_time)
except :
    client_socket.close()
    print('Done' )
    print(time.time()-tot_time)
