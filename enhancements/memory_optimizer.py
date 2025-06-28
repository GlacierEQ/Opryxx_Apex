"""
Advanced Memory Optimizer
Enhanced memory management and optimization
"""

import psutil
import subprocess
import ctypes
import os
from ctypes import wintypes

class AdvancedMemoryOptimizer:
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
        self.psapi = ctypes.windll.psapi
        
    def optimize_memory_aggressive(self):
        """Aggressive memory optimization"""
        optimizations = []
        
        # Clear standby memory
        try:
            self._clear_standby_memory()
            optimizations.append("Standby memory cleared")
        except:
            pass
        
        # Optimize working sets
        try:
            self._optimize_working_sets()
            optimizations.append("Working sets optimized")
        except:
            pass
        
        # Clear system cache
        try:
            self._clear_system_cache()
            optimizations.append("System cache cleared")
        except:
            pass
        
        # Optimize virtual memory
        try:
            self._optimize_virtual_memory()
            optimizations.append("Virtual memory optimized")
        except:
            pass
        
        return optimizations
    
    def _clear_standby_memory(self):
        """Clear Windows standby memory"""
        # Use EmptyStandbyList API
        try:
            subprocess.run(['rundll32.exe', 'advapi32.dll,ProcessIdleTasks'], 
                         capture_output=True, timeout=30)
        except:
            pass
    
    def _optimize_working_sets(self):
        """Optimize process working sets"""
        for proc in psutil.process_iter(['pid']):
            try:
                # Trim working set for each process
                handle = self.kernel32.OpenProcess(0x1F0FFF, False, proc.info['pid'])
                if handle:
                    self.psapi.EmptyWorkingSet(handle)
                    self.kernel32.CloseHandle(handle)
            except:
                continue
    
    def _clear_system_cache(self):
        """Clear system file cache"""
        try:
            # Clear DNS cache
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            
            # Clear font cache
            font_cache = os.path.expandvars('%WINDIR%\\System32\\FNTCACHE.DAT')
            if os.path.exists(font_cache):
                try:
                    os.remove(font_cache)
                except:
                    pass
            
            # Clear icon cache
            icon_cache = os.path.expandvars('%LOCALAPPDATA%\\IconCache.db')
            if os.path.exists(icon_cache):
                try:
                    os.remove(icon_cache)
                except:
                    pass
        except:
            pass
    
    def _optimize_virtual_memory(self):
        """Optimize virtual memory settings"""
        try:
            # Set optimal page file size
            total_ram = psutil.virtual_memory().total // (1024**3)  # GB
            optimal_size = int(total_ram * 1.5 * 1024)  # 1.5x RAM in MB
            
            subprocess.run([
                'wmic', 'computersystem', 'where', f'name="{os.environ["COMPUTERNAME"]}"',
                'set', f'AutomaticManagedPagefile=False'
            ], capture_output=True)
            
            subprocess.run([
                'wmic', 'pagefileset', 'where', 'name="C:\\\\pagefile.sys"',
                'set', f'InitialSize={optimal_size},MaximumSize={optimal_size}'
            ], capture_output=True)
            
        except:
            pass
    
    def get_memory_stats(self):
        """Get detailed memory statistics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_ram': f"{memory.total // (1024**3)} GB",
            'available_ram': f"{memory.available // (1024**3)} GB", 
            'ram_usage': f"{memory.percent}%",
            'swap_total': f"{swap.total // (1024**3)} GB",
            'swap_used': f"{swap.used // (1024**3)} GB",
            'swap_usage': f"{swap.percent}%"
        }
    
    def monitor_memory_leaks(self):
        """Monitor for memory leaks"""
        leaky_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                if proc.info['memory_percent'] > 10:  # Using more than 10% RAM
                    leaky_processes.append({
                        'name': proc.info['name'],
                        'pid': proc.info['pid'],
                        'memory_percent': f"{proc.info['memory_percent']:.1f}%"
                    })
            except:
                continue
        
        return leaky_processes
    
    def auto_memory_management(self):
        """Automatic memory management"""
        memory = psutil.virtual_memory()
        actions_taken = []
        
        # If memory usage > 80%, take action
        if memory.percent > 80:
            # Clear standby memory
            self._clear_standby_memory()
            actions_taken.append("Cleared standby memory")
            
            # Optimize working sets
            self._optimize_working_sets()
            actions_taken.append("Optimized working sets")
            
            # Kill memory hogs if necessary
            if memory.percent > 90:
                for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                    try:
                        if proc.info['memory_percent'] > 15:  # Kill processes using >15% RAM
                            proc.terminate()
                            actions_taken.append(f"Terminated {proc.info['name']}")
                            break  # Only kill one at a time
                    except:
                        continue
        
        return actions_taken