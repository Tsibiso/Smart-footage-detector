from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    incident_id: int
    timestamp: datetime | None = None

    rule: str
    severity: str
    class_name: str

    track_id: int | None = None
    zone: str | None = None

    description: str

    dwell_time: float | None = None
    status: str = "OPEN"


class IncidentResponse(BaseModel):
    id: int
    incident_id: int
    timestamp: datetime

    rule: str
    severity: str
    class_name: str

    track_id: int | None
    zone: str | None

    description: str

    dwell_time: float | None
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )