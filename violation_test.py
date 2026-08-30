
import time
import csv
import os
import cv2

last_violation_time = {}

log_file = "violation_log.csv"
image_folder = "violation_images"

# Create image folder if it doesn't exist
os.makedirs(image_folder, exist_ok=True)

# Create CSV file if it doesn't exist
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Worker", "Missing PPE", "Video Time", "Image"])


def report_violation(worker_name, missing, frame, video_time):

    current_time = video_time

    # Don't log unknown workers
    if worker_name == "Unknown":
        worker_name = "Unknown"

    # First violation for this worker
    if worker_name not in last_violation_time:
        last_violation_time[worker_name] = 0

    # Report only once every 3 seconds
    if current_time - last_violation_time[worker_name] >= 3:

        print("--------------------")
        print(f"🚨 Worker {worker_name} - PPE VIOLATION")
        print(f"Missing: {missing}")
        print("--------------------")

        # Create image filename
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        safe_name = worker_name.replace(" ", "_")

        image_name = (
            f"violation_{safe_name}_{timestamp}.jpg"
        )

        image_path = os.path.join(
            image_folder,
            image_name
        )

        # Save violation image
        cv2.imwrite(image_path, frame)

        # Save violation information to CSV
        with open(log_file, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                worker_name,
                ", ".join(missing),
                f"{video_time:.2f}",
                image_name
            ])

        # Update last violation time
        last_violation_time[worker_name] = current_time