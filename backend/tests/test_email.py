from send_mail import send_email  # Replace with your module name
import os

def test_send_email():
    # Dummy data
    ciphertext = b"This is a test ciphertext."
    signature = b"DummySignature"
    nonce = os.urandom(12)  # Random nonce
    tag = b"RandomTag"

    # SMTP and email configuration
    smtp_server = "smtp.gmail.com"  # Gmail's SMTP server
    port = 587
    sender_email = "a.freecash2@gmail.com"
    recipient_email = "a.freecash2@gmail.com"

    # Call the send_email function
    try:
        send_email(smtp_server, port, sender_email, recipient_email, ciphertext, signature, nonce, tag)
        print("Test email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")