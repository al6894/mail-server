import unittest
import json
import requests
from base64 import b64encode

BASE_URL = "http://127.0.0.1:5000"  # URL of your Flask app

class TestSecureEmail(unittest.TestCase):
    def test_signature_verification(self):
        """Test resistance to tampered signatures."""
        payload = {
            "senderEmail": "a.freecash2@gmail.com",
            "recipientEmail": "a.freecash2@gmail.com",
            "subject": "Signature Test",
            "body": "This is a test email to simulate signature tampering.",
        }

        # Send the original request
        response = requests.post(f"{BASE_URL}/send-secure-email", json=payload)
        self.assertEqual(response.status_code, 200)

        # Simulate tampering by modifying the signature in the payload
        tampered_payload = json.loads(response.text)
        tampered_payload["signature"] = b64encode(b"tampered-signature").decode('utf-8')

        # Send the tampered payload
        tampered_response = requests.post(f"{BASE_URL}/send-secure-email", json=tampered_payload)
        self.assertEqual(tampered_response.status_code, 500)  # Should fail due to signature mismatch

if __name__ == "__main__":
    unittest.main()