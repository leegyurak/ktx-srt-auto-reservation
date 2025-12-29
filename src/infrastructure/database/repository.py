"""SQLAlchemy implementation of domain repository interfaces"""
from sqlalchemy import select

from src.infrastructure.database.session import DatabaseManager
from src.infrastructure.database.models import User, Card, TrainType


class SQLAlchemyUserRepository:
    """SQLAlchemy implementation of IUserRepository"""

    def find_by_train_type(self, train_type: str) -> User | None:
        """
        Find user by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            User if found, None otherwise
        """
        train_type_enum = TrainType.KORAIL if train_type == "KORAIL" else TrainType.SRT

        with DatabaseManager.get_session() as session:
            stmt = select(User).where(User.train_type == train_type_enum)
            user = session.execute(stmt).scalar_one_or_none()
            if user:
                # Load attributes before expunging
                _ = (user.id, user.username, user.password, user.train_type)
                session.expunge(user)
            return user

    def save(self, username: str, password: str, train_type: str) -> User:
        """
        Save or update user credentials

        Args:
            username: The encrypted username
            password: The encrypted password
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            The saved User entity
        """
        train_type_enum = TrainType.KORAIL if train_type == "KORAIL" else TrainType.SRT

        with DatabaseManager.get_session() as session:
            stmt = select(User).where(User.train_type == train_type_enum)
            existing_user = session.execute(stmt).scalar_one_or_none()

            if existing_user:
                # Update existing user
                existing_user.username = username
                existing_user.password = password
                session.flush()
                # Load attributes before expunging
                _ = (existing_user.id, existing_user.username, existing_user.password, existing_user.train_type)
                session.expunge(existing_user)
                return existing_user
            else:
                # Create new user
                new_user = User(
                    username=username,
                    password=password,
                    train_type=train_type_enum
                )
                session.add(new_user)
                session.flush()
                # Load attributes before expunging
                _ = (new_user.id, new_user.username, new_user.password, new_user.train_type)
                session.expunge(new_user)
                return new_user

    def delete(self, train_type: str) -> bool:
        """
        Delete user by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            True if deleted, False if not found
        """
        train_type_enum = TrainType.KORAIL if train_type == "KORAIL" else TrainType.SRT

        with DatabaseManager.get_session() as session:
            stmt = select(User).where(User.train_type == train_type_enum)
            user = session.execute(stmt).scalar_one_or_none()

            if user:
                session.delete(user)
                return True
            return False


class SQLAlchemyCardRepository:
    """SQLAlchemy implementation of ICardRepository"""

    def find_by_train_type(self, train_type: str) -> Card | None:
        """
        Find card by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            Card if found, None otherwise
        """
        train_type_enum = TrainType.KORAIL if train_type == "KORAIL" else TrainType.SRT

        with DatabaseManager.get_session() as session:
            stmt = select(Card).where(Card.train_type == train_type_enum)
            card = session.execute(stmt).scalar_one_or_none()
            if card:
                # Load attributes before expunging
                _ = (card.id, card.card_number, card.card_password,
                     card.card_expired_date, card.card_validate_number,
                     card.is_corporate, card.train_type)
                session.expunge(card)
            return card

    def save(
        self,
        card_number: str,
        card_password: str,
        card_expired_date: str,
        card_validate_number: str,
        is_corporate: bool,
        train_type: str
    ) -> Card:
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
            The saved Card entity
        """
        train_type_enum = TrainType.KORAIL if train_type == "KORAIL" else TrainType.SRT

        with DatabaseManager.get_session() as session:
            stmt = select(Card).where(Card.train_type == train_type_enum)
            existing_card = session.execute(stmt).scalar_one_or_none()

            if existing_card:
                # Update existing card
                existing_card.card_number = card_number
                existing_card.card_password = card_password
                existing_card.card_expired_date = card_expired_date
                existing_card.card_validate_number = card_validate_number
                existing_card.is_corporate = is_corporate
                session.flush()
                # Load attributes before expunging
                _ = (existing_card.id, existing_card.card_number, existing_card.card_password,
                     existing_card.card_expired_date, existing_card.card_validate_number,
                     existing_card.is_corporate, existing_card.train_type)
                session.expunge(existing_card)
                return existing_card
            else:
                # Create new card
                new_card = Card(
                    card_number=card_number,
                    card_password=card_password,
                    card_expired_date=card_expired_date,
                    card_validate_number=card_validate_number,
                    is_corporate=is_corporate,
                    train_type=train_type_enum
                )
                session.add(new_card)
                session.flush()
                # Load attributes before expunging
                _ = (new_card.id, new_card.card_number, new_card.card_password,
                     new_card.card_expired_date, new_card.card_validate_number,
                     new_card.is_corporate, new_card.train_type)
                session.expunge(new_card)
                return new_card

    def delete(self, train_type: str) -> bool:
        """
        Delete card by train type

        Args:
            train_type: The train type ("KORAIL" or "SRT")

        Returns:
            True if deleted, False if not found
        """
        train_type_enum = TrainType.KORAIL if train_type == "KORAIL" else TrainType.SRT

        with DatabaseManager.get_session() as session:
            stmt = select(Card).where(Card.train_type == train_type_enum)
            card = session.execute(stmt).scalar_one_or_none()

            if card:
                session.delete(card)
                return True
            return False
