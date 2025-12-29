"""Database session management"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from src.infrastructure.database.models import Base


class DatabaseManager:
    """Database connection and session manager"""

    _engine = None
    _session_factory = None

    @classmethod
    def get_db_path(cls) -> Path:
        """Get the database file path"""
        # Store database in user's home directory
        home_dir = Path.home()
        app_dir = home_dir / ".ktx-srt-macro"
        app_dir.mkdir(exist_ok=True)
        return app_dir / "credentials.db"

    @classmethod
    def initialize(cls) -> None:
        """Initialize database engine and create tables if needed"""
        if cls._engine is None:
            db_path = cls.get_db_path()
            # Use sqlite with absolute path
            database_url = f"sqlite:///{db_path}"
            cls._engine = create_engine(
                database_url,
                echo=False,  # Set to True for SQL debugging
                connect_args={"check_same_thread": False}  # Needed for SQLite
            )
            cls._session_factory = sessionmaker(
                bind=cls._engine,
                autocommit=False,
                autoflush=False
            )

            # Create all tables
            Base.metadata.create_all(cls._engine)

    @classmethod
    @contextmanager
    def get_session(cls) -> Generator[Session, None, None]:
        """
        Get a database session context manager

        Usage:
            with DatabaseManager.get_session() as session:
                # Use session here
                pass
        """
        if cls._session_factory is None:
            cls.initialize()

        session = cls._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def reset_database(cls) -> None:
        """Reset the database (drop all tables and recreate)"""
        if cls._engine is not None:
            Base.metadata.drop_all(cls._engine)
            Base.metadata.create_all(cls._engine)
