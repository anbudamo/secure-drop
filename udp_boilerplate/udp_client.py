import socket

server_ip = '10.10.55.10'
server_port = 9999

data = input("Enter a message: ").encode('utf-8')

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

udp_socket.sendto(data, (server_ip, server_port))

data, server_address = udp_socket.recvfrom(1024)
print(f"Received from server: {data}")

udp_socket.close()
