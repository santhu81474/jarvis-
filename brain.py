# Yet another trivial change for commit
import ollama
import json
import re
import requests
import sys

# Constants
MODEL_NAME = "llama3.2-vision:11b"

SYSTEM_PROMPT = """You are JARVIS, a diligent and helpful student assistant. You are here to follow the user's instructions perfectly.
Always confirm what you are doing in the 'speak' field (e.g., "Yes, I am opening YouTube for you now").
You must respond ONLY with a JSON object. Never explain. Never add text outside the JSON. 

IMPORTANT: If the application you need (like Chrome, Notepad, or VS Code) is ALREADY visible on the screen, DO NOT use the 'OPEN' action. Instead, just interact with the window by CLICKING or TYPING as needed.

If you need to open an application or a website that is NOT visible, use the OPEN action.

The JSON must have:
{
  "speak": "confirmation message to user", 
  "actions": [{"type": "OPEN", "app_name": "notepad"}, ...]
}

- OPEN (app_name): IMPORTANT: Use this to start apps or SEARCH. For searching, use 'OPEN youtube search [query]' or 'OPEN google search [query]'.
- CLICK (x, y): Left click. Use NORMALIZED coordinates (0.0 to 1.0) where 0.5 is the middle.
- DOUBLE_CLICK (x, y): Double click at normalized coordinates.
- RIGHT_CLICK (x, y): Right click at normalized coordinates.
- TYPE (text): Type text. It will automatically press 'enter' for searches.
- KEY (key_name): Press a key or combo (e.g. 'enter', 'ctrl+c', 'alt+tab').
- SCROLL (amount): Scroll up (positive) or down (negative).
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

import base64

def think(command, image_bytes):
    """Send command and screenshot to Ollama and parse response."""
    try:
        kwargs = {
            "model": MODEL_NAME,
            "system": SYSTEM_PROMPT,
            "prompt": command,
            "format": 'json',
            "stream": False,
            "options": {
                "num_ctx": 2048,
                "temperature": 0.1
            }
        }
        
        if image_bytes:
            img_base64 = base64.b64encode(image_bytes).decode('utf-8')
            kwargs["images"] = [img_base64]
            
        print(f"[DEBUG] Requesting thinking from {MODEL_NAME}...")
        response = ollama.generate(**kwargs)
        
        response_text = response.get('response', '')
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
