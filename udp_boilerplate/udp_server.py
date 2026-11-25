import socket

server_ip = '0.0.0.0'  # listen on all interfaces
server_port = 9999

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((server_ip, server_port))

print(f'Server is running on {server_ip}:{server_port}')

while True:
    try:
        data, client_address = udp_socket.recvfrom(1024)
        print(f'Received from {client_address}: {data}')

        udp_socket.sendto(data, client_address)
    except KeyboardInterrupt:
        print('\nServer stopped.')
        break

udp_socket.close()
