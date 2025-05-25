from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
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
    __tablename__ = "service"
    __table_args__ = {"schema": SCHEMA}
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    uri: Mapped[str] = mapped_column()

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    ping: WriteOnlyMapped["Ping"] = relationship()

    def __init__(self, name: str, uri: str):
        self.name = name
        self.uri = uri


class Ping(db.Model):
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
