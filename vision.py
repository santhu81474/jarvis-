import mss
import mss.tools
from PIL import Image
import io
import base64
import os
import platform

def capture_screen():
    """Capture the primary monitor and return as bytes and base64."""
    if platform.system() == "Linux" and not os.environ.get('DISPLAY'):
        print("[ERROR] No DISPLAY environment variable found. Vision may fail on Linux.")

    with mss.mss() as sct:
        # Get the primary monitor
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Load into Pillow
        img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        
        # Resize if larger than 1280x720 to save tokens/bandwidth
        max_width = 1280
        max_height = 720
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Convert to base64
        base64_string = base64.b64encode(img_bytes).decode('utf-8')
        
        return img_bytes, base64_string

if __name__ == "__main__":
    # Test block
    img_bytes, b64 = capture_screen()
    print(f"Captured screen: {len(img_bytes)} bytes, Base64 length: {len(b64)}")
    with open("test_capture.png", "wb") as f:
        f.write(img_bytes)
    print("Saved test capture to test_capture.png")
