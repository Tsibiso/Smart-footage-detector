import time
from datetime import datetime


class ZoneEngine:

    def __init__(
        self,
        zones,
        restricted_zone="RESTRICTED",
        dwell_threshold=5.0
    ):
        self.zones = zones

        self.restricted_zone = restricted_zone
        self.dwell_threshold = dwell_threshold

        self.object_zones = {}
        self.events = []

    def point_in_zone(
        self,
        x,
        y,
        zone
    ):
        x1 = zone["x1"]
        y1 = zone["y1"]
        x2 = zone["x2"]
        y2 = zone["y2"]

        return (
            x1 <= x <= x2
            and
            y1 <= y <= y2
        )

    def get_zone(
        self,
        x,
        y
    ):
        for zone_name, zone in self.zones.items():

            if self.point_in_zone(
                x,
                y,
                zone
            ):
                return zone_name

        return "OUTSIDE"

    def create_event(
        self,
        event_type,
        class_name,
        track_id,
        zone_name,
        dwell_time=None
    ):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "class_name": class_name,
            "track_id": track_id,
            "zone": zone_name,
            "dwell_time": dwell_time
        }

        self.events.append(event)

        message = (
            f"[{timestamp}] "
            f"{class_name.upper()} "
            f"#{track_id} "
            f"{event_type} "
            f"| zone: {zone_name}"
        )

        if dwell_time is not None:
            message += (
                f" | dwell: {dwell_time}s"
            )

        print(message)

        return event

    def process(
        self,
        detected_objects
    ):
        current_time = time.time()
        current_track_ids = set()

        # Only events created during this
        # processing cycle are returned.
        new_events = []

        for obj in detected_objects:

            track_id = obj["track_id"]
            class_name = obj["class_name"]

            center_x = obj.get("center_x")
            center_y = obj.get("center_y")

            current_track_ids.add(track_id)

            current_zone = self.get_zone(
                center_x,
                center_y
            )

            # ==================================================
            # NEW OBJECT
            # ==================================================

            if track_id not in self.object_zones:

                self.object_zones[track_id] = {
                    "class_name": class_name,
                    "current_zone": current_zone,
                    "zone_enter_time": (
                        current_time
                        if current_zone != "OUTSIDE"
                        else None
                    ),
                    "security_alerted": False
                }

                if current_zone != "OUTSIDE":

                    event = self.create_event(
                        "ZONE_ENTERED",
                        class_name,
                        track_id,
                        current_zone
                    )

                    new_events.append(event)

                continue

            # ==================================================
            # EXISTING OBJECT
            # ==================================================

            tracked = self.object_zones[track_id]

            previous_zone = tracked["current_zone"]

            # ==================================================
            # ZONE CHANGED
            # ==================================================

            if current_zone != previous_zone:

                # ----------------------------------------------
                # LEFT PREVIOUS ZONE
                # ----------------------------------------------

                if previous_zone != "OUTSIDE":

                    event = self.create_event(
                        "ZONE_EXITED",
                        class_name,
                        track_id,
                        previous_zone
                    )

                    new_events.append(event)

                # ----------------------------------------------
                # ENTERED NEW ZONE
                # ----------------------------------------------

                if current_zone != "OUTSIDE":

                    event = self.create_event(
                        "ZONE_ENTERED",
                        class_name,
                        track_id,
                        current_zone
                    )

                    new_events.append(event)

                    # Start new dwell timer
                    tracked["zone_enter_time"] = (
                        current_time
                    )

                else:

                    # Object is outside all zones
                    tracked["zone_enter_time"] = None

                # Reset security alert
                tracked["security_alerted"] = False

                tracked["current_zone"] = current_zone

                continue

            # ==================================================
            # DWELL TIME
            # ==================================================

            if (
                current_zone != "OUTSIDE"
                and
                tracked["zone_enter_time"] is not None
            ):

                dwell_time = (
                    current_time
                    -
                    tracked["zone_enter_time"]
                )

                # ==============================================
                # RESTRICTED ZONE SECURITY RULE
                # ==============================================

                if (
                    class_name == "person"
                    and
                    current_zone == self.restricted_zone
                    and
                    dwell_time >= self.dwell_threshold
                    and
                    not tracked["security_alerted"]
                ):

                    event = self.create_event(
                        "SECURITY_ALERT",
                        class_name,
                        track_id,
                        current_zone,
                        round(dwell_time, 2)
                    )

                    new_events.append(event)

                    tracked["security_alerted"] = True

            # Keep current zone updated
            tracked["current_zone"] = current_zone

        # ======================================================
        # REMOVE TRACKS THAT ARE NO LONGER DETECTED
        # ======================================================

        for track_id in list(
            self.object_zones.keys()
        ):

            if track_id not in current_track_ids:

                del self.object_zones[
                    track_id
                ]

        # Return ONLY events generated during
        # this processing cycle.
        return new_events