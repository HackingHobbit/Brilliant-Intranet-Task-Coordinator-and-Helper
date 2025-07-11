import whisper
import tempfile
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Load Whisper model once
_model = None

def get_whisper_model():
    """Get or load Whisper model"""
    global _model
    if _model is None:
        try:
            logger.info("Loading Whisper model...")
            _model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    return _model

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file to text using Whisper
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    try:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load model
        model = get_whisper_model()
        
        # Transcribe
        logger.info(f"Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path)
        
        text = result["text"].strip()
        logger.info(f"Transcription completed: {text[:100]}...")
        
        return text
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise

def transcribe_audio_data(audio_data: bytes) -> str:
    """
    Transcribe audio data to text
    
    Args:
        audio_data: Raw audio data
        
    Returns:
        Transcribed text
    """
    try:
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            return transcribe_audio(temp_path)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Audio data transcription failed: {e}")
        raise

def transcribe_microphone(duration: int = 5) -> str:
    """
    Record and transcribe from microphone
    
    Args:
        duration: Recording duration in seconds
        
    Returns:
        Transcribed text
    """
    try:
        import pyaudio
        import wave
        
        # Audio settings
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        logger.info(f"Recording for {duration} seconds...")
        frames = []
        
        # Record
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        # Stop recording
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            wf = wave.open(temp_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            temp_path = temp_file.name
        
        try:
            return transcribe_audio(temp_path)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        logger.error(f"Microphone transcription failed: {e}")
        raise

if __name__ == "__main__":
    # Test transcription
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        if os.path.exists(audio_file):
            text = transcribe_audio(audio_file)
            print(f"Transcription: {text}")
        else:
            print(f"File not found: {audio_file}")
    else:
        print("Usage: python stt.py <audio_file>")
        print("Or call transcribe_microphone() for live recording") 