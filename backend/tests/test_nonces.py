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

        # First request
        first_response = requests.post(f"{BASE_URL}/send-secure-email", json=payload)
        self.assertEqual(first_response.status_code, 200)

        # Extract the returned nonce and timestamp from the first response
        first_json = first_response.json()
        nonce = first_json["nonce"]  

        # Wait for the nonce to expire (10 seconds + buffer)
        time.sleep(13)

        # Now we modify the payload for the second request to include the exact same nonce
        second_payload = payload.copy()
        second_payload["nonce"] = nonce

        # Second request with identical nonce and timestamp
        second_response = requests.post(f"{BASE_URL}/send-secure-email", json=second_payload)
        self.assertNotEqual(second_response.status_code, 200)

if __name__ == "__main__":
    unittest.main()