import requests
import json
import uuid
import time

# URL of the Flask endpoint
url = "http://127.0.0.1:5000/send-secure-email"

# Generate unique nonce and timestamp
nonce = str(uuid.uuid4())
timestamp = str(int(time.time()))

# JSON payload
data = {
    "senderEmail": "test.sender@example.com",
    "recipientEmail": "test.recipient@example.com",
    "subject": "Test Secure Email",
    "body": "This is a test email with secure encryption.",
    "nonce": nonce,         # Unique nonce
    "timestamp": timestamp  # Current timestamp
}

try:
    # Send a POST request
    response = requests.post(url, json=data)
    
    # Check the response status code
    if response.status_code == 200:
        print("Email sent successfully!")
        print("Response:", response.json())
    else:
        print("Failed to send email.")
        print("Error:", response.json())
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)
