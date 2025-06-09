import uuid
from typing import Self

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func, select
from sqlalchemy.orm import Mapped, mapped_column

from downtime_panda.extensions import db


class Subscription(db.Model):
    __tablename__ = "subscription"

    # ---------------------------------- COLUMNS --------------------------------- #
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        primary_key=True,
    )
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"), primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=False,
        unique=False,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    uuid: Mapped[str] = mapped_column(
        Uuid(),
        index=True,
        nullable=False,
        unique=True,
        default=uuid.uuid4,
    )

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    user: Mapped["User"] = db.relationship("User", back_populates="subscriptions")
    service: Mapped["Service"] = db.relationship("Service")

    # ----------------------------- STANDARD METHODS ----------------------------- #
    def __init__(self, user_id: int, service_id: int, name: str):
        self.user_id = user_id
        self.service_id = service_id
        self.name = name

    def __repr__(self):
        return f"<Subscription {self.id}>"

    # ------------------------------- CONSTRUCTORS ------------------------------- #
    @classmethod
    def subscribe_user_to_service(
        cls, user: "User", service: "Service", name: str
    ) -> Self:
        """Create a new subscription for a user to a service."""
        subscription = cls(user_id=user.id, service_id=service.id, name=name)
        db.session.add(subscription)
        db.session.commit()
        return subscription

    @classmethod
    def get_subscriptions_by_user(cls, user: "User") -> list[Self]:
        """Get all subscriptions for a user."""
        query = select(cls).filter_by(user_id=user.id)
        subscriptions = db.session.execute(query).scalars().all()
        return subscriptions

    @classmethod
    def get_user_subscription_by_uuid(cls, user: "User", sub_uuid: str) -> Self | None:
        sub_uuid = uuid.UUID(sub_uuid)
        query = select(cls).filter_by(user_id=user.id, uuid=sub_uuid)
        subscription = db.session.execute(query).scalars().one_or_none()
        return subscription


from downtime_panda.blueprints.service.models import Service  # noqa: E402
from downtime_panda.blueprints.user.models import User  # noqa: E402
