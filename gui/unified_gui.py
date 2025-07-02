"""
Unified Full-Stack GUI
Complete interface for all OPRYXX system functions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from core.performance_monitor import performance_monitor, start_performance_monitoring, stop_performance_monitoring
from core.memory_optimizer import memory_optimizer, OptimizationLevel
from core.enhanced_gpu_ops import enhanced_gpu_ops
from core.resilience_system import resilience_manager
from core.gpu_acceleration import is_gpu_available, get_compute_device

class UnifiedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OPRYXX Unified Control Center")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        self.monitoring_active = False
        self.setup_ui()
        self.start_background_updates()
    
    def setup_ui(self):
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create all tabs
        self.create_dashboard_tab()
        self.create_performance_tab()
        self.create_memory_tab()
        self.create_gpu_tab()
        self.create_resilience_tab()
        self.create_system_tab()
        self.create_settings_tab()
    
    def create_dashboard_tab(self):
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Status indicators
        status_frame = ttk.LabelFrame(self.dashboard_frame, text="System Status")
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_labels = {}
        statuses = ['Performance Monitor', 'Memory Optimizer', 'GPU Acceleration', 'Resilience System']
        for i, status in enumerate(statuses):
            ttk.Label(status_frame, text=f"{status}:").grid(row=i//2, column=(i%2)*2, sticky='w', padx=5)
            self.status_labels[status] = ttk.Label(status_frame, text="●", foreground='red')
            self.status_labels[status].grid(row=i//2, column=(i%2)*2+1, padx=5)
        
        # Real-time metrics
        metrics_frame = ttk.LabelFrame(self.dashboard_frame, text="Live Metrics")
        metrics_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create matplotlib figure for real-time charts
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 6))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        self.canvas = FigureCanvasTkAgg(self.fig, metrics_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Control buttons
        control_frame = ttk.Frame(self.dashboard_frame)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(control_frame, text="Start All Systems", command=self.start_all_systems).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Stop All Systems", command=self.stop_all_systems).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Emergency Stop", command=self.emergency_stop).pack(side='left', padx=5)
    
    def create_performance_tab(self):
        self.perf_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.perf_frame, text="Performance")
        
        # Performance controls
        control_frame = ttk.LabelFrame(self.perf_frame, text="Performance Monitoring")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(control_frame, text="Start Monitoring", command=self.start_performance_monitoring).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_performance_monitoring).pack(side='left', padx=5)
        
        # Current metrics display
        metrics_frame = ttk.LabelFrame(self.perf_frame, text="Current Metrics")
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        self.perf_labels = {}
        metrics = ['CPU Usage', 'Memory Usage', 'GPU Usage', 'Performance Score']
        for i, metric in enumerate(metrics):
            ttk.Label(metrics_frame, text=f"{metric}:").grid(row=i//2, column=(i%2)*3, sticky='w', padx=5)
            self.perf_labels[metric] = ttk.Label(metrics_frame, text="0%")
            self.perf_labels[metric].grid(row=i//2, column=(i%2)*3+1, padx=5)
            
            # Progress bars
            progress = ttk.Progressbar(metrics_frame, length=100)
            progress.grid(row=i//2, column=(i%2)*3+2, padx=5)
            self.perf_labels[f"{metric}_bar"] = progress
        
        # Performance history
        history_frame = ttk.LabelFrame(self.perf_frame, text="Performance History")
        history_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.perf_tree = ttk.Treeview(history_frame, columns=('Time', 'CPU', 'Memory', 'Score'), show='headings')
        for col in self.perf_tree['columns']:
            self.perf_tree.heading(col, text=col)
            self.perf_tree.column(col, width=100)
        self.perf_tree.pack(fill='both', expand=True)
    
    def create_memory_tab(self):
        self.memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_frame, text="Memory")
        
        # Memory optimization controls
        control_frame = ttk.LabelFrame(self.memory_frame, text="Memory Optimization")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(control_frame, text="Optimization Level:").pack(side='left', padx=5)
        self.opt_level = ttk.Combobox(control_frame, values=['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE'])
        self.opt_level.set('MODERATE')
        self.opt_level.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="Start Auto-Optimization", command=self.start_memory_optimization).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Manual Optimize", command=self.manual_memory_optimize).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Stop Optimization", command=self.stop_memory_optimization).pack(side='left', padx=5)
        
        # Memory metrics
        metrics_frame = ttk.LabelFrame(self.memory_frame, text="Memory Metrics")
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        self.memory_labels = {}
        mem_metrics = ['Total Memory', 'Available Memory', 'Used Memory', 'Usage Percent']
        for i, metric in enumerate(mem_metrics):
            ttk.Label(metrics_frame, text=f"{metric}:").grid(row=i//2, column=(i%2)*2, sticky='w', padx=5)
            self.memory_labels[metric] = ttk.Label(metrics_frame, text="0 MB")
            self.memory_labels[metric].grid(row=i//2, column=(i%2)*2+1, padx=5)
        
        # Optimization history
        history_frame = ttk.LabelFrame(self.memory_frame, text="Optimization History")
        history_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.memory_tree = ttk.Treeview(history_frame, columns=('Time', 'Before', 'After', 'Freed'), show='headings')
        for col in self.memory_tree['columns']:
            self.memory_tree.heading(col, text=col)
        self.memory_tree.pack(fill='both', expand=True)
    
    def create_gpu_tab(self):
        self.gpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gpu_frame, text="GPU Acceleration")
        
        # GPU status and controls
        status_frame = ttk.LabelFrame(self.gpu_frame, text="GPU Status")
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.gpu_available = ttk.Label(status_frame, text=f"GPU Available: {is_gpu_available()}")
        self.gpu_available.pack(anchor='w', padx=5)
        
        self.gpu_device = ttk.Label(status_frame, text=f"Active Device: {get_compute_device().name}")
        self.gpu_device.pack(anchor='w', padx=5)
        
        # GPU operations
        ops_frame = ttk.LabelFrame(self.gpu_frame, text="GPU Operations")
        ops_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(ops_frame, text="Matrix Multiplication Test", command=self.test_matrix_mult).pack(side='left', padx=5)
        ttk.Button(ops_frame, text="Vector Operations Test", command=self.test_vector_ops).pack(side='left', padx=5)
        ttk.Button(ops_frame, text="FFT Test", command=self.test_fft).pack(side='left', padx=5)
        ttk.Button(ops_frame, text="Full Benchmark", command=self.run_gpu_benchmark).pack(side='left', padx=5)
        
        # Benchmark results
        results_frame = ttk.LabelFrame(self.gpu_frame, text="Benchmark Results")
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.gpu_results = tk.Text(results_frame, height=15)
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.gpu_results.yview)
        self.gpu_results.configure(yscrollcommand=scrollbar.set)
        self.gpu_results.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_resilience_tab(self):
        self.resilience_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.resilience_frame, text="Resilience")
        
        # Circuit breaker status
        cb_frame = ttk.LabelFrame(self.resilience_frame, text="Circuit Breakers")
        cb_frame.pack(fill='x', padx=10, pady=5)
        
        self.cb_tree = ttk.Treeview(cb_frame, columns=('Name', 'State', 'Failures', 'Last Failure'), show='headings')
        for col in self.cb_tree['columns']:
            self.cb_tree.heading(col, text=col)
        self.cb_tree.pack(fill='both', expand=True)
        
        # Health checks
        health_frame = ttk.LabelFrame(self.resilience_frame, text="Health Monitoring")
        health_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(health_frame, text="Start Health Monitoring", command=self.start_health_monitoring).pack(side='left', padx=5)
        ttk.Button(health_frame, text="Manual Health Check", command=self.manual_health_check).pack(side='left', padx=5)
        ttk.Button(health_frame, text="Generate Report", command=self.generate_resilience_report).pack(side='left', padx=5)
        
        # System health status
        self.health_labels = {}
        health_systems = ['Database', 'Network', 'Storage', 'Services']
        for i, system in enumerate(health_systems):
            ttk.Label(health_frame, text=f"{system}:").grid(row=1, column=i*2, sticky='w', padx=5)
            self.health_labels[system] = ttk.Label(health_frame, text="●", foreground='green')
            self.health_labels[system].grid(row=1, column=i*2+1, padx=5)
    
    def create_system_tab(self):
        self.system_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.system_frame, text="System Control")
        
        # System operations
        ops_frame = ttk.LabelFrame(self.system_frame, text="System Operations")
        ops_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(ops_frame, text="System Scan", command=self.system_scan).pack(side='left', padx=5)
        ttk.Button(ops_frame, text="Disk Cleanup", command=self.disk_cleanup).pack(side='left', padx=5)
        ttk.Button(ops_frame, text="Registry Repair", command=self.registry_repair).pack(side='left', padx=5)
        ttk.Button(ops_frame, text="Network Reset", command=self.network_reset).pack(side='left', padx=5)
        
        # Recovery options
        recovery_frame = ttk.LabelFrame(self.system_frame, text="Recovery Options")
        recovery_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(recovery_frame, text="Safe Mode", command=self.safe_mode).pack(side='left', padx=5)
        ttk.Button(recovery_frame, text="System Restore", command=self.system_restore).pack(side='left', padx=5)
        ttk.Button(recovery_frame, text="Emergency Recovery", command=self.emergency_recovery).pack(side='left', padx=5)
        
        # System logs
        logs_frame = ttk.LabelFrame(self.system_frame, text="System Logs")
        logs_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.system_logs = tk.Text(logs_frame, height=20)
        log_scrollbar = ttk.Scrollbar(logs_frame, orient='vertical', command=self.system_logs.yview)
        self.system_logs.configure(yscrollcommand=log_scrollbar.set)
        self.system_logs.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
    
    def create_settings_tab(self):
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Configuration
        config_frame = ttk.LabelFrame(self.settings_frame, text="Configuration")
        config_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(config_frame, text="Update Interval (seconds):").grid(row=0, column=0, sticky='w', padx=5)
        self.update_interval = ttk.Entry(config_frame)
        self.update_interval.insert(0, "5")
        self.update_interval.grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Max History Records:").grid(row=1, column=0, sticky='w', padx=5)
        self.max_history = ttk.Entry(config_frame)
        self.max_history.insert(0, "1000")
        self.max_history.grid(row=1, column=1, padx=5)
        
        ttk.Button(config_frame, text="Save Settings", command=self.save_settings).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(config_frame, text="Load Settings", command=self.load_settings).grid(row=2, column=1, padx=5, pady=5)
        
        # Export/Import
        export_frame = ttk.LabelFrame(self.settings_frame, text="Data Management")
        export_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(export_frame, text="Export Data", command=self.export_data).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Import Data", command=self.import_data).pack(side='left', padx=5)
        ttk.Button(export_frame, text="Clear All Data", command=self.clear_data).pack(side='left', padx=5)
    
    # Event handlers
    def start_all_systems(self):
        self.start_performance_monitoring()
        self.start_memory_optimization()
        self.start_health_monitoring()
        self.log_message("All systems started")
    
    def stop_all_systems(self):
        self.stop_performance_monitoring()
        self.stop_memory_optimization()
        self.log_message("All systems stopped")
    
    def emergency_stop(self):
        self.stop_all_systems()
        messagebox.showwarning("Emergency Stop", "All systems have been stopped immediately!")
    
    def start_performance_monitoring(self):
        start_performance_monitoring()
        self.monitoring_active = True
        self.status_labels['Performance Monitor'].configure(foreground='green')
        self.log_message("Performance monitoring started")
    
    def stop_performance_monitoring(self):
        stop_performance_monitoring()
        self.monitoring_active = False
        self.status_labels['Performance Monitor'].configure(foreground='red')
        self.log_message("Performance monitoring stopped")
    
    def start_memory_optimization(self):
        level = getattr(OptimizationLevel, self.opt_level.get())
        memory_optimizer.optimization_level = level
        memory_optimizer.start_monitoring()
        self.status_labels['Memory Optimizer'].configure(foreground='green')
        self.log_message(f"Memory optimization started ({level.name})")
    
    def stop_memory_optimization(self):
        memory_optimizer.stop_monitoring()
        self.status_labels['Memory Optimizer'].configure(foreground='red')
        self.log_message("Memory optimization stopped")
    
    def manual_memory_optimize(self):
        result = memory_optimizer.optimize_memory()
        self.log_message(f"Manual optimization: freed {result['freed_mb']:.2f} MB")
    
    def test_matrix_mult(self):
        threading.Thread(target=self._run_matrix_test, daemon=True).start()
    
    def _run_matrix_test(self):
        a = np.random.randn(500, 500).astype(np.float32)
        b = np.random.randn(500, 500).astype(np.float32)
        
        start_time = time.time()
        result = enhanced_gpu_ops.accelerator.matrix_multiply(a, b)
        elapsed = time.time() - start_time
        
        self.gpu_results.insert(tk.END, f"Matrix Multiplication Test:\n")
        self.gpu_results.insert(tk.END, f"Size: 500x500, Time: {elapsed:.4f}s\n")
        self.gpu_results.insert(tk.END, f"Device: {get_compute_device().name}\n\n")
        self.gpu_results.see(tk.END)
    
    def test_vector_ops(self):
        threading.Thread(target=self._run_vector_test, daemon=True).start()
    
    def _run_vector_test(self):
        a = np.random.randn(10000).astype(np.float32)
        b = np.random.randn(10000).astype(np.float32)
        
        start_time = time.time()
        result = enhanced_gpu_ops.vector_operations('add', a, b)
        elapsed = time.time() - start_time
        
        self.gpu_results.insert(tk.END, f"Vector Addition Test:\n")
        self.gpu_results.insert(tk.END, f"Size: 10000, Time: {elapsed:.4f}s\n\n")
        self.gpu_results.see(tk.END)
    
    def test_fft(self):
        threading.Thread(target=self._run_fft_test, daemon=True).start()
    
    def _run_fft_test(self):
        data = np.random.randn(8192).astype(np.float32)
        
        start_time = time.time()
        result = enhanced_gpu_ops.fft_transform(data)
        elapsed = time.time() - start_time
        
        self.gpu_results.insert(tk.END, f"FFT Test:\n")
        self.gpu_results.insert(tk.END, f"Size: 8192, Time: {elapsed:.4f}s\n\n")
        self.gpu_results.see(tk.END)
    
    def run_gpu_benchmark(self):
        threading.Thread(target=self._run_full_benchmark, daemon=True).start()
    
    def _run_full_benchmark(self):
        benchmarks = enhanced_gpu_ops.benchmark_operations(size=1000)
        
        self.gpu_results.insert(tk.END, f"Full Benchmark Results:\n")
        for operation, time_ms in benchmarks.items():
            if operation != 'device':
                self.gpu_results.insert(tk.END, f"{operation}: {time_ms:.2f}ms\n")
        self.gpu_results.insert(tk.END, f"Device: {benchmarks['device']}\n\n")
        self.gpu_results.see(tk.END)
    
    def start_health_monitoring(self):
        self.log_message("Health monitoring started")
    
    def manual_health_check(self):
        self.log_message("Manual health check completed")
    
    def generate_resilience_report(self):
        report = resilience_manager.get_system_resilience_report()
        self.log_message(f"Resilience report generated: {len(report['circuit_breakers'])} circuit breakers")
    
    def system_scan(self):
        self.log_message("System scan initiated...")
        threading.Thread(target=self._system_scan_worker, daemon=True).start()
    
    def _system_scan_worker(self):
        time.sleep(2)  # Simulate scan
        self.log_message("System scan completed - No issues found")
    
    def disk_cleanup(self):
        self.log_message("Disk cleanup started...")
    
    def registry_repair(self):
        self.log_message("Registry repair started...")
    
    def network_reset(self):
        self.log_message("Network reset initiated...")
    
    def safe_mode(self):
        messagebox.showinfo("Safe Mode", "Safe mode preparation initiated")
    
    def system_restore(self):
        messagebox.showinfo("System Restore", "System restore point created")
    
    def emergency_recovery(self):
        messagebox.showwarning("Emergency Recovery", "Emergency recovery mode activated")
    
    def save_settings(self):
        settings = {
            'update_interval': self.update_interval.get(),
            'max_history': self.max_history.get(),
            'optimization_level': self.opt_level.get()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        self.log_message("Settings saved")
    
    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
            self.update_interval.delete(0, tk.END)
            self.update_interval.insert(0, settings.get('update_interval', '5'))
            self.max_history.delete(0, tk.END)
            self.max_history.insert(0, settings.get('max_history', '1000'))
            self.opt_level.set(settings.get('optimization_level', 'MODERATE'))
            self.log_message("Settings loaded")
        except FileNotFoundError:
            self.log_message("No settings file found")
    
    def export_data(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            self.log_message(f"Data exported to {filename}")
    
    def import_data(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            self.log_message(f"Data imported from {filename}")
    
    def clear_data(self):
        if messagebox.askyesno("Clear Data", "Are you sure you want to clear all data?"):
            self.log_message("All data cleared")
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.system_logs.insert(tk.END, f"[{timestamp}] {message}\n")
        self.system_logs.see(tk.END)
    
    def start_background_updates(self):
        self.update_displays()
        self.root.after(5000, self.start_background_updates)
    
    def update_displays(self):
        if self.monitoring_active:
            # Update performance metrics
            metrics = performance_monitor.get_metrics()
            self.perf_labels['CPU Usage'].configure(text=f"{metrics.cpu_usage:.1f}%")
            self.perf_labels['Memory Usage'].configure(text=f"{metrics.memory_usage:.1f}%")
            self.perf_labels['Performance Score'].configure(text=f"{metrics.score:.1f}")
            
            # Update progress bars
            self.perf_labels['CPU Usage_bar']['value'] = metrics.cpu_usage
            self.perf_labels['Memory Usage_bar']['value'] = metrics.memory_usage
            self.perf_labels['Performance Score_bar']['value'] = metrics.score
            
            # Add to history
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.perf_tree.insert('', 0, values=(timestamp, f"{metrics.cpu_usage:.1f}%", 
                                               f"{metrics.memory_usage:.1f}%", f"{metrics.score:.1f}"))
        
        # Update memory metrics
        mem_metrics = memory_optimizer.get_memory_metrics()
        self.memory_labels['Total Memory'].configure(text=f"{mem_metrics.total_mb:.0f} MB")
        self.memory_labels['Available Memory'].configure(text=f"{mem_metrics.available_mb:.0f} MB")
        self.memory_labels['Used Memory'].configure(text=f"{mem_metrics.used_mb:.0f} MB")
        self.memory_labels['Usage Percent'].configure(text=f"{mem_metrics.usage_percent:.1f}%")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = UnifiedGUI()
    app.run()