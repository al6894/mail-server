import time
import uuid

def create_email_header():
    timestamp = int(time.time())
    nonce = str(uuid.uuid4())
    return {"timestamp": timestamp, "nonce": nonce}

def validate_replay(header, received_nonces):
    current_time = int(time.time())
    timestamp, nonce = header["timestamp"], header["nonce"]

    if nonce in received_nonces:
        return False  # Replay detected

    # Update condition to reject messages exactly 300 seconds old or more
    if current_time - timestamp >= 300:  # Expired if 300 seconds or more
        return False  # Expired message

    received_nonces.add(nonce)
    return True