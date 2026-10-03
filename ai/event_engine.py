import time
from datetime import datetime


class EventEngine:

    def __init__(self, timeout=2.0):

        self.tracked_objects = {}

        self.timeout = timeout

        self.events = []

    # ========================================================
    # CREATE EVENT
    # ========================================================

    def create_event(
        self,
        event_type,
        class_name,
        track_id,
        first_seen=None,
        last_seen=None,
        start_position=None,
        end_position=None,
        confidence=None
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        duration = None

        if (
            first_seen is not None
            and last_seen is not None
        ):

            duration = round(
                last_seen - first_seen,
                2
            )

        event = {

            "timestamp": timestamp,

            "event_type": event_type,

            "class_name": class_name,

            "track_id": track_id,

            "duration": duration,

            "start_position": start_position,

            "end_position": end_position,

            "confidence": confidence

        }

        self.events.append(event)

        print(
            f"[{timestamp}] "
            f"{class_name.upper()} #{track_id} "
            f"{event_type}"
        )

        return event

    # ========================================================
    # PROCESS OBJECTS
    # ========================================================

    def process(self, detected_objects):

        current_time = time.time()

        current_track_ids = set()

        # ====================================================
        # PROCESS CURRENT DETECTIONS
        # ====================================================

        for obj in detected_objects:

            track_id = obj["track_id"]

            class_name = obj["class_name"]

            confidence = obj.get(
                "confidence",
                None
            )

            center_x = obj.get(
                "center_x",
                None
            )

            center_y = obj.get(
                "center_y",
                None
            )

            position = (
                center_x,
                center_y
            )

            current_track_ids.add(
                track_id
            )

            # =================================================
            # NEW OBJECT
            # =================================================

            if track_id not in self.tracked_objects:

                self.tracked_objects[track_id] = {

                    "class_name": class_name,

                    "first_seen": current_time,

                    "last_seen": current_time,

                    "confidence": confidence,

                    "start_position": position,

                    "last_position": position,

                    "position_history": [
                        position
                    ]

                }

                self.create_event(

                    "ENTERED",

                    class_name,

                    track_id,

                    current_time,

                    current_time,

                    start_position=position,

                    end_position=position,

                    confidence=confidence

                )

            # =================================================
            # EXISTING OBJECT
            # =================================================

            else:

                tracked = self.tracked_objects[
                    track_id
                ]

                tracked["last_seen"] = current_time

                tracked["last_position"] = position

                tracked["confidence"] = confidence

                tracked["position_history"].append(
                    position
                )

        # ====================================================
        # DETECT EXITED OBJECTS
        # ====================================================

        for track_id in list(
            self.tracked_objects.keys()
        ):

            tracked = self.tracked_objects[
                track_id
            ]

            last_seen = tracked[
                "last_seen"
            ]

            # -----------------------------------------------
            # OBJECT DISAPPEARED
            # -----------------------------------------------

            if (

                track_id not in current_track_ids

                and

                current_time - last_seen
                > self.timeout

            ):

                self.create_event(

                    "EXITED",

                    tracked["class_name"],

                    track_id,

                    tracked["first_seen"],

                    tracked["last_seen"],

                    start_position=tracked[
                        "start_position"
                    ],

                    end_position=tracked[
                        "last_position"
                    ],

                    confidence=tracked[
                        "confidence"
                    ]

                )

                del self.tracked_objects[
                    track_id
                ]

        return self.events