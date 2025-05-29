import json
from datetime import datetime
from typing import Self

import flask_login
from argon2 import PasswordHasher
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, exists
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    WriteOnlyMapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


SCHEMA = "downtime_panda"


class Service(db.Model):
    """Service model to store service information and related pings."""

    __tablename__ = "service"
    __table_args__ = {"schema": SCHEMA}
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    uri: Mapped[str] = mapped_column()

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    ping: WriteOnlyMapped["Ping"] = relationship(order_by="Ping.pinged_at.desc()")

    def __init__(self, name: str, uri: str):
        self.name = name
        self.uri = uri


class Ping(db.Model):
    """Ping model to store service ping data."""

    __tablename__ = "ping"
    __table_args__ = {"schema": SCHEMA}
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey(f"{SCHEMA}.service.id"))
    http_response: Mapped[int] = mapped_column()
    pinged_at: Mapped[datetime] = mapped_column()

    def __init__(self, service_id: int, http_status: int, pinged_at: datetime):
        self.service_id = service_id
        self.http_response = http_status
        self.pinged_at = pinged_at

    def dump_json(self):
        return json.dumps(self.as_dict())

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "service_id": self.service_id,
            "http_response": self.http_response,
            "pinged_at": self.pinged_at.isoformat(),
        }


class User(db.Model, flask_login.UserMixin):
    """User model for authentication and user management."""

    __tablename__ = "user"
    __table_args__ = {"schema": SCHEMA}
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()

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
