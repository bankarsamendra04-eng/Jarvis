import cv2
import os

sample_dir = os.path.join("backend", "auth", "samples")
cascade_path = os.path.join("backend", "auth", "haarcascade_frontalface_default.xml")

if not os.path.exists(sample_dir):
    os.makedirs(sample_dir, exist_ok=True)

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cam.set(3, 640)
cam.set(4, 480)

detector = cv2.CascadeClassifier(cascade_path)

face_id = input("Enter a Numeric user ID here (e.g., 1, 2): ")
print("Taking samples, look directly at the camera...")
count = 0

while True:
    ret, img = cam.read()
    if not ret or img is None:
        continue

    converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(converted_image, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        count += 1
        sample_file = os.path.join(sample_dir, f"face.{face_id}.{count}.jpg")
        cv2.imwrite(sample_file, converted_image[y:y + h, x:x + w])
        cv2.imshow('Face Sampling - Press ESC to stop', img)

    k = cv2.waitKey(100) & 0xff
    if k == 27 or count >= 50:
        break

print(f"Captured {count} samples. Closing camera...")
cam.release()
cv2.destroyAllWindows()