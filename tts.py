import os
import tempfile
import logging
from typing import Optional
import wave
import numpy as np

logger = logging.getLogger(__name__)

# Global voice model
_voice = None

def get_piper_voice():
    """Get or load Piper voice model"""
    global _voice
    if _voice is None:
        try:
            from piper import PiperVoice
            
            # Try to load the voice model
            voice_path = "models/en_US-amy-medium.onnx"
            config_path = "models/en_US-amy-medium.onnx.json"
            
            # Check if model files exist
            if not os.path.exists(voice_path):
                logger.warning(f"Piper voice model not found at {voice_path}")
                logger.info("Please download the model from: https://huggingface.co/rhasspy/piper-voices")
                raise FileNotFoundError(f"Voice model not found: {voice_path}")
            
            logger.info("Loading Piper voice model...")
            _voice = PiperVoice.load(voice_path, config_path)
            logger.info("Piper voice model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Piper voice model: {e}")
            raise
    return _voice

def text_to_speech(text: str, output_path: Optional[str] = None) -> str:
    """
    Convert text to speech using Piper
    
    Args:
        text: Text to convert to speech
        output_path: Optional output path for audio file
        
    Returns:
        Path to generated audio file
    """
    try:
        if not text.strip():
            raise ValueError("Empty text provided")
        
        # Load voice model
        voice = get_piper_voice()
        
        # Generate speech
        logger.info(f"Generating speech for: {text[:50]}...")
        audio_data = voice.synthesize(text)
        
        # Determine output path
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                output_path = temp_file.name
        
        # Save as WAV file
        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(22050)  # Sample rate
            wf.writeframes(audio_data)
        
        logger.info(f"Speech generated successfully: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Text-to-speech failed: {e}")
        raise

def text_to_speech_data(text: str) -> bytes:
    """
    Convert text to speech and return as audio data
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Audio data as bytes
    """
    try:
        # Generate speech to temporary file
        temp_path = text_to_speech(text)
        
        # Read audio data
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return audio_data
        
    except Exception as e:
        logger.error(f"Text-to-speech data generation failed: {e}")
        raise

def list_available_voices() -> list:
    """
    List available voice models
    
    Returns:
        List of available voice model paths
    """
    try:
        models_dir = "models"
        if not os.path.exists(models_dir):
            return []
        
        voices = []
        for file in os.listdir(models_dir):
            if file.endswith('.onnx'):
                voices.append(os.path.join(models_dir, file))
        
        return voices
        
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        return []

def download_voice_model(voice_name: str = "en_US-amy-medium") -> bool:
    """
    Download a voice model from Hugging Face
    
    Args:
        voice_name: Name of the voice model to download
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import requests
        import zipfile
        
        # Create models directory
        os.makedirs("models", exist_ok=True)
        
        # Download URL
        base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
        voice_url = f"{base_url}/{voice_name}.onnx"
        config_url = f"{base_url}/{voice_name}.onnx.json"
        
        logger.info(f"Downloading voice model: {voice_name}")
        
        # Download model file
        response = requests.get(voice_url)
        if response.status_code == 200:
            model_path = f"models/{voice_name}.onnx"
            with open(model_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Downloaded model to: {model_path}")
        else:
            logger.error(f"Failed to download model: {response.status_code}")
            return False
        
        # Download config file
        response = requests.get(config_url)
        if response.status_code == 200:
            config_path = f"models/{voice_name}.onnx.json"
            with open(config_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Downloaded config to: {config_path}")
        else:
            logger.error(f"Failed to download config: {response.status_code}")
            return False
        
        logger.info(f"Voice model {voice_name} downloaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download voice model: {e}")
        return False

def get_audio_duration(audio_path: str) -> float:
    """
    Get duration of audio file in seconds
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Duration in seconds
    """
    try:
        with wave.open(audio_path, 'rb') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        logger.error(f"Failed to get audio duration: {e}")
        return 0.0

if __name__ == "__main__":
    # Test TTS
    import sys
    
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        try:
            output_path = text_to_speech(text)
            duration = get_audio_duration(output_path)
            print(f"Generated speech: {output_path}")
            print(f"Duration: {duration:.2f} seconds")
        except Exception as e:
            print(f"TTS failed: {e}")
    else:
        print("Usage: python tts.py <text>")
        print("Example: python tts.py 'Hello, this is a test of the text to speech system.'") 