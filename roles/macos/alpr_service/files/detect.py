from collections import defaultdict
from ultralytics import YOLO
import cv2
import json
import numpy as np
import os
import requests
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# CONFIGURATION
CAMERA_ID = int(os.getenv("CAMERA_ID", "0"))
OUTPUT_DIR = os.getenv("DETECTIONS_DIR", os.path.expanduser("~/orangead/alpr/detections"))
MAX_IMAGES_PER_CAR = int(os.getenv("MAX_IMAGES_PER_CAR", "5"))
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "5"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
CAR_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck
ALPR_SERVICE_URL = os.getenv("ALPR_SERVICE_URL", "http://localhost:8081/v1/plate-reader/")
ALPR_REGION = os.getenv("ALPR_REGION", "ca")

def send_image_to_plate_reader(image_path: str):
    """
    Sends an image to the local ALPR plate-reader and saves the JSON result
    in the same folder with a .json extension.
    """

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found at '{image_path}'")

    print(f"Sending image: {image_path} to plate-reader...")

    url = ALPR_SERVICE_URL
    files = {
        "upload": open(image_path, "rb")
    }
    data = {
        "regions": ALPR_REGION,
        "direction": "true",
        "mmc": "true",
        "config": '{"mode":"fast", "detection_mode":"vehicle"}'
    }

    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        result_json = response.json()
    except requests.RequestException as e:
        print(f"Error sending request: {e}")
        return

    json_path = os.path.splitext(image_path)[0] + ".json"
    with open(json_path, "w") as json_file:
        json.dump(result_json, json_file, indent=2)

    print(f"Response saved to: {json_path}")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"ALPR Monitor Configuration:")
print(f"  Camera ID: {CAMERA_ID}")
print(f"  Output Directory: {OUTPUT_DIR}")
print(f"  Service URL: {ALPR_SERVICE_URL}")
print(f"  Region: {ALPR_REGION}")
print(f"  Confidence Threshold: {CONFIDENCE_THRESHOLD}")
print(f"  Max Images per Car: {MAX_IMAGES_PER_CAR}")
print(f"  Frame Skip: {FRAME_SKIP}")
print("")

def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

# Load model with tracking
model = YOLO("yolov8n.pt")  # you can replace with yolov8m.pt or yolov8l.pt for better accuracy

# Track images for each car
tracked_images = defaultdict(list)
frame_count = 0

# Open camera
cap = cv2.VideoCapture(CAMERA_ID)
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(frame, persist=True, conf=CONFIDENCE_THRESHOLD, verbose=False)

    if results[0].boxes.id is None:
        frame_count += 1
        continue

    boxes = results[0].boxes.xyxy.cpu().numpy()
    ids = results[0].boxes.id.cpu().numpy().astype(int)
    clss = results[0].boxes.cls.cpu().numpy().astype(int)

    for box, track_id, cls in zip(boxes, ids, clss):
        if cls not in CAR_CLASSES:
            continue

        x1, y1, x2, y2 = map(int, box)
        if x2 - x1 < 50 or y2 - y1 < 50:
            continue  # Skip very small detections

        if frame_count % FRAME_SKIP != 0:
            continue  # Limit capture rate

        car_crop = frame[y1:y2, x1:x2]
        tracked_images[track_id].append(car_crop)

        if len(tracked_images[track_id]) >= MAX_IMAGES_PER_CAR:
            # Evaluate sharpest image
            best_img = max(tracked_images[track_id], key=lambda img: variance_of_laplacian(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)))
            filename = os.path.join(OUTPUT_DIR, f"car_{track_id}.jpg")
            cv2.imwrite(filename, best_img)
            print(f"Saved best image for car #{track_id} to {filename}")
            send_image_to_plate_reader(filename)
            tracked_images.pop(track_id)  # Done with this car

    frame_count += 1

cap.release()
cv2.destroyAllWindows()