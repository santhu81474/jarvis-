# Yet another minor change for a commit
import mss
import mss.tools
import pyautogui
import io
import base64
import os
import platform
from PIL import Image

def capture_screen():
    """Capture the primary screen and return bytes and base64 string."""
    try:
        # Using pyautogui as it's more reliable for Windows desktop capture
        img = pyautogui.screenshot()
        
        # Save a debug image so the user can verify what JARVIS sees
        img.save("last_view.png")
        
        # Higher resolution for better detail in Vision models
        max_width = 1920
        max_height = 1080
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to bytes for Ollama
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Encode to base64
        base64_string = base64.b64encode(img_bytes).decode('utf-8')
        
        return img_bytes, base64_string
    except Exception as e:
        print(f"[ERROR] Screen capture failed: {e}")
        return None, None

if __name__ == "__main__":
    # Test block
    img_bytes, b64 = capture_screen()
    print(f"Captured screen: {len(img_bytes)} bytes, Base64 length: {len(b64)}")
    with open("test_capture.png", "wb") as f:
        f.write(img_bytes)
    print("Saved test capture to test_capture.png")
