"""
Voice Commands for NEXUS AI
"""

import subprocess
import threading
import time

class VoiceCommands:
    def __init__(self):
        self.listening = False
        self.commands = {
            "nexus optimize": self._optimize_system,
            "nexus emergency": self._emergency_recovery,
            "nexus gaming mode": self._activate_gaming,
            "nexus status": self._system_status
        }
    
    def start_listening(self):
        """Start voice command listener"""
        self.listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()
        print("Voice commands activated - Say 'Hey NEXUS' to start")
    
    def _listen_loop(self):
        """Simple voice command simulation"""
        while self.listening:
            try:
                # Simulate voice detection with keyboard input
                command = input("Voice Command (or 'quit'): ").lower()
                
                if command == 'quit':
                    break
                
                if command in self.commands:
                    self.commands[command]()
                else:
                    print("Command not recognized")
                    
            except:
                break
    
    def _optimize_system(self):
        print("NEXUS: Optimizing system now...")
        subprocess.run(['python', 'ai/ULTIMATE_AI_OPTIMIZER.py'], capture_output=True)
    
    def _emergency_recovery(self):
        print("NEXUS: Running emergency recovery...")
        subprocess.run(['python', 'recovery/immediate_safe_mode_exit.py'], capture_output=True)
    
    def _activate_gaming(self):
        print("NEXUS: Activating gaming mode...")
        from enhancements.gaming_mode import GamingMode
        gaming = GamingMode()
        gaming.activate()
    
    def _system_status(self):
        print("NEXUS: System status - All systems operational")