import os
import wave
import pyaudio

def transcribe_audio(audio_data):
    with open('temp.wav', 'wb') as f:
        f.write(audio_data)
    # Assume Whisper.cpp binary in path
    os.system('./whisper.cpp/main -m models/ggml-small.en.bin -f temp.wav --output-txt')
    with open('temp.txt', 'r') as f:
        text = f.read().strip()
    os.remove('temp.wav')
    os.remove('temp.txt')
    return text