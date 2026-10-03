import math
from datetime import datetime


class MovementEngine:

    def __init__(
        self,
        movement_threshold=20,
        stopped_threshold=5
    ):

        # Minimum pixel distance between frames
        # before an object is considered moving.
        self.movement_threshold = movement_threshold

        # Distance below this is considered stationary.
        self.stopped_threshold = stopped_threshold

        # Store previous position/state for each track.
        self.tracked_objects = {}

        # Store generated movement events.
        self.events = []

    # ========================================================
    # CALCULATE DISTANCE
    # ========================================================

    def calculate_distance(
        self,
        previous_position,
        current_position
    ):

        if (
            previous_position is None
            or current_position is None
        ):

            return 0.0

        previous_x, previous_y = previous_position

        current_x, current_y = current_position

        distance = math.sqrt(

            (current_x - previous_x) ** 2

            +

            (current_y - previous_y) ** 2

        )

        return round(distance, 2)

    # ========================================================
    # CREATE MOVEMENT EVENT
    # ========================================================

    def create_event(
        self,
        event_type,
        class_name,
        track_id,
        position,
        distance
    ):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        event = {

            "timestamp": timestamp,

            "event_type": event_type,

            "class_name": class_name,

            "track_id": track_id,

            "position": position,

            "distance": distance

        }

        self.events.append(event)

        print(

            f"[{timestamp}] "

            f"{class_name.upper()} "

            f"#{track_id} "

            f"{event_type} "

            f"| distance: {distance}px"

        )

        return event

    # ========================================================
    # PROCESS OBJECTS
    # ========================================================

    def process(
        self,
        detected_objects
    ):

        current_track_ids = set()

        for obj in detected_objects:

            track_id = obj["track_id"]

            class_name = obj["class_name"]

            center_x = obj.get(
                "center_x"
            )

            center_y = obj.get(
                "center_y"
            )

            current_position = (

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

                    "last_position":
                        current_position,

                    "state": "UNKNOWN"

                }

                continue

            # =================================================
            # EXISTING OBJECT
            # =================================================

            tracked = self.tracked_objects[
                track_id
            ]

            previous_position = tracked[
                "last_position"
            ]

            previous_state = tracked[
                "state"
            ]

            # =================================================
            # CALCULATE MOVEMENT
            # =================================================

            distance = self.calculate_distance(

                previous_position,

                current_position

            )

            # =================================================
            # DETERMINE STATE
            # =================================================

            if distance >= self.movement_threshold:

                current_state = "MOVING"

            elif distance <= self.stopped_threshold:

                current_state = "STOPPED"

            else:

                # Keep previous state when movement
                # is between the two thresholds.
                current_state = previous_state

            # =================================================
            # STATE CHANGED
            # =================================================

            if current_state != previous_state:

                if current_state == "MOVING":

                    self.create_event(

                        "MOVEMENT_STARTED",

                        class_name,

                        track_id,

                        current_position,

                        distance

                    )

                elif current_state == "STOPPED":

                    self.create_event(

                        "MOVEMENT_STOPPED",

                        class_name,

                        track_id,

                        current_position,

                        distance

                    )

            # =================================================
            # UPDATE OBJECT
            # =================================================

            tracked["last_position"] = (
                current_position
            )

            tracked["state"] = (
                current_state
            )

        # ====================================================
        # REMOVE LOST TRACKS
        # ====================================================

        for track_id in list(
            self.tracked_objects.keys()
        ):

            if track_id not in current_track_ids:

                del self.tracked_objects[
                    track_id
                ]

        return self.events