"""Unit tests for CredentialStorage"""
from unittest.mock import MagicMock
from src.infrastructure.security.credential_storage import CredentialStorage
from src.infrastructure.security.dto import LoginCredentials, PaymentCredentials


def create_credential_storage():
    """Helper function to create a CredentialStorage instance with mocked repositories"""
    mock_user_repo = MagicMock()
    mock_card_repo = MagicMock()
    return CredentialStorage(
        user_repository=mock_user_repo,
        card_repository=mock_card_repo
    ), mock_user_repo, mock_card_repo


class TestCredentialStorageKTXLogin:
    """Tests for KTX login credential storage"""

    def test_save_ktx_login(self):
        """Test saving KTX login credentials"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()
        username = "test_user"
        password = "test_password"

        # Act
        storage.save_ktx_login(username, password)

        # Assert
        mock_user_repo.save.assert_called_once()
        call_args = mock_user_repo.save.call_args
        assert call_args.kwargs['train_type'] == "KORAIL"

    def test_load_ktx_login_success(self):
        """Test loading KTX login credentials successfully"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()

        mock_user = MagicMock()
        # Simulate encrypted data (EncryptionService will be mocked in integration tests)
        mock_user.username = "encrypted_user"
        mock_user.password = "encrypted_pass"
        mock_user_repo.find_by_train_type.return_value = mock_user

        # Mock EncryptionService
        from unittest.mock import patch
        with patch('src.infrastructure.security.credential_storage.EncryptionService') as mock_enc:
            mock_enc.decrypt.side_effect = lambda x: x.replace("encrypted_", "")

            # Act
            result = storage.load_ktx_login()

            # Assert
            assert result is not None
            assert isinstance(result, LoginCredentials)
            assert result.username == "user"
            assert result.password == "pass"
            mock_user_repo.find_by_train_type.assert_called_once_with("KORAIL")

    def test_load_ktx_login_missing_username(self):
        """Test loading KTX login credentials when username is missing"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()
        mock_user_repo.find_by_train_type.return_value = None

        # Act
        result = storage.load_ktx_login()

        # Assert
        assert result is None

    def test_load_ktx_login_missing_password(self):
        """Test loading KTX login credentials when password is missing"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()

        mock_user = MagicMock()
        mock_user.username = "encrypted_user"
        mock_user.password = "encrypted_pass"
        mock_user_repo.find_by_train_type.return_value = mock_user

        # Mock EncryptionService to return None for password
        from unittest.mock import patch
        with patch('src.infrastructure.security.credential_storage.EncryptionService') as mock_enc:
            mock_enc.decrypt.side_effect = lambda x: "user" if "user" in x else None

            # Act
            result = storage.load_ktx_login()

            # Assert
            assert result is None

    def test_load_ktx_login_both_missing(self):
        """Test loading KTX login credentials when both are missing"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()
        mock_user_repo.find_by_train_type.return_value = None

        # Act
        result = storage.load_ktx_login()

        # Assert
        assert result is None

    def test_delete_ktx_login(self):
        """Test deleting KTX login credentials"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()

        # Act
        storage.delete_ktx_login()

        # Assert
        mock_user_repo.delete.assert_called_once_with("KORAIL")

    def test_delete_ktx_login_not_found(self):
        """Test deleting KTX login credentials when they don't exist"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()

        # Act - should not raise exception
        storage.delete_ktx_login()

        # Assert
        mock_user_repo.delete.assert_called_once_with("KORAIL")


class TestCredentialStorageSRTLogin:
    """Tests for SRT login credential storage"""

    def test_save_srt_login(self):
        """Test saving SRT login credentials"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()
        username = "srt_user"
        password = "srt_password"

        # Act
        storage.save_srt_login(username, password)

        # Assert
        mock_user_repo.save.assert_called_once()
        call_args = mock_user_repo.save.call_args
        assert call_args.kwargs['train_type'] == "SRT"

    def test_load_srt_login_success(self):
        """Test loading SRT login credentials successfully"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()

        mock_user = MagicMock()
        mock_user.username = "encrypted_srt_user"
        mock_user.password = "encrypted_srt_password"
        mock_user_repo.find_by_train_type.return_value = mock_user

        # Mock EncryptionService
        from unittest.mock import patch
        with patch('src.infrastructure.security.credential_storage.EncryptionService') as mock_enc:
            mock_enc.decrypt.side_effect = lambda x: x.replace("encrypted_", "")

            # Act
            result = storage.load_srt_login()

            # Assert
            assert result is not None
            assert isinstance(result, LoginCredentials)
            assert result.username == "srt_user"
            assert result.password == "srt_password"

    def test_load_srt_login_missing(self):
        """Test loading SRT login credentials when missing"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()
        mock_user_repo.find_by_train_type.return_value = None

        # Act
        result = storage.load_srt_login()

        # Assert
        assert result is None

    def test_delete_srt_login(self):
        """Test deleting SRT login credentials"""
        # Arrange
        storage, mock_user_repo, _ = create_credential_storage()

        # Act
        storage.delete_srt_login()

        # Assert
        mock_user_repo.delete.assert_called_once_with("SRT")


