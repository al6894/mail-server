import unittest
import requests

BASE_URL = "http://127.0.0.1:5000"  # URL of your Flask app

class TestSecureEmail(unittest.TestCase):
    def test_mitm_attack(self):
        """Test resistance to MITM attacks by modifying the payload."""
        payload = {
            "senderEmail": "a.freecash2@gmail.com",
            "recipientEmail": "a.freecash2@gmail.com",
            "subject": "MITM Attack Test",
            "body": "This is a test email to simulate a MITM attack.",
        }

        # Send the original request
        response = requests.post(f"{BASE_URL}/send-secure-email", json=payload)
        self.assertEqual(response.status_code, 200)

        # Simulate a MITM attack by modifying the payload
        tampered_payload = payload.copy()
        tampered_payload["body"] = "This is a tampered body."

        # Send the tampered payload
        tampered_response = requests.post(f"{BASE_URL}/send-secure-email", json=tampered_payload)
        self.assertEqual(tampered_response.status_code, 500)  # Should fail due to HMAC mismatch

if __name__ == "__main__":
    unittest.main()