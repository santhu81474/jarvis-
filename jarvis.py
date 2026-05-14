# One more trivial change for commit
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
   ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
   ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
   ██║███████║██████╔╝██║   ██║██║███████╗
   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
   ██║██║  ██║██║  ██║ ╚████╔╝ ██║███████║
   ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
{Fore.MAGENTA}          V1.0 - LOCAL AI ASSISTANT
{Style.RESET_ALL}
"""

def startup_checks():
    """Perform all necessary checks before starting."""
    print(BANNER)
    print(f"{Fore.BLUE}[SYSTEM]{Style.RESET_ALL} Initializing JARVIS core protocols...")
    
    # Check FFmpeg
    print(f"{Fore.BLUE}[SYSTEM]{Style.RESET_ALL} Verifying media dependencies (FFmpeg)...")
    listener.check_dependencies()
    
    # Check Ollama
    print(f"{Fore.BLUE}[SYSTEM]{Style.RESET_ALL} Connecting to Neural Engine (Ollama)...")
    ok, msg = brain.check_ollama()
    if not ok:
        print(f"{Fore.RED}[CRITICAL ERROR] {msg}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[ADVICE] Ensure Ollama is running and '{brain.MODEL_NAME}' is pulled.{Style.RESET_ALL}")
        tts.speak("Neural engine offline. Please check the terminal for instructions.")
        sys.exit(1)
    
    # Load Whisper
    print(f"{Fore.BLUE}[SYSTEM]{Style.RESET_ALL} Loading Speech-to-Text processor...")
    listener.load_whisper_model()
    
    print(f"\n{Fore.GREEN}[SUCCESS] All systems operational. JARVIS is online.{Style.RESET_ALL}")
    tts.speak("JARVIS online. How can I assist you today?")

def main():
    try:
        startup_checks()
        
        # Calibrate once at startup
        silence_threshold = listener.calibrate_silence_threshold()
        
        while True:
            print(f"\n{Fore.WHITE}Waiting for wake word...{Style.RESET_ALL}")
            
            if listener.listen_for_wake_word(silence_threshold):
                active_conversation = True
                
                while active_conversation:
                    # 2. Record command
                    command = listener.record_command(silence_threshold)
                    
                    if not command or len(command) < 2:
                        # If silence for too long, exit active conversation
                        print(f"{Fore.YELLOW}No command detected. Returning to sleep mode.{Style.RESET_ALL}")
                        active_conversation = False
                        break
                    
                    # Check for exit commands
                    exit_commands = ["goodbye", "go to sleep", "stop listening", "that is all", "bye"]
                    if any(ext in command.lower() for ext in exit_commands):
                        tts.speak("Of course. I'll be here if you need me. Just say Jarvis to wake me up again.")
                        active_conversation = False
                        break

                    # 3. Capture Screen
                    print(f"{Fore.CYAN}[JARVIS] Observing screen...{Style.RESET_ALL}")
                    img_bytes, img_base64 = vision.capture_screen()
                    
                    # 4. Think and decide
                    print(f"{Fore.MAGENTA}[JARVIS] Thinking...{Style.RESET_ALL}")
                    decision = brain.think(command, img_bytes)
                    
                    # 5. Confirm and Speak
                    if decision.get('speak'):
                        print(f"{Fore.YELLOW}[JARVIS] Speaking: {decision['speak']}{Style.RESET_ALL}")
                        tts.speak(decision['speak']) # Block speaking to ensure user hears confirmation
                    
                    # 6. Execute Actions in a loop
                    actions = decision.get('actions', [])
                    retries = 0
                    max_retries = 2
                    
                    while actions and retries < max_retries:
                        print(f"{Fore.GREEN}[JARVIS] Executing {len(actions)} actions (Step {retries+1})...{Style.RESET_ALL}")
                        result = executor.execute_actions(actions)
                        
                        if result == "SCREENSHOT_REQUESTED":
                            retries += 1
                            print(f"{Fore.BLUE}[JARVIS] Re-evaluating screen to verify...{Style.RESET_ALL}")
                            img_bytes, _ = vision.capture_screen()
                            decision = brain.think("Verify progress and confirm if the task is done.", img_bytes)
                            if decision.get('speak'):
                                tts.speak(decision['speak'])
                            actions = decision.get('actions', [])
                        else:
                            break
                    
                    print(f"{Fore.CYAN}Ready for your next command...{Style.RESET_ALL}")
                    # Loop repeats to record_command again immediately
                
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
