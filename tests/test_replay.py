from replay_protection import create_email_header, validate_replay
from unittest.mock import patch

def test_replay_protection_without_wait():
    # Create headers with mocked timestamps
    with patch("time.time") as mock_time:
        mock_time.return_value = 1000000  # Simulated start time
        header1 = create_email_header()

        mock_time.return_value = 1000001  # Slightly later for a new header
        header2 = create_email_header()

        received_nonces = set()

        # Validate first header (should pass)
        assert validate_replay(header1, received_nonces) == True

        # Reuse the same header (should fail due to replay)
        assert validate_replay(header1, received_nonces) == False

        # Simulate 301 seconds later
        mock_time.return_value = 1000301  # 301 seconds past the first header
        assert validate_replay(header2, received_nonces) == False  # Expired
