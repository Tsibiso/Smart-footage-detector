from datetime import datetime

from app.database import SessionLocal
from app.models import Incident


class SecurityRuleEngine:

    def __init__(self):
        self.incidents = []

    def create_incident(
        self,
        rule,
        severity,
        class_name,
        track_id,
        zone,
        description,
        dwell_time=None
    ):
        timestamp = datetime.now()

        incident = {
            "incident_id": len(self.incidents) + 1,
            "timestamp": timestamp,
            "rule": rule,
            "severity": severity,
            "class_name": class_name,
            "track_id": track_id,
            "zone": zone,
            "description": description,
            "dwell_time": dwell_time,
            "status": "OPEN"
        }

        # Keep the existing in-memory incident list
        self.incidents.append(incident)

        # ---------------------------------------------------------
        # SAVE INCIDENT TO DATABASE
        # ---------------------------------------------------------

        db = SessionLocal()

        try:
            db_incident = Incident(
                incident_id=incident["incident_id"],
                timestamp=incident["timestamp"],
                rule=incident["rule"],
                severity=incident["severity"],
                class_name=incident["class_name"],
                track_id=incident["track_id"],
                zone=incident["zone"],
                description=incident["description"],
                dwell_time=incident["dwell_time"],
                status=incident["status"]
            )

            db.add(db_incident)
            db.commit()
            db.refresh(db_incident)

            print("DATABASE: Incident saved successfully.")

        except Exception as e:
            db.rollback()
            print(f"DATABASE ERROR: {e}")

        finally:
            db.close()

        # ---------------------------------------------------------
        # CONSOLE SECURITY INCIDENT
        # ---------------------------------------------------------

        print()
        print("=" * 60)
        print("SECURITY INCIDENT")
        print("=" * 60)
        print(f"Incident ID : {incident['incident_id']}")
        print(f"Timestamp   : {timestamp}")
        print(f"Rule        : {rule}")
        print(f"Severity    : {severity}")
        print(f"Object      : {class_name.upper()}")
        print(f"Track ID    : {track_id}")
        print(f"Zone        : {zone}")

        if dwell_time is not None:
            print(f"Dwell Time  : {dwell_time}s")

        print(f"Description : {description}")
        print(f"Status      : OPEN")
        print("=" * 60)
        print()

        return incident

    def process_zone_event(self, event):

        if event["event_type"] != "SECURITY_ALERT":
            return None

        class_name = event["class_name"]

        # Only people trigger the current
        # restricted-zone intrusion rule.
        if class_name != "person":
            return None

        zone = event["zone"]
        track_id = event["track_id"]
        dwell_time = event.get("dwell_time")

        incident = self.create_incident(
            rule="RESTRICTED_ZONE_INTRUSION",
            severity="HIGH",
            class_name=class_name,
            track_id=track_id,
            zone=zone,
            description=(
                "Person remained inside a restricted "
                "zone beyond the configured dwell threshold."
            ),
            dwell_time=dwell_time
        )

        return incident