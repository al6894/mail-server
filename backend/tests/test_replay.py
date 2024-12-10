import unittest
import requests
import time

BASE_URL = "http://127.0.0.1:5000"  # URL where the Flask app is running

class TestReplayAttack(unittest.TestCase):
    def test_replay_attack(self):
        payload = {
            "senderEmail": "a.freecash2@gmail.com",
            "recipientEmail": "a.freecash2@gmail.com",
            "subject": "Replay Attack Test",
            "body": "This is a test email to simulate a replay attack.",
        }
        
        # First request
        first_response = requests.post(f"{BASE_URL}/send-secure-email", json=payload)
        self.assertEqual(first_response.status_code, 200)

        # Extract the returned nonce and timestamp from the first response
        first_json = first_response.json()
        nonce = first_json["nonce"]        # This should be the same nonce used by the server
        timestamp = first_json["timestamp"] # Same timestamp used by the server

        # Modify the payload for the second request to include the exact same nonce and timestamp
        second_payload = payload.copy()
        second_payload["nonce"] = nonce
        second_payload["timestamp"] = timestamp

        # Wait to stay within the valid window (e.g., 2 seconds out of 10)
        time.sleep(2)

        # Second request with identical nonce and timestamp
        second_response = requests.post(f"{BASE_URL}/send-secure-email", json=second_payload)

        # If the server implemented replay detection, it should return a 550 or similar error.
        self.assertNotEqual(second_response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
