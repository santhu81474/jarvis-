import listener
import vision
import brain
import executor
import tts
from colorama import init, Fore, Style
import sys
import time

# Initialize colorama
init()

BANNER = f"""
{Fore.CYAN}
   ____.  _____  __________ ____   ____._________________
  |    | /  _  \ \______   \\   \ /   /|   \_   _____/   \\
  |    |/  /_\  \ |       _/ \   Y   / |   ||    __)_ \   \\
/\__|    /    |    \|    |   \  \     /  |   ||        \ \   \\
\________\____|__  /|____|_  /   \___/   |___/_______  /  \___/
                 \/        \/                        \/        
                      V1.0 - LOCAL AI ASSISTANT
{Style.RESET_ALL}
"""

def startup_checks():
    """Perform all necessary checks before starting."""
    print(BANNER)
    print("[SYSTEM] Starting JARVIS initial diagnostics...")
    
    # Check FFmpeg
    listener.check_dependencies()
    
    # Check Ollama
    ok, msg = brain.check_ollama()
    if not ok:
        print(f"{Fore.RED}[ERROR] {msg}{Style.RESET_ALL}")
        tts.speak("Ollama is not ready. Please check the terminal for instructions.")
        sys.exit(1)
    
    # Load Whisper
    listener.load_whisper_model()
    
    print(f"{Fore.GREEN}[SYSTEM] All systems nominal. JARVIS is online.{Style.RESET_ALL}")
    tts.speak("JARVIS online. How can I assist you?")

def main():
    try:
        startup_checks()
        
        # Calibrate once at startup
        silence_threshold = listener.calibrate_silence_threshold()
        
        while True:
            print(f"\n{Fore.WHITE}Waiting for wake word...{Style.RESET_ALL}")
            
            # 1. Listen for "Jarvis"
            if listener.listen_for_wake_word(silence_threshold):
                # 2. Record command
                command = listener.record_command(silence_threshold)
                print(f"{Fore.YELLOW}Command received: {command}{Style.RESET_ALL}")
                
                if not command or len(command) < 2:
                    continue
                
                # 3. Capture Screen
                print(f"{Fore.BLUE}[JARVIS] Observing screen...{Style.RESET_ALL}")
                img_bytes, _ = vision.capture_screen()
                
                # 4. Think
                print(f"{Fore.MAGENTA}[JARVIS] Thinking...{Style.RESET_ALL}")
                decision = brain.think(command, img_bytes)
                
                # 5. Speak (Async)
                if decision.get('speak'):
                    tts.speak_async(decision['speak'])
                
                # 6. Execute Actions
                actions = decision.get('actions', [])
                if actions:
                    print(f"{Fore.GREEN}[JARVIS] Executing {len(actions)} actions...{Style.RESET_ALL}")
                    result = executor.execute_actions(actions)
                    
                    # Handle recursive screenshot request
                    if result == "SCREENSHOT_REQUESTED":
                        print(f"{Fore.BLUE}[JARVIS] Re-evaluating screen...{Style.RESET_ALL}")
                        img_bytes, _ = vision.capture_screen()
                        decision = brain.think("Verify task progress and continue.", img_bytes)
                        if decision.get('speak'):
                            tts.speak_async(decision['speak'])
                        executor.execute_actions(decision.get('actions', []))
                
                print(f"{Fore.CYAN}Ready.{Style.RESET_ALL}")
                
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}JARVIS shutting down. Goodbye.{Style.RESET_ALL}")
        tts.speak("JARVIS shutting down. Goodbye.")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}[CRITICAL ERROR] {e}{Style.RESET_ALL}")
        tts.speak("A critical error occurred. I must shut down.")
        sys.exit(1)

if __name__ == "__main__":
    main()
