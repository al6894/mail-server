import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import b64encode

def send_email(smtp_server, port, sender_email, recipient_email, ciphertext, signature, nonce, tag):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Secure Email"
    
    # Attach encrypted content and metadata
    msg.attach(MIMEText("Encrypted email content attached.", 'plain'))
    msg.attach(MIMEText(f"Ciphertext: {b64encode(ciphertext).decode()}", 'plain'))
    msg.attach(MIMEText(f"Signature: {b64encode(signature).decode()}", 'plain'))
    msg.attach(MIMEText(f"Nonce: {b64encode(nonce).decode()}", 'plain'))
    msg.attach(MIMEText(f"Tag: {b64encode(tag).decode()}", 'plain'))
    
    # Send the email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, "your_password")
        server.send_message(msg)