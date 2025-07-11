import cv2
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
import os

# Import MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logging.warning("MediaPipe not available. Facial landmarks will be disabled.")

logger = logging.getLogger(__name__)

class FacialLandmarks:
    """Facial landmarks detection using MediaPipe"""
    
    def __init__(self, static_image_mode: bool = True, max_num_faces: int = 1):
        """
        Initialize facial landmarks detector
        
        Args:
            static_image_mode: Whether to use static image mode
            max_num_faces: Maximum number of faces to detect
        """
        self.static_image_mode = static_image_mode
        self.max_num_faces = max_num_faces
        self.face_mesh = None
        
        # Initialize MediaPipe
        self._init_mediapipe()
    
    def _init_mediapipe(self):
        """Initialize MediaPipe face mesh"""
        try:
            if not MEDIAPIPE_AVAILABLE:
                logger.warning("MediaPipe not available")
                return
            
            mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=self.static_image_mode,
                max_num_faces=self.max_num_faces,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )
            
            logger.info("MediaPipe face mesh initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe: {e}")
            self.face_mesh = None
    
    def detect_landmarks(self, image_path: str) -> List[Dict]:
        """
        Detect facial landmarks in image
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of facial landmarks for each detected face
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return []
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return []
            
            return self._process_image(image)
            
        except Exception as e:
            logger.error(f"Landmark detection failed: {e}")
            return []
    
    def detect_landmarks_from_array(self, image: np.ndarray) -> List[Dict]:
        """
        Detect facial landmarks from numpy array
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of facial landmarks for each detected face
        """
        try:
            return self._process_image(image)
        except Exception as e:
            logger.error(f"Landmark detection from array failed: {e}")
            return []
    
    def _process_image(self, image: np.ndarray) -> List[Dict]:
        """
        Process image to detect facial landmarks
        
        Args:
            image: Input image
            
        Returns:
            List of facial landmarks
        """
        try:
            if self.face_mesh is None:
                logger.warning("MediaPipe face mesh not initialized")
                return []
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect landmarks
            results = self.face_mesh.process(rgb_image)
            
            landmarks_list = []
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    landmarks = self._extract_landmarks(face_landmarks, image.shape)
                    landmarks_list.append(landmarks)
            
            return landmarks_list
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return []
    
    def _extract_landmarks(self, face_landmarks, image_shape: Tuple[int, int, int]) -> Dict:
        """
        Extract landmarks from MediaPipe results
        
        Args:
            face_landmarks: MediaPipe face landmarks
            image_shape: Shape of input image (height, width, channels)
            
        Returns:
            Dictionary containing landmark data
        """
        try:
            height, width = image_shape[:2]
            
            # Extract all landmarks
            landmarks = []
            for landmark in face_landmarks.landmark:
                # Convert normalized coordinates to pixel coordinates
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                z = landmark.z
                
                landmarks.append([x, y, z])
            
            # Extract specific landmark groups
            lip_landmarks = self._get_lip_landmarks(landmarks)
            eye_landmarks = self._get_eye_landmarks(landmarks)
            eyebrow_landmarks = self._get_eyebrow_landmarks(landmarks)
            
            return {
                'all_landmarks': landmarks,
                'lip_landmarks': lip_landmarks,
                'eye_landmarks': eye_landmarks,
                'eyebrow_landmarks': eyebrow_landmarks,
                'image_shape': [width, height],
                'landmark_count': len(landmarks)
            }
            
        except Exception as e:
            logger.error(f"Landmark extraction failed: {e}")
            return {}
    
    def _get_lip_landmarks(self, landmarks: List[List[float]]) -> Dict:
        """Extract lip-related landmarks"""
        # MediaPipe lip landmark indices
        lip_indices = [
            61, 84, 17, 314, 405, 320, 307, 375, 321, 308, 324, 318, 78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308
        ]
        
        lip_landmarks = [landmarks[i] for i in lip_indices if i < len(landmarks)]
        
        return {
            'upper_lip': lip_landmarks[:12],
            'lower_lip': lip_landmarks[12:],
            'all_lip': lip_landmarks
        }
    
    def _get_eye_landmarks(self, landmarks: List[List[float]]) -> Dict:
        """Extract eye-related landmarks"""
        # MediaPipe eye landmark indices
        left_eye_indices = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        right_eye_indices = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        left_eye = [landmarks[i] for i in left_eye_indices if i < len(landmarks)]
        right_eye = [landmarks[i] for i in right_eye_indices if i < len(landmarks)]
        
        return {
            'left_eye': left_eye,
            'right_eye': right_eye,
            'eyes': left_eye + right_eye
        }
    
    def _get_eyebrow_landmarks(self, landmarks: List[List[float]]) -> Dict:
        """Extract eyebrow-related landmarks"""
        # MediaPipe eyebrow landmark indices
        left_eyebrow_indices = [276, 283, 282, 295, 285, 300, 293, 334, 296, 336, 285, 417, 465, 357, 460, 469, 454, 447, 377]
        right_eyebrow_indices = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46, 124, 35, 111, 143, 112, 145, 116, 117, 119]
        
        left_eyebrow = [landmarks[i] for i in left_eyebrow_indices if i < len(landmarks)]
        right_eyebrow = [landmarks[i] for i in right_eyebrow_indices if i < len(landmarks)]
        
        return {
            'left_eyebrow': left_eyebrow,
            'right_eyebrow': right_eyebrow,
            'eyebrows': left_eyebrow + right_eyebrow
        }
    
    def get_face_bounds(self, landmarks: List[List[float]]) -> Dict:
        """
        Get face bounding box from landmarks
        
        Args:
            landmarks: List of landmark coordinates
            
        Returns:
            Face bounding box
        """
        try:
            if not landmarks:
                return {}
            
            # Get bounding box
            x_coords = [landmark[0] for landmark in landmarks]
            y_coords = [landmark[1] for landmark in landmarks]
            
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            return {
                'x_min': x_min,
                'y_min': y_min,
                'x_max': x_max,
                'y_max': y_max,
                'width': x_max - x_min,
                'height': y_max - y_min,
                'center': [(x_min + x_max) // 2, (y_min + y_max) // 2]
            }
            
        except Exception as e:
            logger.error(f"Failed to get face bounds: {e}")
            return {}
    
    def get_lip_contour(self, landmarks: List[List[float]]) -> List[List[float]]:
        """
        Get lip contour for animation
        
        Args:
            landmarks: Lip landmarks
            
        Returns:
            Lip contour points
        """
        try:
            if len(landmarks) < 8:
                return []
            
            # Use outer lip points for contour
            contour_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            contour = [landmarks[i] for i in contour_indices if i < len(landmarks)]
            
            return contour
            
        except Exception as e:
            logger.error(f"Failed to get lip contour: {e}")
            return []
    
    def calculate_lip_openness(self, landmarks: List[List[float]]) -> float:
        """
        Calculate lip openness for animation
        
        Args:
            landmarks: Lip landmarks
            
        Returns:
            Lip openness value (0-1)
        """
        try:
            if len(landmarks) < 12:
                return 0.0
            
            # Use upper and lower lip points
            upper_lip = landmarks[:6]
            lower_lip = landmarks[6:12]
            
            # Calculate average Y coordinates
            upper_y = sum(point[1] for point in upper_lip) / len(upper_lip)
            lower_y = sum(point[1] for point in lower_lip) / len(lower_lip)
            
            # Calculate openness
            openness = abs(upper_y - lower_y)
            
            # Normalize to 0-1 range (adjust based on your needs)
            max_openness = 50  # Adjust this value based on your image scale
            normalized_openness = min(openness / max_openness, 1.0)
            
            return normalized_openness
            
        except Exception as e:
            logger.error(f"Failed to calculate lip openness: {e}")
            return 0.0
    
    def detect_landmarks_video(self, video_path: str, output_path: Optional[str] = None) -> List[Dict]:
        """
        Detect landmarks in video file
        
        Args:
            video_path: Path to video file
            output_path: Optional output video path
            
        Returns:
            List of landmark data for each frame
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return []
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return []
            
            frame_landmarks = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect landmarks in frame
                landmarks = self.detect_landmarks_from_array(frame)
                if landmarks:
                    frame_landmarks.append({
                        'frame': frame_count,
                        'landmarks': landmarks[0] if landmarks else {}
                    })
                
                frame_count += 1
            
            cap.release()
            
            logger.info(f"Processed {frame_count} frames, found landmarks in {len(frame_landmarks)} frames")
            return frame_landmarks
            
        except Exception as e:
            logger.error(f"Video landmark detection failed: {e}")
            return []
    
    def get_model_info(self) -> Dict:
        """Get information about the landmark detection model"""
        info = {
            'mediapipe_available': MEDIAPIPE_AVAILABLE,
            'face_mesh_initialized': self.face_mesh is not None,
            'static_image_mode': self.static_image_mode,
            'max_num_faces': self.max_num_faces
        }
        return info

