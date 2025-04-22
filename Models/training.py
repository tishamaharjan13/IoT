import cv2
import os
import numpy as np

def train_model():
    dataset_path = 'dataset'
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    face_samples = []
    ids = []
    label_map = {}  # To save label-name mapping
    current_id = 0

    for person_name in os.listdir(dataset_path):
        person_path = os.path.join(dataset_path, person_name)
        if not os.path.isdir(person_path):
            continue

        label_map[current_id] = person_name

        for image_name in os.listdir(person_path):
            img_path = os.path.join(person_path, image_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            face = cv2.resize(img, (200, 200))
            face_samples.append(face)
            ids.append(current_id)

        current_id += 1

    recognizer.train(face_samples, np.array(ids))
    recognizer.save('trainer.yml')

    # Save labels
    with open('labels.txt', 'w') as f:
        for id_, name in label_map.items():
            f.write(f"{id_},{name}\n")

    print("[INFO] Training complete. Model saved to trainer.yml.")

# if __name__ == "__main__":
#     train_model()
