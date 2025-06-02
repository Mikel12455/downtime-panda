from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from downtime_panda.blueprints.user.models import User
from downtime_panda.extensions import db


class APIToken(db.Model):
    """Model for API tokens associated with users."""

    __tablename__ = "api_token"

    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
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
