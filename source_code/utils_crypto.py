from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    return private_key, private_key.public_key()

def serialize_public_key(pub):
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize_public_key(pem):
    return serialization.load_pem_public_key(pem)

def encrypt_key(pub, session_key):
    return pub.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_session_key(priv, encrypted_key):
    return priv.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def generate_session_key():
    return Fernet.generate_key()

def encrypt_message(session_key, message: str) -> bytes:
    return Fernet(session_key).encrypt(message.encode())

def decrypt_message(session_key, ciphertext: bytes) -> str:
    return Fernet(session_key).decrypt(ciphertext).decode()