import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import b64encode
from dotenv import load_dotenv
import os

load_dotenv()

def send_encrypted_email(smtp_server, port, sender_email, recipient_email, subject, ciphertext, hmac_signature, iv):
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach encrypted content and HMAC
    msg.attach(MIMEText(f"Ciphertext: {b64encode(ciphertext).decode()}", 'plain'))
    msg.attach(MIMEText(f"HMAC: {b64encode(hmac_signature).decode()}", 'plain'))
    msg.attach(MIMEText(f"IV: {b64encode(iv).decode()}", 'plain'))

    # Send the email
    with smtplib.SMTP(smtp_server, port) as server:
        # password = os.getenv("PW")
        # if not password:
        #     raise ValueError("Environment variable 'PW' is not set.")
        # TLS not supported on local SMTP
        #server.starttls()
        # No authentication supported on local SMTP, otherwise use Google code to verify identity
        #server.login(sender_email, password)
        server.send_message(msg)
        server.send_message(msg)

def send_unencrypted_email(smtp_server, port, sender_email, recipient_email, subject, body):
    # Create the email
    msg = MIMEText(body, 'plain')
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Send the email
    with smtplib.SMTP(smtp_server, port) as server:
        password = os.getenv("PW")
        if not password:
            raise ValueError("Environment variable 'PW' is not set.")
        # No authentication supported on local SMTP, otherwise use Google code to verify identity
        #server.login(sender_email, password)
        server.send_message(msg)