import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from base64 import b64encode
from dotenv import load_dotenv

load_dotenv()

def send_encrypted_email(smtp_server, port, sender_email, recipient_email, subject, ciphertext, iv, hmac_signature, nonce, timestamp):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(f"Ciphertext: {b64encode(ciphertext).decode()}", 'plain'))
    msg.attach(MIMEText(f"HMAC: {b64encode(hmac_signature).decode()}", 'plain'))
    msg.attach(MIMEText(f"IV: {b64encode(iv).decode()}", 'plain'))
    msg.attach(MIMEText(f"Nonce: {b64encode(nonce).decode()}", 'plain'))
    msg.attach(MIMEText(f"Timestamp: {b64encode(timestamp).decode()}", 'plain'))
    email_content = msg.as_string().encode()

    # Load the sender's private key for signing
    with open("sprivate_key.pem", "rb") as key_file:
        sender_private_key = load_pem_private_key(key_file.read(), password=None)

    # Sign the email content with the sender's private key
    signature = sender_private_key.sign(
        email_content,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    msg.attach(MIMEText(f"Signature: {b64encode(signature).decode()}", 'plain'))
    email_content = msg.as_string().encode()

    # Load the recipient's public key
    with open("rpublic_key.pem", "rb") as key_file:
        recipient_public_key = load_pem_public_key(key_file.read())

    # Encrypt the serialized email content
    encrypted_email = recipient_public_key.encrypt(
        email_content,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Base64 encode the encrypted email for transmission
    encoded_email = b64encode(encrypted_email)
    print(f"Encoded email being sent: {encoded_email}")

    with smtplib.SMTP(smtp_server, port) as server:
        server.sendmail(sender_email, recipient_email, encoded_email)

def send_unencrypted_email(smtp_server, port, sender_email, recipient_email, subject, body):
    msg = MIMEText(body, 'plain')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.send_message(msg)

# NOTE: To work with gmail.com, need PW in .env