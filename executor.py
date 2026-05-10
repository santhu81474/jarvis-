import pyautogui
import pyperclip
import time
import subprocess
import os
import platform

# Safety Settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.3      # Small pause between actions

def open_app(app_name):
    """Open an application cross-platform with smart alias matching."""
    # Smart mapping for common voice mis-transcriptions
    aliases = {
        "load pad": "notepad",
        "note pad": "notepad",
        "browser": "chrome",
        "file explorer": "explorer",
        "files": "explorer",
        "terminal": "cmd",
        "command prompt": "cmd",
        "calculator": "calc",
        "noodle": "notepad",
        "v-score": "code",
        "v score": "code",
        "vs code": "code",
        "visual studio": "code"
    }
    
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
    """Handle system level actions like volume and brightness."""
    try:
        if a_type == "VOLUME_UP":
            for _ in range(5): pyautogui.press('volumeup')
        elif a_type == "VOLUME_DOWN":
            for _ in range(5): pyautogui.press('volumedown')
        elif a_type == "MUTE":
            pyautogui.press('volumemute')
        elif a_type == "MINIMIZE_ALL":
            if platform.system() == "Windows":
                pyautogui.hotkey('win', 'd')
            else:
                pyautogui.hotkey('command', 'f3') # Mac show desktop
    except Exception as e:
        print(f"[ERROR] System action {a_type} failed: {e}")

def execute_actions(actions):
    """Execute a list of action dicts."""
    for action in actions:
        try:
            a_type = action.get('type', '').upper()
            x = action.get('x')
            y = action.get('y')
            text = action.get('text')
            key = action.get('key_name')
            amount = action.get('amount')
            app = action.get('app_name')
            seconds = action.get('seconds', 1)

            print(f"[EXECUTOR] Action: {a_type}")

            # New System Actions
            if a_type in ["VOLUME_UP", "VOLUME_DOWN", "MUTE", "MINIMIZE_ALL"]:
                handle_system_action(a_type)
                continue

            if a_type == "CLICK":
                pyautogui.click(x, y)
            elif a_type == "DOUBLE_CLICK":
                pyautogui.doubleClick(x, y)
            elif a_type == "RIGHT_CLICK":
                pyautogui.rightClick(x, y)
            elif a_type == "TYPE":
                pyperclip.copy(text)
                if platform.system() == "Darwin":
                    pyautogui.hotkey('command', 'v')
                else:
                    pyautogui.hotkey('ctrl', 'v')
            elif a_type == "KEY":
                if '+' in key:
                    pyautogui.hotkey(*key.split('+'))
                else:
                    pyautogui.press(key)
            elif a_type == "SCROLL":
                pyautogui.scroll(amount if amount else -300)
            elif a_type == "OPEN":
                open_app(app)
            elif a_type == "WAIT":
                time.sleep(seconds)
            elif a_type == "SCREENSHOT":
                return "SCREENSHOT_REQUESTED"
        except Exception as e:
            print(f"[ERROR] Action {a_type} failed: {e}")
    return True

if __name__ == "__main__":
    # Test block
    print("Executor test: Typing 'Hello from JARVIS'")
    execute_actions([{"type": "TYPE", "text": "Hello from JARVIS"}])
