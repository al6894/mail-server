import os
import time
import hmac
import json
import binascii
import hashlib
import asyncio
from email import message_from_bytes
from aiosmtpd.controller import Controller
from dotenv import load_dotenv
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.padding import PSS, MGF1
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.exceptions import InvalidSignature

# Load environment variables
load_dotenv()

class SecureHandler:
    def __init__(self):
        key_base64 = os.getenv("SHARED_KEY")
        if key_base64 is None:
            raise ValueError("Environment variable 'SHARED_KEY' is not set. Please check your .env file.")
        # Add padding if needed
        missing_padding = len(key_base64) % 4
        if missing_padding:
            key_base64 += '=' * (4 - missing_padding)

        self.symmetric_key = b64decode(key_base64)
        with open("rprivate_key.pem", "rb") as key_file:
            self.recipient_private_key = load_pem_private_key(key_file.read(), password=None)
        with open("spublic_key.pem", "rb") as key_file:
            self.sender_public_key = load_pem_public_key(key_file.read())

        self.processed_nonces = {}  # Dictionary to map nonces to their timestamps
        self.valid_window = 300  # Valid time window in seconds (e.g., 5 minutes)

    def cleanup_expired_nonces(self):
        current_time = int(time.time())
        self.processed_nonces = {
            nonce: timestamp
            for nonce, timestamp in self.processed_nonces.items()
            if current_time - timestamp <= self.valid_window
        }

    async def handle_DATA(self, server, session, envelope):
        mime_message = message_from_bytes(envelope.content)
        if mime_message.is_multipart():
            for part in mime_message.walk():
                if part.get_content_type() == "text/plain":  
                    encrypted_payload = part.get_payload(decode=True)  
                    break
        else:
            encrypted_payload = mime_message.get_payload(decode=True)  
        
        normalized_payload = encrypted_payload.replace(b'\r\n', b'').replace(b'\n', b'').strip()
        try:
            decoded_bytes = b64decode(normalized_payload)
            decoded_string = decoded_bytes.decode('utf-8').strip()
            parsed_data = json.loads(decoded_string)
        except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
            raise ValueError(f"Error processing payload: {e}")

        decoded_data = b64decode(parsed_data['encrypted_data'])
        decoded_aes_key = b64decode(parsed_data['encrypted_aes_key'])
        iv = b64decode(parsed_data['iv'])
        signature = b64decode(parsed_data['signature'])

        # Decrypt the AES key using recipient's private RSA key
        try:
            aes_key = self.recipient_private_key.decrypt(
                decoded_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
        except Exception as e:
            print(f"Error decrypting AES key: {e}")
            return 550, b'AES Key Decryption Failed'
        
        # Initialize the AES cipher in CFB mode
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(decoded_data) + decryptor.finalize()
        sender_public_key = self.sender_public_key 

        # Verify the signature sent by sender using their public key
        try:
            sender_public_key.verify(
                signature,
                decrypted_data,
                PSS(
                    mgf=MGF1(SHA256()),
                    salt_length=PSS.MAX_LENGTH,
                ),
                SHA256(),
            )
            print("Signature verification successful.")
        except InvalidSignature:
            print("Signature verification failed: Invalid signature.")
            return 550, b'Signature Verification Failed'
        except Exception as e:
            print(f"An error occurred during signature verification: {e}")
            return 550, b'Signature Verification Failed'
                
        # Decrypt the encrypted data
        try:
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(decoded_data) + decryptor.finalize()
        except Exception as e:
            print(f"Error decrypting email content: {e}")
            return 550, b'Decryption Failed'
        
        # Verify Timestamp (prevent replay attacks)
        try:
            # Decode bytes to string and parse into dictionary
            string_decoded_data = decrypted_data.decode('utf-8')
            parsed_data = json.loads(string_decoded_data)
            
            # Access the timestamp
            message_time = int(parsed_data['timestamp'])
            current_time = int(time.time())
            
            # Allow a time window of 5 minutes (300 seconds)
            if abs(current_time - message_time) > 300:
                print("Timestamp verification failed: message is too old or too far in the future.")
                return 550, b'Timestamp Verification Failed'
            print("Timestamp verification successful.")
        except ValueError:
            print("Invalid timestamp format.")
            return 550, b'Timestamp Verification Failed'
        except KeyError:
            print("Timestamp key missing in decoded data.")
            return 550, b'Timestamp Verification Failed'
        
        # Verify Nonce (prevent replay attacks)
        self.cleanup_expired_nonces()
        if parsed_data['nonce'] in self.processed_nonces:
            print("Replay attack detected: nonce has already been used.")
            return 550, b'Replay Attack Detected'
        self.processed_nonces[parsed_data['nonce']] = message_time
        print("Nonce verification successful.")

        # Verify HMAC
        try:
            body = parsed_data['body'].encode('utf-8')  # Encode string to bytes 
            nonce = b64decode(parsed_data['nonce'])  # Decode Base64 to bytes
            timestamp = parsed_data['timestamp'].encode('utf-8')  # Encode string to bytes
            received_hmac = b64decode(parsed_data['hmac']) # Decode the hmac sent by sender

            hmac_data = body + nonce + timestamp # use same hmac_data creation as sender
            computed_hmac = hmac.new(self.symmetric_key, hmac_data, hashlib.sha256).digest()

            # Compare the received HMAC with the computed HMAC
            if not hmac.compare_digest(received_hmac, computed_hmac):
                print("HMAC verification failed: data integrity compromised.")
                return 550, b'HMAC Verification Failed'

            print("HMAC verification successful.")
        except Exception as e:
            print(f"Error verifying HMAC: {e}")
            return 550, b'HMAC Verification Failed'
        return '250 OK'


if __name__ == "__main__":
    handler = SecureHandler()
    controller = Controller(handler, hostname="localhost", port=1025)
    controller.start()
    print("SMTP server running on localhost:1025")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()