"""Secure credential storage using platform-specific keychains"""
import keyring
from typing import Optional

from src.infrastructure.security.dto import LoginCredentials, PaymentCredentials


class CredentialStorage:
    """
    Platform-specific secure credential storage

    Uses:
    - macOS: Keychain
    - Windows: Windows Credential Locker
    - Linux: Secret Service API (freedesktop.org)
    """

    SERVICE_NAME = "KTX-SRT-Macro"

    # Key names for different credential types
    KEY_KTX_USERNAME = "ktx_username"
    KEY_KTX_PASSWORD = "ktx_password"
    KEY_SRT_USERNAME = "srt_username"
    KEY_SRT_PASSWORD = "srt_password"

    # Payment credentials (shared between KTX and SRT)
    KEY_CARD_NUMBER = "card_number"
    KEY_CARD_PASSWORD = "card_password"
    KEY_CARD_EXPIRE = "card_expire"
    KEY_CARD_VALIDATION = "card_validation"
    KEY_CARD_CORPORATE = "card_corporate"

    @staticmethod
    def _set_credential(key: str, value: str) -> None:
        """Store credential securely"""
        keyring.set_password(CredentialStorage.SERVICE_NAME, key, value)

    @staticmethod
    def _get_credential(key: str) -> Optional[str]:
        """Retrieve credential securely"""
        return keyring.get_password(CredentialStorage.SERVICE_NAME, key)

    @staticmethod
    def _delete_credential(key: str) -> None:
        """Delete credential"""
        try:
            keyring.delete_password(CredentialStorage.SERVICE_NAME, key)
        except keyring.errors.PasswordDeleteError:
            pass  # Credential doesn't exist

    # KTX Login Credentials
    @staticmethod
    def save_ktx_login(username: str, password: str) -> None:
        """Save KTX login credentials"""
        CredentialStorage._set_credential(CredentialStorage.KEY_KTX_USERNAME, username)
        CredentialStorage._set_credential(CredentialStorage.KEY_KTX_PASSWORD, password)

    @staticmethod
    def load_ktx_login() -> Optional[LoginCredentials]:
        """Load KTX login credentials"""
        username = CredentialStorage._get_credential(CredentialStorage.KEY_KTX_USERNAME)
        password = CredentialStorage._get_credential(CredentialStorage.KEY_KTX_PASSWORD)

        if username and password:
            return LoginCredentials(username=username, password=password)
        return None

    @staticmethod
    def delete_ktx_login() -> None:
        """Delete KTX login credentials"""
        CredentialStorage._delete_credential(CredentialStorage.KEY_KTX_USERNAME)
        CredentialStorage._delete_credential(CredentialStorage.KEY_KTX_PASSWORD)

    # SRT Login Credentials
    @staticmethod
    def save_srt_login(username: str, password: str) -> None:
        """Save SRT login credentials"""
        CredentialStorage._set_credential(CredentialStorage.KEY_SRT_USERNAME, username)
        CredentialStorage._set_credential(CredentialStorage.KEY_SRT_PASSWORD, password)

    @staticmethod
    def load_srt_login() -> Optional[LoginCredentials]:
        """Load SRT login credentials"""
        username = CredentialStorage._get_credential(CredentialStorage.KEY_SRT_USERNAME)
        password = CredentialStorage._get_credential(CredentialStorage.KEY_SRT_PASSWORD)

        if username and password:
            return LoginCredentials(username=username, password=password)
        return None

    @staticmethod
    def delete_srt_login() -> None:
        """Delete SRT login credentials"""
        CredentialStorage._delete_credential(CredentialStorage.KEY_SRT_USERNAME)
        CredentialStorage._delete_credential(CredentialStorage.KEY_SRT_PASSWORD)

    # Payment Credentials (shared between KTX and SRT)
    @staticmethod
    def save_payment(
        card_number: str,
        card_password: str,
        expire: str,
        validation_number: str,
        is_corporate: bool
    ) -> None:
        """Save payment credentials"""
        CredentialStorage._set_credential(CredentialStorage.KEY_CARD_NUMBER, card_number)
        CredentialStorage._set_credential(CredentialStorage.KEY_CARD_PASSWORD, card_password)
        CredentialStorage._set_credential(CredentialStorage.KEY_CARD_EXPIRE, expire)
        CredentialStorage._set_credential(CredentialStorage.KEY_CARD_VALIDATION, validation_number)
        CredentialStorage._set_credential(CredentialStorage.KEY_CARD_CORPORATE, str(is_corporate))

    @staticmethod
    def load_payment() -> Optional[PaymentCredentials]:
        """Load payment credentials"""
        card_number = CredentialStorage._get_credential(CredentialStorage.KEY_CARD_NUMBER)
        card_password = CredentialStorage._get_credential(CredentialStorage.KEY_CARD_PASSWORD)
        expire = CredentialStorage._get_credential(CredentialStorage.KEY_CARD_EXPIRE)
        validation_number = CredentialStorage._get_credential(CredentialStorage.KEY_CARD_VALIDATION)
        is_corporate_str = CredentialStorage._get_credential(CredentialStorage.KEY_CARD_CORPORATE)

        if all([card_number, card_password, expire, validation_number, is_corporate_str]):
            return PaymentCredentials(
                card_number=card_number,
                card_password=card_password,
                expire=expire,
                validation_number=validation_number,
                is_corporate=(is_corporate_str == "True")
            )
        return None

    @staticmethod
    def delete_payment() -> None:
        """Delete payment credentials"""
        CredentialStorage._delete_credential(CredentialStorage.KEY_CARD_NUMBER)
        CredentialStorage._delete_credential(CredentialStorage.KEY_CARD_PASSWORD)
        CredentialStorage._delete_credential(CredentialStorage.KEY_CARD_EXPIRE)
        CredentialStorage._delete_credential(CredentialStorage.KEY_CARD_VALIDATION)
        CredentialStorage._delete_credential(CredentialStorage.KEY_CARD_CORPORATE)