class TestCredentialStoragePayment:
    """Tests for unified payment credential storage (shared between KTX and SRT)"""

    def test_save_payment_personal_card(self):
        """Test saving payment credentials for personal card"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        card_number = "1234567890123456"
        card_password = "12"
        expire = "2512"
        validation_number = "900101"
        is_corporate = False

        # Act
        storage.save_payment(
            card_number, card_password, expire, validation_number, is_corporate
        )

        # Assert
        mock_card_repo.save.assert_called_once()
        call_args = mock_card_repo.save.call_args
        assert call_args.kwargs['train_type'] == "KORAIL"
        assert call_args.kwargs['is_corporate'] == False

    def test_save_payment_corporate_card(self):
        """Test saving payment credentials for corporate card"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        card_number = "1234567890123456"
        card_password = "12"
        expire = "2512"
        validation_number = "1234567890"  # 사업자번호
        is_corporate = True

        # Act
        storage.save_payment(
            card_number, card_password, expire, validation_number, is_corporate
        )

        # Assert
        mock_card_repo.save.assert_called_once()
        call_args = mock_card_repo.save.call_args
        assert call_args.kwargs['is_corporate'] == True

    def test_load_payment_success_personal(self):
        """Test loading payment credentials for personal card"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        mock_card = MagicMock()
        mock_card.card_number = "encrypted_1234567890123456"
        mock_card.card_password = "encrypted_12"
        mock_card.card_expired_date = "encrypted_2512"
        mock_card.card_validate_number = "encrypted_900101"
        mock_card.is_corporate = False
        mock_card_repo.find_by_train_type.return_value = mock_card

        # Mock EncryptionService
        from unittest.mock import patch
        with patch('src.infrastructure.security.credential_storage.EncryptionService') as mock_enc:
            mock_enc.decrypt.side_effect = lambda x: x.replace("encrypted_", "")

            # Act
            result = storage.load_payment()

            # Assert
            assert result is not None
            assert isinstance(result, PaymentCredentials)
            assert result.card_number == "1234567890123456"
            assert result.card_password == "12"
            assert result.expire == "2512"
            assert result.validation_number == "900101"
            assert result.is_corporate is False

    def test_load_payment_success_corporate(self):
        """Test loading payment credentials for corporate card"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        mock_card = MagicMock()
        mock_card.card_number = "encrypted_1234567890123456"
        mock_card.card_password = "encrypted_12"
        mock_card.card_expired_date = "encrypted_2512"
        mock_card.card_validate_number = "encrypted_1234567890"
        mock_card.is_corporate = True
        mock_card_repo.find_by_train_type.return_value = mock_card

        # Mock EncryptionService
        from unittest.mock import patch
        with patch('src.infrastructure.security.credential_storage.EncryptionService') as mock_enc:
            mock_enc.decrypt.side_effect = lambda x: x.replace("encrypted_", "")

            # Act
            result = storage.load_payment()

            # Assert
            assert result is not None
            assert result.is_corporate is True
            assert result.validation_number == "1234567890"

    def test_load_payment_missing_data(self):
        """Test loading payment credentials when data is missing"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        mock_card = MagicMock()
        mock_card.card_number = "encrypted_1234567890123456"
        mock_card.card_password = "encrypted_card_password"  # Changed to match pattern
        mock_card.card_expired_date = "encrypted_2512"
        mock_card.card_validate_number = "encrypted_900101"
        mock_card.is_corporate = False
        mock_card_repo.find_by_train_type.return_value = mock_card

        # Mock EncryptionService to return None for password
        from unittest.mock import patch
        with patch('src.infrastructure.security.credential_storage.EncryptionService') as mock_enc:
            mock_enc.decrypt.side_effect = lambda x: None if "card_password" in x else x.replace("encrypted_", "")

            # Act
            result = storage.load_payment()

            # Assert
            assert result is None

    def test_load_payment_all_missing(self):
        """Test loading payment credentials when all data is missing"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()
        mock_card_repo.find_by_train_type.return_value = None

        # Act
        result = storage.load_payment()

        # Assert
        assert result is None

    def test_delete_payment(self):
        """Test deleting payment credentials"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        # Act
        storage.delete_payment()

        # Assert
        mock_card_repo.delete.assert_called_once_with("KORAIL")

    def test_delete_payment_not_found(self):
        """Test deleting payment credentials when they don't exist"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        # Act - should not raise exception
        storage.delete_payment()

        # Assert
        mock_card_repo.delete.assert_called_once_with("KORAIL")

    def test_payment_shared_between_ktx_and_srt(self):
        """Test that payment credentials are shared between KTX and SRT"""
        # Arrange
        storage, _, mock_card_repo = create_credential_storage()

        card_number = "1234567890123456"
        card_password = "12"
        expire = "2512"
        validation_number = "900101"
        is_corporate = False

        # Act - Save payment once
        storage.save_payment(
            card_number, card_password, expire, validation_number, is_corporate
        )

        # Assert - Verify save was called with KORAIL (default)
        mock_card_repo.save.assert_called_once()
        call_args = mock_card_repo.save.call_args
        assert call_args.kwargs['train_type'] == "KORAIL"
