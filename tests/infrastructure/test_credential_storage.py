"""Tests for credential storage"""
import pytest
from pathlib import Path

from src.infrastructure.security.credential_storage import CredentialStorage
from src.infrastructure.database.session import DatabaseManager
from src.infrastructure.database.repository import SQLAlchemyUserRepository, SQLAlchemyCardRepository


@pytest.fixture
def credential_storage() -> CredentialStorage:
    """Fixture that provides a CredentialStorage instance with test database"""
    # Use a test database
    original_get_db_path = DatabaseManager.get_db_path

    def test_db_path() -> Path:
        return Path("/tmp/test_credentials_storage.db")

    DatabaseManager.get_db_path = test_db_path
    DatabaseManager._engine = None
    DatabaseManager._session_factory = None
    DatabaseManager.initialize()
    DatabaseManager.reset_database()

    # Create storage instance with test repositories
    storage = CredentialStorage(
        user_repository=SQLAlchemyUserRepository(),
        card_repository=SQLAlchemyCardRepository()
    )

    yield storage

    # Cleanup
    DatabaseManager.get_db_path = original_get_db_path
    test_db = Path("/tmp/test_credentials_storage.db")
    if test_db.exists():
        test_db.unlink()


class TestKTXLoginCredentials:
    """Test cases for KTX login credentials"""

    def test_save_and_load_ktx_login(self, credential_storage: CredentialStorage) -> None:
        """Test saving and loading KTX login credentials"""
        # Save
        credential_storage.save_ktx_login("ktx_user", "ktx_password123")

        # Load
        creds = credential_storage.load_ktx_login()

        assert creds is not None
        assert creds.username == "ktx_user"
        assert creds.password == "ktx_password123"

    def test_update_ktx_login(self, credential_storage: CredentialStorage) -> None:
        """Test updating KTX login credentials"""
        # Save initial
        credential_storage.save_ktx_login("old_user", "old_pass")

        # Update
        credential_storage.save_ktx_login("new_user", "new_pass")

        # Load
        creds = credential_storage.load_ktx_login()

        assert creds is not None
        assert creds.username == "new_user"
        assert creds.password == "new_pass"

    def test_delete_ktx_login(self, credential_storage: CredentialStorage) -> None:
        """Test deleting KTX login credentials"""
        # Save
        credential_storage.save_ktx_login("user", "pass")

        # Delete
        credential_storage.delete_ktx_login()

        # Load should return None
        creds = credential_storage.load_ktx_login()

        assert creds is None

    def test_load_non_existent_ktx_login(self, credential_storage: CredentialStorage) -> None:
        """Test loading non-existent KTX login returns None"""
        creds = credential_storage.load_ktx_login()

        assert creds is None

    def test_ktx_login_encryption(self, credential_storage: CredentialStorage) -> None:
        """Test that KTX login credentials are encrypted"""
        # Save
        credential_storage.save_ktx_login("plaintext_user", "plaintext_pass")

        # Load from repository directly to check encryption
        from src.infrastructure.database.repository import SQLAlchemyUserRepository

        user_repo = SQLAlchemyUserRepository()
        user = user_repo.find_by_train_type("KORAIL")

        assert user is not None
        # Should be encrypted (not equal to plaintext)
        assert user.username != "plaintext_user"
        assert user.password != "plaintext_pass"
        # Should be base64 encoded strings
        assert len(user.username) > len("plaintext_user")
        assert len(user.password) > len("plaintext_pass")


