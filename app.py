from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import sys
import traceback
import logging
import tempfile
import atexit
from datetime import datetime
from pathlib import Path
from port_manager import PortManager

# Import our modules
try:
    from stt import transcribe_audio
    from tts import text_to_speech
    from memory import MemoryManager
    from tools import AgentTools
    from vision import analyze_image
    from landmarks import detect_landmarks
    from warp import warp_lips
    from setup_keys import get_key_manager, set_key
    import keyring
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are installed")
    # Don't exit immediately, try to continue with limited functionality
    logger.error(f"Failed to import some modules: {e}")

    # Set fallback functions
    def transcribe_audio(path): return "Transcription unavailable"
    def text_to_speech(text): return None
    def analyze_image(path): return {"error": "Vision unavailable"}
    def detect_landmarks(path): return []
    def warp_lips(path, visemes): return []

    MemoryManager = None
    AgentTools = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Temporary file management
temp_files = set()

def create_temp_file(suffix='', prefix='avatar_'):
    """Create a temporary file and track it for cleanup"""
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, delete=False)
    temp_files.add(temp_file.name)
    temp_file.close()
    return temp_file.name

def cleanup_temp_files():
    """Clean up all temporary files"""
    for temp_file in temp_files.copy():
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                temp_files.remove(temp_file)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")

# Register cleanup function
atexit.register(cleanup_temp_files)

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {
        "email_mode": "local",
        "calendar_mode": "local",
        "financial_api": "yfinance",
        "enable_3d": False,
        "llm_model": "llama3",
        "stt_model": "whisper-small",
        "tts_voice": "en_US-amy-medium"
    }
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

# Initialize components
try:
    memory_mgr = MemoryManager() if MemoryManager else None
    tools = AgentTools(config, keyring) if AgentTools else None
    logger.info("Components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    memory_mgr = None
    tools = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'memory': memory_mgr is not None,
            'tools': tools is not None
        }
    })

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Transcribe audio input"""
    temp_path = None
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400

        # Save temporary audio file
        temp_path = create_temp_file(suffix='.wav', prefix='audio_')
        audio_file.save(temp_path)

        # Transcribe
        text = transcribe_audio(temp_path)

        return jsonify({'text': text})

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                temp_files.discard(temp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")

@app.route('/generate_response', methods=['POST'])
def generate_response():
    """Generate AI response with memory and tools"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'No query provided'}), 400
        
        query = data['query']
        logger.info(f"Processing query: {query}")
        
        # Get session history
        history = ""
        if memory_mgr:
            history = memory_mgr.get_session_history()
        
        # Get relevant knowledge
        knowledge = ""
        if memory_mgr:
            knowledge = memory_mgr.retrieve_knowledge(query)
        
        # Generate response using Ollama
        try:
            import ollama
            response = ollama.generate(
                model=config.get('llm_model', 'llama3'),
                prompt=f"Context: {knowledge}\nHistory: {history}\nQuery: {query}\nResponse:"
            )
            response_text = response['response']
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            response_text = "I'm sorry, I'm having trouble processing your request right now."
        
        # Update memories
        if memory_mgr:
            memory_mgr.add_to_session(query, response_text)
            memory_mgr.update_agent_memory(query, response_text)
        
        return jsonify({'response': response_text})
    
    except Exception as e:
        logger.error(f"Response generation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def tts():
    """Convert text to speech"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        audio_path = text_to_speech(text)
        
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype='audio/wav')
        else:
            return jsonify({'error': 'Failed to generate audio'}), 500
    
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_image', methods=['POST'])
def analyze_img():
    """Analyze uploaded image"""
    temp_path = None
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Save temporary image
        temp_path = create_temp_file(suffix='.jpg', prefix='image_')
        image_file.save(temp_path)

        # Analyze image
        result = analyze_image(temp_path)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                temp_files.discard(temp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")

@app.route('/landmarks', methods=['POST'])
def landmarks():
    """Detect facial landmarks"""
    temp_path = None
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400

        # Save temporary image
        temp_path = create_temp_file(suffix='.jpg', prefix='landmarks_')
        image_file.save(temp_path)

        # Detect landmarks
        landmarks = detect_landmarks(temp_path)

        return jsonify({'landmarks': landmarks})

    except Exception as e:
        logger.error(f"Landmark detection error: {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                temp_files.discard(temp_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")

@app.route('/warp', methods=['POST'])
def warp():
    """Warp avatar lips based on visemes"""
    try:
        data = request.get_json()
        if not data or 'image_path' not in data or 'visemes' not in data:
            return jsonify({'error': 'Missing image_path or visemes'}), 400
        
        image_path = data['image_path']
        visemes = data['visemes']
        
        frames = warp_lips(image_path, visemes)
        return jsonify({'frames': frames})
    
    except Exception as e:
        logger.error(f"Warping error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/update_config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        new_config = request.get_json()
        if not new_config:
            return jsonify({'error': 'No configuration provided'}), 400
        
        # Update config
        config.update(new_config)
        
        # Save to file
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({'status': 'updated'})
    
    except Exception as e:
        logger.error(f"Config update error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/set_key', methods=['POST'])
def set_key():
    """Set API key in keyring"""
    try:
        data = request.get_json()
        if not data or 'service' not in data or 'key' not in data or 'value' not in data:
            return jsonify({'error': 'Missing service, key, or value'}), 400
        
        service = data['service']
        key = data['key']
        value = data['value']
        
        set_key(service, key, value)
        return jsonify({'status': 'set'})
    
    except Exception as e:
        logger.error(f"Key setting error: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/get_config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify(config)

if __name__ == '__main__':
    print("Starting Local AI Avatar Flask Backend...")

    # Setup port management
    port_manager = PortManager()

    try:
        # Find and allocate an available port
        port = port_manager.allocate_port()
        port_manager.create_port_file(port)

        backend_url = f"http://localhost:{port}"
        print(f"Backend will be available at {backend_url}")

        # Cleanup port file on exit
        def cleanup():
            port_manager.cleanup_port_file()
        atexit.register(cleanup)

        # Start the Flask app
        app.run(host='0.0.0.0', port=port, debug=False)

    except Exception as e:
        logger.error(f"Failed to start backend: {e}")
        print(f"Error: {e}")
        sys.exit(1)