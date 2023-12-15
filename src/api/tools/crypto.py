import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.config import settings


class Crypto:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=settings.CRYPTO_SALT,
        iterations=480000,
    )

    cipher_suite = Fernet(
        base64.urlsafe_b64encode(kdf.derive(settings.CRYPTO_PASSWORD))
    )

    @classmethod
    def encrypt(cls, phone_number: str):
        encrypted_phone_number = cls.cipher_suite.encrypt(phone_number.encode())
        return encrypted_phone_number

    @classmethod
    def decrypt(cls, encrypted_phone_number: bytes):
        decrypted_phone_number = cls.cipher_suite.decrypt(encrypted_phone_number)
        return decrypted_phone_number
