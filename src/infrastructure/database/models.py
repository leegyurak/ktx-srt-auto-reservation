"""SQLAlchemy database models for credential storage"""
from sqlalchemy import String, Boolean, Integer, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class TrainType(str, enum.Enum):
    """Train type enumeration"""
    KORAIL = "KORAIL"
    SRT = "SRT"


class User(Base):
    """User credentials table"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False)  # Encrypted
    password: Mapped[str] = mapped_column(String, nullable=False)  # Encrypted
    train_type: Mapped[str] = mapped_column(SQLEnum(TrainType), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, train_type={self.train_type})>"


class Card(Base):
    """Payment card credentials table"""
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_number: Mapped[str] = mapped_column(String, nullable=False)  # Encrypted
    card_password: Mapped[str] = mapped_column(String, nullable=False)  # Encrypted
    card_expired_date: Mapped[str] = mapped_column(String, nullable=False)  # Encrypted (YYMM format)
    card_validate_number: Mapped[str] = mapped_column(String, nullable=False)  # Encrypted (birth date or business number)
    is_corporate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    train_type: Mapped[str] = mapped_column(SQLEnum(TrainType), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Card(id={self.id}, train_type={self.train_type}, is_corporate={self.is_corporate})>"
