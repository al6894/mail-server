import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from email.utils import formataddr
from send_mail import send_email
from crypto_utils import encrypt_email, sign_email

load_dotenv()

# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
RECIPIENT_NAME = os.getenv("RECIPIENT_NAME")
PASSWORD = os.getenv("PW")

def prepare_email_content():
    # Example plaintext content
    content = "This is a secure email containing sensitive information."
    
    # Generate symmetric key
    symmetric_key = os.urandom(32)

    # Encrypt the content
    nonce, ciphertext, tag = encrypt_email(content, symmetric_key)

    # Sign the content
    signature = sign_email(content, "private_key.pem")

    return nonce, ciphertext, tag, signature

def main():
    try:
        nonce, ciphertext, tag, signature = prepare_email_content()
    except Exception as e:
        print(f"Failed to prepare email content: {e}")
        return

    # Send the email
    try:
        send_email(
            smtp_server=SMTP_SERVER,
            port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            recipient_email=RECIPIENT_EMAIL,
            ciphertext=ciphertext,
            signature=signature,
            nonce=nonce,
            tag=tag
        )
        print(f"Secure email sent successfully to {formataddr((RECIPIENT_NAME, RECIPIENT_EMAIL))}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    main()