"""Unit tests for security DTOs"""
from src.infrastructure.security.dto import LoginCredentials, PaymentCredentials


class TestLoginCredentials:
    """Tests for LoginCredentials DTO"""

    def test_login_credentials_creation(self):
        """Test creating LoginCredentials with valid data"""
        # Arrange & Act
        credentials = LoginCredentials(
            username="test_user",
            password="test_password"
        )

        # Assert
        assert credentials.username == "test_user"
        assert credentials.password == "test_password"

    def test_login_credentials_equality(self):
        """Test LoginCredentials equality comparison"""
        # Arrange
        credentials1 = LoginCredentials(username="user1", password="pass1")
        credentials2 = LoginCredentials(username="user1", password="pass1")
        credentials3 = LoginCredentials(username="user2", password="pass2")

        # Assert
        assert credentials1 == credentials2
        assert credentials1 != credentials3

    def test_login_credentials_immutability(self):
        """Test that LoginCredentials fields can be modified (dataclass default)"""
        # Arrange
        credentials = LoginCredentials(username="user1", password="pass1")

        # Act - dataclass allows modification by default
        credentials.username = "user2"

        # Assert
        assert credentials.username == "user2"

    def test_login_credentials_with_empty_strings(self):
        """Test LoginCredentials with empty strings"""
        # Arrange & Act
        credentials = LoginCredentials(username="", password="")

        # Assert
        assert credentials.username == ""
        assert credentials.password == ""

    def test_login_credentials_with_special_characters(self):
        """Test LoginCredentials with special characters"""
        # Arrange & Act
        credentials = LoginCredentials(
            username="user@example.com",
            password="P@ssw0rd!#$%"
        )

        # Assert
        assert credentials.username == "user@example.com"
        assert credentials.password == "P@ssw0rd!#$%"


class TestPaymentCredentials:
    """Tests for PaymentCredentials DTO"""

    def test_payment_credentials_creation_personal_card(self):
        """Test creating PaymentCredentials for personal card"""
        # Arrange & Act
        credentials = PaymentCredentials(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False
        )

        # Assert
        assert credentials.card_number == "1234567890123456"
        assert credentials.card_password == "12"
        assert credentials.expire == "2512"
        assert credentials.validation_number == "900101"
        assert credentials.is_corporate is False

    def test_payment_credentials_creation_corporate_card(self):
        """Test creating PaymentCredentials for corporate card"""
        # Arrange & Act
        credentials = PaymentCredentials(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="1234567890",  # 사업자번호
            is_corporate=True
        )

        # Assert
        assert credentials.card_number == "1234567890123456"
        assert credentials.card_password == "12"
        assert credentials.expire == "2512"
        assert credentials.validation_number == "1234567890"
        assert credentials.is_corporate is True

    def test_payment_credentials_equality(self):
        """Test PaymentCredentials equality comparison"""
        # Arrange
        credentials1 = PaymentCredentials(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False
        )
        credentials2 = PaymentCredentials(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False
        )
        credentials3 = PaymentCredentials(
            card_number="9876543210987654",
            card_password="34",
            expire="2612",
            validation_number="800101",
            is_corporate=False
        )

        # Assert
        assert credentials1 == credentials2
        assert credentials1 != credentials3

    def test_payment_credentials_with_empty_strings(self):
        """Test PaymentCredentials with empty strings"""
        # Arrange & Act
        credentials = PaymentCredentials(
            card_number="",
            card_password="",
            expire="",
            validation_number="",
            is_corporate=False
        )

        # Assert
        assert credentials.card_number == ""
        assert credentials.card_password == ""
        assert credentials.expire == ""
        assert credentials.validation_number == ""
        assert credentials.is_corporate is False

    def test_payment_credentials_corporate_flag_toggle(self):
        """Test that corporate flag can be toggled"""
        # Arrange
        credentials = PaymentCredentials(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False
        )

        # Act
        credentials.is_corporate = True

        # Assert
        assert credentials.is_corporate is True

    def test_payment_credentials_all_fields_present(self):
        """Test that all required fields are present"""
        # Arrange & Act
        credentials = PaymentCredentials(
            card_number="1234567890123456",
            card_password="12",
            expire="2512",
            validation_number="900101",
            is_corporate=False
        )

        # Assert - check all attributes exist
        assert hasattr(credentials, "card_number")
        assert hasattr(credentials, "card_password")
        assert hasattr(credentials, "expire")
        assert hasattr(credentials, "validation_number")
        assert hasattr(credentials, "is_corporate")
