import cv2
import os


def capture_face(name):
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("[ERROR] Could not open webcam.")
        return

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if detector.empty():
        print("[ERROR] Failed to load face cascade classifier.")
        return

    dataset_path = 'dataset'
    user_folder = os.path.join(dataset_path, name)

    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    count = 0
    print("📷 Starting face capture. Press ESC to stop.")
    
    while True:
        ret, img = cam.read()
        if not ret:
            print("[ERROR] Failed to capture frame from camera.")
            break

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            cv2.putText(img, "No face detected", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            for (x, y, w, h) in faces:
                face = gray[y:y+h, x:x+w]
                face = cv2.resize(face, (200, 200))
                filename = f"{user_folder}/{count}.jpg"
                cv2.imwrite(filename, face)
                count += 1
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                print(f"[INFO] Captured image: {filename}")

        cv2.imshow('Capturing Faces', img)
        if cv2.waitKey(1) == 27 or count >= 20:
            print("✅ Capture completed.")
            break

    cam.release()
    cv2.destroyAllWindows()

# # ✅ Run it
# if __name__ == "__main__":
#     user_name = input("Enter your name: ")
#     capture_face(user_name)