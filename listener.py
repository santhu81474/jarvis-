# Another minor change for commit
import pyaudio
import wave
import whisper
import numpy as np
import tempfile
import os
import sys
import shutil
import time
import platform

# --- Constants ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_DURATION = 3.0       # wait 3 seconds of silence before stopping
MAX_RECORD_SECONDS = 20      # maximum recording time

# Global whisper model
whisper_model = None


def check_dependencies():
    """Check if ffmpeg is available."""
    # List of possible ffmpeg paths
    ffmpeg_path = shutil.which('ffmpeg')
    
    if ffmpeg_path is None:
        # Check some common non-PATH locations on Windows
        possible_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe")
        ]
        for p in possible_paths:
            if os.path.exists(p):
                ffmpeg_path = p
                os.environ["PATH"] += os.pathsep + os.path.dirname(p)
                break

    if ffmpeg_path is None:
        print("\n[ERROR] ffmpeg is not installed or not in PATH.")
        print("Whisper requires ffmpeg to process audio.")
        if platform.system() == "Windows":
            print("Install via: winget install Gyan.FFmpeg")
        elif platform.system() == "Darwin":
            print("Install via: brew install ffmpeg")
        else:
            print("Install via: sudo apt install ffmpeg")
        sys.exit(1)


def play_beep():
    """Play a short beep sound to notify the user JARVIS is listening."""
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 300)
        else:
            print("\a")
    except Exception:
        pass


def load_whisper_model():
    """Load whisper model once at startup."""
    global whisper_model
    if whisper_model is None:
        print("[JARVIS] Loading standard speech model...")
        try:
            whisper_model = whisper.load_model("base")
            print("[JARVIS] Speech model ready.")
        except Exception as e:
            print(f"[ERROR] Failed to load Whisper model: {e}")
            sys.exit(1)


def calibrate_silence_threshold():
    """Calibrate microphone for 1 second to find ambient noise level."""
    print("[JARVIS] Calibrating microphone (stay quiet for 1 second)...")
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(int(RATE / CHUNK * 1)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.int16))
        stream.stop_stream()
        stream.close()
        p.terminate()
        ambient_audio = np.concatenate(frames)
        ambient_rms = np.sqrt(np.mean(ambient_audio.astype(np.float32) ** 2))
        # Set threshold to 1.1x ambient (more sensitive), floor 150, ceiling 500
        threshold = min(max(ambient_rms * 1.1, 150), 500)
        print(f"[JARVIS] Silence threshold set to {threshold:.0f}")
        return threshold
    except Exception as e:
        print(f"[WARNING] Calibration failed: {e}. Using default threshold 500.")
        return 500


def get_rms(audio_chunk_bytes):
    """Calculate RMS of an audio chunk."""
    audio_array = np.frombuffer(audio_chunk_bytes, dtype=np.int16)
    return np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))


