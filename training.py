import face_recognition
import os
import pickle

face_encodings = []
face_labels = []

face_dir = "face_dataset"
for user_name in os.listdir(face_dir):
    user_dir = os.path.join(face_dir, user_name)
    if os.path.isdir(user_dir):
        for filename in os.listdir(user_dir):
            image_path = os.path.join(user_dir, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                face_encodings.append(encodings[0])
                face_labels.append(user_name)  # Label with user's name

# Save encodings for recognition
with open("face_encodings.pkl", "wb") as f:
    pickle.dump((face_encodings, face_labels), f)

print("Training completed. Model saved.")