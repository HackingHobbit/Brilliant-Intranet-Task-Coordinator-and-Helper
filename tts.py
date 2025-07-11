import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set the voice to Samantha (female, futuristic)
voices = engine.getProperty('voices')
for voice in voices:
    if 'Samantha' in voice.name:
        engine.setProperty('voice', voice.id)
        break

# Optional: Adjust speech rate and volume
engine.setProperty('rate', 150)  # Speed of speech (words per minute)
engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)

def text_to_speech(text):
    """
    Converts the given text to speech and plays it.
    
    Args:
        text (str): The text to be spoken.
    """
    engine.say(text)
    engine.runAndWait()

# Example usage
if __name__ == "__main__":
    text_to_speech("Hello, this is a test of the text-to-speech functionality.")

# Optional: To save the speech to a file instead of playing it
# def save_to_file(text, filename='output.mp3'):
#     engine.save_to_file(text, filename)
#     engine.runAndWait()