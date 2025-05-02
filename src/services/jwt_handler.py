import base64
import binascii
import datetime
from enum import StrEnum
import hashlib
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pydantic import ValidationError

from core import settings
from models import User
from schemas import JWTAuthSchema


class JWTErrorEnum(StrEnum):
    EXPIRED = "expired"
    UNRECOGNIZED = "unrecognized"
    BROKEN = "broken"


class JWTInvalidTokenException(Exception):
    def __init__(self, token: JWTAuthSchema, cause: JWTErrorEnum):
        self.token = token
        self.cause = cause


class JWTHandler:
    def __get_cipher(self, key: bytes, iv: bytes) -> Cipher:
        if len(key) not in {16, 24, 32}:
            raise ValueError("Invalid Key")

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        return cipher

    def __encrypt(self, data: bytes, key: bytes) -> bytes:
        iv = os.urandom(16)
        cipher = self.__get_cipher(key, iv)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return iv + ciphertext

    def __decrypt(self, data: bytes, key: bytes) -> bytes:
        iv, ciphertext = data[:16], data[16:]
        cipher = self.__get_cipher(key, iv)
        unpadder = padding.PKCS7(128).unpadder()

        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
        return unpadded_data

    def __init__(self, jwt: JWTAuthSchema):
        self.__jwt = jwt

    def __calc_jwt_signature(self, encrypt_signature: bool = True) -> JWTAuthSchema:
        jwtcp = JWTAuthSchema.model_validate(
            self.__jwt.model_dump(exclude={"signature"})
        )
        token_json = jwtcp.model_dump_json(exclude="signature")
        signature = hashlib.sha256(token_json.encode()).hexdigest()
        if encrypt_signature:
            sig_key = settings.get().SIGNATURE_KEY_PATH.read_bytes()
            signature = self.__encrypt(signature.encode(), sig_key)
            signature = base64.b64encode(signature).decode()
        jwtcp.signature = signature
        return jwtcp

    def to_jwt(self) -> str:
        jwt = self.__calc_jwt_signature()
        return base64.urlsafe_b64encode(jwt.model_dump_json().encode()).decode()

    @classmethod
    def from_jwt(cls, jwt: str) -> "JWTAuthSchema":
        try:
            token_json = base64.urlsafe_b64decode(jwt.encode()).decode()
            return JWTAuthSchema.model_validate_json(token_json)
        except (binascii.Error, ValidationError, UnicodeDecodeError) as e:
            raise JWTInvalidTokenException(None, JWTErrorEnum.BROKEN) from e

    @classmethod
    def from_model_user(cls, user: User, requested_from: str) -> "JWTAuthSchema":
        """
        Creates a JWTAuthSchema instance from a User model.

        Args:
            user (User): The user model instance.
            requested_from (str): The source from which the request originated.

        Returns:
            JWTAuthSchema: A new JWTAuthSchema instance.
        """
        return JWTAuthSchema(user_id=user.id, requested_from=requested_from)

    def check(self) -> None:
        if self.__jwt.expires_at < datetime.datetime.now():
            raise JWTInvalidTokenException(self.__jwt, JWTErrorEnum.EXPIRED)
        jwtcp = self.__calc_jwt_signature(encrypt_signature=False)
        sig_key = settings.get().SIGNATURE_KEY_PATH.read_bytes()
        received_signature = base64.b64decode(self.__jwt.signature.encode())
        try:
            received_signature = self.__decrypt(received_signature, sig_key).decode()
        except ValueError as e:
            raise JWTInvalidTokenException(self.__jwt, JWTErrorEnum.BROKEN) from e
        if jwtcp.signature != received_signature:
            raise JWTInvalidTokenException(self.__jwt, JWTErrorEnum.UNRECOGNIZED)
