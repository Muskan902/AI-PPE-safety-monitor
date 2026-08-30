import streamlit as st
import pandas as pd
import os
from PIL import Image

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="PPE Safety Monitor",
    page_icon="🦺",
    layout="wide"
)

st.title("🦺 PPE Safety Monitoring Dashboard")
st.caption("AI-Based Personal Protective Equipment Monitoring System")

st.divider()

# -----------------------------
# File paths
# -----------------------------
LOG_FILE = "violation_log.csv"
IMAGE_FOLDER = "violation_images"

# -----------------------------
# Read violation log
# -----------------------------
if os.path.exists(LOG_FILE):

    df = pd.read_csv(LOG_FILE)

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Number of violation records
    total_violations = len(df)

    # Count different PPE violations
    helmet_violations = 0
    goggles_violations = 0
    gloves_violations = 0
    boots_violations = 0

    # Search all text in the CSV for missing PPE
    for _, row in df.iterrows():

        row_text = " ".join(
            str(value).lower()
            for value in row.values
        )

        if "helmet" in row_text:
            helmet_violations += 1

        if "goggle" in row_text:
            goggles_violations += 1

        if "glove" in row_text:
            gloves_violations += 1

        if "boot" in row_text:
            boots_violations += 1

else:

    df = pd.DataFrame()

    total_violations = 0
    helmet_violations = 0
    goggles_violations = 0
    gloves_violations = 0
    boots_violations = 0


# -----------------------------
# Main metrics
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "⚠️ Total Violations",
        total_violations
    )

with col2:
    st.metric(
        "🪖 Helmet Violations",
        helmet_violations
    )

with col3:
    st.metric(
        "🧤 Gloves Violations",
        gloves_violations
    )

with col4:
    st.metric(
        "🥾 Boots Violations",
        boots_violations
    )

st.divider()


# -----------------------------
# PPE violation statistics
# -----------------------------
st.subheader("🎥 PPE Detection Video")

VIDEO_FILE = r"runs\detect\predict-12\test.avi"

if os.path.exists(VIDEO_FILE):
    st.video(VIDEO_FILE)
else:
    st.warning("Detection video not found.")
st.subheader("📊 PPE Violation Statistics")

stats = pd.DataFrame({
    "PPE Item": [
        "Helmet",
        "Goggles",
        "Gloves",
        "Boots"
    ],
    "Violations": [
        helmet_violations,
        goggles_violations,
        gloves_violations,
        boots_violations
    ]
})

st.bar_chart(
    stats.set_index("PPE Item")
)


# -----------------------------
# Violation log
# -----------------------------
st.subheader("📝 Violation Log")

if not df.empty:
    st.dataframe(
        df,
        use_container_width=True
    )
else:
    st.info(
        "No violation log found yet."
    )


# -----------------------------
# Saved violation images
# -----------------------------
st.divider()

st.subheader("📸 Violation Evidence")

if os.path.exists(IMAGE_FOLDER):

    image_files = [
        file for file in os.listdir(IMAGE_FOLDER)
        if file.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ]

    if image_files:

        cols = st.columns(3)

        for index, image_file in enumerate(image_files):

            image_path = os.path.join(
                IMAGE_FOLDER,
                image_file
            )

            with cols[index % 3]:

                image = Image.open(image_path)

                st.image(
                    image,
                    caption=image_file,
                    use_container_width=True
                )

    else:
        st.info(
            "No violation images found."
        )

else:
    st.info(
        "Violation image folder not found."
    )


# -----------------------------
# Refresh button
# -----------------------------
st.divider()

if st.button("🔄 Refresh Dashboard"):

    st.rerun()