class TestSRTLoginCredentials:
    """Test cases for SRT login credentials"""

    def test_save_and_load_srt_login(self, credential_storage: CredentialStorage) -> None:
        """Test saving and loading SRT login credentials"""
        # Save
        credential_storage.save_srt_login("srt_user", "srt_password123")

        # Load
        creds = credential_storage.load_srt_login()

        assert creds is not None
        assert creds.username == "srt_user"
        assert creds.password == "srt_password123"

    def test_update_srt_login(self, credential_storage: CredentialStorage) -> None:
        """Test updating SRT login credentials"""
        # Save initial
        credential_storage.save_srt_login("old_user", "old_pass")

        # Update
        credential_storage.save_srt_login("new_user", "new_pass")

        # Load
        creds = credential_storage.load_srt_login()

        assert creds is not None
        assert creds.username == "new_user"
        assert creds.password == "new_pass"

    def test_delete_srt_login(self, credential_storage: CredentialStorage) -> None:
        """Test deleting SRT login credentials"""
        # Save
        credential_storage.save_srt_login("user", "pass")

        # Delete
        credential_storage.delete_srt_login()

        # Load should return None
        creds = credential_storage.load_srt_login()

        assert creds is None

    def test_load_non_existent_srt_login(self, credential_storage: CredentialStorage) -> None:
        """Test loading non-existent SRT login returns None"""
        creds = credential_storage.load_srt_login()

        assert creds is None


