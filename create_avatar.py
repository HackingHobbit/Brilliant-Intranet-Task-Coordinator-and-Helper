import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

def create_avatar(image_path, visemes):
    image = cv2.imread(image_path)
    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    if not results.multi_face_landmarks:
        raise ValueError("No face detected")

    landmarks = results.multi_face_landmarks[0].landmark
    lip_points = np.array([(landmark.x * image.shape[1], landmark.y * image.shape[0]) for landmark in landmarks[48:68]])  # Lip indices

    frames = []
    for viseme in visemes:
        warped_image = image.copy()
        # Warp lips: Simple affine for viseme
        transformation = np.eye(3)
        if viseme == 'A':
            transformation[1,1] = 1.2  # Scale Y
        warped_image = cv2.warpAffine(warped_image, transformation[:2], (image.shape[1], image.shape[0]))
        frames.append(warped_image)

    return frames  # List of images for rendering