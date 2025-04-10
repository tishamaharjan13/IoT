import cv2
import os
import time
import pickle

# Create directory for storing images
face_dir = "face_dataset"
os.makedirs(face_dir, exist_ok=True)

# Load OpenCV's face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Get the user's name
user_name = input("Enter your name: ")

# Create a subdirectory for the user
user_dir = os.path.join(face_dir, user_name)
os.makedirs(user_dir, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Cannot access camera.")
    exit()

print(f"Capturing images for {user_name}... Look at the camera.")

count = 0
start_time = time.time()

while time.time() - start_time < 30:  # Capture for 30 seconds
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]
        face_path = os.path.join(user_dir, f"face_{count}.jpg")
        cv2.imwrite(face_path, face)
        count += 1
        print(f"Saved: {face_path}")

    cv2.imshow("Face Capture", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):  # Press 'q' to quit early
        break

cap.release()
cv2.destroyAllWindows()
print("Face capture completed.")