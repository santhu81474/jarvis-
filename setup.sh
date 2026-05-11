#!/bin/bash
# JARVIS Setup Script for Linux/Mac
echo -e "\033[0;36mStarting JARVIS Setup...\033[0m"

# 1. Install System Dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing system dependencies for Linux..."
    sudo apt update
    sudo apt install -y portaudio19-dev espeak ffmpeg python3-pip python3-venv
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing system dependencies for Mac..."
    brew install portaudio ffmpeg
fi

# 2. Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "\033[0;33m[WARNING] Ollama not found. Installing Ollama...\033[0m"
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 3. Create Virtual Environment
if [ ! -d "jarvis_env" ]; then
    echo -e "\033[0;36mCreating virtual environment 'jarvis_env'...\033[0m"
    python3 -m venv jarvis_env
fi

# 4. Install Requirements
echo -e "\033[0;36mInstalling dependencies...\033[0m"
source jarvis_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "\n\033[0;32mSetup Complete!\033[0m"
echo -e "\033[0;36mTo start JARVIS:\033[0m"
echo -e "1. Ensure Ollama is running: \033[0;33mollama serve\033[0m"
echo -e "2. Pull the model: \033[0;33mollama pull llama3.2-vision:11b\033[0m"
echo -e "3. Run: \033[0;33msource jarvis_env/bin/activate && python jarvis.py\033[0m"
