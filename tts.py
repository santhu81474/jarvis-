import pyttsx3
import threading

# Initialize engine
engine = pyttsx3.init()

# Configure voice
engine.setProperty('rate', 175)

# Try to find a female voice
voices = engine.getProperty('voices')
female_voice_found = False
for voice in voices:
    if "female" in voice.name.lower() or "zira" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        female_voice_found = True
        break

if not female_voice_found and len(voices) > 0:
    engine.setProperty('voice', voices[0].id)

def speak(text):
    """Speak text using pyttsx3 (blocks until done)."""
    print(f"[JARVIS] Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def speak_async(text):
    """Speak text in a separate thread so it doesn't block actions."""
    threading.Thread(target=speak, args=(text,), daemon=True).start()

if __name__ == "__main__":
    # Test block
    speak("Hello, I am JARVIS. Testing my voice output.")