# Global instance for convenience
_landmark_detector = None

def get_landmark_detector() -> FacialLandmarks:
    """Get global landmark detector instance"""
    global _landmark_detector
    if _landmark_detector is None:
        _landmark_detector = FacialLandmarks()
    return _landmark_detector

def detect_landmarks(image_path: str) -> List[Dict]:
    """
    Detect facial landmarks in image
    
    Args:
        image_path: Path to image file
        
    Returns:
        List of facial landmarks
    """
    detector = get_landmark_detector()
    return detector.detect_landmarks(image_path)

def detect_landmarks_from_array(image: np.ndarray) -> List[Dict]:
    """
    Detect facial landmarks from numpy array
    
    Args:
        image: Input image as numpy array
        
    Returns:
        List of facial landmarks
    """
    detector = get_landmark_detector()
    return detector.detect_landmarks_from_array(image)

if __name__ == "__main__":
    # Test landmark detection
    detector = FacialLandmarks()
    
    # Test with sample image if available
    test_image = "assets/avatar.jpg"
    if os.path.exists(test_image):
        landmarks = detector.detect_landmarks(test_image)
        print(f"Detected {len(landmarks)} faces")
        
        if landmarks:
            face_data = landmarks[0]
            print(f"Landmark count: {face_data.get('landmark_count', 0)}")
            
            # Test lip openness
            lip_landmarks = face_data.get('lip_landmarks', {})
            if lip_landmarks.get('all_lip'):
                openness = detector.calculate_lip_openness(lip_landmarks['all_lip'])
                print(f"Lip openness: {openness:.3f}")
    else:
        print(f"Test image not found: {test_image}")
    
    # Print model info
    info = detector.get_model_info()
    print(f"Model info: {info}") 