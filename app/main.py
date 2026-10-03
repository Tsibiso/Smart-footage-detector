from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Incident
from .schemas import IncidentResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path




Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Smart Footage Detector API",
    description="AI video intelligence and security platform",
    version="1.0.0"
)
# =========================================================
# SNAPSHOT STORAGE
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parent.parent

SNAPSHOT_DIR = BACKEND_DIR / "snapshots"

SNAPSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

app.mount(
    "/snapshots",
    StaticFiles(directory=str(SNAPSHOT_DIR)),
    name="snapshots"
)

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "name": "Smart Footage Detector API",
        "status": "online",
        "version": "1.0.0"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/api/health")
def health():
    return {
        "status": "healthy"
    }



# =========================================================
# INCIDENTS
# =========================================================

@app.get("/api/incidents")
def get_incidents(
    db: Session = Depends(get_db)
):

    incidents = (
        db.query(Incident)
        .order_by(Incident.timestamp.desc())
        .all()
    )

    results = []

    for incident in incidents:

        # =================================================
        # FIND SNAPSHOT
        # =================================================

        snapshot_files = list(
            SNAPSHOT_DIR.glob(
                f"incident_{incident.incident_id}_*.jpg"
            )
        )

        snapshot_url = None

        if snapshot_files:

            snapshot_url = (
                f"/snapshots/{snapshot_files[0].name}"
            )

        # =================================================
        # BUILD RESPONSE
        # =================================================

        results.append({

            "id": incident.id,

            "incident_id": incident.incident_id,

            "timestamp": incident.timestamp,

            "rule": incident.rule,

            "severity": incident.severity,

            "class_name": incident.class_name,

            "track_id": incident.track_id,

            "zone": incident.zone,

            "description": incident.description,

            "dwell_time": incident.dwell_time,

            "status": incident.status,

            "snapshot_url": snapshot_url

        })

    return results

