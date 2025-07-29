"""Performance History Panel for the MASTER GUI"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import dates as mdates
from matplotlib import style
import psutil

# Use a modern style for the plots
style.use('seaborn-v0_8-darkgrid')

class PerformanceHistoryPanel(ttk.Frame):
    """Panel for visualizing historical performance metrics"""
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._setup_ui()
        self._update_interval = 60000  # 1 minute
        self._schedule_updates()
    
    def _setup_ui(self) -> None:
        """Initialize the UI components"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Label(
            header,
            text="Performance History",
            font=('Helvetica', 12, 'bold')
        ).pack(side='left')
        
        # Time range selector
        time_frame = ttk.Frame(header)
        time_frame.pack(side='right', padx=5)
        
        ttk.Label(time_frame, text="Time Range:").pack(side='left', padx=2)
        
        self.time_range_var = tk.StringVar(value="24h")
        time_ranges = [
            ("1 Hour", "1h"),
            ("24 Hours", "24h"),
            ("7 Days", "7d"),
            ("30 Days", "30d")
        ]
        
        for text, value in time_ranges:
            rb = ttk.Radiobutton(
                time_frame,
                text=text,
                variable=self.time_range_var,
                value=value,
                command=self._update_charts
            )
            rb.pack(side='left', padx=2)
        
        # Main content
        content = ttk.Frame(self)
        content.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        
        # Create notebook for different metrics
        self.notebook = ttk.Notebook(content)
        self.notebook.grid(row=0, column=0, sticky='nsew')
        
        # Create tabs for each metric type
        self.metric_tabs = {}
        self.figures = {}
        self.axes = {}
        self.canvases = {}
        self.toolbars = {}
        
        # Define metrics to track
        self.metrics = [
            ('CPU', 'cpu.usage', 'CPU Usage (%)', 'percentage'),
            ('Memory', 'memory.percent', 'Memory Usage (%)', 'percentage'),
            ('Disk', 'disk.usage', 'Disk Usage (%)', 'percentage'),
            ('Network', 'network.bytes_recv', 'Network Received (MB)', 'bytes')
        ]
        
        for tab_name, metric_id, ylabel, unit in self.metrics:
            # Create a frame for each tab
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=tab_name)
            self.metric_tabs[metric_id] = frame
            
            # Configure grid
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)  # Chart area
            
            # Create figure and axis
            fig = Figure(figsize=(8, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Format x-axis for dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
            fig.autofmt_xdate()
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            
            # Create toolbar
            toolbar_frame = ttk.Frame(frame)
            toolbar_frame.grid(row=0, column=0, sticky='ew')
            
            toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
            toolbar.update()
            
            # Add canvas to frame
            canvas.get_tk_widget().grid(row=1, column=0, sticky='nsew')
            
            # Store references
            self.figures[metric_id] = fig
            self.axes[metric_id] = ax
            self.canvases[metric_id] = canvas
            self.toolbars[metric_id] = toolbar
            
            # Set labels
            ax.set_ylabel(ylabel)
            ax.set_title(f"{tab_name} Over Time")
            
            # Set y-axis limits based on unit
            if unit == 'percentage':
                ax.set_ylim(0, 100)  # 0-100% for percentages
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            self,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        ).grid(row=2, column=0, sticky='ew', padx=5, pady=2)
        
        # Initial update
        self._update_charts()
    
    def _schedule_updates(self) -> None:
        """Schedule periodic updates"""
        self._update_charts()
        self.after(self._update_interval, self._schedule_updates)
    
    def _update_charts(self) -> None:
        """Update all charts with current data"""
        try:
            time_range = self.time_range_var.get()
            
            # Get time range
            now = datetime.now()
            if time_range == '1h':
                start_time = now - timedelta(hours=1)
                interval = '5m'
            elif time_range == '24h':
                start_time = now - timedelta(days=1)
                interval = '1h'
            elif time_range == '7d':
                start_time = now - timedelta(days=7)
                interval = '6h'
            else:  # 30d
                start_time = now - timedelta(days=30)
                interval = '1d'
            
            # Update each chart
            for tab_name, metric_id, ylabel, unit in self.metrics:
                self._update_chart(metric_id, start_time, now, interval, unit)
            
            # Update status
            self.status_var.set(f"Last updated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            self.status_var.set(f"Error updating charts: {str(e)}")
    
    def _update_chart(
        self, 
        metric_id: str, 
        start_time: datetime, 
        end_time: datetime, 
        interval: str,
        unit: str
    ) -> None:
        """Update a single chart with data"""
        # In a real implementation, this would fetch data from the PerformanceTracker
        # For now, we'll generate some sample data
        timestamps, values = self._generate_sample_data(metric_id, start_time, end_time, interval)
        
        # Get chart components
        ax = self.axes[metric_id]
        fig = self.figures[metric_id]
        
        # Clear previous plot
        ax.clear()
        
        # Plot data
        ax.plot(timestamps, values, 'b-', label='Actual')
        
        # Add prediction if we have enough data
        if len(values) > 10:
            # Simple prediction: average of last few points
            last_value = sum(values[-5:]) / 5
            pred_timestamps = [timestamps[-1], end_time]
            pred_values = [last_value, last_value * 1.1]  # 10% increase
            
            ax.plot(pred_timestamps, pred_values, 'r--', label='Predicted')
            ax.axvspan(timestamps[-1], end_time, color='red', alpha=0.1)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M'))
        fig.autofmt_xdate()
        
        # Set title and labels
        ax.set_title(f"{metric_id.split('.')[0].capitalize()} Over Time")
        ax.set_xlabel('Time')
        
        # Set y-axis label based on unit
        if unit == 'percentage':
            ax.set_ylabel('Usage (%)')
            ax.set_ylim(0, 100)
        elif unit == 'bytes':
            ax.set_ylabel('Data (MB)')
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Redraw canvas
        self.canvases[metric_id].draw()
    
    def _generate_sample_data(
        self, 
        metric_id: str, 
        start_time: datetime, 
        end_time: datetime, 
        interval: str
    ) -> Tuple[List[datetime], List[float]]:
        """Generate sample data for demonstration"""
        # In a real implementation, this would fetch data from PerformanceTracker
        
        # Calculate time delta based on interval
        if interval == '5m':
            delta = timedelta(minutes=5)
        elif interval == '1h':
            delta = timedelta(hours=1)
        elif interval == '6h':
            delta = timedelta(hours=6)
        else:  # 1d
            delta = timedelta(days=1)
        
        # Generate timestamps
        current = start_time
        timestamps = []
        
        while current <= end_time:
            timestamps.append(current)
            current += delta
        
        # Generate values based on metric type
        values = []
        base_value = {
            'cpu.usage': 20,
            'memory.percent': 40,
            'disk.usage': 50,
            'network.bytes_recv': 100
        }.get(metric_id, 0)
        
        # Add some variation
        import math
        import random
        
        for i, ts in enumerate(timestamps):
            # Add daily pattern
            hour = ts.hour
            daily_variation = math.sin((hour / 24) * 2 * math.pi) * 20
            
            # Add some random noise
            noise = random.uniform(-5, 5)
            
            # Calculate value
            value = base_value + daily_variation + noise
            
            # Ensure value is within bounds
            if 'usage' in metric_id or 'percent' in metric_id:
                value = max(0, min(100, value))
            else:
                value = max(0, value)
            
            values.append(value)
        
        return timestamps, values

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Performance History")
    root.geometry("800x600")
    
    panel = PerformanceHistoryPanel(root)
    panel.pack(fill='both', expand=True)
    
    root.mainloop()
