"""Tests for encryption service"""
import pytest

from src.infrastructure.security.encryption import EncryptionService


class TestEncryptionService:
    """Test cases for EncryptionService"""

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Test that encryption and decryption work correctly"""
        plaintext = "test_password_123"

        # Encrypt
        encrypted = EncryptionService.encrypt(plaintext)

        # Should be different from plaintext
        assert encrypted != plaintext

        # Decrypt
        decrypted = EncryptionService.decrypt(encrypted)

        # Should match original
        assert decrypted == plaintext

    def test_encrypt_empty_string(self) -> None:
        """Test encrypting empty string"""
        encrypted = EncryptionService.encrypt("")
        assert encrypted == ""

    def test_decrypt_empty_string(self) -> None:
        """Test decrypting empty string"""
        decrypted = EncryptionService.decrypt("")
        assert decrypted is None

    def test_encrypt_produces_different_ciphertexts(self) -> None:
        """Test that same plaintext produces different ciphertexts (due to random IV)"""
        plaintext = "same_password"

        encrypted1 = EncryptionService.encrypt(plaintext)
        encrypted2 = EncryptionService.encrypt(plaintext)

        # Should be different due to random IV
        assert encrypted1 != encrypted2

        # But both should decrypt to same plaintext
        assert EncryptionService.decrypt(encrypted1) == plaintext
        assert EncryptionService.decrypt(encrypted2) == plaintext

    def test_decrypt_invalid_data(self) -> None:
        """Test decrypting invalid data returns None"""
        invalid_data = "not_base64_encrypted_data"

        decrypted = EncryptionService.decrypt(invalid_data)

        assert decrypted is None

    def test_encrypt_unicode(self) -> None:
        """Test encrypting unicode characters"""
        plaintext = "한글비밀번호123!@#"

        encrypted = EncryptionService.encrypt(plaintext)
        decrypted = EncryptionService.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_special_characters(self) -> None:
        """Test encrypting special characters"""
        plaintext = "p@$$w0rd!#%&*()_+-=[]{}|;:',.<>?/~`"

        encrypted = EncryptionService.encrypt(plaintext)
        decrypted = EncryptionService.decrypt(encrypted)

        assert decrypted == plaintext

    def test_encrypt_long_text(self) -> None:
        """Test encrypting long text"""
        plaintext = "a" * 1000

        encrypted = EncryptionService.encrypt(plaintext)
        decrypted = EncryptionService.decrypt(encrypted)

        assert decrypted == plaintext

    def test_machine_id_derivation(self) -> None:
        """Test that machine ID derivation is consistent"""
        # Get machine ID twice
        machine_id1 = EncryptionService._get_machine_id()
        machine_id2 = EncryptionService._get_machine_id()

        # Should be the same
        assert machine_id1 == machine_id2
        # Should not be empty
        assert len(machine_id1) > 0

    def test_key_derivation(self) -> None:
        """Test that key derivation is consistent"""
        # Derive key twice
        key1 = EncryptionService._derive_key()
        key2 = EncryptionService._derive_key()

        # Should be the same
        assert key1 == key2

        # Should be 32 bytes (256 bits)
        assert len(key1) == 32
