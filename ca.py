# Bryce Greene nov 1
# simulated sertificate authority for SecureDrop
# in a real deployment this would be a separate server.
# clients assume it's trusted
 

import json
import time
from pathlib import Path
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
 
CA_DIR = Path("ca")
CA_KEY_FILE = CA_DIR / "ca_private.pem"
CA_PUB_FILE = CA_DIR / "ca_public.pem"
CERT_LIFETIME = 365 * 24 * 3600  # one year in seconds
 
# helper function to convert python obj to json string
def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
 
# loads the CA keypair, generating it if none exists
def _load_ca_key():
    if not CA_KEY_FILE.exists():
        CA_DIR.mkdir(parents=True, exist_ok=True)
        key = RSA.generate(2048)
        CA_KEY_FILE.write_bytes(key.export_key())
        CA_PUB_FILE.write_bytes(key.publickey().export_key())
        return key
    return RSA.import_key(CA_KEY_FILE.read_bytes())
 
# CA binds name and email to public key and signs it
def issue_certificate(name, email, publicKeyPem):
    caKey = _load_ca_key()
    now = int(time.time())
    cert = {
        # unique identifier for cert
        "serial": get_random_bytes(8).hex(),
        "issuer": "simulated CA for SecureDrop",
        "name": name,
        "email": email,
        "public_key": publicKeyPem,
        # active for:
        "not_before": now,
        "not_after": now + CERT_LIFETIME,
    }
    # sign it by passing in CA private key
    signature = pss.new(caKey).sign(SHA256.new(_canonical(cert)))
    return {"cert": cert, "signature": signature.hex()}
 
#
def verify_certificate(signed_cert):
   try: 
        cert = signed_cert["cert"]
        signature = bytes.fromhex(signed_cert["signature"])
        required_fields = {
             "serial",
             "issuer",
             "name",
             "email",
             "public_key",
             "not_before",
             "not_after"
        }
        if not isinstance(cert, dict):
             return False
        if not required_fields.issubset(cert.keys()):
             return False
        if cert["issuer"] != "simulated CA for SecureDrop":
             return False
        if not isinstance(cert["not_before"], int):
             return False
        if not isinstance(cert["not_after"], int):
             return False
        current_time = int(time.time())
        if current_time < cert["not_before"]:
             return False
        if current_time > cert["not_after"]:
             return False
        ca_public_key = RSA.import_key(CA_PUB_FILE.read_bytes())
        certificate_hash = SHA256.new(_canonical(cert))
        verifier = pss.new(ca_public_key)
        verifier.verify(certificate_hash, signature)
        return True
   except(KeyError, TypeError, ValueError, FileNotFoundError):
        return False

# for testing
if __name__ == "__main__":
        ca_key = _load_ca_key()
        print("ca initialized")
