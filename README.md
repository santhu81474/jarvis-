# J.A.R.V.I.S. - Local AI Computer Controller

A fully functional, 100% local JARVIS AI assistant that runs on your laptop using Llama 3.2 Vision via Ollama. It can hear you, see your screen, and control your mouse/keyboard.

## Features
- **Hands-Free**: Wake word detection ("Jarvis") and voice commands.
- **Multimodal Intelligence**: Uses Llama 3.2 Vision to understand your screen context.
- **Computer Control**: Can click, type, open apps, scroll, and use hotkeys.
- **100% Local**: Privacy-focused; no data leaves your machine.

---

## Setup Instructions

### 1. Install System Dependencies
- **Ollama**: Download from [ollama.com](https://ollama.com) and install.
- **FFmpeg**: 
  - Windows: `choco install ffmpeg` (or download from ffmpeg.org and add to PATH).
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **PortAudio** (for microphone):
  - Linux: `sudo apt install portaudio19-dev`
  - Mac: `brew install portaudio`

### 2. Pull the AI Model
Open a terminal and run:
```bash
ollama pull llama3.2-vision:11b
```

### 3. Install Python Dependencies
It is recommended to use a virtual environment:
**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File setup_windows.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 4. Run JARVIS
Once the setup is complete and Ollama is running:
```bash
python jarvis.py
```

---

## How to Use
1. Say **"Jarvis"**.
2. Wait for the **beep**.
3. Speak your command (e.g., "Open Notepad and type: Hello JARVIS is online!").
4. Watch JARVIS see your screen and execute the actions.

---

## Troubleshooting

### PyAudio Error (Windows)
If you get errors installing `pyaudio`, ensure you have the [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed.

### Ollama Not Found
Ensure `ollama serve` is running in another terminal.

### Screen Capture Issues (Linux)
Ensure the `DISPLAY` environment variable is set correctly in your session.

### Permission Errors (Mac)
You may need to grant "Accessibility" and "Screen Recording" permissions to your Terminal/IDE in System Settings.

---

## Safety Note
JARVIS has control over your mouse and keyboard. 
- **Failsafe**: Move your mouse to any **corner of the screen** to immediately abort any automated movement.
- **Stop**: Press `Ctrl+C` in the terminal to shut down JARVIS.
