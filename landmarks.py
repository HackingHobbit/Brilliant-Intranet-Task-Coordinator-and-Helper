import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)

def detect_landmarks(image_path):
    image = cv2.imread(image_path)
    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if results.multi_face_landmarks:
        return [[p.x, p.y, p.z] for p in results.multi_face_landmarks[0].landmark]
    return []