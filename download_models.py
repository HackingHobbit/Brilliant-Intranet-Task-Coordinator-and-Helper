import os
import requests
import subprocess

def download_models():
    # Ollama Llama3
    if not os.path.exists('models/llama3.gguf'):
        print("Downloading Llama3...")
        subprocess.run(['ollama', 'pull', 'llama3'])

    # Whisper.cpp
    if not os.path.exists('models/ggml-small.en.bin'):
        print("Downloading Whisper model...")
        url = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin'
        response = requests.get(url)
        with open('models/ggml-small.en.bin', 'wb') as f:
            f.write(response.content)

    # Piper voice
    if not os.path.exists('models/en_US-amy-medium.onnx'):
        print("Downloading Piper voice...")
        url = 'https://huggingface.co/rhasspy/piper-voices/resolve/main/en_US/en_US-amy-medium.onnx'
        response = requests.get(url)
        with open('models/en_US-amy-medium.onnx', 'wb') as f:
            f.write(response.content)

    # YOLOv8
    from ultralytics import YOLO
    YOLO('yolov8n.pt')  # Downloads if missing

    print("Models downloaded.")

if __name__ == '__main__':
    os.makedirs('models', exist_ok=True)
    download_models()