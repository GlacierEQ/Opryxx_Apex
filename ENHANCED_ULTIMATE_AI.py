"""
Enhanced Ultimate AI Optimizer
Now with notifications, gaming mode, voice commands, and web dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai.ULTIMATE_AI_OPTIMIZER import UltimateAIOptimizer
from enhancements.notifications import NexusNotifications
from enhancements.gaming_mode import GamingMode
from enhancements.voice_commands import VoiceCommands
from enhancements.dashboard import WebDashboard
import threading
import time

class EnhancedUltimateAI(UltimateAIOptimizer):
    def __init__(self):
        super().__init__()
        self.notifications = NexusNotifications()
        self.gaming_mode = GamingMode()
        self.voice_commands = VoiceCommands()
        self.dashboard = WebDashboard()
        
    def start_enhanced_optimization(self):
        """Start enhanced optimization with all features"""
        print("ENHANCED NEXUS AI STARTING...")
        
        # Start web dashboard
        self.dashboard.start()
        
        # Start voice commands
        self.voice_commands.start_listening()
        
        # Start base optimization
        self.start_ultimate_optimization()
        
        print("ALL ENHANCEMENTS ACTIVE!")
        print("- Notifications enabled")
        print("- Gaming mode ready")
        print("- Voice commands active")
        print("- Web dashboard running at http://localhost:8080")
    
    def _scan_and_autofix(self):
        """Enhanced scan with notifications"""
        # Check for gaming mode
        if self.gaming_mode.is_game_running() and not self.gaming_mode.active:
            self.gaming_mode.activate()
            self.notifications.notify("Gaming Mode", "Ultra-performance activated!")
        
        # Run original scan
        super()._scan_and_autofix()
        
        # Notify fixes
        if self.problems_solved > 0:
            self.notifications.ai_fixed_issue(f"{self.problems_solved} issues resolved")
    
    def _aggressive_optimization(self):
        """Enhanced optimization with notifications"""
        old_optimizations = self.optimizations_performed
        super()._aggressive_optimization()
        
        new_optimizations = self.optimizations_performed - old_optimizations
        if new_optimizations > 0:
            self.notifications.system_optimized(f"{new_optimizations} optimizations applied")

def main():
    """Launch Enhanced Ultimate AI"""
    print("ENHANCED NEXUS AI - Ultimate PC Optimizer")
    print("=" * 50)
    
    enhanced_ai = EnhancedUltimateAI()
    enhanced_ai.start_enhanced_optimization()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEnhanced NEXUS AI shutting down...")

if __name__ == "__main__":
    main()