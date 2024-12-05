import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from email.utils import formataddr
from send_mail import send_email
from crypto_utils import encrypt_email, sign_email

# Load environment variables
load_dotenv()

app = Flask(__name__)

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
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
        # Prepare email content
        nonce, ciphertext, tag, signature = prepare_email_content(body)

        # Send the email
        send_email(
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
        return jsonify({"message": f"Secure email sent successfully to {recipient_email}!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)