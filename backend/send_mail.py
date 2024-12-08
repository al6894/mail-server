import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

    with smtplib.SMTP(smtp_server, port) as server:
        server.send_message(msg)

def send_unencrypted_email(smtp_server, port, sender_email, recipient_email, subject, body):
    msg = MIMEText(body, 'plain')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.send_message(msg)

# NOTE: To work with gmail.com, need PW in .env