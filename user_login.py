# Connor Kelleher 
#Comp 2300 Milestone 2

import json 
import getpass
import hmac
from pathlib import Path
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from add_contacts import add_contact, list_contacts

DATA_DIR = Path ("data") #creates directory
USER_FILE = DATA_DIR / "user.json" #creates user file "user.json" which will be located in DATA_DIR directory


def hash_password(password):
    salt = get_random_bytes(16)
    hashed_password = PBKDF2(password.encode("utf-8"),salt,32, count =100000, hmac_hash_module= SHA256)
    return {"salt": salt.hex(), "hashed_password": hashed_password.hex()}

def load_user():
    try:    # open file while handling possible error
        with USER_FILE.open("r", encoding ="utf-8") as file: #opens file for reading
            return json.load(file) #loads json file
    except (FileNotFoundError, json.JSONDecodeError, OSError): #handles error if file is nto found
        print("Unable to load registered information")
        return None

def verify_password(password,salt_hex, stored_hash_hex): #verify password = hash
    try:
        salt = bytes.fromhex(salt_hex) #converts from hex to bytes
        stored_hash = bytes.fromhex(stored_hash_hex) #converts from hx to bytes 
    except (ValueError, TypeError): #handles invalid data types
        return False
    if len(salt) != 16 or len(stored_hash) != 32: #makes sure the salt is 16 bytes and hash is 32
        return False
    computed_hash = PBKDF2(password.encode("utf-8"), salt, 32, count = 100000, hmac_hash_module=SHA256)#hash the inputted password
    return hmac.compare_digest(computed_hash, stored_hash)#make sure they match 

def decrypt_private_key(user, password):
    salt_hex = user["private_key_salt"]
    nonce_hex = user["private_key_nonce"]
    tag_hex = user["private_key_tag"]
    ciphertext_hex = user["encrypted_private_key"]
    salt = bytes.fromhex(salt_hex)
    nonce = bytes.fromhex(nonce_hex)
    tag = bytes.fromhex(tag_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    if len(salt) != 16:
        raise ValueError("Invalid private key salt")
    if len(nonce) != 16:
        raise ValueError("Invalid private key nonce")
    if len(tag) != 16:
        raise ValueError("Invalid private key authentication tag")
    encryption_key = PBKDF2(password.encode("utf-8"), salt, 32, count = 100000, hmac_hash_module=SHA256)
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=nonce)
    private_key_pem = cipher.decrpyt_and_verify(ciphertext,tag)
    private_key = RSA.import_key(private_key_pem)
    return private_key
def login():
    user = load_user() #loads registered user information from json file
    if not isinstance(user, dict): #error if there is no user
        print("No registered user found.")
        print("Please register prior to logging in")
        return
    
    stored_email = user.get("email") # gets stored email
    encryption_salt_hex = user.get("encryption_salt")
    salt_hex = user.get("salt")
    stored_hash_hex = user.get("hashed_password") # gets stored password hashes 

    if not all(isinstance(value, str) for value in (stored_email, encryption_salt_hex, salt_hex, stored_hash_hex)): #makes sure both are strings
        print("Invalid user data") #prints error if they aren't
        return 
    try: 
        encryption_salt = bytes.fromhex(encryption_salt_hex)
        if len(encryption_salt) != 16:
            print("invalid encryption slat")
            return
    except ValueError:
        print("invalid encryption slat")
        return
    
    while True:
        email = input("Enter Email Address: ").strip().lower() #get inputted user email
        password = getpass.getpass("Enter Password: ") # get their password
        email_matches = hmac.compare_digest(
            email.encode("utf-8"), stored_email.strip().lower().encode("utf-8")
        ) #returns true if stored email = inputted email
        if email_matches and verify_password(password, salt_hex, stored_hash_hex): #makes sure both email and password matches
            # create symmetric key for encrypting/decrypting user data (eg: contacts) by hashing password
            session_cookie = PBKDF2(password.encode("utf-8"),encryption_salt,32, count =100000, hmac_hash_module= SHA256)
            private_key = decrypt_private_key(user, password)
            password = None
            print("Welcome to SecureDrop") # login authenticated goto secure shell
            secure_drop_shell(session_cookie, private_key)
            return 

        password = None 
        print("Email and password combination failed to login\n")

def secure_drop_shell(cookie, private_key):
    print('type "help" for commands') #help command

    while True:
        command = input("secure_drop> ").strip().lower() # reads command with secure_drop> format
        if command == "help": #if help is the command print comands
            print('  "add"  -> Add a new contact')
            print('  "list" -> List all online contacts')
            print('  "send" -> Transfer file to contact')
            print('  "exit" -> Exit Securedrop')
        elif command == "exit": # if exit end program
            print("Exiting SecureDrop.")
            break
        elif command == "add": # if add command
            add_contact(cookie)
            continue
        elif command == "list": # if list command
            list_contacts(cookie)
            continue
        elif command in ("send"): # if other commands run approiate program
            print("NOT IMPLEMENTED YET")
        elif command == "":# if blank continue running
            continue
        else:# if any other input print error message
            print("Unkwon command. type 'help' for commands")

if __name__ == "__main__":
    try:
        if USER_FILE.exists(): #if there are any registered users let a login attempt
            login()
        else:#if not print error message and exit SecureDrop
            print("No users are registered please register before logging in")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting SecureDrop.")
