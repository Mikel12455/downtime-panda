from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
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


class Service(db.Model):
    __tablename__ = "service"
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    uri: Mapped[str] = mapped_column()

    # ------------------------------- RELATIONSHIPS ------------------------------ #
    ping: WriteOnlyMapped["Ping"] = relationship(
        order_by="ping.pinged_at DESC",
    )


class Ping(db.Model):
    __tablename__ = "ping"
    # ---------------------------------- COLUMNS --------------------------------- #
    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column()
    http_status: Mapped[int] = mapped_column()
    pinged_at: Mapped[datetime] = mapped_column()
