from ultralytics import YOLO
import cv2
import winsound
import time
from ppe_compliance import check_ppe
from violation_test import report_violation

# Load your trained model
model = YOLO("runs/detect/train-7/weights/best.pt")


# Tracking
results = model.track(
    source=0,
    stream=True,
    persist=True,
    tracker="bytetrack.yaml",
    conf=0.5
)

print("📹 Live PPE monitoring started")
print("Press Q to stop")

# Keep track of video time
fps = 30
frame_number = 0
violation_workers=set()
violation_details={}
stable_ids = {}
next_worker_id = 1
last_alarm_time=[0]

for result in results:
    violation_workers.clear()
    violation_details.clear()

    frame_number += 1
    video_time = frame_number / fps

    persons = []
    ppe_items = []

    # Read detections
    for box in result.boxes:

        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        if class_name == "Person":

            track_id = int(box.id[0]) if box.id is not None else -1
            
            persons.append(
                (track_id, x1, y1, x2, y2)
            )

        elif class_name in [
            "helmet",
            "gloves",
            "vest",
            "boots",
            "goggles",
            "no_helmet",
            "no_gloves",
            "no_boots",
            "no_goggle"
        ]:

            ppe_items.append(
                (class_name, x1, y1, x2, y2)
            )

    # Check each worker
    for worker_id, x1, y1, x2, y2 in persons:

        person_ppe = []

        px1, py1, px2, py2 = x1, y1, x2, y2

        # Find PPE belonging to this worker
        for item in ppe_items:

            name, ix1, iy1, ix2, iy2 = item

            center_x = (ix1 + ix2) / 2
            center_y = (iy1 + iy2) / 2

            if px1 <= center_x <= px2 and py1 <= center_y <= py2:
                person_ppe.append(name)

        # Check PPE compliance
        status, missing = check_ppe(person_ppe)

        if missing:
            violation_details[track_id]=missing
            violation_workers.add(track_id)

            # Report violation
            report_violation(
                track_id,
                missing,
                result.orig_img,
                video_time
            )

            # Red box
            cv2.rectangle(
                result.orig_img,
                (int(px1), int(py1)),
                (int(px2), int(py2)),
                (0, 0, 255),
                2
            )

            text = f"VIOLATION: Missing {', '.join(missing)}"

            cv2.putText(
                result.orig_img,
                text,
                (int(px1), max(30, int(py1) - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        else:

            # Green box
            cv2.rectangle(
                result.orig_img,
                (int(px1), int(py1)),
                (int(px2), int(py2)),
                (0, 255, 0),
                2
            )

            cv2.putText(
                result.orig_img,
                "SAFE",
                (int(px1), max(30, int(py1) - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    # Show live video
    # Alarm for active violations
    if violation_workers: 
     current_time=time.time()
     if current_time- last_alarm_time[0] >= 3:
        winsound.Beep(1000, 500)
        last_alarm_time[0] = video_time
    
    cv2.putText(
    result.orig_img,
    "PPE SAFETY MONITOR",
    (20, 30),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.8,
    (255, 255, 255),
    2
     )

    cv2.putText(
    result.orig_img,
    f"Workers Detected: {len(persons)}",
    (20, 60),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (255, 255, 255),
    2
    )

    cv2.putText(
    result.orig_img,
    f"Current Violations: {len(violation_workers)}",
    (20, 90),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (255, 255, 255),
    2
    )

    # Press Q to sto
    y_position = 120

    for worker_id, missing in violation_details.items():

      text = f"Worker {worker_id}: Missing {', '.join(missing)}"

      cv2.putText(
        result.orig_img,
        text,
        (20, y_position),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        2
    )

    y_position += 25
    cv2.imshow("PPE Safety Monitor", result.orig_img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
           break

cv2.destroyAllWindows()

print("✅ Live PPE monitoring stopped")