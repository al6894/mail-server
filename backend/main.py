import os
import time
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
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
PASSWORD = os.getenv("PW")

def prepare_email_content(content):
    try:
        # Generate symmetric key
        symmetric_key = os.urandom(32)

        # Encrypt the content
        nonce, ciphertext, tag = encrypt_email(content, symmetric_key)

        # Sign the content
        signature = sign_email(content, "private_key.pem")

        return nonce, ciphertext, tag, signature
    except Exception as e:
        raise RuntimeError(f"Error preparing email content: {e}")
    
metrics = {
    "secure": [],
    "non_secure": []
}

@app.route('/send-secure-email', methods=['POST'])
def send_secure_email():
    data = request.json

    # Validate the request payload
    sender_email = data.get("senderEmail")
    recipient_email = data.get("recipientEmail")
    subject = data.get("subject", "Secure Email")
    body = data.get("body")

    if not all([sender_email, recipient_email, body]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        start_time = time.time()

        # Prepare email content
        nonce, ciphertext, tag, signature = prepare_email_content(body)

        # Send the email
        send_encrypted_email(
            smtp_server=SMTP_SERVER,
            port=SMTP_PORT,
            sender_email=sender_email,
            recipient_email=recipient_email,
            subject=subject,
            ciphertext=ciphertext,
            signature=signature,
            nonce=nonce,
            tag=tag,
        )

        elapsed_time = time.time() - start_time
        metrics["secure"].append(elapsed_time)

        return jsonify({
            "message": f"Secure email sent successfully to {recipient_email}!",
            "time_taken": elapsed_time,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send-insecure-email', methods=['POST'])
def send_insecure_email():
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
        start_time = time.time()

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
        elapsed_time = time.time() - start_time
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