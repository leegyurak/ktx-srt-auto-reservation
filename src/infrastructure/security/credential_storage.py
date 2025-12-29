"""Secure credential storage using SQLite with AES-256-CBC encryption"""
from src.infrastructure.security.dto import LoginCredentials, PaymentCredentials
from src.infrastructure.security.encryption import EncryptionService
from src.infrastructure.database.session import DatabaseManager
from src.domain.repositories.credential_repository import IUserRepository, ICardRepository


class CredentialStorage:
    """
    SQLite-based secure credential storage with AES-256-CBC encryption

    All sensitive data is encrypted using AES-256-CBC with a key derived from the MAC address.
    Data is stored in SQLite database at ~/.ktx-srt-macro/credentials.db

    This class follows Clean Architecture principles:
    - Depends on domain interfaces (IUserRepository, ICardRepository)
    - Infrastructure implementations are injected via constructor
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        card_repository: ICardRepository
    ) -> None:
        """
        Initialize credential storage with repository dependencies

        Args:
            user_repository: Implementation of IUserRepository
            card_repository: Implementation of ICardRepository
        """
        self._user_repo = user_repository
        self._card_repo = card_repository
        # Ensure database is initialized when instance is created
        DatabaseManager.initialize()

    # KTX Login Credentials
    def save_ktx_login(self, username: str, password: str) -> None:
        """Save KTX login credentials (encrypted)"""
        # Encrypt credentials
        encrypted_username = EncryptionService.encrypt(username)
        encrypted_password = EncryptionService.encrypt(password)

        # Save using repository
        self._user_repo.save(
            username=encrypted_username,
            password=encrypted_password,
            train_type="KORAIL"
        )

    def load_ktx_login(self) -> LoginCredentials | None:
        """Load KTX login credentials (decrypted)"""
        try:
            # Load using repository
            user = self._user_repo.find_by_train_type("KORAIL")

            if user:
                # Decrypt credentials
                username = EncryptionService.decrypt(user.username)
                password = EncryptionService.decrypt(user.password)

                if username and password:
                    return LoginCredentials(username=username, password=password)
                else:
                    # Decryption failed - delete corrupted data
                    self._user_repo.delete("KORAIL")

            return None
        except Exception:
            # If any error occurs, delete corrupted data and return None
            try:
                self._user_repo.delete("KORAIL")
            except Exception:
                pass
            return None

    def delete_ktx_login(self) -> None:
        """Delete KTX login credentials"""
        self._user_repo.delete("KORAIL")

    # SRT Login Credentials
    def save_srt_login(self, username: str, password: str) -> None:
        """Save SRT login credentials (encrypted)"""
        # Encrypt credentials
        encrypted_username = EncryptionService.encrypt(username)
        encrypted_password = EncryptionService.encrypt(password)

        # Save using repository
        self._user_repo.save(
            username=encrypted_username,
            password=encrypted_password,
            train_type="SRT"
        )

    def load_srt_login(self) -> LoginCredentials | None:
        """Load SRT login credentials (decrypted)"""
        # Load using repository
        user = self._user_repo.find_by_train_type("SRT")

        if user:
            # Decrypt credentials
            username = EncryptionService.decrypt(user.username)
            password = EncryptionService.decrypt(user.password)

            if username and password:
                return LoginCredentials(username=username, password=password)

        return None

    def delete_srt_login(self) -> None:
        """Delete SRT login credentials"""
        self._user_repo.delete("SRT")

    # Payment Credentials
    def save_payment(
        self,
        card_number: str,
        card_password: str,
        expire: str,
        validation_number: str,
        is_corporate: bool,
        train_type: str = "KORAIL"
    ) -> None:
        """
        Save payment credentials (encrypted)

        Args:
            card_number: Card number (16 digits)
            card_password: Card password (2 digits)
            expire: Card expiration date (YYMM format)
            validation_number: Birth date (YYMMDD) or business number (10 digits)
            is_corporate: Whether it's a corporate card
            train_type: "KORAIL" or "SRT" (default: "KORAIL")
        """
        # Encrypt credentials
        encrypted_card_number = EncryptionService.encrypt(card_number)
        encrypted_card_password = EncryptionService.encrypt(card_password)
        encrypted_expire = EncryptionService.encrypt(expire)
        encrypted_validation = EncryptionService.encrypt(validation_number)

        # Save using repository
        self._card_repo.save(
            card_number=encrypted_card_number,
            card_password=encrypted_card_password,
            card_expired_date=encrypted_expire,
            card_validate_number=encrypted_validation,
            is_corporate=is_corporate,
            train_type=train_type
        )

    def load_payment(self, train_type: str = "KORAIL") -> PaymentCredentials | None:
        """
        Load payment credentials (decrypted)

        Args:
            train_type: "KORAIL" or "SRT" (default: "KORAIL")

        Returns:
            PaymentCredentials if found, None otherwise
        """
        # Load using repository
        card = self._card_repo.find_by_train_type(train_type)

        if card:
            # Decrypt credentials
            card_number = EncryptionService.decrypt(card.card_number)
            card_password = EncryptionService.decrypt(card.card_password)
            expire = EncryptionService.decrypt(card.card_expired_date)
            validation_number = EncryptionService.decrypt(card.card_validate_number)

            if all([card_number, card_password, expire, validation_number]):
                return PaymentCredentials(
                    card_number=card_number,
                    card_password=card_password,
                    expire=expire,
                    validation_number=validation_number,
                    is_corporate=card.is_corporate
                )

        return None

    def delete_payment(self, train_type: str = "KORAIL") -> None:
        """
        Delete payment credentials

        Args:
            train_type: "KORAIL" or "SRT" (default: "KORAIL")
        """
        self._card_repo.delete(train_type)
