from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from .database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    incident_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    rule = Column(
        String,
        nullable=False
    )

    severity = Column(
        String,
        nullable=False
    )

    class_name = Column(
        String,
        nullable=False
    )

    track_id = Column(
        Integer,
        nullable=True
    )

    zone = Column(
        String,
        nullable=True
    )

    description = Column(
        String,
        nullable=False
    )

    dwell_time = Column(
        Float,
        nullable=True
    )

    status = Column(
        String,
        default="OPEN",
        nullable=False
    )