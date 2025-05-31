from typing import Self

import flask_login
from argon2 import PasswordHasher
from sqlalchemy import BigInteger, String, exists
from sqlalchemy.orm import Mapped, mapped_column

from downtime_panda.extensions import db


class User(db.Model, flask_login.UserMixin):
    """User model for authentication and user management."""

    __tablename__ = "user"
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @classmethod
    def add_user(cls, username: str, email: str, password: str) -> Self:
        """Add a new user to the database.

        Args:
            username (str): Username of the user
            email (str): Email of the user
            password (str): Password of the user

        Raises:
            ValueError: If the username or email already exists in the database

        Returns:
            Self: The created user instance
        """
        if cls.username_exists(username):
            raise ValueError(f"Username '{username}' already exists.")

        if cls.email_exists(email):
            raise ValueError(f"Email '{email}' already exists.")

        ph = PasswordHasher()
        password_hash = ph.hash(password)

        user = cls(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def username_exists(cls, username: str) -> bool:
        """Check if a username already exists in the database."""
        return db.session.query(exists().where(cls.username == username)).scalar()

    @classmethod
    def email_exists(cls, email: str) -> bool:
        """Check if an email already exists in the database."""
        return db.session.query(exists().where(cls.email == email)).scalar()

    @classmethod
    def get_by_id(cls, user_id: int) -> Self | None:
        """Retrieve a user by their ID."""
        return db.session.get(cls, user_id)

    @classmethod
    def get_by_username(cls, username: str) -> Self | None:
        """Retrieve a user by their username."""
        return db.session.query(cls).filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email: str) -> Self | None:
        """Retrieve a user by their email."""
        return db.session.query(cls).filter_by(email=email).first()

    def verify_password(self, password: str) -> bool:
        """Verify the provided password against the stored hash, and rehash if necessary."""
        ph = PasswordHasher()
        try:
            ph.verify(self.password_hash, password)

            if ph.check_needs_rehash(self.password_hash):
                # Rehash the password if needed
                self.password_hash = ph.hash(password)
                db.session.commit()

            return True
        except Exception:
            return False
