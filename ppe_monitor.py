from ultralytics import YOLO
import cv2
from deepface import DeepFace
from ppe_compliance import check_ppe
from violation_test import report_violation
import os
worker_names={}
WORKERS = {
    "worker1": "faces/worker1.png",
    "worker2": "faces/worker2.png"
}



def identify_worker(person_crop):
    try:
        best_worker = "Unknown"
        best_distance = 999

        for worker_name, worker_image in WORKERS.items():

            result = DeepFace.verify(
                img1_path=person_crop,
                img2_path=worker_image,
                model_name="Facenet512",
                detector_backend="retinaface",
                enforce_detection=True,
                silent=True
            )

            distance = float(result["distance"])

            print(f"{worker_name}: distance = {distance:.4f}")

            if distance < best_distance:
                best_distance = distance
                best_worker = worker_name

        # Strict matching
        if best_distance <= 0.35:
            return best_worker

        return "Unknown"

    except Exception as e:
        print("Face recognition error:", e)
        return "Unknown"
# Load your trained model
model = YOLO("runs/detect/train-7/weights/best.pt")

# Open the input video
cap = cv2.VideoCapture("test_video/demo.mp4")

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("ppe_output.mp4", fourcc, fps, (width, height))

cap.release()

results = model.track(
    "test_video/demo.mp4",
    persist=True,
    tracker="bytetrack.yaml",
    conf=0.5
)


frame_number=0
for result in results:
    frame_number+=1
    video_time=frame_number/fps


    persons = []
    ppe_items = []

    # Get all detections
    for box in result.boxes:

        class_id = int(box.cls[0])
        class_name = model.names[class_id]

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        if class_name == "Person":
         track_id = int(box.id[0]) if box.id is not None else -1
         persons.append((track_id, x1, y1, x2, y2))

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

            ppe_items.append((class_name, x1, y1, x2, y2))

    # Check each person
    for track_id, x1, y1, x2, y2 in persons:

        px1, py1, px2, py2 = x1, y1, x2, y2
        person_ppe = []

        # Crop the person
        person_crop = result.orig_img[
            int(py1):int(py2),
            int(px1):int(px2)
        ]

        # Face recognition every 15 frames
        if track_id not in worker_names and frame_number % 15 == 0:

            if person_crop.size > 0:

                name = identify_worker(person_crop)

                if name != "Unknown":
                    worker_names[track_id] = name

        # Get worker name
        worker_name = worker_names.get(track_id, "Unknown")

        # Find PPE belonging to this person
        for item in ppe_items:

            name, ix1, iy1, ix2, iy2 = item

            center_x = (ix1 + ix2) / 2
            center_y = (iy1 + iy2) / 2

            if px1 <= center_x <= px2 and py1 <= center_y <= py2:
                person_ppe.append(name)

        # Check PPE compliance
        status, missing = check_ppe(person_ppe)

        if missing:

            # Print violation
            report_violation(
                worker_name,
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

            # Violation text
            text = f"{worker_name}: VIOLATION - Missing {', '.join(missing)}"

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

            # SAFE text
            cv2.putText(
                result.orig_img,
                f"{worker_name}: SAFE",
                (int(px1), max(30, int(py1) - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    # Save frame
    out.write(result.orig_img)
# Finish writing the video
out.release()

print("✅ PPE monitoring completed!")
print("✅ Output saved as ppe_output.mp4")