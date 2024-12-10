import os
from os import urandom
import time
import json
import hmac
import hashlib
import smtplib
import uuid
from base64 import b64decode, b64encode, encodebytes
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from email.mime.text import MIMEText
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app)

# SMTP Configuration
SMTP_SERVER = "localhost"
SMTP_PORT = 1025
PASSWORD = os.getenv("PW")
    
metrics = []

@app.route('/send-secure-email', methods=['POST'])
def send_secure_email():
    start_time = time.perf_counter()
    data = request.json
    sender_email = data.get("senderEmail", "a.freecash2@gmail.com")
    recipient_email = data.get("recipientEmail", "a.freecash2@gmail.com")
    subject = data.get("subject", "Secure Email")
    body = data.get("body", "Test")
    nonce = data.get("nonce") or str(uuid.uuid4()).encode()
    timestamp = data.get("timestamp") or str(int(time.time())).encode()


    try:
        # Step 1: Prepare HMAC signature and metadata
        symmetric_key = os.getenv("SHARED_KEY")
        # Padding to account for missing = in .env for the key
        missing_padding = len(symmetric_key) % 4
        if missing_padding:
            symmetric_key += '=' * (4 - missing_padding)
        symmetric_key = b64decode(symmetric_key)
        hmac_data = body.encode() + nonce + timestamp
        hmac_signature = hmac.new(symmetric_key, hmac_data, hashlib.sha256).digest()

        email_data = {
            "subject": subject,
            "body": body,
            "hmac": b64encode(hmac_signature).decode('utf-8'),  
            "nonce": b64encode(nonce).decode('utf-8'),          
            "timestamp": timestamp.decode('utf-8'),             
        }

        # Step 2: Generate a random AES key and IV
        aes_key = urandom(32)  # 256-bit AES key
        iv = urandom(16)       # Initialization vector

        # Step 3: Encrypt email data using AES
        serialized_email_data = json.dumps(email_data).encode('utf-8')
        cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        encrypted_email_data = encryptor.update(serialized_email_data) + encryptor.finalize()

        # Step 4: Sign the serialized email data using sender's private RSA key
        with open("sprivate_key.pem", "rb") as key_file:
            sender_private_key = load_pem_private_key(key_file.read(), password=None)
        signature = sender_private_key.sign(
            serialized_email_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

        # Include the signature in the payload
        encrypted_payload = {
            "encrypted_data": b64encode(encrypted_email_data).decode('utf-8'),
            "iv": b64encode(iv).decode('utf-8'),
            "signature": b64encode(signature).decode('utf-8'),
        }

        # Step 5: Encrypt the AES key using recipient's public RSA key
        with open("rpublic_key.pem", "rb") as key_file:
            recipient_public_key = load_pem_public_key(key_file.read())
        encrypted_aes_key = recipient_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Include the encrypted AES key in the payload
        encrypted_payload["encrypted_aes_key"] = b64encode(encrypted_aes_key).decode('utf-8')

        # Step 6: Serialize the final payload
        serialized_payload = json.dumps(encrypted_payload).encode('utf-8')

        # Step 7: Wrap the bytes to prevent too long error
        wrapped_payload = encodebytes(serialized_payload)
        # Create a MIMEText email
        mime_message = MIMEText(wrapped_payload.decode('utf-8'), 'plain')
        mime_message['From'] = sender_email
        mime_message['To'] = recipient_email
        mime_message['Subject'] = subject

        # Step 8: Send the email with the payload
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.sendmail(sender_email, recipient_email, mime_message.as_string())

        # Measure time taken
        total_time = time.perf_counter() - start_time
        metrics.append(total_time)

        return jsonify({
            "message": f"Secure email sent successfully to {recipient_email}!",
            "time_taken": total_time,
            "nonce": email_data["nonce"],
            "timestamp": email_data["timestamp"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify(metrics), 200

if __name__ == "__main__":
    app.run(debug=True)