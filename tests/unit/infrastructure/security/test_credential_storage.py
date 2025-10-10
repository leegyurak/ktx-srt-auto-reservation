"""Unit tests for CredentialStorage"""
from unittest.mock import patch
from src.infrastructure.security.credential_storage import CredentialStorage
from src.infrastructure.security.dto import LoginCredentials, PaymentCredentials


class TestCredentialStorageConstants:
    """Tests for CredentialStorage constants"""

    def test_service_name(self):
        """Test that SERVICE_NAME is correctly defined"""
        assert CredentialStorage.SERVICE_NAME == "KTX-SRT-Macro"

    def test_key_constants_exist(self):
        """Test that all key constants are defined"""
        # Login keys
        assert hasattr(CredentialStorage, "KEY_KTX_USERNAME")
        assert hasattr(CredentialStorage, "KEY_KTX_PASSWORD")
        assert hasattr(CredentialStorage, "KEY_SRT_USERNAME")
        assert hasattr(CredentialStorage, "KEY_SRT_PASSWORD")

        # Payment keys (unified for both KTX and SRT)
        assert hasattr(CredentialStorage, "KEY_CARD_NUMBER")
        assert hasattr(CredentialStorage, "KEY_CARD_PASSWORD")
        assert hasattr(CredentialStorage, "KEY_CARD_EXPIRE")
        assert hasattr(CredentialStorage, "KEY_CARD_VALIDATION")
        assert hasattr(CredentialStorage, "KEY_CARD_CORPORATE")


@patch("src.infrastructure.security.credential_storage.keyring")
class TestCredentialStorageKTXLogin:
    """Tests for KTX login credential storage"""

    def test_save_ktx_login(self, mock_keyring):
        """Test saving KTX login credentials"""
        # Arrange
        username = "test_user"
        password = "test_password"

        # Act
        CredentialStorage.save_ktx_login(username, password)

        # Assert
        assert mock_keyring.set_password.call_count == 2
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "ktx_username", username
        )
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "ktx_password", password
        )

    def test_load_ktx_login_success(self, mock_keyring):
        """Test loading KTX login credentials successfully"""
        # Arrange
        mock_keyring.get_password.side_effect = ["test_user", "test_password"]

        # Act
        result = CredentialStorage.load_ktx_login()

        # Assert
        assert result is not None
        assert isinstance(result, LoginCredentials)
        assert result.username == "test_user"
        assert result.password == "test_password"
        assert mock_keyring.get_password.call_count == 2

    def test_load_ktx_login_missing_username(self, mock_keyring):
        """Test loading KTX login credentials when username is missing"""
        # Arrange
        mock_keyring.get_password.side_effect = [None, "test_password"]

        # Act
        result = CredentialStorage.load_ktx_login()

        # Assert
        assert result is None

    def test_load_ktx_login_missing_password(self, mock_keyring):
        """Test loading KTX login credentials when password is missing"""
        # Arrange
        mock_keyring.get_password.side_effect = ["test_user", None]

        # Act
        result = CredentialStorage.load_ktx_login()

        # Assert
        assert result is None

    def test_load_ktx_login_both_missing(self, mock_keyring):
        """Test loading KTX login credentials when both are missing"""
        # Arrange
        mock_keyring.get_password.side_effect = [None, None]

        # Act
        result = CredentialStorage.load_ktx_login()

        # Assert
        assert result is None

    def test_delete_ktx_login(self, mock_keyring):
        """Test deleting KTX login credentials"""
        # Act
        CredentialStorage.delete_ktx_login()

        # Assert
        assert mock_keyring.delete_password.call_count == 2
        mock_keyring.delete_password.assert_any_call("KTX-SRT-Macro", "ktx_username")
        mock_keyring.delete_password.assert_any_call("KTX-SRT-Macro", "ktx_password")

    def test_delete_ktx_login_not_found(self, mock_keyring):
        """Test deleting KTX login credentials when they don't exist"""
        # Arrange
        import keyring.errors
        mock_keyring.delete_password.side_effect = keyring.errors.PasswordDeleteError("Not found")
        mock_keyring.errors.PasswordDeleteError = keyring.errors.PasswordDeleteError

        # Act - should not raise exception
        CredentialStorage.delete_ktx_login()

        # Assert
        assert mock_keyring.delete_password.call_count == 2


@patch("src.infrastructure.security.credential_storage.keyring")
class TestCredentialStorageSRTLogin:
    """Tests for SRT login credential storage"""

    def test_save_srt_login(self, mock_keyring):
        """Test saving SRT login credentials"""
        # Arrange
        username = "srt_user"
        password = "srt_password"

        # Act
        CredentialStorage.save_srt_login(username, password)

        # Assert
        assert mock_keyring.set_password.call_count == 2
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "srt_username", username
        )
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "srt_password", password
        )

    def test_load_srt_login_success(self, mock_keyring):
        """Test loading SRT login credentials successfully"""
        # Arrange
        mock_keyring.get_password.side_effect = ["srt_user", "srt_password"]

        # Act
        result = CredentialStorage.load_srt_login()

        # Assert
        assert result is not None
        assert isinstance(result, LoginCredentials)
        assert result.username == "srt_user"
        assert result.password == "srt_password"

    def test_load_srt_login_missing(self, mock_keyring):
        """Test loading SRT login credentials when missing"""
        # Arrange
        mock_keyring.get_password.side_effect = [None, None]

        # Act
        result = CredentialStorage.load_srt_login()

        # Assert
        assert result is None

    def test_delete_srt_login(self, mock_keyring):
        """Test deleting SRT login credentials"""
        # Act
        CredentialStorage.delete_srt_login()

        # Assert
        assert mock_keyring.delete_password.call_count == 2


