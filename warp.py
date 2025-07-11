import cv2
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
import os
import json

logger = logging.getLogger(__name__)

class LipWarping:
    """Lip sync warping for avatar animation"""
    
    def __init__(self):
        """Initialize lip warping system"""
        self.viseme_shapes = self._load_viseme_shapes()
        self.logger = logging.getLogger(__name__)
    
    def _load_viseme_shapes(self) -> Dict[str, Dict]:
        """Load viseme shape definitions"""
        # Define basic viseme shapes for lip deformation
        visemes = {
            'A': {  # Open mouth
                'lip_openness': 0.8,
                'lip_width': 1.2,
                'lip_height': 1.5
            },
            'E': {  # Slight open
                'lip_openness': 0.4,
                'lip_width': 1.1,
                'lip_height': 1.2
            },
            'I': {  # Wide smile
                'lip_openness': 0.3,
                'lip_width': 1.3,
                'lip_height': 1.1
            },
            'O': {  # Rounded lips
                'lip_openness': 0.6,
                'lip_width': 0.9,
                'lip_height': 1.3
            },
            'U': {  # Pursed lips
                'lip_openness': 0.2,
                'lip_width': 0.8,
                'lip_height': 1.4
            },
            'F': {  # Lower lip bite
                'lip_openness': 0.1,
                'lip_width': 1.0,
                'lip_height': 1.0
            },
            'M': {  # Closed lips
                'lip_openness': 0.0,
                'lip_width': 1.0,
                'lip_height': 1.0
            },
            'B': {  # Slight open
                'lip_openness': 0.3,
                'lip_width': 1.0,
                'lip_height': 1.1
            },
            'P': {  # Pucker
                'lip_openness': 0.1,
                'lip_width': 0.7,
                'lip_height': 1.2
            },
            'R': {  # Rounded
                'lip_openness': 0.5,
                'lip_width': 0.8,
                'lip_height': 1.3
            },
            'S': {  # Slight open
                'lip_openness': 0.2,
                'lip_width': 1.1,
                'lip_height': 1.0
            },
            'T': {  # Tongue touch
                'lip_openness': 0.4,
                'lip_width': 1.0,
                'lip_height': 1.1
            },
            'D': {  # Dental
                'lip_openness': 0.3,
                'lip_width': 1.0,
                'lip_height': 1.0
            },
            'L': {  # Lateral
                'lip_openness': 0.4,
                'lip_width': 1.2,
                'lip_height': 1.1
            },
            'N': {  # Nasal
                'lip_openness': 0.2,
                'lip_width': 1.0,
                'lip_height': 1.0
            },
            'G': {  # Velar
                'lip_openness': 0.5,
                'lip_width': 1.0,
                'lip_height': 1.2
            },
            'K': {  # Velar stop
                'lip_openness': 0.4,
                'lip_width': 1.0,
                'lip_height': 1.1
            },
            'H': {  # Glottal
                'lip_openness': 0.6,
                'lip_width': 1.1,
                'lip_height': 1.3
            },
            'W': {  # Labial-velar
                'lip_openness': 0.3,
                'lip_width': 0.8,
                'lip_height': 1.2
            },
            'Y': {  # Palatal
                'lip_openness': 0.4,
                'lip_width': 1.1,
                'lip_height': 1.1
            }
        }
        
        return visemes
    
    def warp_lips(self, image_path: str, visemes: List[str], 
                  landmarks: Optional[List[Dict]] = None) -> List[np.ndarray]:
        """
        Warp lips based on viseme sequence
        
        Args:
            image_path: Path to avatar image
            visemes: List of viseme codes
            landmarks: Optional facial landmarks
            
        Returns:
            List of warped image frames
        """
        try:
            # Load image
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            frames = []
            
            for viseme in visemes:
                # Warp image for this viseme
                warped_frame = self._warp_frame(image, viseme, landmarks)
                frames.append(warped_frame)
            
            self.logger.info(f"Generated {len(frames)} warped frames for {len(visemes)} visemes")
            return frames
            
        except Exception as e:
            self.logger.error(f"Lip warping failed: {e}")
            return []
    
    def _warp_frame(self, image: np.ndarray, viseme: str, 
                    landmarks: Optional[List[Dict]] = None) -> np.ndarray:
        """
        Warp a single frame for a viseme
        
        Args:
            image: Input image
            viseme: Viseme code
            landmarks: Facial landmarks
            
        Returns:
            Warped image
        """
        try:
            # Get viseme shape parameters
            viseme_params = self.viseme_shapes.get(viseme.upper(), self.viseme_shapes['A'])
            
            # Create warped image
            warped_image = image.copy()
            
            if landmarks and len(landmarks) > 0:
                # Use provided landmarks for precise warping
                warped_image = self._warp_with_landmarks(image, viseme_params, landmarks[0])
            else:
                # Use default lip region warping
                warped_image = self._warp_default_region(image, viseme_params)
            
            return warped_image
            
        except Exception as e:
            self.logger.error(f"Frame warping failed: {e}")
            return image
    
    def _warp_with_landmarks(self, image: np.ndarray, viseme_params: Dict, 
                            landmarks: Dict) -> np.ndarray:
        """
        Warp image using facial landmarks
        
        Args:
            image: Input image
            viseme_params: Viseme parameters
            landmarks: Facial landmarks
            
        Returns:
            Warped image
        """
        try:
            # Get lip landmarks
            lip_landmarks = landmarks.get('lip_landmarks', {})
            all_lip = lip_landmarks.get('all_lip', [])
            
            if not all_lip:
                # Fallback to default warping
                return self._warp_default_region(image, viseme_params)
            
            # Convert landmarks to numpy array
            lip_points = np.array(all_lip, dtype=np.float32)
            
            # Apply viseme transformations
            transformed_points = self._apply_viseme_transform(lip_points, viseme_params)
            
            # Create transformation matrix
            if len(lip_points) >= 4:
                # Use perspective transform for more realistic warping
                matrix = cv2.getPerspectiveTransform(lip_points[:4], transformed_points[:4])
                warped = cv2.warpPerspective(image, matrix, (image.shape[1], image.shape[0]))
            else:
                # Use affine transform as fallback
                matrix = cv2.getAffineTransform(lip_points[:3], transformed_points[:3])
                warped = cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]))
            
            return warped
            
        except Exception as e:
            self.logger.error(f"Landmark-based warping failed: {e}")
            return image
    
    def _warp_default_region(self, image: np.ndarray, viseme_params: Dict) -> np.ndarray:
        """
        Warp default lip region when landmarks are not available
        
        Args:
            image: Input image
            viseme_params: Viseme parameters
            
        Returns:
            Warped image
        """
        try:
            height, width = image.shape[:2]
            
            # Define default lip region (center of image)
            lip_center_x = width // 2
            lip_center_y = height // 2 + height // 4  # Slightly below center
            
            lip_width = width // 6
            lip_height = height // 8
            
            # Calculate warped region
            openness = viseme_params.get('lip_openness', 0.5)
            width_factor = viseme_params.get('lip_width', 1.0)
            height_factor = viseme_params.get('lip_height', 1.0)
            
            # Create source points
            src_points = np.array([
                [lip_center_x - lip_width//2, lip_center_y - lip_height//2],
                [lip_center_x + lip_width//2, lip_center_y - lip_height//2],
                [lip_center_x + lip_width//2, lip_center_y + lip_height//2],
                [lip_center_x - lip_width//2, lip_center_y + lip_height//2]
            ], dtype=np.float32)
            
            # Create destination points with warping
            warped_width = int(lip_width * width_factor)
            warped_height = int(lip_height * height_factor)
            
            # Adjust height based on openness
            if openness > 0.5:
                warped_height = int(warped_height * (1 + openness))
            
            dst_points = np.array([
                [lip_center_x - warped_width//2, lip_center_y - warped_height//2],
                [lip_center_x + warped_width//2, lip_center_y - warped_height//2],
                [lip_center_x + warped_width//2, lip_center_y + warped_height//2],
                [lip_center_x - warped_width//2, lip_center_y + warped_height//2]
            ], dtype=np.float32)
            
            # Apply perspective transform
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            warped = cv2.warpPerspective(image, matrix, (width, height))
            
            return warped
            
        except Exception as e:
            self.logger.error(f"Default region warping failed: {e}")
            return image
    
    def _apply_viseme_transform(self, points: np.ndarray, viseme_params: Dict) -> np.ndarray:
        """
        Apply viseme transformation to landmark points
        
        Args:
            points: Input landmark points
            viseme_params: Viseme parameters
            
        Returns:
            Transformed points
        """
        try:
            transformed_points = points.copy()
            
            # Get parameters
            openness = viseme_params.get('lip_openness', 0.5)
            width_factor = viseme_params.get('lip_width', 1.0)
            height_factor = viseme_params.get('lip_height', 1.0)
            
            # Calculate center of lip region
            center_x = np.mean(points[:, 0])
            center_y = np.mean(points[:, 1])
            
            # Apply transformations
            for i in range(len(transformed_points)):
                # Scale from center
                x, y = transformed_points[i]
                
                # Apply width scaling
                x = center_x + (x - center_x) * width_factor
                
                # Apply height scaling based on openness
                if openness > 0.5:
                    # Open mouth: expand vertically
                    y = center_y + (y - center_y) * height_factor * (1 + openness)
                else:
                    # Closed mouth: contract vertically
                    y = center_y + (y - center_y) * height_factor * (1 - openness * 0.5)
                
                transformed_points[i] = [x, y]
            
            return transformed_points
            
        except Exception as e:
            self.logger.error(f"Viseme transform failed: {e}")
            return points
    
    def create_viseme_sequence(self, text: str, frame_rate: int = 30) -> List[str]:
        """
        Create viseme sequence from text
        
        Args:
            text: Input text
            frame_rate: Target frame rate
            
        Returns:
            List of viseme codes
        """
        try:
            # Simple phoneme to viseme mapping
            phoneme_to_viseme = {
                'a': 'A', 'e': 'E', 'i': 'I', 'o': 'O', 'u': 'U',
                'f': 'F', 'v': 'F', 'm': 'M', 'b': 'B', 'p': 'P',
                'r': 'R', 's': 'S', 't': 'T', 'd': 'D', 'l': 'L',
                'n': 'N', 'g': 'G', 'k': 'K', 'h': 'H', 'w': 'W',
                'y': 'Y'
            }
            
            # Convert text to lowercase and extract phonemes
            text_lower = text.lower()
            visemes = []
            
            for char in text_lower:
                if char.isalpha():
                    viseme = phoneme_to_viseme.get(char, 'A')
                    # Add viseme for multiple frames based on frame rate
                    frames_per_viseme = max(1, frame_rate // 10)  # 10 visemes per second
                    visemes.extend([viseme] * frames_per_viseme)
                else:
                    # Add neutral viseme for non-alphabetic characters
                    visemes.extend(['A'] * (frame_rate // 20))
            
            return visemes
            
        except Exception as e:
            self.logger.error(f"Viseme sequence creation failed: {e}")
            return ['A'] * frame_rate  # Default sequence
    
    def save_frames(self, frames: List[np.ndarray], output_dir: str, 
                   base_name: str = "frame") -> List[str]:
        """
        Save warped frames to files
        
        Args:
            frames: List of image frames
            output_dir: Output directory
            base_name: Base filename
            
        Returns:
            List of saved file paths
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            saved_paths = []
            for i, frame in enumerate(frames):
                filename = f"{base_name}_{i:04d}.png"
                filepath = os.path.join(output_dir, filename)
                
                cv2.imwrite(filepath, frame)
                saved_paths.append(filepath)
            
            self.logger.info(f"Saved {len(saved_paths)} frames to {output_dir}")
            return saved_paths
            
        except Exception as e:
            self.logger.error(f"Failed to save frames: {e}")
            return []
    
    def create_video(self, frames: List[np.ndarray], output_path: str, 
                    frame_rate: int = 30) -> bool:
        """
        Create video from warped frames
        
        Args:
            frames: List of image frames
            output_path: Output video path
            frame_rate: Video frame rate
            
        Returns:
            True if successful
        """
        try:
            if not frames:
                return False
            
            height, width = frames[0].shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, frame_rate, (width, height))
            
            # Write frames
            for frame in frames:
                out.write(frame)
            
            out.release()
            
            self.logger.info(f"Video created: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create video: {e}")
            return False
    
    def get_viseme_info(self) -> Dict:
        """Get information about available visemes"""
        return {
            'available_visemes': list(self.viseme_shapes.keys()),
            'viseme_count': len(self.viseme_shapes),
            'default_viseme': 'A'
        }

# Global instance for convenience
_warping = None

def get_warping() -> LipWarping:
    """Get global warping instance"""
    global _warping
    if _warping is None:
        _warping = LipWarping()
    return _warping

def warp_lips(image_path: str, visemes: List[str], 
              landmarks: Optional[List[Dict]] = None) -> List[np.ndarray]:
    """
    Warp lips based on viseme sequence
    
    Args:
        image_path: Path to avatar image
        visemes: List of viseme codes
        landmarks: Optional facial landmarks
        
    Returns:
        List of warped image frames
    """
    warping = get_warping()
    return warping.warp_lips(image_path, visemes, landmarks)

if __name__ == "__main__":
    # Test lip warping
    warping = LipWarping()
    
    # Test with sample image if available
    test_image = "assets/avatar.jpg"
    if os.path.exists(test_image):
        # Create test viseme sequence
        visemes = ['A', 'E', 'I', 'O', 'U', 'A']
        
        # Test warping
        frames = warping.warp_lips(test_image, visemes)
        print(f"Generated {len(frames)} warped frames")
        
        # Test viseme sequence creation
        text = "Hello world"
        sequence = warping.create_viseme_sequence(text)
        print(f"Created viseme sequence: {sequence[:10]}...")
    else:
        print(f"Test image not found: {test_image}")
    
    # Print viseme info
    info = warping.get_viseme_info()
    print(f"Viseme info: {info}") 