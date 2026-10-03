from ultralytics import YOLO
import cv2
import time
from pathlib import Path
from datetime import datetime

from event_engine import EventEngine
from movement_engine import MovementEngine
from zone_engine import ZoneEngine
from security_rules import SecurityRuleEngine


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "yolo11n.pt"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

VIDEO_PATH = PROJECT_ROOT / "videos" / "test.mp4"

SNAPSHOT_DIR = PROJECT_ROOT / "backend" / "snapshots"

SNAPSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO(MODEL_NAME)

print("YOLO model loaded successfully.")


# ============================================================
# VIDEO DETECTOR
# ============================================================

def detect_video(video_source):

    # ========================================================
    # EVENT ENGINE
    # ========================================================

    event_engine = EventEngine(
        timeout=4.0
    )

    # ========================================================
    # MOVEMENT ENGINE
    # ========================================================

    movement_engine = MovementEngine(
        movement_threshold=20,
        stopped_threshold=5
    )

    # ========================================================
    # ZONE CONFIGURATION
    # ========================================================

    zones = {
        "ENTRANCE": {
            "x1": 0,
            "y1": 250,
            "x2": 300,
            "y2": 480
        },

        "RESTRICTED": {
            "x1": 300,
            "y1": 100,
            "x2": 640,
            "y2": 450
        }
    }

    # ========================================================
    # ZONE ENGINE
    # ========================================================

    zone_engine = ZoneEngine(zones)

    # ========================================================
    # SECURITY ENGINE
    # ========================================================

    security_engine = SecurityRuleEngine()

    # ========================================================
    # OPEN VIDEO
    # ========================================================

    print(
        f"Opening video source: {video_source}"
    )

    cap = cv2.VideoCapture(
        video_source
    )

    if not cap.isOpened():

        print(
            "ERROR: Could not open video source."
        )

        return

    print(
        "Video opened successfully."
    )

    print(
        "Press Q to stop."
    )

    previous_time = time.time()

    # ========================================================
    # MAIN VIDEO LOOP
    # ========================================================

    while True:

        success, frame = cap.read()

        if not success:

            print(
                "Video finished."
            )

            break

        # ====================================================
        # OBJECT TRACKING
        # ====================================================

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        result = results[0]

        # ====================================================
        # COLLECT TRACKED OBJECTS
        # ====================================================

        detected_objects = []

        if result.boxes is not None:

            for box in result.boxes:

                # --------------------------------------------
                # TRACK ID
                # --------------------------------------------

                if box.id is None:
                    continue

                track_id = int(
                    box.id[0]
                )

                # --------------------------------------------
                # CLASS
                # --------------------------------------------

                class_id = int(
                    box.cls[0]
                )

                class_name = model.names[
                    class_id
                ]

                # --------------------------------------------
                # CONFIDENCE
                # --------------------------------------------

                confidence = float(
                    box.conf[0]
                )

                # --------------------------------------------
                # BOUNDING BOX
                # --------------------------------------------

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                # --------------------------------------------
                # CENTER POSITION
                # --------------------------------------------

                center_x = int(
                    (x1 + x2) / 2
                )

                center_y = int(
                    (y1 + y2) / 2
                )

                # --------------------------------------------
                # STORE OBJECT
                # --------------------------------------------

                detected_objects.append({
                    "track_id": track_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "center_x": center_x,
                    "center_y": center_y
                })

        # ====================================================
        # EVENT ENGINE
        # ====================================================

        event_engine.process(
            detected_objects
        )

        # ====================================================
        # MOVEMENT ENGINE
        # ====================================================

        movement_engine.process(
            detected_objects
        )

        # ====================================================
        # ZONE ENGINE
        # ====================================================

        zone_events = zone_engine.process(
            detected_objects
        )

        # ====================================================
        # CREATE DISPLAY FRAME
        # ====================================================

        annotated_frame = frame.copy()

        # ====================================================
        # DRAW ZONES
        # ====================================================

        for zone_name, zone in zones.items():

            x1 = zone["x1"]
            y1 = zone["y1"]

            x2 = zone["x2"]
            y2 = zone["y2"]

            # ----------------------------------------------
            # ZONE RECTANGLE
            # ----------------------------------------------

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (255, 255, 255),
                2
            )

            # ----------------------------------------------
            # ZONE LABEL
            # ----------------------------------------------

            cv2.putText(
                annotated_frame,
                zone_name,
                (x1 + 10, y1 + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        # ====================================================
        # DRAW OBJECT DETECTIONS
        # ====================================================

        if result.boxes is not None:

            for box in result.boxes:

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                class_id = int(
                    box.cls[0]
                )

                class_name = model.names[
                    class_id
                ]

                confidence = float(
                    box.conf[0]
                )

                track_id = None

                if box.id is not None:

                    track_id = int(
                        box.id[0]
                    )

                # --------------------------------------------
                # LABEL
                # --------------------------------------------

                if track_id is not None:

                    label = (
                        f"{class_name} "
                        f"#{track_id} "
                        f"{confidence:.2f}"
                    )

                else:

                    label = (
                        f"{class_name} "
                        f"{confidence:.2f}"
                    )

                # --------------------------------------------
                # DRAW BOUNDING BOX
                # --------------------------------------------

                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 255, 255),
                    2
                )

                # --------------------------------------------
                # DRAW LABEL
                # --------------------------------------------

                cv2.putText(
                    annotated_frame,
                    label,
                    (
                        x1,
                        max(y1 - 10, 20)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                # --------------------------------------------
                # CENTER POINT
                # --------------------------------------------

                center_x = int(
                    (x1 + x2) / 2
                )

                center_y = int(
                    (y1 + y2) / 2
                )

                cv2.circle(
                    annotated_frame,
                    (
                        center_x,
                        center_y
                    ),
                    4,
                    (255, 255, 255),
                    -1
                )

        # ====================================================
        # SECURITY RULES
        # ====================================================

        for event in zone_events:

            incident = security_engine.process_zone_event(
                event
            )

            # ------------------------------------------------
            # CAPTURE SNAPSHOT FOR SECURITY INCIDENT
            # ------------------------------------------------

            if incident is not None:

                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                track_id = incident["track_id"]

                snapshot_filename = (
                    f"incident_"
                    f"{incident['incident_id']}_"
                    f"{timestamp}_"
                    f"track{track_id}.jpg"
                )

                snapshot_path = (
                    SNAPSHOT_DIR /
                    snapshot_filename
                )

                # ------------------------------------------------
                # SAVE INCIDENT SNAPSHOT
                # ------------------------------------------------

                snapshot_success = cv2.imwrite(
                    str(snapshot_path),
                    annotated_frame
                )

                if snapshot_success:

                    print(
                        f"SNAPSHOT: Saved successfully -> "
                        f"{snapshot_path}"
                    )

                else:

                    print(
                        "SNAPSHOT ERROR: "
                        "Could not save incident snapshot."
                    )

        # ====================================================
        # OBJECT COUNTS
        # ====================================================

        people_count = 0

        vehicle_count = 0

        object_count = 0

        if result.boxes is not None:

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                class_name = model.names[
                    class_id
                ]

                object_count += 1

                if class_name == "person":

                    people_count += 1

                if class_name in [
                    "car",
                    "motorcycle",
                    "bus",
                    "truck"
                ]:

                    vehicle_count += 1

        # ====================================================
        # FPS
        # ====================================================

        current_time = time.time()

        elapsed = (
            current_time
            - previous_time
        )

        if elapsed > 0:

            fps = 1 / elapsed

        else:

            fps = 0

        previous_time = current_time

        # ====================================================
        # INFORMATION PANEL
        # ====================================================

        panel_height = 170

        cv2.rectangle(
            annotated_frame,
            (0, 0),
            (360, panel_height),
            (20, 20, 20),
            -1
        )

        cv2.putText(
            annotated_frame,
            "SMART FOOTAGE DETECTOR",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"People:     {people_count}",
            (15, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Vehicles:   {vehicle_count}",
            (15, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"Objects:    {object_count}",
            (15, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f"FPS:        {fps:.1f}",
            (15, 155),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "Smart Footage Detector",
            annotated_frame
        )

        # ====================================================
        # QUIT
        # ====================================================

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    # ========================================================
    # CLEANUP
    # ========================================================

    cap.release()

    cv2.destroyAllWindows()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if VIDEO_PATH.exists():

        print(
            f"Using video: {VIDEO_PATH}"
        )

        detect_video(
            str(VIDEO_PATH)
        )

    else:

        print(
            "No test video found."
        )

        print(
            "Starting webcam instead..."
        )

        detect_video(0)