import secrets
from typing import Self

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from downtime_panda.extensions import db


class APIToken(db.Model):
    """Model for API tokens associated with users."""

    __tablename__ = "api_token"

    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer(), "sqlite"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger(),
        ForeignKey("user.id"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    user: Mapped["User"] = relationship(
        "User",
        back_populates="api_tokens",
    )

    # ----------------------------- STANDARD METHODS ----------------------------- #
    def __init__(self, user_id: int, token: str):
        self.user_id = user_id
        self.token = token

    def __repr__(self) -> str:
        return f"<APIToken {self.id} for User {self.user_id}>"

    # ------------------------------- CONSTRUCTORS ------------------------------- #
    @classmethod
    def create_for_user(cls, user: "User") -> Self:
        """
        Create a new API token for the user.
        """

        token = APIToken(user_id=user.id, token=secrets.token_hex(16))
        db.session.add(token)
        db.session.commit()

        return token

    @classmethod
    def find_by_id(cls, token_id: int, user: "User") -> Self | None:
        """Finds a token by ID.

        Args:
            id (int): The token's ID
            user (User): The user who generated the token

        Returns:
            Self: The token, or `None` if not found
        """
        query = select(APIToken).filter_by(id=token_id, user_id=user.id)
        token = db.session.execute(query).scalar()
        return token

    def revoke(self) -> None:
        """
        Revoke this API token.
        """

        db.session.delete(self)
        db.session.commit()

    def exists(self) -> bool:
        query = select(APIToken).filter_by(id=self.id)
        token = db.session.execute(query).scalar_one_or_none()
        return True if token else False


from downtime_panda.blueprints.user.models import User  # noqa: E402
