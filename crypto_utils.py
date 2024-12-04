from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives import serialization
import os

# Encrypt email content using AES-GCM
def encrypt_email(content, symmetric_key):
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(content.encode()) + encryptor.finalize()
    return nonce, ciphertext, encryptor.tag

# Decrypt email content using AES-GCM
def decrypt_email(ciphertext, nonce, tag, symmetric_key):
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext

# Sign email content using RSA
def sign_email(content, private_key_path):
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None)
    
    signature = private_key.sign(
        content.encode(),
        padding.PSS(
            mgf=padding.MGF1(SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        SHA256(),
    )
    return signature

# Verify email signature using RSA
def verify_signature(content, signature, public_key_path):
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())
    
    try:
        public_key.verify(
            signature,
            content.encode(),
            padding.PSS(
                mgf=padding.MGF1(SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            SHA256(),
        )
        return True
    except Exception:
        return False