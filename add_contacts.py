#Anbu Damodaran Oct 29
#COMP 2300

from pathlib import Path
import json
from Crypto.Cipher import AES

DATA_DIR = Path("data") #creates directory
USER_FILE = DATA_DIR / "user.json" #creates user file "user.json" which will be located in DATA_DIR directory

def load_user():
    try:    # open file while handling possible error
        with USER_FILE.open("r", encoding ="utf-8") as file: #opens file for reading
            return json.load(file) #loads json file
    except (FileNotFoundError, json.JSONDecodeError, OSError): #handles error if file is nto found
        print("Unable to load registered information")
        return None

    
def add_contact(cookie):
    # get full name and email address
    full_name = input("Enter Full Name: ").strip().lower()
    email = input("Enter Email Address: ").strip().lower()

    # inputs are required
    if not full_name or not email:
        print("Full Name and Email Address required to add a contact")
        return 

    # write new contact to user's data
    user = load_user()
    if user is None:
        return

    # encrypt name and email using cookie
    name_cipher = AES.new(cookie, AES.MODE_GCM)
    full_name_enc, full_name_tag = name_cipher.encrypt_and_digest(full_name.encode())
    email_cipher = AES.new(cookie, AES.MODE_GCM)
    email_enc, email_tag = email_cipher.encrypt_and_digest(email.encode())

    full_name_ciphertext = (name_cipher.nonce + full_name_tag + full_name_enc).hex()
    email_ciphertext = (email_cipher.nonce + email_tag + email_enc).hex()
    
    user['contacts'].append({'full_name': full_name_ciphertext, 'email': email_ciphertext})
    
    with USER_FILE.open("w") as file:
        json.dump(user, file, indent=4)

    print("Contact Added.")
    return 

def list_contacts(cookie):
    print("The following contacts are online:")
    user = load_user()
    if user is None:
        return
    contacts = user.get("contacts", [])
    if not contacts:
        print("You have no contacts added.  Type 'add' to add contacts")
        return 
    
    # print users contacts
    for contact in contacts:
        full_name_ciphertext = bytes.fromhex(contact['full_name'])
        email_ciphertext = bytes.fromhex(contact['email'])

        name_cipher = AES.new(cookie, AES.MODE_GCM, nonce=full_name_ciphertext[:16])
        full_name_tag, full_name_enc = full_name_ciphertext[16:32], full_name_ciphertext[32:]
        full_name = name_cipher.decrypt_and_verify(full_name_enc, full_name_tag)

        email_cipher = AES.new(cookie, AES.MODE_GCM, nonce=email_ciphertext[:16])
        email_tag, email_enc = email_ciphertext[16:32], email_ciphertext[32:]
        email = email_cipher.decrypt_and_verify(email_enc, email_tag)

        print(f"* {full_name.decode()} <{email.decode()}>")
