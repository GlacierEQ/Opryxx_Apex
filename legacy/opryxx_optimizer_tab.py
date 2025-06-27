"""
OPRYXX PC Optimizer Tab Integration
Created by Cascade AI - 2025-05-20
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import time
from datetime import datetime
from pc_optimizer import PCOptimizer

def setup_optimizer_tab(parent, notebook, status_queue, log_queue, progress_queue):
    """Set up the PC Optimizer tab in the OPRYXX GUI"""
    
    # Create the tab
    optimizer_tab = ttk.Frame(notebook)
    notebook.add(optimizer_tab, text="PC Optimizer")
    
    # Create the overall layout
    top_frame = tk.Frame(optimizer_tab, bg="#1e1e2f")
    top_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Create title 
    title_label = tk.Label(top_frame, text="🚀 OPRYXX System Optimization",
                          font=("Consolas", 18, "bold"), bg="#1e1e2f", fg="#e0e0e0")
    title_label.pack(pady=10)
    
    # Create section for system info
    info_frame = tk.Frame(optimizer_tab, bg="#1e1e2f")
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Create system info display
    info_label = tk.Label(info_frame, text="System Health Overview", 
                         font=("Consolas", 12, "bold"), bg="#1e1e2f", fg="#00c3ff")
    info_label.pack(anchor=tk.W, padx=5, pady=5)
    
    # Create metrics frame with 3 columns
    metrics_frame = tk.Frame(info_frame, bg="#1e1e2f")
    metrics_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Create metric displays
    metric_frames = []
    metric_labels = []
    metric_values = []
    
    for i, (icon, name) in enumerate([
        ("💻", "CPU Usage"),
        ("🧠", "Memory Usage"),
        ("💾", "Disk Space"),
        ("🌡️", "Temp Files"),
        ("🚀", "Performance"),
        ("🔌", "Power Mode")
    ]):
        # Create frame for each metric
        frame = tk.Frame(metrics_frame, bg="#2d2d44", width=120, height=80)
        frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        frame.pack_propagate(False)
        
        # Add label and value
        label = tk.Label(frame, text=f"{icon} {name}", bg="#2d2d44", fg="#00c3ff", font=("Consolas", 10, "bold"))
        label.pack(pady=(10, 0))
        
        value = tk.Label(frame, text="...", bg="#2d2d44", fg="#e0e0e0", font=("Consolas", 12))
        value.pack(pady=5)
        
        metric_frames.append(frame)
        metric_labels.append(label)
        metric_values.append(value)
    
    # Create action buttons frame
    actions_frame = tk.Frame(optimizer_tab, bg="#1e1e2f")
    actions_frame.pack(fill=tk.X, padx=10, pady=5)
    
    action_label = tk.Label(actions_frame, text="Optimization Actions", 
                          font=("Consolas", 12, "bold"), bg="#1e1e2f", fg="#00c3ff")
    action_label.pack(anchor=tk.W, padx=5, pady=5)
    
    # Create button grid for actions
    button_frame = tk.Frame(actions_frame, bg="#1e1e2f")
    button_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Define action buttons
    actions = [
        ("System Analysis", "Scan system for issues and provide recommendations", run_system_analysis),
        ("Clean Temporary Files", "Remove temporary files to free up disk space", run_temp_cleanup),
        ("Optimize Drives", "Defragment HDDs, trim SSDs, and optimize storage", run_drive_optimization),
        ("Repair Windows", "Run SFC and DISM to repair system files", run_windows_repair),
        ("Reset Network", "Reset network stack and configurations", run_network_reset),
        ("Full Optimization", "Run all optimization tasks for maximum performance", run_full_optimization)
    ]
    
    # Create function to create styled buttons
    def create_action_button(parent, text, description, command):
        frame = tk.Frame(parent, bg="#2d2d44", bd=1, relief=tk.RAISED)
        
        btn = tk.Button(frame, text=text, bg="#3a3a5c", fg="#ffffff",
                       font=("Consolas", 10, "bold"), bd=0, padx=10, pady=5,
                       activebackground="#545483", activeforeground="#ffffff",
                       command=lambda: command(optimizer))
        btn.pack(side=tk.TOP, fill=tk.X, padx=1, pady=1)
        
        desc = tk.Label(frame, text=description, bg="#2d2d44", fg="#b0b0b0",
                      font=("Consolas", 8), wraplength=180)
        desc.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        return frame, btn
    
    # Create the buttons
    button_objects = []
    for i, (title, description, command) in enumerate(actions):
        row = i // 3
        col = i % 3
        
        frame, btn = create_action_button(button_frame, title, description, command)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        button_objects.append(btn)
        
        # Configure grid column
        button_frame.columnconfigure(col, weight=1)
    
    # Configure grid rows
    for row in range((len(actions) + 2) // 3):
        button_frame.rowconfigure(row, weight=1)
    
    # Add progress section
    progress_frame = tk.Frame(optimizer_tab, bg="#1e1e2f")
    progress_frame.pack(fill=tk.X, padx=10, pady=5)
    
    progress_label = tk.Label(progress_frame, text="Optimization Progress", 
                            font=("Consolas", 12, "bold"), bg="#1e1e2f", fg="#00c3ff")
    progress_label.pack(anchor=tk.W, padx=5, pady=5)
    
    # Add status label and progress bar
    status_label = tk.Label(progress_frame, text="Ready", bg="#1e1e2f", fg="#e0e0e0",
                          font=("Consolas", 10))
    status_label.pack(anchor=tk.W, padx=5, pady=2)
    
    progress_var = tk.IntVar(value=0)
    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, mode="determinate",
                                  length=100, maximum=100)
    progress_bar.pack(fill=tk.X, padx=5, pady=5)
    
    # Add control buttons
    control_frame = tk.Frame(progress_frame, bg="#1e1e2f")
    control_frame.pack(fill=tk.X, padx=5, pady=5)
    
    stop_button = tk.Button(control_frame, text="Stop", bg="#7a1a1a", fg="#ffffff",
                          font=("Consolas", 10, "bold"), padx=10, pady=5)
    stop_button.pack(side=tk.RIGHT, padx=5)
    
    # Add log frame
    log_frame = tk.Frame(optimizer_tab, bg="#1e1e2f")
    log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    log_label = tk.Label(log_frame, text="Optimization Log", 
                       font=("Consolas", 12, "bold"), bg="#1e1e2f", fg="#00c3ff")
    log_label.pack(anchor=tk.W, padx=5, pady=5)
    
    # Add log display with scrollbar
    log_display = tk.Text(log_frame, bg="#0f0f1e", fg="#00ff00", font=("Consolas", 9),
                        wrap=tk.WORD, height=10)
    log_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_display.yview)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    log_display.config(yscrollcommand=log_scrollbar.set)
    
    # Save references to important widgets
    widgets = {
        "metric_values": metric_values,
        "status_label": status_label,
        "progress_var": progress_var,
        "progress_bar": progress_bar,
        "log_display": log_display,
        "stop_button": stop_button,
        "button_objects": button_objects
    }
    
    # Create PC Optimizer instance
    optimizer = create_optimizer(widgets, status_queue, log_queue, progress_queue)
    
    # Connect stop button
    stop_button.config(command=optimizer.stop)
    
    # Start system analysis on tab creation
    threading.Thread(target=lambda: update_system_metrics(optimizer, widgets), daemon=True).start()
    
    return optimizer_tab, optimizer, widgets

def create_optimizer(widgets, status_queue, log_queue, progress_queue):
    """Create PCOptimizer instance with callbacks"""
    
    def update_status_callback(text):
        status_queue.put(text)
        widgets["status_label"].config(text=text)
    
    def update_log_callback(text):
        log_queue.put(text)
        
        # Also update the log display directly
        log_display = widgets["log_display"]
        log_display.insert(tk.END, text)
        log_display.see(tk.END)
    
    def update_progress_callback(value):
        progress_queue.put(value)
        widgets["progress_var"].set(value)
    
    return PCOptimizer(
        update_status_callback=update_status_callback,
        update_log_callback=update_log_callback,
        update_progress_callback=update_progress_callback
    )

def update_system_metrics(optimizer, widgets):
    """Update system metrics display"""
    try:
        # Run system analysis
        results = optimizer.analyze_system()
        
        # Update metric displays
        metric_values = widgets["metric_values"]
        
        # CPU Usage
        metric_values[0].config(
            text=f"{results['cpu_usage']}%",
            fg=get_color_for_value(results['cpu_usage'], [70, 90])
        )
        
        # Memory Usage
        metric_values[1].config(
            text=f"{results['memory_usage']}%",
            fg=get_color_for_value(results['memory_usage'], [70, 90])
        )
        
        # Disk Space (average of all drives)
        if results['disk_space']:
            avg_usage = sum(info['percent'] for info in results['disk_space'].values()) / len(results['disk_space'])
            metric_values[2].config(
                text=f"{avg_usage:.1f}% Used",
                fg=get_color_for_value(avg_usage, [80, 90])
            )
        else:
            metric_values[2].config(text="N/A")
        
        # Temp Files
        temp_size_gb = results['temp_files_size'] / (1024 * 1024 * 1024)
        metric_values[3].config(
            text=f"{temp_size_gb:.2f} GB",
            fg=get_color_for_value(temp_size_gb, [1, 5])
        )
        
        # Performance Rating
        # Calculate a simple performance rating
        performance_score = 100
        
        # Reduce for high CPU/memory usage
        performance_score -= max(0, results['cpu_usage'] - 60) * 0.5
        performance_score -= max(0, results['memory_usage'] - 60) * 0.5
        
        # Reduce for disk space issues
        if results['disk_space']:
            for info in results['disk_space'].values():
                if info['percent'] > 90:
                    performance_score -= 15
                elif info['percent'] > 80:
                    performance_score -= 10
        
        # Reduce for temp file size
        if temp_size_gb > 5:
            performance_score -= 15
        elif temp_size_gb > 1:
            performance_score -= 5
        
        # Clamp to 0-100 range
        performance_score = max(0, min(100, performance_score))
        
        metric_values[4].config(
            text=f"{performance_score:.0f}/100",
            fg=get_color_for_value(performance_score, [60, 80], invert=True)
        )
        
        # Power Mode
        try:
            import subprocess
            result = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True)
            
            power_mode = "Balanced"
            if "Power Saver" in result.stdout:
                power_mode = "Power Saver"
            elif "High performance" in result.stdout:
                power_mode = "High Perf."
            elif "Ultimate Performance" in result.stdout:
                power_mode = "Ultimate"
            
            color = "#e0e0e0"
            if power_mode == "High Perf." or power_mode == "Ultimate":
                color = "#00ff00"
            elif power_mode == "Power Saver":
                color = "#ff9900"
            
            metric_values[5].config(text=power_mode, fg=color)
        except:
            metric_values[5].config(text="Unknown")
        
    except Exception as e:
        print(f"Error updating metrics: {e}")
    
    # Schedule next update
    threading.Timer(30, lambda: update_system_metrics(optimizer, widgets)).start()

def get_color_for_value(value, thresholds, invert=False):
    """Get color for a value based on thresholds [warning_threshold, critical_threshold]"""
    if invert:
        if value >= thresholds[1]:
            return "#00ff00"  # Green
        elif value >= thresholds[0]:
            return "#ffff00"  # Yellow
        else:
            return "#ff0000"  # Red
    else:
        if value >= thresholds[1]:
            return "#ff0000"  # Red
        elif value >= thresholds[0]:
            return "#ffff00"  # Yellow
        else:
            return "#00ff00"  # Green

# Action functions
def run_system_analysis(optimizer):
    threading.Thread(target=optimizer.analyze_system, daemon=True).start()

def run_temp_cleanup(optimizer):
    threading.Thread(target=optimizer.clean_temp_files, daemon=True).start()

def run_drive_optimization(optimizer):
    threading.Thread(target=optimizer.optimize_drives, daemon=True).start()

def run_windows_repair(optimizer):
    def repair_task():
        optimizer.scan_system_files()
        optimizer.run_dism_repair()
    
    threading.Thread(target=repair_task, daemon=True).start()

def run_network_reset(optimizer):
    threading.Thread(target=optimizer.reset_network, daemon=True).start()

def run_full_optimization(optimizer):
    threading.Thread(target=optimizer.run_full_optimization, daemon=True).start()
