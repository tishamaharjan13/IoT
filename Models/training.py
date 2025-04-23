import cv2
import os
import numpy as np

def train_model():
    dataset_path = 'dataset'
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Initialize empty training data
    face_samples = []
    ids = []
    label_map = {}
    current_id = 0

    # Check if dataset directory exists
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    # Check if there are any person folders
    person_folders = [f for f in os.listdir(dataset_path) 
                     if os.path.isdir(os.path.join(dataset_path, f))]
    
    if not person_folders:
        # No users in system - create empty model and labels
        print("[INFO] No users in system. Creating empty model.")
        with open('labels.txt', 'w') as f:
            pass  # Empty file
        recognizer.write('trainer.yml')  # Create empty model
        return True

    # Process existing users
    for person_name in person_folders:
        person_path = os.path.join(dataset_path, person_name)
        images_added = False

        # Process each image in the person's folder
        for image_name in os.listdir(person_path):
            img_path = os.path.join(person_path, image_name)
            try:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue

                # Resize and add to training data
                face = cv2.resize(img, (200, 200))
                face_samples.append(face)
                ids.append(current_id)
                images_added = True
            except Exception as e:
                print(f"[WARNING] Error processing {img_path}: {str(e)}")
                continue

        if images_added:
            label_map[current_id] = person_name
            current_id += 1
        else:
            print(f"[WARNING] No valid images found for {person_name}. Skipping.")

    # Handle training
    try:
        if len(face_samples) > 0:
            recognizer.train(face_samples, np.array(ids))
            print("[INFO] Model trained with available data.")
        else:
            print("[INFO] No valid training data. Creating empty model.")
        
        recognizer.save('trainer.yml')
        
        with open('labels.txt', 'w') as f:
            for id_, name in label_map.items():
                f.write(f"{id_},{name}\n")
        
        print("[INFO] Training data updated successfully.")
        return True
        
    except Exception as e:
        print(f"[ERROR] Training failed: {str(e)}")
        return False