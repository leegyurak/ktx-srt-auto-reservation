"""Domain repository interfaces for credential management"""
from typing import Protocol

from src.domain.models.entities import UserEntity, CardEntity


class IUserRepository(Protocol):
    """Interface for User repository operations (domain layer)"""

    def find_by_train_type(self, train_type: str) -> UserEntity | None:
        """
        Find user by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            UserEntity if found, None otherwise
        """
        ...

    def save(self, username: str, password: str, train_type: str) -> UserEntity:
        """
        Save or update user credentials

        Args:
            username: The encrypted username
            password: The encrypted password
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            The saved UserEntity
        """
        ...

    def delete(self, train_type: str) -> bool:
        """
        Delete user by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            True if deleted, False if not found
        """
        ...


class ICardRepository(Protocol):
    """Interface for Card repository operations (domain layer)"""

    def find_by_train_type(self, train_type: str) -> CardEntity | None:
        """
        Find card by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            CardEntity if found, None otherwise
        """
        ...

    def save(
        self,
        card_number: str,
        card_password: str,
        card_expired_date: str,
        card_validate_number: str,
        is_corporate: bool,
        train_type: str
    ) -> CardEntity:
        """
        Save or update card credentials

        Args:
            card_number: The encrypted card number
            card_password: The encrypted card password
            card_expired_date: The encrypted expiration date (YYMM)
            card_validate_number: The encrypted validation number
            is_corporate: Whether it's a corporate card
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            The saved CardEntity
        """
        ...

    def delete(self, train_type: str) -> bool:
        """
        Delete card by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            True if deleted, False if not found
        """
        ...
