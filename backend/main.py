import os
import time
import hmac
import hashlib
import smtplib
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

def prepare_email_content(content, symmetric_key):
    try:
        # Generate IV (Initialization Vector) for AES
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(symmetric_key), modes.CFB(iv))
        encryptor = cipher.encryptor()

        # Encrypt the content using AES
        ciphertext = encryptor.update(content.encode()) + encryptor.finalize()

        # Generate HMAC for the ciphertext
        hmac_key = symmetric_key  # Reusing symmetric key for HMAC
        mac = hmac.new(hmac_key, ciphertext, hashlib.sha256).digest()

        return iv, ciphertext, mac
    except Exception as e:
        raise RuntimeError(f"Error preparing email content: {e}")
    
metrics = {
    "secure": [],
    "non_secure": []
}

@app.route('/send-secure-email', methods=['POST'])
def send_secure_email():
    data = request.json
    sender_email = data.get("senderEmail")
    recipient_email = data.get("recipientEmail")
    subject = data.get("subject", "Secure Email")
    body = data.get("body")

    if not all([sender_email, recipient_email, body]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        start_time = time.perf_counter()
        # Read the key from .env
        key_base64 = os.getenv("SHARED_KEY")

        # Add padding if needed
        missing_padding = len(key_base64) % 4
        if missing_padding:
            key_base64 += '=' * (4 - missing_padding)

        # Decode the Base64 key
        symmetric_key = b64decode(key_base64)
        iv, ciphertext, hmac_signature = prepare_email_content(body, symmetric_key)
        encryption_time = time.perf_counter() - start_time

        # Send the email
        send_encrypted_email(
            smtp_server=SMTP_SERVER,
            port=SMTP_PORT,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            ciphertext=ciphertext,
            hmac_signature=hmac_signature,
            iv=iv,
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
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT) # Local server to test MITM attack
    server.set_debuglevel(1)
    data = request.json

    # Validate the request payload
    sender_email = data.get("senderEmail")
    recipient_email = data.get("recipientEmail")
    subject = data.get("subject", "Regular Email")
    body = data.get("body")

    if not all([sender_email, recipient_email, body]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Start performance tracking
        start_time = time.perf_counter()

        # Send the email (no security measures)
        send_unencrypted_email(
            smtp_server=SMTP_SERVER,
            port=SMTP_PORT,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            body=body,  # No encryption/signing
        )

        # Calculate time taken
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