
from deepface import DeepFace


WORKERS = {
    "worker1": "faces/worker1.png",
    "worker2": "faces/worker2.png"
}


def identify_face(image_path):
    try:
        best_worker = "Unknown"
        best_distance = 999

        for worker_name, worker_image in WORKERS.items():

            result = DeepFace.verify(
                img1_path=image_path,
                img2_path=worker_image,
                model_name="Facenet512",
                detector_backend="retinaface",
                enforce_detection=True,
                silent=True
            )

            distance = result["distance"]

            print(
                f"{worker_name}: distance = {distance:.4f}"
            )

            if distance < best_distance:
                best_distance = distance
                best_worker = worker_name

        # Reject very poor matches
        if best_distance > 0.40:
            return "Unknown"

        return best_worker

    except Exception as e:
        print("Face recognition error:", e)
        return "Unknown"