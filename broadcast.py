import socket
import json
import threading
import re


### set up udp socket
broadcast_ip = '255.255.255.255'  # broadcast address
server_ip = '0.0.0.0'  # listen on all interfaces
server_port = 9999
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((server_ip, server_port))
# set broadcast mode for socket options
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
# set communication timeout (seconds)
udp_socket.settimeout(2)


def register():
    while True:
        # get input data from user
        name = input("Enter full name: ").strip()
        email = input("Enter email address: ").strip().lower()

        # input validation 
        if not name or not email:
            print("All fields are required to register")
            continue

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            print("Invalid email address")
            continue

        # creat dictionary containing user info
        user_data = {
                "name": name,
                "email": email,
                "contacts": []
                }

        print("User Registered.")
        return user_data

def list_contacts():
    print("The following contacts are online:")

    # broadcast to clients 
    data = {
        "type": "discovery", 
        "name": user_data['name'],
        "email": user_data['email']
        }
    udp_socket.sendto(json.dumps(data).encode("utf-8"), (broadcast_ip, server_port))

    # receive and print out responses
    # while True:
    #     try:
    #         data, server_address = udp_socket.recvfrom(1024)
    #         print(f"Received from {server_address}: {data.decode('utf-8')}")

    #     except socket.timeout:
    #         break

def add_contact():
    while True:
        # get full name and email address
        full_name = input("Enter Full Name: ").strip().lower()
        email = input("Enter Email Address: ").strip().lower()

        # inputs are required
        if not full_name or not email:
            print("Full Name and Email Address required to add a contact")
            continue 

        # add new contact to user's data
        user_data['contacts'].append({'full_name': full_name, 'email': email})

        print("Contact Added.")
        return 


def secure_drop_shell():
    print('type "help" for commands') #help command

    while True:
        command = input("secure_drop> ").strip().lower() # reads command with secure_drop> format
        if command == "help": #if help is the command print comands
            print('  "exit" -> Exit Securedrop')
        elif command == "exit": # if exit end program
            print("Exiting SecureDrop.")
            break
        elif command == "add": # if add command
            add_contact()
            continue
        elif command == "list": # if list command
            list_contacts()
            continue
        elif command == "":# if blank continue running
            continue
        else:# if any other input print error message
            print("Unkwon command. type 'help' for commands")


def listen(stop_event):
    print(f'Server is running on {server_ip}:{server_port}')
    while not stop_event.is_set():
        try:
            raw_data, client_address = udp_socket.recvfrom(1024)
            data = json.loads(raw_data.decode('utf-8'))

            if user_data['name'] == data['name'] and user_data['email'] == data['email']:
                continue

            if data['type'] == "discovery":
                response = {
                    'type': 'response',
                    **user_data
                }
                print(f'Received broadcast from {client_address}')
                udp_socket.sendto(json.dumps(response).encode("utf-8"), client_address)
            elif data['type'] == "response":
                print(f'* {data['name']: <{data['email']}>}')
        except socket.timeout:
            continue

    return 

stop_event = threading.Event()
t = threading.Thread(target=listen, args=(stop_event,))
t.start()

user_data = register()
secure_drop_shell()

stop_event.set()
t.join()
udp_socket.close()
