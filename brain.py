import ollama
import json
import re
import requests
import sys

# Constants
MODEL_NAME = "llava"

SYSTEM_PROMPT = """You are JARVIS, an AI that controls a computer. You see the user's screen and receive voice commands. 
You must respond ONLY with a JSON object. Never explain. Never add text outside the JSON. 

The JSON must have:
{
  "speak": "what to say to user", 
  "actions": [{"type": "CLICK", "x": 100, "y": 200}, ...]
}

Action types:
- CLICK (x, y): Left click at coordinates.
- DOUBLE_CLICK (x, y): Double click at coordinates.
- RIGHT_CLICK (x, y): Right click at coordinates.
- TYPE (text): Type the specified text.
- KEY (key_name): Press a key or combo (e.g. 'enter', 'ctrl+c', 'alt+tab').
- SCROLL (amount): Scroll up (positive) or down (negative).
- OPEN (app_name): Open an application or path.
- WAIT (seconds): Pause execution.
- SCREENSHOT: Take a new screenshot and re-evaluate.

Chain multiple actions in order. For complex tasks, include SCREENSHOT between steps to verify progress.
"""

def check_ollama():
    """Verify Ollama is running and model is available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code != 200:
            return False, "Ollama returned error status."
        
        models = [m['name'] for m in response.json().get('models', [])]
        if MODEL_NAME not in models and f"{MODEL_NAME}:latest" not in models:
            return False, f"Model {MODEL_NAME} not found. Run: ollama pull {MODEL_NAME}"
        
        return True, "Ollama is ready."
    except Exception:
        return False, "Ollama is not running. Run: ollama serve"

def think(command, image_bytes):
    """Send command and screenshot to Ollama and parse response."""
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT,
                },
                {
                    'role': 'user',
                    'content': f"Command: {command}",
                    'images': [image_bytes]
                }
            ],
            options={'temperature': 0}
        )
        
        response_text = response['message']['content']
        print(f"[DEBUG] Brain Raw Response: {response_text}")
        
        # Parse JSON safely
        return parse_json_response(response_text)
        
    except Exception as e:
        print(f"[ERROR] Brain communication failed: {e}")
        return {"speak": "I'm having trouble thinking right now.", "actions": []}

def parse_json_response(text):
    """Extract and parse JSON from model response."""
    try:
        # Try direct parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Try regex extraction for markdown blocks or garbage text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        
    return {"speak": "I couldn't process that command correctly.", "actions": []}

if __name__ == "__main__":
    # Test block
    ok, msg = check_ollama()
    print(msg)
    if ok:
        print("Brain test: Ask it what it sees (requires image bytes).")
