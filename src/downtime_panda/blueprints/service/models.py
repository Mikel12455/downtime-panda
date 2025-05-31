import json
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from downtime_panda.extensions import db


class Service(db.Model):
    """Service model to store service information and related pings."""

    __tablename__ = "service"
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    uri: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    ping: WriteOnlyMapped["Ping"] = relationship(order_by="Ping.pinged_at.desc()")

    def __init__(self, name: str, uri: str):
        self.name = name
        self.uri = uri


class Ping(db.Model):
    """Ping model to store service ping data."""

    __tablename__ = "ping"
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey(Service.id, onupdate="CASCADE", ondelete="RESTRICT"), nullable=False
    )
    http_response: Mapped[int] = mapped_column(Integer(), nullable=False)
    pinged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

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
