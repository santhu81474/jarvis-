# Minor change for quick commit
import pyttsx3
import threading
import queue
import time
import platform

# For Windows threading support
if platform.system() == "Windows":
    import pythoncom

# Setup voice queue for thread-safety
voice_queue = queue.Queue()

def voice_worker():
    """Background worker to process speech requests sequentially."""
    if platform.system() == "Windows":
        pythoncom.CoInitialize()

    worker_engine = pyttsx3.init()
    worker_engine.setProperty('rate', 185)
    
    # Configure voice in the worker thread
    w_voices = worker_engine.getProperty('voices')
    voice_found = False
    
    # Priority 1: Indian Female
    for v in w_voices:
        if "IN" in v.id or "India" in v.name:
            if "female" in v.name.lower() or "heera" in v.name.lower() or "zira" in v.name.lower():
                worker_engine.setProperty('voice', v.id)
                voice_found = True
                break
    
    # Priority 2: Any Female
    if not voice_found:
        for v in w_voices:
            if "female" in v.name.lower() or "zira" in v.name.lower():
                worker_engine.setProperty('voice', v.id)
                voice_found = True
                break
    
    while True:
        text = voice_queue.get()
        if text is None: break
        try:
            worker_engine.say(text)
            worker_engine.runAndWait()
        except Exception as e:
            print(f"[ERROR] TTS Failed: {e}")
            # Re-init engine if it crashes
            worker_engine = pyttsx3.init()
        voice_queue.task_done()

# Start the background voice thread
threading.Thread(target=voice_worker, daemon=True).start()

def speak(text):
    """Add text to the voice queue."""
    if not text: return
    print(f"[JARVIS] Speaking: {text}")
    voice_queue.put(text)

def speak_async(text):
    """Speak text (already async via queue)."""
    speak(text)

if __name__ == "__main__":
    speak("Testing the new thread-safe voice queue.")
    time.sleep(3)
