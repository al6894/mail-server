import unittest
import time
import requests

BASE_URL = "http://127.0.0.1:5000"  # URL of your Flask app

class TestSecureEmail(unittest.TestCase):
    def test_expired_nonce(self):
        """Test resistance to expired nonces by delaying the request."""
        payload = {
            "senderEmail": "a.freecash2@gmail.com",
            "recipientEmail": "a.freecash2@gmail.com",
            "subject": "Expired Nonce Test",
            "body": "This is a test email to simulate an expired nonce.",
        }

        # Send the original request
        response = requests.post(f"{BASE_URL}/send-secure-email", json=payload)
        self.assertEqual(response.status_code, 200)

        # Wait for the nonce to expire (300 seconds + buffer)
        time.sleep(11)

        # Replay the same payload
        expired_response = requests.post(f"{BASE_URL}/send-secure-email", json=payload)
        self.assertEqual(expired_response.status_code, 550)  # Should fail due to expired nonce

if __name__ == "__main__":
    unittest.main()