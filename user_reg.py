#Bryce Greene Nov 1
#COMP 2300

import getpass
import json
import re
from pathlib import Path
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from ca import issue_certificate
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES

DATA_DIR = Path("data") #creating directory variable

USER_FILE = DATA_DIR / "user.json" # creating user file variable equal to 
#"user.json" located in DATA_DIR directory


def register():
    # get input data from user
    name = input("Enter full name: ").strip()
    email = input("Enter email address: ").strip().lower()
    password = getpass.getpass("Enter Password: ")
    confirmation = getpass.getpass("Re-enter Password: ")

    # input validation 
    if not name or not email or not password:
        print("All fields are required to register")
        return

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        print("Invalid email address")
        return

    if password != confirmation:
        print("Passwords do not match")
        return

    # hash password using helper func
    hashed_password = hash_password(password)
    # create new directory to store user data
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    #generate RSA public and private keys to prove identity
    user_key = RSA.generate(2048)
    private_key_pem = user_key.export_key()
    public_key_pem = user_key.publickey().export_key()
    encrypted_private_key_data = encrypt_private_key(private_key_pem, password)
    # get certificate from trusted CA (simulated in this case with ca.py)
    certificate = issue_certificate(name, email, public_key_pem.decode("utf-8"))
    
    
    # creat dictionary containing user info
    user_data = {
            "name": name,
            "email": email,
            "contacts": [],
            "salt": hashed_password["salt"],
            "encryption_salt": get_random_bytes(16).hex(),
            "hashed_password": hashed_password["hashed_password"],
            **encrypted_private_key_data,
            "certificate": certificate
            }

    # open user.json and dump user_data into it
    with USER_FILE.open("w") as file:
        json.dump(user_data, file, indent=4)


    print("Passwords match.\nUser Registered.\nExiting SecureDrop")

# function that hashes password with SHA256 and PBKDF2
def hash_password(password):
    salt = get_random_bytes(16)
    hashed_password = PBKDF2(password.encode("utf-8"),salt,32, count =100000, hmac_hash_module= SHA256)
    return {"salt": salt.hex(), "hashed_password": hashed_password.hex()}

def encrypt_private_key(private_key_pem, password):
    salt = get_random_bytes(16)
    encryption_key = PBKDF2(password.encode("utf-8"), salt, 32, count = 100000, hmac_hash_module=SHA256)
    cipher = AES.new(encryption_key, AES.MODE_GCM, nonce=get_random_bytes(16))
    ciphertext , tag = cipher.encrypt_and_digest(private_key_pem)
    return {
        "private_key_salt": salt.hex(),
        "private_key_nonce": cipher.nonce.hex(),
        "private_key_tag": tag.hex(),
        "encrypted_private_key": ciphertext.hex()
    }

if __name__ == "__main__":
    # check if user info already exists
    if not USER_FILE.exists():
        print("No users are registered with this client")

        choice = input("do you want to register a new user (y/n)? "
                       ).strip().lower()
        if choice == "y":
            register()
        elif choice == "n":
            print("Exiting SecureDrop.")
        else:
            print("Invalid choice. Please enter y or n.")

    else:
        print("A user is already registered.")
