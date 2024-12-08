import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import b64encode

# Replay Attack Simulation
def replay_attack():
    # Components of the original message
    encrypted_message = b'[\xd5\xfd,'
    nonce = b'b851d4fe-d3c3-4dea-9cf9-c0093414f763'
    timestamp = b'1733699345'
    hmac_signature = b'\x01#\xaa&\xbe{\x82\xc6\xc0\xef\x96\xa7mo\xd0\xfc\x04\xe5\xb9\x83\xf51\x0e|\xd3N\x93.\xfe\xc9\xc5X'
    iv = b'\x8f\xe9\x14\xb5\rg\xafu\x9e\x8f\xf6\x0b\x9f\xc4bj'

    # Encode the components in Base64 for sending
    encrypted_message_encoded = b64encode(encrypted_message).decode()
    nonce_encoded = b64encode(nonce).decode()
    timestamp_encoded = b64encode(timestamp).decode()
    hmac_encoded = b64encode(hmac_signature).decode()
    iv_encoded = b64encode(iv).decode()

    # Construct the email
    msg = MIMEMultipart()
    msg['From'] = "attacker@example.com"
    msg['To'] = "victim@example.com"
    msg['Subject'] = "Replay Attack Test"

    # Attach the replayed components
    msg.attach(MIMEText(f"Ciphertext: {encrypted_message_encoded}", 'plain'))
    msg.attach(MIMEText(f"HMAC: {hmac_encoded}", 'plain'))
    msg.attach(MIMEText(f"IV: {iv_encoded}", 'plain'))
    msg.attach(MIMEText(f"Nonce: {nonce_encoded}", 'plain'))
    msg.attach(MIMEText(f"Timestamp: {timestamp_encoded}", 'plain'))

    # Send the email to the SMTP server
    smtp_server = "localhost"
    smtp_port = 1025  # Replace with the actual port used by your SMTP server

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.send_message(msg)
            print("Replay attack message sent successfully.")
    except Exception as e:
        print(f"Error sending replay attack message: {e}")


if __name__ == "__main__":
    replay_attack()