def listen_for_wake_word(silence_threshold):
    """
    Wait for the user to say 'Jarvis'.
    Uses a 2-second sliding window with 0.5 second slide step.
    """
    print("\n[JARVIS] Say 'Jarvis' to wake me up...")
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        print(f"[ERROR] Cannot open microphone: {e}")
        p.terminate()
        return False

    frames = []
    chunks_per_second = int(RATE / CHUNK)
    # 3-second window for better context
    window_chunks = chunks_per_second * 3
    slide_chunks = chunks_per_second * 1

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            if len(frames) >= window_chunks:
                # Process the window
                window_audio = np.frombuffer(b''.join(frames), dtype=np.int16)
                window_rms = np.sqrt(np.mean(window_audio.astype(np.float32) ** 2))
                
                if window_rms > silence_threshold:
                    # Save temporary file
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                        tmp_path = tmp.name

                    with wave.open(tmp_path, 'wb') as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(2)
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))

                    try:
                        # High-speed wake word detection
                        result = whisper_model.transcribe(
                            tmp_path, 
                            fp16=False, 
                            language='en',
                            initial_prompt="Jarvis, YouTube.",
                            beam_size=1,
                            temperature=0
                        )
                        text = result['text'].lower().strip()
                        
                        # Hallucination filter: ignore common Whisper noise phrases and very short snippets
                        hallucinations = ["thank you", "you", "subs", "watching", "always", "bye", "please", "like", "share", "subscribe"]
                        is_hallucination = any(h == text.strip('.') for h in hallucinations) or len(text) < 3
                        
                        if text and not is_hallucination:
                            print(f"[DEBUG] Heard: {text}")
                            
                            # Check for "Jarvis" and common mis-transcriptions
                            wake_aliases = ['jarvis', 'charvace', 'charvis', 'jarve', 'service', 'garvis', 'javis', 'jarirus', 'jarries', 'dan', 'servers', 'server']
                            if any(alias in text for alias in wake_aliases):
                                print(f"[WAKE] Recognized: {text}")
                                stream.stop_stream()
                                stream.close()
                                p.terminate()
                                if os.path.exists(tmp_path):
                                    os.unlink(tmp_path)
                                return True
                    except Exception:
                        pass
                    finally:
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)

                # Slide window forward
                frames = frames[slide_chunks:]

        except KeyboardInterrupt:
            break
        except Exception:
            continue

    stream.stop_stream()
    stream.close()
    p.terminate()
    return False


def record_command(silence_threshold):
    """
    Record the user's command after wake word is detected.
    - Plays a beep so user knows to speak
    - Waits 1.5 seconds before starting (gives user time to react)
    - Records until 3 seconds of silence or 20 seconds max
    - Shows live volume bar so user knows it's recording
    """
    play_beep()
    print("[JARVIS] Get ready to speak your command...")
    time.sleep(1.5)  # give user time to react to beep before recording starts
    print("[JARVIS] RECORDING NOW - say your command clearly...")

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)

    frames = []
    silent_chunks = 0
    max_silent_chunks = int(SILENCE_DURATION * (RATE / CHUNK))
    total_chunks = 0
    max_total_chunks = int(MAX_RECORD_SECONDS * (RATE / CHUNK))
    started_speaking = False

    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            total_chunks += 1

            rms = get_rms(data)

            # Show live volume bar so user knows mic is active
            bars = min(int(rms / 40), 20)
            print(f"\r[MIC] {'█' * bars}{' ' * (20 - bars)} {rms:.0f}   ", end='', flush=True)

            if rms >= silence_threshold:
                started_speaking = True
                silent_chunks = 0
            else:
                if started_speaking:
                    silent_chunks += 1

            # Only stop after user has spoken AND silence detected
            if started_speaking and silent_chunks >= max_silent_chunks:
                break

            if total_chunks >= max_total_chunks:
                break

        except Exception as e:
            print(f"\n[WARNING] Recording error: {e}")
            break

    print("\n[JARVIS] Processing your command...")
    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        return ""

    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        tmp_path = tmp.name

    with wave.open(tmp_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    try:
        # High-speed transcription with context bias
        vocab = "Jarvis, YouTube, Google, Chrome, Notepad, Calendar, VS Code, Search, Open, Close, Windows, Visual Studio Code."
        result = whisper_model.transcribe(
            tmp_path, 
            fp16=False, 
            language='en',
            initial_prompt=vocab,
            beam_size=1,        # Fast response
            temperature=0
        )
        command = result['text'].strip().lower()
        
        # Human-like Command Cleanup
        if "youve bill" in command or "open youve" in command: command = "open youtube"
        if "ou so" in command or "vsc" in command or "o so" in command: command = "open vs code"
        if "lord pad" in command or "lord book" in command: command = "open notepad"
        
        print(f"[JARVIS] You said: {command}")
        return command
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        return ""
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    check_dependencies()
    load_whisper_model()
    thresh = calibrate_silence_threshold()
    if listen_for_wake_word(thresh):
        cmd = record_command(thresh)
        print(f"You said: {cmd}")