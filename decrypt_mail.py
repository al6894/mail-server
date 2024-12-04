from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash

def decrypt_email(ciphertext, nonce, tag, symmetric_key):
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext

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
    except Exception as e:
        return False

# Example usage
decrypted_content = decrypt_email(ciphertext, nonce, tag, symmetric_key)
is_valid = verify_signature(decrypted_content, signature, "public_key.pem")
