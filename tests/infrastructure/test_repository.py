"""Tests for repository layer"""
import pytest
import tempfile
from pathlib import Path

from src.infrastructure.database.session import DatabaseManager
from src.infrastructure.database.models import TrainType, User, Card
from src.infrastructure.database.repository import SQLAlchemyUserRepository, SQLAlchemyCardRepository


@pytest.fixture(autouse=True)
def setup_test_database() -> None:
    """Setup test database before each test"""
    # Use a test database in platform-appropriate temp directory
    original_get_db_path = DatabaseManager.get_db_path

    # Create a temporary directory that works on all platforms
    temp_dir = Path(tempfile.gettempdir())
    test_db_file = temp_dir / "test_credentials.db"

    def test_db_path() -> Path:
        return test_db_file

    DatabaseManager.get_db_path = test_db_path
    DatabaseManager._engine = None
    DatabaseManager._session_factory = None
    DatabaseManager.initialize()
    DatabaseManager.reset_database()

    yield

    # Cleanup: close all connections and delete database file
    try:
        # Close engine and sessions first
        if DatabaseManager._engine is not None:
            DatabaseManager._engine.dispose()
        DatabaseManager._engine = None
        DatabaseManager._session_factory = None

        # Restore original path function
        DatabaseManager.get_db_path = original_get_db_path

        # Remove database file and related files
        if test_db_file.exists():
            test_db_file.unlink()

        # Remove any SQLite journal/wal files
        for ext in ['-journal', '-wal', '-shm']:
            journal_file = test_db_file.parent / f"{test_db_file.name}{ext}"
            if journal_file.exists():
                journal_file.unlink()
    except Exception as e:
        # If cleanup fails, at least try to restore the path
        DatabaseManager.get_db_path = original_get_db_path
        print(f"Warning: Test cleanup failed: {e}")


class TestUserRepository:
    """Test cases for SQLAlchemyUserRepository"""

    def test_save_new_user(self) -> None:
        """Test saving a new user"""
        repo = SQLAlchemyUserRepository()
        user = repo.save(
            username="encrypted_username",
            password="encrypted_password",
            train_type="KORAIL"
        )

        assert user.id is not None
        assert user.username == "encrypted_username"
        assert user.password == "encrypted_password"
        assert user.train_type == TrainType.KORAIL

    def test_save_updates_existing_user(self) -> None:
        """Test that saving updates existing user with same train_type"""
        repo = SQLAlchemyUserRepository()
        # Save first time
        repo.save(
            username="old_username",
            password="old_password",
            train_type="KORAIL"
        )

        # Save again with same train_type
        updated_user = repo.save(
            username="new_username",
            password="new_password",
            train_type="KORAIL"
        )

        # Should have updated, not created new
        assert updated_user.username == "new_username"
        assert updated_user.password == "new_password"

        # Should only have one user
        found_user = repo.find_by_train_type("KORAIL")
        assert found_user is not None
        assert found_user.username == "new_username"

    def test_find_by_train_type(self) -> None:
        """Test finding user by train type"""
        repo = SQLAlchemyUserRepository()
        # Save user
        repo.save(
            username="test_user",
            password="test_pass",
            train_type="SRT"
        )

        # Find it
        found = repo.find_by_train_type("SRT")

        assert found is not None
        assert found.username == "test_user"
        assert found.train_type == TrainType.SRT

    def test_find_by_train_type_not_found(self) -> None:
        """Test finding non-existent user returns None"""
        repo = SQLAlchemyUserRepository()
        found = repo.find_by_train_type("KORAIL")

        assert found is None

    def test_delete_existing_user(self) -> None:
        """Test deleting existing user"""
        repo = SQLAlchemyUserRepository()
        # Save user
        repo.save(
            username="to_delete",
            password="password",
            train_type="KORAIL"
        )

        # Delete it
        result = repo.delete("KORAIL")

        assert result is True

        # Should not be found anymore
        found = repo.find_by_train_type("KORAIL")
        assert found is None

    def test_delete_non_existent_user(self) -> None:
        """Test deleting non-existent user returns False"""
        repo = SQLAlchemyUserRepository()
        result = repo.delete("KORAIL")

        assert result is False

    def test_separate_storage_for_different_train_types(self) -> None:
        """Test that KORAIL and SRT users are stored separately"""
        repo = SQLAlchemyUserRepository()
        # Save KORAIL user
        repo.save(
            username="korail_user",
            password="korail_pass",
            train_type="KORAIL"
        )

        # Save SRT user
        repo.save(
            username="srt_user",
            password="srt_pass",
            train_type="SRT"
        )

        # Both should exist independently
        korail_user = repo.find_by_train_type("KORAIL")
        srt_user = repo.find_by_train_type("SRT")

        assert korail_user is not None
        assert srt_user is not None
        assert korail_user.username == "korail_user"
        assert srt_user.username == "srt_user"


