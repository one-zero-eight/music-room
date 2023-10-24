from cryptography.fernet import Fernet

from src.config import settings


class Crypto:
    secret_key = settings.CRYPTO_SECRET_KEY
    cipher_suite = Fernet(secret_key)

    @classmethod
    def encrypt(cls, phone_number: str):
        encrypted_phone_number = cls.cipher_suite.encrypt(phone_number.encode())
        return encrypted_phone_number

    @classmethod
    def decrypt(cls, encrypted_phone_number: bytes):
        decrypted_phone_number = cls.cipher_suite.decrypt(encrypted_phone_number)
        return decrypted_phone_number
