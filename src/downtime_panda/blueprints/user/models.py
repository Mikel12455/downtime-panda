import secrets
import uuid
from typing import Self

import flask_login
from argon2 import PasswordHasher
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Uuid,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from downtime_panda.blueprints.service.models import Service
from downtime_panda.extensions import db

subscription = Table(
    "subscription",
    db.metadata,
    Column("user_id", BigInteger(), ForeignKey("user.id"), primary_key=True),
    Column("service_id", BigInteger(), ForeignKey("service.id"), primary_key=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "uuid",
        Uuid(),
        index=True,
        nullable=False,
        unique=True,
        default=uuid.uuid4,
    ),
)


class User(db.Model, flask_login.UserMixin):
    """User model for authentication and user management."""

    __tablename__ = "user"

    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    services: Mapped[list[Service]] = relationship(secondary=subscription)
    api_tokens: Mapped[list["APIToken"]] = relationship(
        "APIToken",
        back_populates="user",
    )

    # ----------------------------- STANDARD METHODS ----------------------------- #
    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self) -> str:
        return f"<User {self.id}>"

    # -------------------------------- CONSTRUCTOR ------------------------------- #
    @classmethod
    def register(cls, username: str, email: str, password: str) -> Self:
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

    # ---------------------------------- METHODS --------------------------------- #
    @classmethod
    def username_exists(cls, username: str) -> bool:
        """Check if a username already exists in the database."""
        return (
            db.session.execute(select(cls).filter_by(username=username)).first()
            is not None
        )

    @classmethod
    def email_exists(cls, email: str) -> bool:
        """Check if an email already exists in the database."""
        return (
            db.session.execute(select(cls).filter_by(email=email)).first() is not None
        )

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

    def subscribe_to_service(self, service: Service) -> None:
        """Subscribe the user to a service."""
        if service not in self.services:
            self.services.append(service)
            db.session.commit()

    def create_token(self):
        """Create a new API token for the user."""
        token = APIToken(user_id=self.id, token=secrets.token_hex(16))
        self.api_tokens.append(token)
        db.session.commit()

    def revoke_token(self, token_id: int) -> None:
        """Revoke an API token for the user."""
        token_to_remove = db.session.execute(
            select(APIToken).filter_by(id=token_id, user_id=self.id)
        ).scalar_one_or_none()

        if not token_to_remove:
            raise ValueError(
                f"Token with ID {token_id} does not exist or does not belong to the user."
            )

        db.session.delete(token_to_remove)
        db.session.commit()


from downtime_panda.blueprints.api.models import APIToken  # noqa: E402
# Import APIToken after User to avoid circular import issues
