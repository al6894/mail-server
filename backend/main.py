import os
import time
import hmac
import hashlib
import smtplib
import uuid
from base64 import b64decode
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from email.utils import formataddr
from send_mail import send_encrypted_email, send_unencrypted_email
from crypto_utils import encrypt_email, sign_email

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# SMTP Configuration
#SMTP_SERVER = "smtp.gmail.com"
SMTP_SERVER = "localhost"
SMTP_PORT = 1025
PASSWORD = os.getenv("PW")

def prepare_email_content(body):
    try:
        symmetric_key = os.getenv("SHARED_KEY")

        # Padding to account for missing = in .env for the key
        missing_padding = len(symmetric_key) % 4
        if missing_padding:
            symmetric_key += '=' * (4 - missing_padding)
        symmetric_key = b64decode(symmetric_key)

        # Generate IV (Initialization Vector) for AES
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(body.encode()) + encryptor.finalize()

        # Add a unique nonce and timestamp to prevent replay attacks
        nonce = str(uuid.uuid4()).encode()
        timestamp = str(int(time.time())).encode()

        # Create a message digest for integrity (HMAC) 
        hmac_data = ciphertext+nonce+timestamp
        hmac_signature = hmac.new(symmetric_key, hmac_data, hashlib.sha256).digest()
        
        return iv, ciphertext, hmac_signature, nonce, timestamp
    except Exception as e:
        raise RuntimeError(f"Error preparing email content: {e}")
    
metrics = {
    "secure": [],
    "non_secure": []
}

@app.route('/send-secure-email', methods=['POST'])
def send_secure_email():
    start_time = time.perf_counter()
    data = request.json
    sender_email = data.get("senderEmail, a.freecash2@gmail.com")
    recipient_email = data.get("recipientEmail, a.freecash2@gmail.com")
    subject = data.get("subject", "Secure Email")
    body = data.get("body", "Test")

    try:
        iv, ciphertext, hmac_signature, nonce, timestamp = prepare_email_content(body)
        encryption_time = time.perf_counter() - start_time

        send_encrypted_email(
            smtp_server=SMTP_SERVER,
            port=SMTP_PORT,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            ciphertext=ciphertext,
            iv=iv,
            hmac_signature=hmac_signature,
            nonce=nonce,
            timestamp=timestamp,
        )
        send_time = time.perf_counter() - encryption_time
        total_time = start_time + encryption_time + send_time
        metrics["secure"].append(total_time)

        return jsonify({
            "message": f"Secure email sent successfully to {recipient_email}!",
            "time_taken": total_time,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/send-insecure-email', methods=['POST'])
def send_insecure_email():
    start_time = time.perf_counter()
    data = request.json

    # Validate the request payload
    sender_email = data.get("senderEmail, a.freecash2@gmail.com")
    recipient_email = data.get("recipientEmail, a.freecash2@gmail.com")
    subject = data.get("subject", "Regular Email")
    body = data.get("body", "Test")

    try:
        send_unencrypted_email(
            smtp_server=SMTP_SERVER,
            port=SMTP_PORT,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            body=body, 
        )

        elapsed_time = time.perf_counter() - start_time
        metrics["non_secure"].append(elapsed_time)

        return jsonify({
            "message": f"Insecure email sent successfully to {recipient_email}!",
            "time_taken": elapsed_time,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/metrics', methods=['GET'])
def get_metrics():
    return jsonify(metrics), 200

if __name__ == "__main__":
    app.run(debug=True)