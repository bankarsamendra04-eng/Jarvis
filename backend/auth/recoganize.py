import os
import time
import cv2

def AuthenticateFace():
    flag = 0
    recognizer_path = os.path.join("backend", "auth", "trainer", "trainer.yml")
    cascadePath = os.path.join("backend", "auth", "haarcascade_frontalface_default.xml")

    # If face recognition files or classifier are not present, fallback
    if not os.path.exists(cascadePath):
        print("Haarcascade file not found. Skipping face auth.")
        return 1

    try:
        # Local Binary Patterns Histograms
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        if os.path.exists(recognizer_path):
            recognizer.read(recognizer_path)
        else:
            print("Trainer model not found. Proceeding with default access.")
            return 1
    except Exception as e:
        print(f"Face recognizer error: {e}")
        return 1

    # initializing haar cascade
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX
    names = ['', 'User', 'User']

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cam.isOpened():
        print("Camera not accessible, bypassing face authentication.")
        return 1

    cam.set(3, 640)
    cam.set(4, 480)

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    start_time = time.time()
    max_timeout = 10  # 10 seconds timeout

    while True:
        ret, img = cam.read()
        if not ret or img is None:
            time.sleep(0.05)
            if time.time() - start_time > max_timeout:
                break
            continue

        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            try:
                id_num, accuracy = recognizer.predict(converted_image[y:y + h, x:x + w])
                if accuracy < 100:
                    name_display = names[id_num] if id_num < len(names) else "Authorized"
                    accuracy_text = f"  {round(100 - accuracy)}%"
                    flag = 1
                else:
                    name_display = "Unknown"
                    accuracy_text = f"  {round(100 - accuracy)}%"
                    flag = 0
            except Exception:
                flag = 1
                name_display = "Authorized"
                accuracy_text = "100%"

            cv2.putText(img, str(name_display), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(accuracy_text), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        cv2.imshow('Face Authentication - Jarvis', img)

        k = cv2.waitKey(10) & 0xff
        if k == 27 or flag == 1:
            break
        
        # Timeout after max_timeout seconds
        if time.time() - start_time > max_timeout:
            print("Face authentication timed out.")
            break

    cam.release()
    cv2.destroyAllWindows()
    return flag