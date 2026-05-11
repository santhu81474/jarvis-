# JARVIS Windows Setup Script
Write-Host "Starting JARVIS Setup for Windows..." -ForegroundColor Cyan

# 1. Check for Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed. Please install Python from python.org" -ForegroundColor Red
    exit
}

# 2. Check for FFmpeg
if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "[WARNING] FFmpeg not found in PATH. Whisper requires FFmpeg." -ForegroundColor Yellow
    Write-Host "Please install FFmpeg (e.g., 'choco install ffmpeg') or download from ffmpeg.org and add to PATH." -ForegroundColor Yellow
}

# 3. Check for Ollama
if (!(Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "[WARNING] Ollama not found. Please install Ollama from ollama.com" -ForegroundColor Yellow
}

# 4. Create Virtual Environment
if (!(Test-Path "jarvis_env")) {
    Write-Host "Creating virtual environment 'jarvis_env'..." -ForegroundColor Cyan
    python -m venv jarvis_env
}

# 5. Install Requirements
Write-Host "Installing dependencies..." -ForegroundColor Cyan
.\jarvis_env\Scripts\python.exe -m pip install --upgrade pip
.\jarvis_env\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "`nSetup Complete!" -ForegroundColor Green
Write-Host "To start JARVIS:" -ForegroundColor Cyan
Write-Host "1. Ensure Ollama is running and you have pulled the model: 'ollama pull llama3.2-vision:11b'" -ForegroundColor Cyan
Write-Host "2. Run: .\jarvis_env\Scripts\python.exe jarvis.py" -ForegroundColor Cyan
