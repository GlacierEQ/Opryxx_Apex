"""
Gaming Mode - Ultra Performance
"""

import psutil
import subprocess

class GamingMode:
    def __init__(self):
        self.active = False
        self.original_settings = {}
    
    def activate(self):
        """Activate ultra-performance gaming mode"""
        self.active = True
        
        # Set high performance power plan
        subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], 
                      capture_output=True)
        
        # Disable Windows Game Mode interference
        subprocess.run(['reg', 'add', 'HKCU\\Software\\Microsoft\\GameBar', 
                       '/v', 'AllowAutoGameMode', '/t', 'REG_DWORD', '/d', '0', '/f'], 
                      capture_output=True)
        
        # Optimize CPU priority
        subprocess.run(['wmic', 'process', 'where', 'name="dwm.exe"', 
                       'CALL', 'setpriority', '64'], capture_output=True)
        
        print("GAMING MODE ACTIVATED - Ultra Performance Ready!")
    
    def deactivate(self):
        """Deactivate gaming mode"""
        self.active = False
        
        # Restore balanced power plan
        subprocess.run(['powercfg', '/setactive', '381b4222-f694-41f0-9685-ff5bb260df2e'], 
                      capture_output=True)
        
        print("Gaming mode deactivated - Normal operation resumed")
    
    def is_game_running(self) -> bool:
        """Detect if games are running"""
        game_processes = ['steam.exe', 'epic', 'game', 'launcher']
        
        for proc in psutil.process_iter(['name']):
            if any(game in proc.info['name'].lower() for game in game_processes):
                return True
        return False