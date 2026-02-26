import cv2
import csv
import os
import time
import subprocess
from datetime import datetime

# CONFIG
CSV_FILE = "attendance_logs.csv"
PHOTO_FOLDER = "detected_faces"
LOG_COOLDOWN_SECONDS = 30
AUTO_STOP_AFTER_SECONDS = 10

os.makedirs(PHOTO_FOLDER, exist_ok=True)

# Create CSV headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Person", "Confidence", "Timestamp", "Photo_File"])

print("Starting Warehouse AI Attendance Recorder...")
print(f"Auto-stop after {AUTO_STOP_AFTER_SECONDS} seconds.")
print("Press ESC to stop early.\n")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open webcam.")
    exit()

try:
    face_detector = cv2.FaceDetectorYN.create(
        "face_detection_yunet_2023mar.onnx", "", (640, 480), 0.7, 0.3, 5000
    )
    print("Face detector loaded.\n")
except Exception as e:
    print("Failed to load model:", e)
    exit()

start_time = time.time()
last_log_time = 0
person_counter = 0

while cap.isOpened():
    if time.time() - start_time >= AUTO_STOP_AFTER_SECONDS:
        print(f"\nAuto-stopped after {AUTO_STOP_AFTER_SECONDS} seconds.")
        break

    success, image = cap.read()
    if not success:
        break

    h, w = image.shape[:2]
    face_detector.setInputSize((w, h))
    _, faces = face_detector.detect(image)

    if faces is not None and len(faces) > 0:
        num_faces = len(faces)
        print(f"Detected {num_faces} face(s)")

        now = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if now - last_log_time >= LOG_COOLDOWN_SECONDS:
            last_log_time = now

            photo_name = f"batch_{timestamp.replace(':', '-')}.jpg"
            photo_path = os.path.join(PHOTO_FOLDER, photo_name)
            cv2.imwrite(photo_path, image)

            for i, face in enumerate(faces):
                person_counter += 1
                conf = float(face[4]) * 100
                conf_text = f"{conf:.1f}%"

                x, y, w, h = face[:4].astype(int)
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, f"Person {person_counter} - {conf_text}", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                try:
                    with open(CSV_FILE, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([f"Person {person_counter}", conf_text, timestamp, photo_name])
                    print(f"  Logged Person {person_counter} - {conf_text}")
                except PermissionError:
                    print("  CSV skipped (close Excel if open)")
                except Exception as e:
                    print(f"  CSV error: {e}")

    cv2.imshow("Warehouse AI Recorder - Stops in 10s", image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

print("\nRecording complete.")
print(f"Total people detected: {person_counter}")

# Auto-open photo folder and CSV
print("Opening photos folder and attendance log...")
try:
    os.startfile(os.path.abspath(PHOTO_FOLDER))
    time.sleep(1)
    os.startfile(os.path.abspath(CSV_FILE))
except:
    print("Could not auto-open. Open manually:")
    print(f"  Photos: {os.path.abspath(PHOTO_FOLDER)}")
    print(f"  Logs: {os.path.abspath(CSV_FILE)}")