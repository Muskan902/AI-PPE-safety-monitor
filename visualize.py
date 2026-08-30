import cv2
import os

# -----------------------------
# 1. Dataset paths
# -----------------------------
image_path = r"datasets\construction-ppe\images\train\image1035.jpeg"
label_path = r"datasets\construction-ppe\labels\train\image1035.txt"

# -----------------------------
# 2. Class names
# -----------------------------
class_names = [
    "helmet",
    "gloves",
    "vest",
    "boots",
    "goggles",
    "none",
    "Person",
    "no_helmet",
    "no_goggle",
    "no_gloves",
    "no_boots"
]

# -----------------------------
# 3. Read image
# -----------------------------
image = cv2.imread(image_path)

if image is None:
    print("ERROR: Image could not be loaded.")
    print("Check the image path.")
    exit()

height, width = image.shape[:2]

# -----------------------------
# 4. Read YOLO labels
# -----------------------------
with open(label_path, "r") as file:
    lines = file.readlines()

# -----------------------------
# 5. Draw bounding boxes
# -----------------------------
for line in lines:

    values = line.strip().split()

    if len(values) != 5:
        continue

    class_id = int(values[0])

    x_center = float(values[1])
    y_center = float(values[2])
    box_width = float(values[3])
    box_height = float(values[4])

    # Convert normalized coordinates to pixels
    x_center *= width
    y_center *= height
    box_width *= width
    box_height *= height

    # Calculate top-left and bottom-right corners
    x1 = int(x_center - box_width / 2)
    y1 = int(y_center - box_height / 2)

    x2 = int(x_center + box_width / 2)
    y2 = int(y_center + box_height / 2)

    # Draw bounding box
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    # Get class name
    class_name = class_names[class_id]

    # Write class name
    cv2.putText(
        image,
        class_name,
        (x1, max(y1 - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

# -----------------------------
# 6. Save result
# -----------------------------
output_path = "visualized.jpg"

cv2.imwrite(output_path, image)

print("Visualization completed!")
print("Saved as:", output_path)

# -----------------------------
# 7. Open the result
# -----------------------------
os.startfile(output_path)