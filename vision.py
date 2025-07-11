import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import os

# Import optional dependencies
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

logger = logging.getLogger(__name__)

class VisionAnalyzer:
    """Computer vision analyzer for object detection and face recognition"""
    
    def __init__(self, yolo_model: str = 'yolov8n.pt'):
        """
        Initialize vision analyzer
        
        Args:
            yolo_model: Path to YOLO model file
        """
        self.yolo_model = yolo_model
        self.yolo_model_instance = None
        self.known_faces = []
        self.known_names = []
        
        # Initialize models
        self._init_models()
    
    def _init_models(self):
        """Initialize YOLO and face recognition models"""
        try:
            # Initialize YOLO
            if YOLO_AVAILABLE:
                self.yolo_model_instance = YOLO(self.yolo_model)
                logger.info(f"YOLO model loaded: {self.yolo_model}")
            else:
                logger.warning("YOLO not available. Object detection will be disabled.")
            
            # Face recognition is loaded on-demand
            if not FACE_RECOGNITION_AVAILABLE:
                logger.warning("face_recognition not available. Face detection will be disabled.")
                
        except Exception as e:
            logger.error(f"Failed to initialize vision models: {e}")
    
    def analyze_image(self, image_path: str, use_webcam: bool = False) -> Dict:
        """
        Analyze image for objects and faces
        
        Args:
            image_path: Path to image file
            use_webcam: Whether to use webcam instead of file
            
        Returns:
            Analysis results dictionary
        """
        try:
            # Load image
            if use_webcam:
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                
                if not ret:
                    return {'error': 'Failed to capture from webcam'}
                
                image = frame
            else:
                if not os.path.exists(image_path):
                    return {'error': f'Image file not found: {image_path}'}
                
                image = cv2.imread(image_path)
                if image is None:
                    return {'error': f'Failed to load image: {image_path}'}
            
            results = {
                'objects': [],
                'faces': [],
                'face_count': 0,
                'image_size': image.shape[:2],
                'analysis_time': 0
            }
            
            # Object detection
            if self.yolo_model_instance:
                object_results = self._detect_objects(image)
                results['objects'] = object_results
            
            # Face detection and recognition
            if FACE_RECOGNITION_AVAILABLE:
                face_results = self._detect_faces(image)
                results['faces'] = face_results['faces']
                results['face_count'] = face_results['face_count']
            
            return results
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {'error': str(e)}
    
    def _detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        Detect objects in image using YOLO
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected objects
        """
        try:
            if not self.yolo_model_instance:
                return []
            
            # Run YOLO detection
            results = self.yolo_model_instance(image)
            
            objects = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get confidence and class
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        class_name = result.names[class_id]
                        
                        objects.append({
                            'class': class_name,
                            'confidence': confidence,
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                        })
            
            # Sort by confidence
            objects.sort(key=lambda x: x['confidence'], reverse=True)
            
            return objects
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return []
    
    def _detect_faces(self, image: np.ndarray) -> Dict:
        """
        Detect and recognize faces in image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Face detection results
        """
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                return {'faces': [], 'face_count': 0}
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face locations
            face_locations = face_recognition.face_locations(rgb_image)
            
            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            faces = []
            for i, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
                # Check if face matches known faces
                name = "Unknown"
                if self.known_faces:
                    matches = face_recognition.compare_faces(self.known_faces, face_encoding)
                    if True in matches:
                        match_index = matches.index(True)
                        name = self.known_names[match_index]
                
                # Get face landmarks (simplified)
                top, right, bottom, left = face_location
                center_x = (left + right) // 2
                center_y = (top + bottom) // 2
                
                faces.append({
                    'id': i,
                    'name': name,
                    'bbox': [left, top, right, bottom],
                    'center': [center_x, center_y],
                    'size': [right - left, bottom - top]
                })
            
            return {
                'faces': faces,
                'face_count': len(faces)
            }
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return {'faces': [], 'face_count': 0}
    
    def add_known_face(self, image_path: str, name: str) -> bool:
        """
        Add a known face for recognition
        
        Args:
            image_path: Path to face image
            name: Name of the person
            
        Returns:
            True if successful
        """
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                logger.warning("Face recognition not available")
                return False
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return False
            
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image)
            if not face_locations:
                logger.error("No faces found in image")
                return False
            
            # Get encoding of first face
            face_encoding = face_recognition.face_encodings(rgb_image, face_locations)[0]
            
            # Add to known faces
            self.known_faces.append(face_encoding)
            self.known_names.append(name)
            
            logger.info(f"Added known face: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add known face: {e}")
            return False
    
    def remove_known_face(self, name: str) -> bool:
        """
        Remove a known face
        
        Args:
            name: Name of the person to remove
            
        Returns:
            True if successful
        """
        try:
            if name in self.known_names:
                index = self.known_names.index(name)
                self.known_names.pop(index)
                self.known_faces.pop(index)
                logger.info(f"Removed known face: {name}")
                return True
            else:
                logger.warning(f"Known face not found: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove known face: {e}")
            return False
    
    def get_known_faces(self) -> List[str]:
        """Get list of known face names"""
        return self.known_names.copy()
    
    def clear_known_faces(self):
        """Clear all known faces"""
        self.known_faces.clear()
        self.known_names.clear()
        logger.info("Cleared all known faces")
    
    def detect_objects_in_webcam(self, duration: int = 5) -> Dict:
        """
        Detect objects in webcam stream
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Detection results
        """
        try:
            if not self.yolo_model_instance:
                return {'error': 'YOLO model not available'}
            
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return {'error': 'Failed to open webcam'}
            
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            all_objects = []
            frame_count = 0
            
            # Record for specified duration
            start_time = cv2.getTickCount()
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Detect objects in frame
                objects = self._detect_objects(frame)
                all_objects.extend(objects)
                frame_count += 1
                
                # Check if duration exceeded
                elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
                if elapsed >= duration:
                    break
            
            cap.release()
            
            # Aggregate results
            object_counts = {}
            for obj in all_objects:
                class_name = obj['class']
                object_counts[class_name] = object_counts.get(class_name, 0) + 1
            
            return {
                'objects_detected': object_counts,
                'total_frames': frame_count,
                'duration': elapsed,
                'fps': frame_count / elapsed if elapsed > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Webcam object detection failed: {e}")
            return {'error': str(e)}
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        info = {
            'yolo_available': YOLO_AVAILABLE,
            'yolo_model': self.yolo_model if self.yolo_model_instance else None,
            'face_recognition_available': FACE_RECOGNITION_AVAILABLE,
            'known_faces_count': len(self.known_faces)
        }
        return info

# Global instance for convenience
_vision_analyzer = None

def get_vision_analyzer() -> VisionAnalyzer:
    """Get global vision analyzer instance"""
    global _vision_analyzer
    if _vision_analyzer is None:
        _vision_analyzer = VisionAnalyzer()
    return _vision_analyzer

def analyze_image(image_path: str, use_webcam: bool = False) -> Dict:
    """
    Analyze image for objects and faces
    
    Args:
        image_path: Path to image file
        use_webcam: Whether to use webcam instead of file
        
    Returns:
        Analysis results
    """
    analyzer = get_vision_analyzer()
    return analyzer.analyze_image(image_path, use_webcam)

def detect_objects_in_webcam(duration: int = 5) -> Dict:
    """
    Detect objects in webcam stream
    
    Args:
        duration: Recording duration in seconds
        
    Returns:
        Detection results
    """
    analyzer = get_vision_analyzer()
    return analyzer.detect_objects_in_webcam(duration)

if __name__ == "__main__":
    # Test vision analyzer
    analyzer = VisionAnalyzer()
    
    # Test with sample image if available
    test_image = "assets/avatar.jpg"
    if os.path.exists(test_image):
        results = analyzer.analyze_image(test_image)
        print(f"Image analysis results: {results}")
    else:
        print(f"Test image not found: {test_image}")
    
    # Print model info
    info = analyzer.get_model_info()
    print(f"Model info: {info}") 