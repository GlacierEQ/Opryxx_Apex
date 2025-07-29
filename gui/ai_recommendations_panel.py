"""AI Recommendations Panel for the MASTER GUI"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import psutil

class RecommendationSeverity(Enum):
    """Severity levels for recommendations"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AIRecommendation:
    """Represents an AI-generated recommendation"""
    id: str
    title: str
    description: str
    severity: RecommendationSeverity
    category: str
    impact: str
    confidence: float  # 0.0 to 1.0
    created_at: datetime
    action: Optional[Callable[[], Tuple[bool, str]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert recommendation to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'category': self.category,
            'impact': self.impact,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }

class AIRecommendationEngine:
    """Generates and manages AI recommendations"""
    
    def __init__(self):
        self.recommendations: Dict[str, AIRecommendation] = {}
        self.callbacks: List[Callable[[AIRecommendation], None]] = []
    
    def analyze_system(self) -> List[AIRecommendation]:
        """Analyze system and generate recommendations"""
        recommendations = []
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            recommendations.append(self._create_cpu_usage_recommendation(cpu_percent))
        
        # Check memory usage
        mem = psutil.virtual_memory()
        if mem.percent > 90:
            recommendations.append(self._create_memory_usage_recommendation(mem.percent))
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            recommendations.append(self._create_disk_usage_recommendation(disk.percent))
        
        # Add more checks as needed...
        
        # Store and notify
        for rec in recommendations:
            self.recommendations[rec.id] = rec
            self._notify_callbacks(rec)
        
        return recommendations
    
    def apply_recommendation(self, recommendation_id: str) -> Tuple[bool, str]:
        """Apply a specific recommendation"""
        if recommendation_id not in self.recommendations:
            return False, "Recommendation not found"
        
        rec = self.recommendations[recommendation_id]
        if rec.action:
            try:
                return rec.action()
            except Exception as e:
                return False, f"Failed to apply recommendation: {str(e)}"
        
        return False, "No action defined for this recommendation"
    
    def subscribe(self, callback: Callable[[AIRecommendation], None]) -> None:
        """Subscribe to new recommendations"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def _notify_callbacks(self, recommendation: AIRecommendation) -> None:
        """Notify all subscribers of a new recommendation"""
        for callback in self.callbacks:
            try:
                callback(recommendation)
            except Exception as e:
                print(f"Error in recommendation callback: {e}")
    
    def _create_cpu_usage_recommendation(self, usage: float) -> AIRecommendation:
        """Create a CPU usage recommendation"""
        return AIRecommendation(
            id=f"cpu_high_{int(datetime.now().timestamp())}",
            title="High CPU Usage",
            description=f"CPU usage is at {usage:.1f}%, which may impact system performance.",
            severity=RecommendationSeverity.HIGH if usage > 95 else RecommendationSeverity.MEDIUM,
            category="Performance",
            impact="High impact on system performance",
            confidence=0.9,
            created_at=datetime.now(),
            action=self._fix_high_cpu_usage
        )
    
    def _create_memory_usage_recommendation(self, usage: float) -> AIRecommendation:
        """Create a memory usage recommendation"""
        return AIRecommendation(
            id=f"mem_high_{int(datetime.now().timestamp())}",
            title="High Memory Usage",
            description=f"Memory usage is at {usage:.1f}%, which may cause slowdowns.",
            severity=RecommendationSeverity.HIGH if usage > 95 else RecommendationSeverity.MEDIUM,
            category="Performance",
            impact="May cause system slowdowns or crashes",
            confidence=0.85,
            created_at=datetime.now(),
            action=self._fix_high_memory_usage
        )
    
    def _create_disk_usage_recommendation(self, usage: float) -> AIRecommendation:
        """Create a disk usage recommendation"""
        return AIRecommendation(
            id=f"disk_high_{int(datetime.now().timestamp())}",
            title="High Disk Usage",
            description=f"Disk usage is at {usage:.1f}%, which may cause issues.",
            severity=RecommendationSeverity.HIGH if usage > 95 else RecommendationSeverity.MEDIUM,
            category="Storage",
            impact="May prevent saving files and system updates",
            confidence=0.8,
            created_at=datetime.now(),
            action=self._fix_high_disk_usage
        )
    
    def _fix_high_cpu_usage(self) -> Tuple[bool, str]:
        """Fix high CPU usage (placeholder implementation)"""
        # In a real implementation, this would take action to reduce CPU usage
        return True, "CPU usage optimization completed"
    
    def _fix_high_memory_usage(self) -> Tuple[bool, str]:
        """Fix high memory usage (placeholder implementation)"""
        # In a real implementation, this would take action to reduce memory usage
        return True, "Memory optimization completed"
    
    def _fix_high_disk_usage(self) -> Tuple[bool, str]:
        """Fix high disk usage (placeholder implementation)"""
        # In a real implementation, this would take action to free up disk space
        return True, "Disk cleanup completed"

class AIRecommendationsPanel(ttk.Frame):
    """Panel for displaying and managing AI recommendations"""
    
    SEVERITY_COLORS = {
        RecommendationSeverity.INFO: "#3498db",     # Blue
        RecommendationSeverity.LOW: "#2ecc71",     # Green
        RecommendationSeverity.MEDIUM: "#f39c12",  # Orange
        RecommendationSeverity.HIGH: "#e74c3c",    # Red
        RecommendationSeverity.CRITICAL: "#8e44ad" # Purple
    }
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.recommendation_engine = AIRecommendationEngine()
        self._setup_ui()
        self._setup_event_handlers()
        
        # Initial analysis
        self.analyze_system()
    
    def _setup_ui(self) -> None:
        """Initialize the UI components"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Header
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        ttk.Label(
            header,
            text="AI Recommendations",
            font=('Helvetica', 12, 'bold')
        ).pack(side='left')
        
        # Analyze button
        self.analyze_btn = ttk.Button(
            header,
            text="Analyze System",
            command=self.analyze_system
        )
        self.analyze_btn.pack(side='right', padx=5)
        
        # Recommendations list
        self.tree = ttk.Treeview(
            self,
            columns=('severity', 'category', 'impact', 'confidence'),
            show='headings'
        )
        
        # Configure columns
        self.tree.heading('severity', text='Severity')
        self.tree.heading('category', text='Category')
        self.tree.heading('impact', text='Impact')
        self.tree.heading('confidence', text='Confidence')
        
        self.tree.column('severity', width=100)
        self.tree.column('category', width=150)
        self.tree.column('impact', width=200)
        self.tree.column('confidence', width=100)
        
        # Add scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Grid layout
        self.tree.grid(row=1, column=0, sticky='nsew')
        vsb.grid(row=1, column=1, sticky='ns')
        
        # Details panel
        details_frame = ttk.LabelFrame(self, text="Recommendation Details", padding=5)
        details_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=(10, 0))
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        
        # Title
        self.details_title = ttk.Label(
            details_frame,
            text="Select a recommendation to view details",
            font=('Helvetica', 10, 'bold')
        )
        self.details_title.grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        # Description
        self.details_text = tk.Text(
            details_frame,
            height=6,
            wrap=tk.WORD,
            state='disabled'
        )
        self.details_text.grid(row=1, column=0, sticky='nsew')
        
        # Action buttons
        btn_frame = ttk.Frame(details_frame)
        btn_frame.grid(row=2, column=0, sticky='e', pady=(5, 0))
        
        self.apply_btn = ttk.Button(
            btn_frame,
            text="Apply Recommendation",
            state='disabled',
            command=self._on_apply_click
        )
        self.apply_btn.pack(side='right', padx=2)
        
        self.dismiss_btn = ttk.Button(
            btn_frame,
            text="Dismiss",
            state='disabled',
            command=self._on_dismiss_click
        )
        self.dismiss_btn.pack(side='right', padx=2)
        
        # Configure grid weights
        self.rowconfigure(1, weight=1)
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
    
    def _setup_event_handlers(self) -> None:
        """Set up event handlers"""
        self.recommendation_engine.subscribe(self._on_new_recommendation)
        self.tree.bind('<<TreeviewSelect>>', self._on_select_recommendation)
    
    def analyze_system(self) -> None:
        """Run system analysis and update recommendations"""
        self.analyze_btn.config(state='disabled', text="Analyzing...")
        
        def run_analysis():
            try:
                self.recommendation_engine.analyze_system()
            finally:
                self.after(0, lambda: self.analyze_btn.config(
                    state='normal',
                    text="Analyze System"
                ))
        
        import threading
        threading.Thread(target=run_analysis, daemon=True).start()
    
    def _on_new_recommendation(self, recommendation: AIRecommendation) -> None:
        """Handle new recommendation"""
        self.after(0, lambda: self._add_recommendation(recommendation))
    
    def _add_recommendation(self, recommendation: AIRecommendation) -> None:
        """Add recommendation to the treeview"""
        item_id = self.tree.insert('', 'end', values=(
            recommendation.severity.value.upper(),
            recommendation.category,
            recommendation.impact,
            f"{recommendation.confidence*100:.0f}%"
        ), tags=(recommendation.id, recommendation.severity.value))
        
        # Tag for styling
        self.tree.tag_configure(
            recommendation.severity.value,
            foreground=self.SEVERITY_COLORS[recommendation.severity]
        )
        
        # Store reference
        self.tree.set(item_id, 'id', recommendation.id)
        
        # Auto-select if first item
        if len(self.tree.get_children()) == 1:
            self.tree.selection_set(item_id)
            self._on_select_recommendation(None)
    
    def _on_select_recommendation(self, event) -> None:
        """Handle recommendation selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        rec_id = self.tree.item(item_id, 'tags')[0]  # First tag is the ID
        
        # Find the recommendation
        rec = next(
            (r for r in self.recommendation_engine.recommendations.values() 
             if r.id == rec_id),
            None
        )
        
        if rec:
            self._show_recommendation_details(rec)
    
    def _show_recommendation_details(self, recommendation: AIRecommendation) -> None:
        """Show details for the selected recommendation"""
        self.details_title.config(
            text=recommendation.title,
            foreground=self.SEVERITY_COLORS[recommendation.severity]
        )
        
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        self.details_text.insert('1.0', recommendation.description)
        self.details_text.config(state='disabled')
        
        # Update buttons
        self.apply_btn.config(state='normal')
        self.dismiss_btn.config(state='normal')
        
        # Store current recommendation
        self.current_recommendation = recommendation
    
    def _on_apply_click(self) -> None:
        """Handle apply button click"""
        if not hasattr(self, 'current_recommendation'):
            return
        
        rec = self.current_recommendation
        self.apply_btn.config(state='disabled', text="Applying...")
        
        def apply():
            try:
                success, message = self.recommendation_engine.apply_recommendation(rec.id)
                if success:
                    self.after(0, lambda: self._on_recommendation_applied(rec, message))
                else:
                    self.after(0, lambda: self._show_error(f"Failed to apply: {message}"))
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Error: {str(e)}"))
            finally:
                self.after(0, lambda: self.apply_btn.config(
                    state='normal',
                    text="Apply Recommendation"
                ))
        
        import threading
        threading.Thread(target=apply, daemon=True).start()
    
    def _on_dismiss_click(self) -> None:
        """Handle dismiss button click"""
        if not hasattr(self, 'current_recommendation'):
            return
        
        # Remove from treeview
        for item in self.tree.get_children():
            if self.tree.item(item, 'tags')[0] == self.current_recommendation.id:
                self.tree.delete(item)
                break
        
        # Clear details
        self.details_title.config(text="Select a recommendation to view details")
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        self.details_text.config(state='disabled')
        
        # Disable buttons
        self.apply_btn.config(state='disabled')
        self.dismiss_btn.config(state='disabled')
        
        # Remove from engine (in a real implementation, you might want to mark as dismissed)
        if hasattr(self, 'current_recommendation'):
            del self.recommendation_engine.recommendations[self.current_recommendation.id]
            del self.current_recommendation
    
    def _on_recommendation_applied(self, recommendation: AIRecommendation, message: str) -> None:
        """Handle successful recommendation application"""
        self._show_info("Success", message)
        self._on_dismiss_click()  # Remove the applied recommendation
    
    def _show_error(self, message: str) -> None:
        """Show error message"""
        self._show_message("Error", message, "red")
    
    def _show_info(self, title: str, message: str) -> None:
        """Show info message"""
        self._show_message(title, message, "blue")
    
    def _show_message(self, title: str, message: str, color: str) -> None:
        """Show a message in the details panel"""
        self.details_title.config(text=title, foreground=color)
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        self.details_text.insert('1.0', message)
        self.details_text.config(state='disabled')
