import cv2
import time
import pyttsx3
import hmac
import hashlib
import base64
import requests

# Initialize the speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def load_labels():
    labels = {}
    try:
        with open("labels.txt", "r") as f:
            for line in f:
                id_str, name = line.strip().split(",", 1)
                labels[int(id_str)] = name
    except Exception as e:
        print("[ERROR] Failed to load labels:", e)
    return labels

def recognize():
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trainer.yml")
    except Exception as e:
        print("[ERROR] Could not load model:", e)
        speak("Face recognition model could not be loaded.")
        return False

    labels = load_labels()
    if not labels:
        print("[ERROR] No labels found.")
        speak("No labels were found.")
        return False

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    print("🔍 Recognizing... (Press ESC to exit)")
    speak("Initializing face recognition. Please look at the camera.")

    recognized_name = None
    access_granted = False
    start_time = time.time()

    while time.time() - start_time < 15:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.equalizeHist(face)
            face = cv2.resize(face, (200, 200))

            id_, conf = recognizer.predict(face)
            print(f"[DEBUG] ID: {id_}, Confidence: {conf:.2f}")

            if conf < 55:  # Lower confidence means better match
                recognized_name = labels.get(id_, "Unknown")
                label_text = f"{recognized_name} ({int(conf)}%)"
                access_granted = True
            else:
                label_text = "Unknown person"

            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, label_text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) == 27 or access_granted:  # ESC key or successful recognition
            break

    cap.release()
    cv2.destroyAllWindows()

    if access_granted and recognized_name:
        message = f"Access granted. Welcome, {recognized_name}."
        print(message)
        speak(message)
        return True
    else:
        message = "Access denied. Face not recognized."
        data = {'key': 'value'}
        headers = {'Content-Type': 'application/json'}
        response = requests.post('https://smsapi.bizmessages.com/v1/sms/send', json=data, headers=headers)
        print(message)
        speak(message)
        return False

if __name__ == "__main__":
    try:
        while True:
            print("\n🔁 Starting new recognition cycle...")
            result = recognize()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n👋 Program exited by user.")
        speak("Program exited. Goodbye.")
