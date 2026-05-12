import pyautogui
import pyperclip
import time
import subprocess
import os
import platform

# Safety Settings
pyautogui.FAILSAFE = False  # Disabled to allow JARVIS full control
pyautogui.PAUSE = 0.3      # Small pause between actions

def open_app(app_name):
    """Open an application cross-platform with smart alias matching."""
    # Smart mapping for common voice mis-transcriptions
    aliases = {
        "load pad": "notepad",
        "note pad": "notepad",
        "browser": "https://www.google.com",
        "internet": "https://www.google.com",
        "web": "https://www.google.com",
        "google": "https://www.google.com",
        "chrome": "chrome",
        "google chrome": "chrome",
        "file explorer": "explorer",
        "files": "explorer",
        "terminal": "wt" if platform.system() == "Windows" else "terminal",
        "command prompt": "cmd",
        "calculator": "calc",
        "notepad": "notepad",
        "noodle": "notepad",
        "notebook": "notepad",
        "vs code": "code",
        "visual studio code": "code",
        "vsc": "code",
        "settings": "ms-settings:" if platform.system() == "Windows" else "systemsettings",
        "control panel": "control",
        "task manager": "taskmgr",
        "calendar": "outlookcal:",
        "youtube": "https://www.youtube.com",
        "youve bill": "https://www.youtube.com",
        "youve": "https://www.youtube.com"
    }
    
    # Smart YouTube search detection
    if "youtube" in app_name.lower() and "search" in app_name.lower():
        query = app_name.lower().replace("youtube", "").replace("search", "").strip()
        if query:
            import urllib.parse
            app_to_open = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        else:
            app_to_open = "https://www.youtube.com"
    else:
        app_to_open = aliases.get(app_name.lower(), app_name)
    print(f"[EXECUTOR] Attempting to open: {app_to_open}")

    try:
        sys_name = platform.system()
        if sys_name == "Windows":
            try:
                os.startfile(app_to_open)
            except:
                subprocess.Popen(['start', '', app_to_open], shell=True)
        elif sys_name == "Darwin": # Mac
            subprocess.Popen(['open', '-a', app_to_open])
        else: # Linux
            subprocess.Popen(['xdg-open', app_to_open])
    except Exception as e:
        print(f"[ERROR] Could not open {app_to_open}: {e}")

def handle_system_action(a_type, amount=None):
    """Handle system level actions like volume and power."""
    try:
        if a_type == "VOLUME_UP":
            for _ in range(5): pyautogui.press('volumeup')
        elif a_type == "VOLUME_DOWN":
            for _ in range(5): pyautogui.press('volumedown')
        elif a_type == "MUTE":
            pyautogui.press('volumemute')
        elif a_type == "MINIMIZE_ALL":
            pyautogui.hotkey('win', 'd') if platform.system() == "Windows" else pyautogui.hotkey('command', 'f3')
        elif a_type == "LOCK":
            os.system("rundll32.exe user32.dll,LockWorkStation") if platform.system() == "Windows" else None
        elif a_type == "SLEEP":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0") if platform.system() == "Windows" else None
        elif a_type.startswith("MEDIA_"):
            key = a_type.split("_")[1].lower() # PLAY, NEXT, PREV
            pyautogui.press(f'playpause' if key == 'play' else f'nexttrack' if key == 'next' else 'prevtrack')
    except Exception as e:
        print(f"[ERROR] System action {a_type} failed: {e}")

def execute_actions(actions):
    """Execute a list of action dicts with coordinate scaling and precision."""
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.1 # Small delay for stability
    screenshot_needed = False
    
    sw, sh = pyautogui.size()
    
    for action in actions:
        try:
            a_type = action.get('type', '').upper()
            x = action.get('x')
            y = action.get('y')
            text = action.get('text')
            app = action.get('app_name')
            key = action.get('key_name')
            amount = action.get('amount')
            seconds = action.get('seconds', 1)

            # Scale coordinates if they are normalized (0 to 1)
            if x is not None and x <= 1.0 and y is not None and y <= 1.0:
                x = int(x * sw)
                y = int(y * sh)
            elif x is not None:
                x = int(x)
                y = int(y)

            print(f"[EXECUTOR] Action: {a_type} at ({x}, {y})" if x is not None else f"[EXECUTOR] Action: {a_type}")

            if a_type == "OPEN":
                open_app(app)
            elif a_type == "CLICK":
                pyautogui.click(x, y)
            elif a_type == "DOUBLE_CLICK":
                pyautogui.doubleClick(x, y)
            elif a_type == "RIGHT_CLICK":
                pyautogui.rightClick(x, y)
            elif a_type == "SCROLL":
                pyautogui.scroll(amount if amount else -300)
            elif a_type == "TYPE":
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.2)
                # Auto-enter for searches
                if "search" in str(action).lower():
                    pyautogui.press('enter')
            elif a_type == "KEY":
                if key and '+' in key:
                    pyautogui.hotkey(*key.split('+'))
                else:
                    pyautogui.press(key if key else text)
            elif a_type == "WAIT":
                time.sleep(seconds)
            elif a_type == "SCREENSHOT":
                screenshot_needed = True
            
            # System actions
            if a_type in ["VOLUME_UP", "VOLUME_DOWN", "MUTE", "MINIMIZE_ALL", "LOCK", "SLEEP"] or a_type.startswith("MEDIA_"):
                handle_system_action(a_type)

        except Exception as e:
            print(f"[ERROR] Action {a_type} failed: {e}")
            
    if screenshot_needed:
        return "SCREENSHOT_REQUESTED"
    return True

if __name__ == "__main__":
    # Test block
    print("Executor test: Typing 'Hello from JARVIS'")
    execute_actions([{"type": "TYPE", "text": "Hello from JARVIS"}])
