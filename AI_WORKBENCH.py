"""
AI WORKBENCH - Intelligent PC Health Management System
Autonomous AI that keeps your PC at peak performance 24/7
"""

import os
import sys
import time
import json
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk

class AIWorkbench:
    def __init__(self):
        self.name = "ARIA"  # Autonomous Recovery & Intelligence Assistant
        self.health_score = 100
        self.active = False
        self.monitoring_interval = 300  # 5 minutes
        self.actions_taken = []
        self.system_state = {}
        
    def start_autonomous_monitoring(self):
        """Start 24/7 autonomous monitoring"""
        self.active = True
        self.log_action("AI WORKBENCH ACTIVATED - Autonomous monitoring started")
        
        def monitor_loop():
            while self.active:
                try:
                    self._perform_health_check()
                    self._take_autonomous_actions()
                    time.sleep(self.monitoring_interval)
                except Exception as e:
                    self.log_action(f"Monitoring error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        threading.Thread(target=monitor_loop, daemon=True).start()
    
    def _perform_health_check(self):
        """Comprehensive system health analysis"""
        health_metrics = {
            'cpu_usage': self._check_cpu_usage(),
            'memory_usage': self._check_memory_usage(),
            'disk_space': self._check_disk_space(),
            'temp_files': self._check_temp_files(),
            'startup_programs': self._check_startup_programs(),
            'system_errors': self._check_system_errors(),
            'network_health': self._check_network_health(),
            'security_status': self._check_security_status()
        }
        
        self.system_state = health_metrics
        self.health_score = self._calculate_health_score(health_metrics)
        
        self.log_action(f"Health check complete - Score: {self.health_score}%")
    
    def _take_autonomous_actions(self):
        """Take intelligent autonomous actions based on system state"""
        actions_taken = []
        
        # Critical actions (health < 70%)
        if self.health_score < 70:
            if self.system_state.get('temp_files', 0) > 1000:  # MB
                if self._clean_temp_files():
                    actions_taken.append("Cleaned temporary files")
            
            if self.system_state.get('memory_usage', 0) > 85:
                if self._optimize_memory():
                    actions_taken.append("Optimized memory usage")
            
            if self.system_state.get('disk_space', 100) < 15:
                if self._free_disk_space():
                    actions_taken.append("Freed disk space")
        
        # Preventive actions (health < 85%)
        elif self.health_score < 85:
            if self._should_defrag():
                if self._schedule_defrag():
                    actions_taken.append("Scheduled disk defragmentation")
            
            if self._check_updates_needed():
                if self._install_updates():
                    actions_taken.append("Installed system updates")
        
        # Optimization actions (health < 95%)
        elif self.health_score < 95:
            if self._optimize_startup():
                actions_taken.append("Optimized startup programs")
            
            if self._clean_registry():
                actions_taken.append("Cleaned registry entries")
        
        if actions_taken:
            self.log_action(f"Autonomous actions: {', '.join(actions_taken)}")
    
    def _check_cpu_usage(self) -> float:
        """Check CPU usage percentage"""
        try:
            result = subprocess.run(['wmic', 'cpu', 'get', 'loadpercentage', '/value'], 
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'LoadPercentage' in line:
                    return float(line.split('=')[1])
        except:
            pass
        return 50.0  # Default if can't determine
    
    def _check_memory_usage(self) -> float:
        """Check memory usage percentage"""
        try:
            result = subprocess.run(['wmic', 'OS', 'get', 'TotalVisibleMemorySize,FreePhysicalMemory', '/value'], 
                                  capture_output=True, text=True)
            total, free = 0, 0
            for line in result.stdout.split('\n'):
                if 'TotalVisibleMemorySize' in line:
                    total = int(line.split('=')[1])
                elif 'FreePhysicalMemory' in line:
                    free = int(line.split('=')[1])
            
            if total > 0:
                return ((total - free) / total) * 100
        except:
            pass
        return 60.0
    
    def _check_disk_space(self) -> float:
        """Check available disk space percentage"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('C:')
            return (free / total) * 100
        except:
            return 50.0
    
    def _check_temp_files(self) -> int:
        """Check temporary files size in MB"""
        try:
            temp_dirs = [os.environ.get('TEMP', ''), 'C:\\Windows\\Temp']
            total_size = 0
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            try:
                                total_size += os.path.getsize(os.path.join(root, file))
                            except:
                                pass
            
            return total_size // (1024 * 1024)  # Convert to MB
        except:
            return 0
    
    def _check_startup_programs(self) -> int:
        """Check number of startup programs"""
        try:
            result = subprocess.run(['wmic', 'startup', 'get', 'name'], 
                                  capture_output=True, text=True)
            return len([line for line in result.stdout.split('\n') if line.strip() and 'Name' not in line])
        except:
            return 10
    
    def _check_system_errors(self) -> int:
        """Check recent system errors"""
        try:
            result = subprocess.run(['wevtutil', 'qe', 'System', '/c:10', '/rd:true', '/f:text'], 
                                  capture_output=True, text=True)
            return result.stdout.lower().count('error')
        except:
            return 0
    
    def _check_network_health(self) -> bool:
        """Check network connectivity"""
        try:
            result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_security_status(self) -> bool:
        """Check Windows Defender status"""
        try:
            result = subprocess.run(['powershell', 'Get-MpComputerStatus'], 
                                  capture_output=True, text=True)
            return 'enabled' in result.stdout.lower()
        except:
            return True  # Assume secure if can't check
    
    def _calculate_health_score(self, metrics: Dict) -> int:
        """Calculate overall system health score"""
        score = 100
        
        # CPU usage penalty
        if metrics['cpu_usage'] > 80:
            score -= 15
        elif metrics['cpu_usage'] > 60:
            score -= 8
        
        # Memory usage penalty
        if metrics['memory_usage'] > 90:
            score -= 20
        elif metrics['memory_usage'] > 75:
            score -= 10
        
        # Disk space penalty
        if metrics['disk_space'] < 10:
            score -= 25
        elif metrics['disk_space'] < 20:
            score -= 15
        
        # Temp files penalty
        if metrics['temp_files'] > 2000:
            score -= 10
        elif metrics['temp_files'] > 1000:
            score -= 5
        
        # Startup programs penalty
        if metrics['startup_programs'] > 20:
            score -= 8
        elif metrics['startup_programs'] > 15:
            score -= 4
        
        # System errors penalty
        score -= min(metrics['system_errors'] * 2, 15)
        
        # Network and security bonuses
        if not metrics['network_health']:
            score -= 5
        if not metrics['security_status']:
            score -= 10
        
        return max(0, min(100, score))
    
    def _clean_temp_files(self) -> bool:
        """Clean temporary files"""
        try:
            temp_dirs = [os.environ.get('TEMP', ''), 'C:\\Windows\\Temp']
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    subprocess.run(['del', '/q', '/s', f'{temp_dir}\\*'], 
                                 shell=True, capture_output=True)
            
            return True
        except:
            return False
    
    def _optimize_memory(self) -> bool:
        """Optimize memory usage"""
        try:
            # Clear system cache
            subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                         capture_output=True)
            return True
        except:
            return False
    
    def _free_disk_space(self) -> bool:
        """Free up disk space"""
        try:
            # Run disk cleanup
            subprocess.run(['cleanmgr', '/sagerun:1'], capture_output=True)
            return True
        except:
            return False
    
    def _should_defrag(self) -> bool:
        """Check if defragmentation is needed"""
        try:
            result = subprocess.run(['defrag', 'C:', '/A'], capture_output=True, text=True)
            return 'fragmented' in result.stdout.lower()
        except:
            return False
    
    def _schedule_defrag(self) -> bool:
        """Schedule disk defragmentation"""
        try:
            subprocess.run(['defrag', 'C:', '/O'], capture_output=True)
            return True
        except:
            return False
    
    def _check_updates_needed(self) -> bool:
        """Check if Windows updates are needed"""
        try:
            result = subprocess.run(['powershell', 'Get-WindowsUpdate'], 
                                  capture_output=True, text=True)
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def _install_updates(self) -> bool:
        """Install Windows updates"""
        try:
            subprocess.run(['usoclient', 'StartDownload'], capture_output=True)
            return True
        except:
            return False
    
    def _optimize_startup(self) -> bool:
        """Optimize startup programs"""
        try:
            # Disable unnecessary startup programs
            result = subprocess.run(['wmic', 'startup', 'where', 'command like "%temp%"', 'delete'], 
                                  capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _clean_registry(self) -> bool:
        """Clean registry entries"""
        try:
            # Basic registry cleanup
            subprocess.run(['reg', 'delete', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 
                          '/v', 'TempEntry', '/f'], capture_output=True)
            return True
        except:
            return False
    
    def log_action(self, action: str):
        """Log AI actions with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] ARIA: {action}"
        self.actions_taken.append(log_entry)
        print(log_entry)
    
    def get_status_report(self) -> Dict:
        """Get comprehensive status report"""
        return {
            'ai_name': self.name,
            'active': self.active,
            'health_score': self.health_score,
            'system_state': self.system_state,
            'recent_actions': self.actions_taken[-10:],  # Last 10 actions
            'monitoring_since': len(self.actions_taken),
            'last_check': datetime.now().isoformat()
        }

class AIWorkbenchGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI WORKBENCH - Intelligent PC Health Manager")
        self.root.geometry("1000x700")
        self.root.configure(bg='#0a0a0a')
        
        self.ai = AIWorkbench()
        self.setup_gui()
        self.update_display()
    
    def setup_gui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#0a0a0a')
        title_frame.pack(fill='x', pady=20)
        
        tk.Label(title_frame, text="🤖 AI WORKBENCH", 
                font=('Arial', 24, 'bold'), fg='#00ff41', bg='#0a0a0a').pack()
        
        tk.Label(title_frame, text="Autonomous PC Health Management", 
                font=('Arial', 12), fg='white', bg='#0a0a0a').pack()
        
        # Status panel
        status_frame = tk.Frame(self.root, bg='#1a1a1a', relief='raised', bd=2)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(status_frame, text="🔋 SYSTEM STATUS", 
                font=('Arial', 14, 'bold'), fg='#00ff41', bg='#1a1a1a').pack(pady=10)
        
        # Health score
        self.health_var = tk.StringVar(value="Health Score: Analyzing...")
        tk.Label(status_frame, textvariable=self.health_var, 
                font=('Arial', 16, 'bold'), fg='#00ff41', bg='#1a1a1a').pack(pady=5)
        
        # AI status
        self.ai_status_var = tk.StringVar(value="AI Status: Standby")
        tk.Label(status_frame, textvariable=self.ai_status_var, 
                font=('Arial', 12), fg='white', bg='#1a1a1a').pack(pady=5)
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#1a1a1a', relief='raised', bd=2)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(control_frame, text="🎛️ AI CONTROLS", 
                font=('Arial', 14, 'bold'), fg='#00ff41', bg='#1a1a1a').pack(pady=10)
        
        buttons_frame = tk.Frame(control_frame, bg='#1a1a1a')
        buttons_frame.pack(pady=10)
        
        tk.Button(buttons_frame, text="🚀 ACTIVATE AI", command=self.activate_ai,
                 bg='#00aa00', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="⏸️ PAUSE AI", command=self.pause_ai,
                 bg='#aa6600', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="🔍 HEALTH CHECK", command=self.manual_health_check,
                 bg='#0066aa', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text="🧹 OPTIMIZE NOW", command=self.optimize_now,
                 bg='#aa0066', fg='white', font=('Arial', 10, 'bold'), padx=20).pack(side='left', padx=5)
        
        # Activity log
        log_frame = tk.Frame(self.root, bg='#1a1a1a', relief='raised', bd=2)
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(log_frame, text="📊 AI ACTIVITY LOG", 
                font=('Arial', 14, 'bold'), fg='#00ff41', bg='#1a1a1a').pack(pady=10)
        
        self.log_text = tk.Text(log_frame, bg='#0a0a0a', fg='#00ff41', 
                               font=('Consolas', 9), wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def activate_ai(self):
        """Activate autonomous AI monitoring"""
        if not self.ai.active:
            self.ai.start_autonomous_monitoring()
            self.ai_status_var.set("AI Status: ACTIVE - Monitoring 24/7")
            self.log_message("🤖 ARIA AI activated - Autonomous monitoring started")
    
    def pause_ai(self):
        """Pause AI monitoring"""
        self.ai.active = False
        self.ai_status_var.set("AI Status: PAUSED")
        self.log_message("⏸️ ARIA AI paused")
    
    def manual_health_check(self):
        """Perform manual health check"""
        self.log_message("🔍 Manual health check initiated...")
        
        def check_worker():
            self.ai._perform_health_check()
            self.root.after(0, lambda: self.log_message(f"✅ Health check complete - Score: {self.ai.health_score}%"))
        
        threading.Thread(target=check_worker, daemon=True).start()
    
    def optimize_now(self):
        """Perform immediate optimization"""
        self.log_message("🧹 Immediate optimization started...")
        
        def optimize_worker():
            self.ai._perform_health_check()
            self.ai._take_autonomous_actions()
            self.root.after(0, lambda: self.log_message("✅ Optimization complete"))
        
        threading.Thread(target=optimize_worker, daemon=True).start()
    
    def update_display(self):
        """Update GUI display"""
        # Update health score
        if self.ai.health_score >= 90:
            color = '#00ff41'
            status = "EXCELLENT"
        elif self.ai.health_score >= 75:
            color = '#ffff00'
            status = "GOOD"
        elif self.ai.health_score >= 50:
            color = '#ff8800'
            status = "FAIR"
        else:
            color = '#ff0000'
            status = "POOR"
        
        self.health_var.set(f"Health Score: {self.ai.health_score}% ({status})")
        
        # Update AI status
        if self.ai.active:
            self.ai_status_var.set("AI Status: ACTIVE - Monitoring 24/7")
        
        # Update log
        recent_actions = self.ai.actions_taken[-5:]  # Last 5 actions
        for action in recent_actions:
            if action not in self.log_text.get(1.0, tk.END):
                self.log_text.insert(tk.END, action + "\n")
                self.log_text.see(tk.END)
        
        # Schedule next update
        self.root.after(5000, self.update_display)  # Update every 5 seconds
    
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.insert(tk.END, log_entry + "\n")
        self.log_text.see(tk.END)
    
    def run(self):
        self.root.mainloop()

def main():
    """Launch AI Workbench"""
    print("🤖 AI WORKBENCH - Intelligent PC Health Manager")
    print("=" * 50)
    
    app = AIWorkbenchGUI()
    app.run()

if __name__ == "__main__":
    main()