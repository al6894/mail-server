import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA256
from crypto_utils import encrypt_email, decrypt_email, sign_email, verify_signature

def generate_rsa_keys():
    """Helper function to generate RSA keys for testing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem, public_key_pem

def test_encrypt_decrypt_email():
    """Test encryption and decryption of email content."""
    content = "This is a test email."
    symmetric_key = os.urandom(32)

    # Encrypt the content
    nonce, ciphertext, tag = encrypt_email(content, symmetric_key)

    # Decrypt the content
    plaintext = decrypt_email(ciphertext, nonce, tag, symmetric_key)

    # Verify the decryption result
    assert plaintext.decode() == content

def test_sign_verify_email():
    """Test signing and verification of email content."""
    content = "This is a test email."
    private_key_pem, public_key_pem = generate_rsa_keys()

    # Save the keys to temporary files
    with open("private_key.pem", "wb") as f:
        f.write(private_key_pem)
    with open("public_key.pem", "wb") as f:
        f.write(public_key_pem)

    # Sign the content
    signature = sign_email(content, "private_key.pem")

    # Verify the signature
    is_valid = verify_signature(content, signature, "public_key.pem")

    # Clean up temporary files
    os.remove("private_key.pem")
    os.remove("public_key.pem")

    # Verify the result
    assert is_valid

def test_invalid_signature():
    """Test verification failure with an invalid signature."""
    content = "This is a test email."
    private_key_pem, public_key_pem = generate_rsa_keys()

    # Save the keys to temporary files
    with open("private_key.pem", "wb") as f:
        f.write(private_key_pem)
    with open("public_key.pem", "wb") as f:
        f.write(public_key_pem)

    # Sign the content
    signature = sign_email(content, "private_key.pem")

    # Tamper with the content
    tampered_content = "This is a tampered email."

    # Verify the tampered content with the original signature
    is_valid = verify_signature(tampered_content, signature, "public_key.pem")

    # Clean up temporary files
    os.remove("private_key.pem")
    os.remove("public_key.pem")

    # Verify the result
    assert not is_valid
