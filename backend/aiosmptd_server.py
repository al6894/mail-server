import hmac
import os
import hashlib
import asyncio
from aiosmtpd.controller import Controller
from dotenv import load_dotenv
from base64 import b64decode
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Your SecureHandler class here
load_dotenv()

class SecureHandler:
    key_base64 = os.getenv("SHARED_KEY")
    if key_base64 is None:
        raise ValueError("Environment variable 'SHARED_KEY' is not set. Please check your .env file.")
    # Add padding if needed
    missing_padding = len(key_base64) % 4
    if missing_padding:
        key_base64 += '=' * (4 - missing_padding)

    # Decode the Base64 key
    symmetric_key = b64decode(key_base64)

    async def handle_DATA(self, server, session, envelope):
        print("Processing email...")

        # Parse email content
        email_content = envelope.content.decode('utf-8')
        lines = email_content.splitlines()

        # Initialize components
        ciphertext = hmac_signature = iv = None

        # Check for encryption markers
        for line in lines:
            if line.startswith("Ciphertext:"):
                ciphertext = b64decode(line.replace("Ciphertext:", "").strip())
            elif line.startswith("HMAC:"):
                hmac_signature = b64decode(line.replace("HMAC:", "").strip())
            elif line.startswith("IV:"):
                iv = b64decode(line.replace("IV:", "").strip())

        # Path 1: Encrypted Email
        if all([ciphertext, hmac_signature, iv]):
            print("Encrypted email detected.")
            # Step 1: Verify HMAC
            computed_hmac = hmac.new(self.symmetric_key, ciphertext, hashlib.sha256).digest()
            if not hmac.compare_digest(hmac_signature, computed_hmac):
                print("Error: HMAC verification failed. Message integrity compromised!")
                return '550 HMAC Verification Failed'

            # Step 2: Decrypt ciphertext
            try:
                cipher = Cipher(algorithms.AES(self.symmetric_key), modes.CFB(iv))
                print(f'Encrypted Message: {ciphertext}')
                decryptor = cipher.decryptor()
                plaintext = decryptor.update(ciphertext) + decryptor.finalize()
                print(f"Decrypted Message: {plaintext.decode('utf-8')}")
            except Exception as e:
                print(f"Error during decryption: {e}")
                return '550 Decryption Error'

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
