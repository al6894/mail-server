import hmac
import os
import hashlib
import time
import asyncio
from aiosmtpd.controller import Controller
from dotenv import load_dotenv
from base64 import b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

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

        # Decode the Base64 key
        self.symmetric_key = b64decode(key_base64)
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
        email_content = envelope.content.decode('utf-8')
        lines = email_content.splitlines()

        # Initialize components
        ciphertext = hmac_signature = iv = nonce = timestamp = None

        # Extract email components
        for line in lines:
            if line.startswith("Ciphertext:"):
                ciphertext = b64decode(line.replace("Ciphertext:", "").strip())
            elif line.startswith("HMAC:"):
                hmac_signature = b64decode(line.replace("HMAC:", "").strip())
            elif line.startswith("IV:"):
                iv = b64decode(line.replace("IV:", "").strip())
            elif line.startswith("Nonce:"):
                nonce = b64decode(line.replace("Nonce:", "").strip())
            elif line.startswith("Timestamp:"):
                timestamp = b64decode(line.replace("Timestamp:", "").strip())


        # Path 1: Encrypted Email
        if all([ciphertext, hmac_signature, iv, nonce, timestamp]):
            print("Encrypted email detected.")

            # Convert timestamp to integer
            try:
                message_time = int(timestamp)
            except ValueError:
                return '550 Timestamp Verification Failed'

            # Step 1: Verify Timestamp (Prevent Delayed Messages)
            current_time = int(time.time())
            if abs(current_time - message_time) > self.valid_window:
                return '550 Timestamp Verification Failed'

            # Step 2: Verify Nonce (Prevent Replay Attacks)
            self.cleanup_expired_nonces()
            if nonce in self.processed_nonces:
                return '550 Replay Attack Detected'
            self.processed_nonces[nonce] = message_time

            # Step 3: Verify HMAC
            hmac_data = ciphertext+nonce+timestamp
            computed_hmac = hmac.new(self.symmetric_key, hmac_data, hashlib.sha256).digest()
            if not hmac.compare_digest(hmac_signature, computed_hmac):
                return '550 HMAC Verification Failed'

            # Step 4: Decrypt Ciphertext
            try:
                cipher = Cipher(algorithms.AES(self.symmetric_key), modes.CFB(iv))
                print(f"Encrypted Message: {ciphertext}")
                print(f"Nonce: {nonce}")
                print(f"Timestamp: {timestamp}")
                print(f"HMAC {hmac_signature}")
                print(f"IV: {iv}")
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                print(f"Decrypted Message: {plaintext.decode('utf-8')}")
            except Exception as e:
                return '550 Decryption Error'

            return '250 OK'

        # Path 2: Unencrypted Email
        else:
            print("Unencrypted email detected.")
            print(f"Plaintext Message: {email_content}")
            return '250 OK'

# Main script to start the SMTP server
if __name__ == "__main__":
    handler = SecureHandler()
    controller = Controller(handler, hostname="localhost", port=1025)
    controller.start()
    print("SMTP server running on localhost:1025")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        controller.stop()
