REQUIRED_PPE = {
    "helmet",
    "gloves",
    "vest",
    "boots",
    "goggles"
}


def check_ppe(detected_items):
    detected_items = set(detected_items)

    missing = set()

    # Explicit violation classes
    if "no_helmet" in detected_items:
        missing.add("helmet")

    if "no_gloves" in detected_items:
        missing.add("gloves")

    if "no_boots" in detected_items:
        missing.add("boots")

    if "no_goggle" in detected_items:
        missing.add("goggles")

    # Normal PPE detections
    if "helmet" not in detected_items and "no_helmet" not in detected_items:
        missing.add("helmet")

    if "gloves" not in detected_items and "no_gloves" not in detected_items:
        missing.add("gloves")

    if "boots" not in detected_items and "no_boots" not in detected_items:
        missing.add("boots")

    if "goggles" not in detected_items and "no_goggle" not in detected_items:
        missing.add("goggles")
    # Vest is different because there is no "no_vest" class
    if "vest" not in detected_items:
        missing.add("vest")

    if not missing:
        return "SAFE", []

    return "PPE VIOLATION", list(missing)