@patch("src.infrastructure.security.credential_storage.keyring")
class TestCredentialStoragePayment:
    """Tests for unified payment credential storage (shared between KTX and SRT)"""

    def test_save_payment_personal_card(self, mock_keyring):
        """Test saving payment credentials for personal card"""
        # Arrange
        card_number = "1234567890123456"
        card_password = "12"
        expire = "2512"
        validation_number = "900101"
        is_corporate = False

        # Act
        CredentialStorage.save_payment(
            card_number, card_password, expire, validation_number, is_corporate
        )

        # Assert
        assert mock_keyring.set_password.call_count == 5
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "card_number", card_number
        )
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "card_password", card_password
        )
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "card_expire", expire
        )
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "card_validation", validation_number
        )
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "card_corporate", "False"
        )

    def test_save_payment_corporate_card(self, mock_keyring):
        """Test saving payment credentials for corporate card"""
        # Arrange
        card_number = "1234567890123456"
        card_password = "12"
        expire = "2512"
        validation_number = "1234567890"  # 사업자번호
        is_corporate = True

        # Act
        CredentialStorage.save_payment(
            card_number, card_password, expire, validation_number, is_corporate
        )

        # Assert
        mock_keyring.set_password.assert_any_call(
            "KTX-SRT-Macro", "card_corporate", "True"
        )

    def test_load_payment_success_personal(self, mock_keyring):
        """Test loading payment credentials for personal card"""
        # Arrange
        mock_keyring.get_password.side_effect = [
            "1234567890123456",  # card_number
            "12",                # card_password
            "2512",              # expire
            "900101",            # validation_number
            "False"              # is_corporate
        ]

        # Act
        result = CredentialStorage.load_payment()

        # Assert
        assert result is not None
        assert isinstance(result, PaymentCredentials)
        assert result.card_number == "1234567890123456"
        assert result.card_password == "12"
        assert result.expire == "2512"
        assert result.validation_number == "900101"
        assert result.is_corporate is False

    def test_load_payment_success_corporate(self, mock_keyring):
        """Test loading payment credentials for corporate card"""
        # Arrange
        mock_keyring.get_password.side_effect = [
            "1234567890123456",  # card_number
            "12",                # card_password
            "2512",              # expire
            "1234567890",        # validation_number (사업자번호)
            "True"               # is_corporate
        ]

        # Act
        result = CredentialStorage.load_payment()

        # Assert
        assert result is not None
        assert result.is_corporate is True
        assert result.validation_number == "1234567890"

    def test_load_payment_missing_data(self, mock_keyring):
        """Test loading payment credentials when data is missing"""
        # Arrange
        mock_keyring.get_password.side_effect = [
            "1234567890123456",  # card_number
            None,                # card_password - missing
            "2512",              # expire
            "900101",            # validation_number
            "False"              # is_corporate
        ]

        # Act
        result = CredentialStorage.load_payment()

        # Assert
        assert result is None

    def test_load_payment_all_missing(self, mock_keyring):
        """Test loading payment credentials when all data is missing"""
        # Arrange
        mock_keyring.get_password.side_effect = [None, None, None, None, None]

        # Act
        result = CredentialStorage.load_payment()

        # Assert
        assert result is None

    def test_delete_payment(self, mock_keyring):
        """Test deleting payment credentials"""
        # Act
        CredentialStorage.delete_payment()

        # Assert
        assert mock_keyring.delete_password.call_count == 5
        mock_keyring.delete_password.assert_any_call("KTX-SRT-Macro", "card_number")
        mock_keyring.delete_password.assert_any_call("KTX-SRT-Macro", "card_password")
        mock_keyring.delete_password.assert_any_call("KTX-SRT-Macro", "card_expire")
        mock_keyring.delete_password.assert_any_call("KTX-SRT-Macro", "card_validation")
        mock_keyring.delete_password.assert_any_call("KTX-SRT-Macro", "card_corporate")

    def test_delete_payment_not_found(self, mock_keyring):
        """Test deleting payment credentials when they don't exist"""
        # Arrange
        import keyring.errors
        mock_keyring.delete_password.side_effect = keyring.errors.PasswordDeleteError("Not found")
        mock_keyring.errors.PasswordDeleteError = keyring.errors.PasswordDeleteError

        # Act - should not raise exception
        CredentialStorage.delete_payment()

        # Assert
        assert mock_keyring.delete_password.call_count == 5

    def test_payment_shared_between_ktx_and_srt(self, mock_keyring):
        """Test that payment credentials are shared between KTX and SRT"""
        # Arrange
        card_number = "1234567890123456"
        card_password = "12"
        expire = "2512"
        validation_number = "900101"
        is_corporate = False

        # Act - Save payment once
        CredentialStorage.save_payment(
            card_number, card_password, expire, validation_number, is_corporate
        )

        # Arrange for load
        mock_keyring.get_password.side_effect = [
            card_number,
            card_password,
            expire,
            validation_number,
            "False"
        ]

        # Act - Load payment (should work for both KTX and SRT)
        result = CredentialStorage.load_payment()

        # Assert - Same credentials should be available for both services
        assert result is not None
        assert result.card_number == card_number
        # Verify that only unified keys were used (no ktx_/srt_ prefix)
        for call in mock_keyring.set_password.call_args_list:
            key_name = call[0][1]  # Second argument is the key name
            assert not key_name.startswith("ktx_"), f"Found KTX-specific key: {key_name}"
            assert not key_name.startswith("srt_"), f"Found SRT-specific key: {key_name}"
