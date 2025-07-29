"""Predictive Analytics Panel for the MASTER GUI"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import psutil
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib import style

# Use a modern style for the plots
style.use('seaborn-v0_8-darkgrid')

class PredictiveAnalyticsPanel(ttk.Frame):
    """Panel for displaying predictive analytics and system trends"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.metrics = {'timestamps': [], 'cpu': [], 'memory': [], 'disk': []}
        self._setup_ui()
        self._update_interval = 60000  # 1 minute
        self._schedule_updates()
    
    def _setup_ui(self) -> None:
        """Initialize the UI components"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header
        ttk.Label(
            self,
            text="Predictive Analytics",
            font=('Helvetica', 12, 'bold')
        ).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        # Notebook for different metrics
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        
        # Create tabs for each metric
        self.figures = {}
        self.axes = {}
        self.canvases = {}
        
        for metric in ['CPU', 'Memory', 'Disk']:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=metric)
            
            # Configure grid
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
            
            # Create figure and canvas
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Format x-axis for dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            fig.autofmt_xdate()
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
            
            # Store references
            self.figures[metric] = fig
            self.axes[metric] = ax
            self.canvases[metric] = canvas
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            self,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        ).grid(row=2, column=0, sticky='ew', padx=5, pady=2)
        
        # Initial update
        self._update_metrics()
    
    def _schedule_updates(self) -> None:
        """Schedule periodic updates"""
        self._update_metrics()
        self.after(self._update_interval, self._schedule_updates)
    
    def _update_metrics(self) -> None:
        """Update metrics with current system data"""
        try:
            now = datetime.now()
            
            # Get current metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Store metrics
            self.metrics['timestamps'].append(now)
            self.metrics['cpu'].append(cpu_percent)
            self.metrics['memory'].append(mem.percent)
            self.metrics['disk'].append(disk.percent)
            
            # Keep only last 100 data points
            max_points = 100
            for key in self.metrics:
                self.metrics[key] = self.metrics[key][-max_points:]
            
            # Update charts
            self._update_charts()
            
            # Update status
            self.status_var.set(
                f"Last updated: {now.strftime('%H:%M:%S')} | "
                f"CPU: {cpu_percent:.1f}% | "
                f"Memory: {mem.percent:.1f}% | "
                f"Disk: {disk.percent:.1f}%"
            )
            
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def _update_charts(self) -> None:
        """Update all charts with current data"""
        if not self.metrics['timestamps']:
            return
        
        timestamps = self.metrics['timestamps']
        
        for metric in ['CPU', 'Memory', 'Disk']:
            key = metric.lower()
            values = self.metrics[key]
            
            # Get figure and axes
            fig = self.figures[metric]
            ax = self.axes[metric]
            
            # Clear previous plot
            ax.clear()
            
            # Plot data
            ax.plot(timestamps, values, 'b-', label='Actual')
            
            # Add prediction (simple linear extrapolation)
            if len(values) > 5:
                # Simple prediction: linear regression of last 5 points
                x = mdates.date2num(timestamps[-5:])
                y = values[-5:]
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                
                # Predict next 3 points
                future_times = [
                    timestamps[-1] + timedelta(minutes=1),
                    timestamps[-1] + timedelta(minutes=2),
                    timestamps[-1] + timedelta(minutes=3)
                ]
                future_x = mdates.date2num(future_times)
                future_y = p(future_x)
                
                # Plot prediction
                ax.plot(future_times, future_y, 'r--', label='Predicted')
                
                # Highlight prediction area
                ax.axvspan(timestamps[-1], future_times[-1], color='red', alpha=0.1)
            
            # Set title and labels
            ax.set_title(f"{metric} Usage")
            ax.set_xlabel('Time')
            ax.set_ylabel('Usage (%)')
            ax.set_ylim(0, 100)  # 0-100% scale
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            fig.autofmt_xdate()
            
            # Add legend
            ax.legend()
            
            # Redraw canvas
            self.canvases[metric].draw()

# Add numpy import at the top if not already present
import numpy as np