class TestPaymentCredentials:
    """Test cases for payment credentials"""

    def test_save_and_load_korail_payment(self, credential_storage: CredentialStorage) -> None:
        """Test saving and loading KORAIL payment credentials"""
        # Save
        credential_storage.save_payment(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Load
        payment = credential_storage.load_payment("KORAIL")

        assert payment is not None
        assert payment.card_number == "1234567890123456"
        assert payment.card_password == "12"
        assert payment.expire == "2512"
        assert payment.validation_number == "900101"
        assert payment.is_corporate is False

    def test_save_and_load_srt_payment(self, credential_storage: CredentialStorage) -> None:
        """Test saving and loading SRT payment credentials"""
        # Save
        credential_storage.save_payment(
            card_number="9876543210987654",
            card_password="99",
            expire="2612",
            validation_number="1234567890",
            is_corporate=True,
            train_type="SRT"
        )

        # Load
        payment = credential_storage.load_payment("SRT")

        assert payment is not None
        assert payment.card_number == "9876543210987654"
        assert payment.card_password == "99"
        assert payment.expire == "2612"
        assert payment.validation_number == "1234567890"
        assert payment.is_corporate is True

    def test_separate_payment_for_korail_and_srt(self, credential_storage: CredentialStorage) -> None:
        """Test that KORAIL and SRT payment credentials are stored separately"""
        # Save KORAIL payment
        credential_storage.save_payment(
            card_number="1111111111111111",
            card_password="11",
            expire="2511",
            validation_number="111111",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Save SRT payment
        credential_storage.save_payment(
            card_number="2222222222222222",
            card_password="22",
            expire="2522",
            validation_number="222222",
            is_corporate=True,
            train_type="SRT"
        )

        # Load both
        korail_payment = credential_storage.load_payment("KORAIL")
        srt_payment = credential_storage.load_payment("SRT")

        # Both should exist
        assert korail_payment is not None
        assert srt_payment is not None

        # Should have different values
        assert korail_payment.card_number == "1111111111111111"
        assert srt_payment.card_number == "2222222222222222"
        assert korail_payment.is_corporate is False
        assert srt_payment.is_corporate is True

    def test_update_payment(self, credential_storage: CredentialStorage) -> None:
        """Test updating payment credentials"""
        # Save initial
        credential_storage.save_payment(
            card_number="1111111111111111",
            card_password="11",
            expire="2511",
            validation_number="111111",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Update
        credential_storage.save_payment(
            card_number="9999999999999999",
            card_password="99",
            expire="2599",
            validation_number="999999",
            is_corporate=True,
            train_type="KORAIL"
        )

        # Load
        payment = credential_storage.load_payment("KORAIL")

        assert payment is not None
        assert payment.card_number == "9999999999999999"
        assert payment.card_password == "99"
        assert payment.is_corporate is True

    def test_delete_korail_payment(self, credential_storage: CredentialStorage) -> None:
        """Test deleting KORAIL payment credentials"""
        # Save
        credential_storage.save_payment(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Delete
        credential_storage.delete_payment("KORAIL")

        # Load should return None
        payment = credential_storage.load_payment("KORAIL")

        assert payment is None

    def test_delete_srt_payment(self, credential_storage: CredentialStorage) -> None:
        """Test deleting SRT payment credentials"""
        # Save
        credential_storage.save_payment(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False,
            train_type="SRT"
        )

        # Delete
        credential_storage.delete_payment("SRT")

        # Load should return None
        payment = credential_storage.load_payment("SRT")

        assert payment is None

    def test_load_non_existent_payment(self, credential_storage: CredentialStorage) -> None:
        """Test loading non-existent payment returns None"""
        payment = credential_storage.load_payment("KORAIL")

        assert payment is None

    def test_payment_encryption(self, credential_storage: CredentialStorage) -> None:
        """Test that payment credentials are encrypted"""
        # Save
        credential_storage.save_payment(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Load from repository directly to check encryption
        from src.infrastructure.database.repository import SQLAlchemyCardRepository

        card_repo = SQLAlchemyCardRepository()
        card = card_repo.find_by_train_type("KORAIL")

        assert card is not None
        # Should be encrypted (not equal to plaintext)
        assert card.card_number != "1234567890123456"
        assert card.card_password != "12"
        assert card.card_expired_date != "2512"
        assert card.card_validate_number != "900101"


class TestCredentialStorageIntegration:
    """Integration tests for credential storage"""

    def test_full_workflow_ktx(self, credential_storage: CredentialStorage) -> None:
        """Test full KTX workflow: save login, save payment, load both"""
        # Save login
        credential_storage.save_ktx_login("ktx_user", "ktx_pass")

        # Save payment
        credential_storage.save_payment(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Load both
        login = credential_storage.load_ktx_login()
        payment = credential_storage.load_payment("KORAIL")

        assert login is not None
        assert payment is not None
        assert login.username == "ktx_user"
        assert payment.card_number == "1234567890123456"

    def test_full_workflow_srt(self, credential_storage: CredentialStorage) -> None:
        """Test full SRT workflow: save login, save payment, load both"""
        # Save login
        credential_storage.save_srt_login("srt_user", "srt_pass")

        # Save payment
        credential_storage.save_payment(
            card_number="9876543210987654",
            card_password="99",
            expire="2612",
            validation_number="1234567890",
            is_corporate=True,
            train_type="SRT"
        )

        # Load both
        login = credential_storage.load_srt_login()
        payment = credential_storage.load_payment("SRT")

        assert login is not None
        assert payment is not None
        assert login.username == "srt_user"
        assert payment.card_number == "9876543210987654"

    def test_independence_of_ktx_and_srt(self, credential_storage: CredentialStorage) -> None:
        """Test that KTX and SRT credentials are completely independent"""
        # Save KTX credentials
        credential_storage.save_ktx_login("ktx_user", "ktx_pass")
        credential_storage.save_payment(
            card_number="1111111111111111",
            card_password="11",
            expire="2511",
            validation_number="111111",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Save SRT credentials
        credential_storage.save_srt_login("srt_user", "srt_pass")
        credential_storage.save_payment(
            card_number="2222222222222222",
            card_password="22",
            expire="2522",
            validation_number="222222",
            is_corporate=True,
            train_type="SRT"
        )

        # All should be loadable independently
        ktx_login = credential_storage.load_ktx_login()
        ktx_payment = credential_storage.load_payment("KORAIL")
        srt_login = credential_storage.load_srt_login()
        srt_payment = credential_storage.load_payment("SRT")

        assert ktx_login is not None
        assert ktx_payment is not None
        assert srt_login is not None
        assert srt_payment is not None

        assert ktx_login.username == "ktx_user"
        assert srt_login.username == "srt_user"
        assert ktx_payment.card_number == "1111111111111111"
        assert srt_payment.card_number == "2222222222222222"
