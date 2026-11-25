import socket

server_ip = '255.255.255.255'  # broadcast address
server_port = 9999

data = input("Enter a message: ").encode('utf-8')

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# set broadcast mode for socket options
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

udp_socket.sendto(data, (server_ip, server_port))

data, server_address = udp_socket.recvfrom(1024)
print(f"Received from server: {data}")

udp_socket.close()