class TestCardRepository:
    """Test cases for CardRepository"""

    def test_save_new_card(self) -> None:
        """Test saving a new card"""
        repo = SQLAlchemyCardRepository()
        card = repo.save(
            card_number="encrypted_number",
            card_password="encrypted_pass",
            card_expired_date="encrypted_date",
            card_validate_number="encrypted_validate",
            is_corporate=False,
            train_type="KORAIL"
        )

        assert card.id is not None
        assert card.card_number == "encrypted_number"
        assert card.is_corporate is False
        assert card.train_type == TrainType.KORAIL

    def test_save_updates_existing_card(self) -> None:
        """Test that saving updates existing card with same train_type"""
        repo = SQLAlchemyCardRepository()
        # Save first time
        repo.save(
            card_number="old_number",
            card_password="old_pass",
            card_expired_date="old_date",
            card_validate_number="old_validate",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Save again with same train_type
        updated_card = repo.save(
            card_number="new_number",
            card_password="new_pass",
            card_expired_date="new_date",
            card_validate_number="new_validate",
            is_corporate=True,
            train_type="KORAIL"
        )

        # Should have updated
        assert updated_card.card_number == "new_number"
        assert updated_card.is_corporate is True

    def test_find_by_train_type(self) -> None:
        """Test finding card by train type"""
        repo = SQLAlchemyCardRepository()
        # Save card
        repo.save(
            card_number="test_number",
            card_password="test_pass",
            card_expired_date="2512",
            card_validate_number="900101",
            is_corporate=False,
            train_type="SRT"
        )

        # Find it
        found = repo.find_by_train_type("SRT")

        assert found is not None
        assert found.card_number == "test_number"
        assert found.train_type == TrainType.SRT

    def test_find_by_train_type_not_found(self) -> None:
        """Test finding non-existent card returns None"""
        repo = SQLAlchemyCardRepository()
        found = repo.find_by_train_type("KORAIL")

        assert found is None

    def test_delete_existing_card(self) -> None:
        """Test deleting existing card"""
        repo = SQLAlchemyCardRepository()
        # Save card
        repo.save(
            card_number="to_delete",
            card_password="pass",
            card_expired_date="2512",
            card_validate_number="900101",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Delete it
        result = repo.delete("KORAIL")

        assert result is True

        # Should not be found anymore
        found = repo.find_by_train_type("KORAIL")
        assert found is None

    def test_delete_non_existent_card(self) -> None:
        """Test deleting non-existent card returns False"""
        repo = SQLAlchemyCardRepository()
        result = repo.delete("KORAIL")

        assert result is False

    def test_separate_storage_for_different_train_types(self) -> None:
        """Test that KORAIL and SRT cards are stored separately"""
        repo = SQLAlchemyCardRepository()
        # Save KORAIL card
        repo.save(
            card_number="korail_number",
            card_password="korail_pass",
            card_expired_date="2512",
            card_validate_number="900101",
            is_corporate=False,
            train_type="KORAIL"
        )

        # Save SRT card
        repo.save(
            card_number="srt_number",
            card_password="srt_pass",
            card_expired_date="2612",
            card_validate_number="1234567890",
            is_corporate=True,
            train_type="SRT"
        )

        # Both should exist independently
        korail_card = repo.find_by_train_type("KORAIL")
        srt_card = repo.find_by_train_type("SRT")

        assert korail_card is not None
        assert srt_card is not None
        assert korail_card.card_number == "korail_number"
        assert srt_card.card_number == "srt_number"
        assert korail_card.is_corporate is False
        assert srt_card.is_corporate is True
