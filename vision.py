from ultralytics import YOLO
import face_recognition
import cv2

model = YOLO('yolov8n.pt')

def analyze_image(image_path, use_webcam=False):
    if use_webcam:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        img = frame if ret else None
        cap.release()
    else:
        img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Invalid image")

    # Objects
    results = model(img)
    objects = [r.names[int(c)] for r in results for c in r.boxes.cls]

    # Faces
    faces = face_recognition.face_locations(img)

    return {'objects': objects, 'faces': len(faces)}