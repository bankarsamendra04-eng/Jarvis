import cv2
import numpy as np
from PIL import Image
import os

sample_path = os.path.join("backend", "auth", "samples")
trainer_dir = os.path.join("backend", "auth", "trainer")
trainer_file = os.path.join(trainer_dir, "trainer.yml")
cascade_path = os.path.join("backend", "auth", "haarcascade_frontalface_default.xml")

if not os.path.exists(trainer_dir):
    os.makedirs(trainer_dir, exist_ok=True)

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cascade_path)

def Images_And_Labels(path):
    if not os.path.exists(path):
        return [], []
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(('.jpg', '.png', '.jpeg'))]     
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        gray_img = Image.open(imagePath).convert('L')
        img_arr = np.array(gray_img, 'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_arr)

        if len(faces) > 0:
            for (x, y, w, h) in faces:
                faceSamples.append(img_arr[y:y + h, x:x + w])
                ids.append(id)
        else:
            faceSamples.append(img_arr)
            ids.append(id)

    return faceSamples, ids

print("Training faces. Please wait a few seconds...")
faces, ids = Images_And_Labels(sample_path)

if len(faces) > 0 and len(ids) > 0:
    recognizer.train(faces, np.array(ids))
    recognizer.write(trainer_file)
    print(f"Model trained successfully on {len(faces)} samples and saved to {trainer_file}")
else:
    print("No face samples found in backend/auth/samples. Please run sample.py first.")