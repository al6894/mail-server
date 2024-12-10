import unittest
import time
import requests

BASE_URL = "http://127.0.0.1:5000"  # URL of your Flask app

class TestSecureEmail(unittest.TestCase):
    def test_timestamp_verification(self):
        """Test resistance to invalid timestamps."""
        payload = {
            "senderEmail": "a.freecash2@gmail.com",
            "recipientEmail": "a.freecash2@gmail.com",
            "subject": "Timestamp Test",
            "body": "This is a test email to simulate an invalid timestamp.",
        }

        # Modify the timestamp to be far in the future
        modified_payload = payload.copy()
        modified_payload["timestamp"] = str(int(time.time()) + 10000)

        response = requests.post(f"{BASE_URL}/send-secure-email", json=modified_payload)
        self.assertEqual(response.status_code, 500)  # Should fail due to invalid timestamp

if __name__ == "__main__":
    unittest.main()