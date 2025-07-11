import warnings
from pydantic import PydanticDeprecatedSince20

warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
warnings.filterwarnings("ignore", message="Mixing V1 models and V2 models")

from flask import Flask, request, jsonify
import json
import keyring
import torch
from stt import transcribe_audio
from tts import text_to_speech
from memory import MemoryManager
from tools import AgentTools
from vision import analyze_image
from landmarks import detect_landmarks
from warp import warp_lips
from crewai import Crew, Agent, Task
import ollama  # Ensure ollama installed and running

app = Flask(__name__)

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

memory_mgr = MemoryManager()
tools = AgentTools(config, keyring)

# M4 Pro optimization
device = torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')
print(f"Using device: {device}")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        audio_data = request.files['audio'].read()
        text = transcribe_audio(audio_data)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_response', methods=['POST'])
def generate_response():
    try:
        query = request.json['query']
        history = memory_mgr.get_session_history()
        context = memory_mgr.retrieve_knowledge(query)

        agent = Agent(
            role='AI Assistant',
            goal='Process query with tools and memories',
            backstory='Local AI with agentic capabilities',
            llm=ollama.chat(model='llama3'),
            tools=tools.get_all_tools()
        )
        task = Task(description=f'Handle: {query} with context: {context} history: {history}', agent=agent)
        crew = Crew(agents=[agent], tasks=[task])
        response = crew.kickoff()

        memory_mgr.update_agent_memory(query, response)
        memory_mgr.add_to_session(query, response)
        memory_mgr.add_to_knowledge(response)  # Async-like

        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def tts():
    try:
        text = request.json['text']
        audio_path = text_to_speech(text)
        return jsonify({'audio_path': audio_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_image', methods=['POST'])
def analyze_img():
    try:
        image_file = request.files['image']
        image_path = 'temp_image.jpg'
        image_file.save(image_path)
        result = analyze_image(image_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/landmarks', methods=['POST'])
def landmarks():
    try:
        image_file = request.files['image']
        image_path = 'temp_image.jpg'
        image_file.save(image_path)
        landmarks = detect_landmarks(image_path)
        return jsonify({'landmarks': landmarks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/warp', methods=['POST'])
def warp():
    try:
        data = request.json
        image_path = data['image_path']
        visemes = data['visemes']
        frames = warp_lips(image_path, visemes)
        return jsonify({'frames': [frame.tolist() for frame in frames]})  # Serialize
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_config', methods=['POST'])
def update_config():
    try:
        new_config = request.json
        with open('config.json', 'w') as f:
            json.dump(new_config, f)
        global config
        config = new_config
        return jsonify({'status': 'updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/set_key', methods=['POST'])
def set_key():
    try:
        data = request.json
        keyring.set_password(data['service'], data['key'], data['value'])
        return jsonify({'status': 'set'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return "Hello, the app is running successfully!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)