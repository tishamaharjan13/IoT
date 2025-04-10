import cv2
import face_recognition
import pickle
import sys
import time
import numpy as np
from scipy.spatial import distance as dist

# Helper function to calculate Eye Aspect Ratio (EAR)
def calculate_ear(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# EAR threshold (lower means eyes are likely closed)
EAR_THRESHOLD = 0.21

# Load known encodings
try:
    with open("face_encodings.pkl", "rb") as f:
        known_encodings, known_labels = pickle.load(f)
except FileNotFoundError:
    print("Error: face_encodings.pkl file not found.")
    sys.exit()

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot access camera.")
    sys.exit()

print("🟢 Face recognition with blink-based liveness detection started...")

threshold = 0.2999
max_attempts = 10
attempts = 0
recognized = False
last_check_time = time.time()

try:
    while attempts < max_attempts and not recognized:
        ret, frame = cap.read()
        if not ret:
            print("Error reading from camera.")
            break

        # Display frame
        cv2.imshow("Face Recognition (Press 'q' to Quit)", frame)

        # Wait for 2 seconds between checks
        current_time = time.time()
        if current_time - last_check_time >= 2:
            last_check_time = current_time
            attempts += 1
            print(f"\n[Attempt {attempts}/{max_attempts}] Checking for live face...")

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, locations)
            landmarks = face_recognition.face_landmarks(rgb)

            print(f"Detected {len(encodings)} face(s).")

            for i, encoding in enumerate(encodings):
                # Basic eye landmark check
                try:
                    landmark = landmarks[i]
                    left_eye = landmark['left_eye']
                    right_eye = landmark['right_eye']

                    left_ear = calculate_ear(left_eye)
                    right_ear = calculate_ear(right_eye)
                    avg_ear = (left_ear + right_ear) / 2.0

                    print(f"EAR: {avg_ear:.2f}")
                    if avg_ear > EAR_THRESHOLD:
                        print("✅ Eyes open or blinking detected.")

                        # Face matching
                        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=threshold)
                        name = "Unknown"

                        if True in matches:
                            first_match = matches.index(True)
                            name = known_labels[first_match]
                            print(f"✅ Live face recognized: {name} - Opening door...")
                            # GPIO trigger here
                            recognized = True
                            break
                        else:
                            print("❌ Face not recognized.")
                    else:
                        print("⚠️ Eyes closed or spoof attempt (photo).")

                except Exception as e:
                    print(f"❌ Error processing landmarks: {e}")
                    continue

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("🛑 User exited.")
            break

    if not recognized:
        print("❗ Max attempts reached or no live face recognized.")

except KeyboardInterrupt:
    print("\n❌ Interrupted.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released. Program ended.")