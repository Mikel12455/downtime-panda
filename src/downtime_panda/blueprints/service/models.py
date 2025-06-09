from datetime import datetime
from typing import Any, Self, Sequence

import pytz
import requests
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, select
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from downtime_panda.extensions import db, scheduler


class Service(db.Model):
    """Service model to store service information and related pings."""

    __tablename__ = "service"
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    uri: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    ping: WriteOnlyMapped["Ping"] = relationship(order_by="Ping.pinged_at.desc()")

    # ----------------------------- STANDARD METHODS ----------------------------- #
    def __init__(self, uri: str):
        self.uri = uri

    def __repr__(self) -> str:
        return f"<Service {self.id}>"

    # -------------------------------- CONSTRUCTOR ------------------------------- #
    @classmethod
    def create_if_not_exists(cls, uri: str) -> Self:
        """Create a new service if it does not already exist."""
        if cls.uri_exists(uri):
            return cls.get_by_uri(uri)

        service = Service(
            uri=uri,
        )
        db.session.add(service)
        db.session.commit()
        db.session.refresh(service)

        # Schedule the ping job for the new service
        trigger = IntervalTrigger(seconds=5)
        scheduler.add_job(
            func=service.ping_service,
            args=[service.id],
            trigger=trigger,
            replace_existing=True,
            id=f"ping_service_{service.id}",
        )

        db.session.commit()
        return service

    @classmethod
    def get_by_uri(cls, uri: str) -> Self | None:
        """Get a service by its URI, or None if it does not exist."""
        return db.session.execute(select(cls).filter_by(uri=uri)).scalar_one_or_none()

    @classmethod
    def uri_exists(cls, uri: str) -> bool:
        """Checks if a service with the specified URI exists."""
        return cls.get_by_uri(uri=uri) is not None

    @classmethod
    def ping_service(cls, service_id: int) -> None:
        with scheduler.app.app_context():
            service = db.session.get(cls, service_id)
            logger.info(service)

            pinged_at = datetime.now(pytz.utc)
            response = requests.head(service.uri)
            ping = Ping(
                service_id=f"ping_service_{service.id}",
                http_status=response.status_code,
                pinged_at=pinged_at,
            )
            service.ping.add(ping)
            db.session.commit()

    def get_latest_ping(self) -> "Ping | None":
        """Get the latest ping for the service."""
        return db.session.execute(
            select(Ping).filter_by(service_id=self.id).order_by(Ping.pinged_at.desc())
        ).scalar()

    def get_latest_n_pings(self, n: int) -> Sequence["Ping"]:
        query = (
            select(Ping)
            .filter_by(service_id=self.id)
            .order_by(Ping.pinged_at.desc())
            .limit(n)
        )
        return db.session.execute(query).scalars().all()

    def get_pings_since_date(self, since: datetime) -> Sequence["Ping"]:
        query = (
            select(Ping)
            .filter_by(service_id=self.id)
            .where(Ping.pinged_at >= since)
            .order_by(Ping.pinged_at.desc())
        )
        return db.session.execute(query).scalars().all()


class Ping(db.Model):
    """Ping model to store service ping data."""

    __tablename__ = "ping"
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey(Service.id, onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    http_response: Mapped[int] = mapped_column(Integer(), nullable=False)
    pinged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ----------------------------- STANDARD METHODS ----------------------------- #
    def __init__(self, service_id: int, http_status: int, pinged_at: datetime):
        self.service_id = service_id
        self.http_response = http_status
        self.pinged_at = pinged_at

    def __repr__(self) -> str:
        return f"<Ping {self.id} for Service {self.service_id}>"

    # ---------------------------------- METHODS --------------------------------- #
    def to_dict(self) -> dict[str, Any]:
        return {
            "http_response": self.http_response,
            "pinged_at": self.pinged_at.isoformat(),
        }
