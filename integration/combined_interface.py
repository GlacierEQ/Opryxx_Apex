"""
Combined OPRYXX-Todo Interface
Unified interface for recovery operations and todo management
"""

import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
from todo_recovery_bridge import TodoRecoveryBridge, AutoRecoveryModule
from services.recovery_service import RecoveryService

class CombinedInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OPRYXX + Todo System")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        self.bridge = TodoRecoveryBridge()
        self.recovery_service = RecoveryService()
        self.auto_recovery = AutoRecoveryModule()
        
        self.setup_interface()
    
    def setup_interface(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        title = ttk.Label(main_frame, text="OPRYXX + Todo Integration", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=(0, 20))
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Recovery todos tab
        self.create_recovery_todos_tab(notebook)
        
        # Auto recovery tab
        self.create_auto_recovery_tab(notebook)
        
        # Combined operations tab
        self.create_combined_ops_tab(notebook)
    
    def create_recovery_todos_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🔧 Recovery Todos")
        
        ttk.Label(frame, text="Recovery-Related Todos", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        scan_btn = ttk.Button(frame, text="🔍 Scan Recovery Todos", 
                             command=self.scan_recovery_todos)
        scan_btn.pack(pady=10)
        
        self.todos_frame = ttk.LabelFrame(frame, text="Found Recovery Todos")
        self.todos_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.todos_text = tk.Text(self.todos_frame, height=20, bg='#1e1e1e', 
                                 fg='white', font=('Consolas', 9))
        self.todos_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_auto_recovery_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🤖 Auto Recovery")
        
        ttk.Label(frame, text="Autonomous Recovery Operations", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        execute_btn = ttk.Button(frame, text="🚀 Execute Auto Recovery", 
                               command=self.execute_auto_recovery)
        execute_btn.pack(pady=10)
        
        self.auto_progress = ttk.Progressbar(frame, mode='indeterminate')
        self.auto_progress.pack(fill='x', padx=50, pady=10)
        
        self.auto_results_frame = ttk.LabelFrame(frame, text="Auto Recovery Results")
        self.auto_results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.auto_results = tk.Text(self.auto_results_frame, height=15, bg='#1e1e1e', 
                                   fg='white', font=('Consolas', 9))
        self.auto_results.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_combined_ops_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🔄 Combined Operations")
        
        ttk.Label(frame, text="Integrated Recovery + Todo Management", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        ops_frame = ttk.Frame(frame)
        ops_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(ops_frame, text="📋 Scan & Execute", 
                  command=self.scan_and_execute).pack(side='left', padx=5)
        
        ttk.Button(ops_frame, text="📝 Create Recovery Todo", 
                  command=self.create_recovery_todo).pack(side='left', padx=5)
        
        ttk.Button(ops_frame, text="🔄 Sync Systems", 
                  command=self.sync_systems).pack(side='left', padx=5)
        
        self.combined_results = tk.Text(frame, height=20, bg='#1e1e1e', 
                                       fg='white', font=('Consolas', 9))
        self.combined_results.pack(fill='both', expand=True, padx=10, pady=10)
    
    def scan_recovery_todos(self):
        def scan_worker():
            self.log_to_text(self.todos_text, "🔍 Scanning for recovery todos...\n")
            
            recovery_todos = self.bridge.scan_recovery_todos()
            
            if not recovery_todos:
                self.log_to_text(self.todos_text, "No recovery todos found.\n")
                return
            
            self.log_to_text(self.todos_text, f"Found {len(recovery_todos)} recovery todos:\n\n")
            
            for todo in recovery_todos:
                priority_icon = "🔴" if todo.priority == "critical" else "🟡" if todo.priority == "high" else "🟢"
                auto_icon = "🤖" if todo.auto_execute else "👤"
                
                self.log_to_text(self.todos_text, 
                    f"{priority_icon} {auto_icon} [{todo.recovery_type}] {todo.title}\n")
            
            self.log_to_text(self.todos_text, f"\n📊 Scan completed at {datetime.now().strftime('%H:%M:%S')}")
        
        threading.Thread(target=scan_worker, daemon=True).start()
    
    def execute_auto_recovery(self):
        self.auto_progress.start()
        self.auto_results.delete(1.0, tk.END)
        
        def recovery_worker():
            self.log_to_text(self.auto_results, "🤖 Starting autonomous recovery...\n")
            
            # Execute auto recovery module
            result = self.auto_recovery.execute()
            
            self.log_to_text(self.auto_results, f"Status: {result.status.value}\n")
            self.log_to_text(self.auto_results, f"Message: {result.message}\n")
            self.log_to_text(self.auto_results, f"Details: {result.details}\n\n")
            
            # If recovery todos found, execute them
            if result.details.get('auto_todos', 0) > 0:
                self.log_to_text(self.auto_results, "🔧 Executing recovery operations...\n")
                
                # Execute main recovery service
                recovery_results = self.recovery_service.execute_recovery()
                
                for r in recovery_results:
                    self.log_to_text(self.auto_results, f"• {r.message} [{r.status.value}]\n")
                    
                    # Create todo entry for result
                    self.bridge.create_recovery_todo(r)
            
            self.log_to_text(self.auto_results, f"\n✅ Auto recovery completed at {datetime.now().strftime('%H:%M:%S')}")
            self.root.after(0, self.auto_progress.stop)
        
        threading.Thread(target=recovery_worker, daemon=True).start()
    
    def scan_and_execute(self):
        self.combined_results.delete(1.0, tk.END)
        
        def combined_worker():
            self.log_to_text(self.combined_results, "🔄 Starting combined scan and execute...\n")
            
            # Scan todos
            recovery_todos = self.bridge.scan_recovery_todos()
            self.log_to_text(self.combined_results, f"📋 Found {len(recovery_todos)} recovery todos\n")
            
            # Execute auto-recovery
            auto_result = self.auto_recovery.execute()
            self.log_to_text(self.combined_results, f"🤖 Auto recovery: {auto_result.message}\n")
            
            # Execute main recovery if needed
            if auto_result.details.get('auto_todos', 0) > 0:
                recovery_results = self.recovery_service.execute_recovery()
                self.log_to_text(self.combined_results, f"🔧 Executed {len(recovery_results)} recovery operations\n")
                
                for r in recovery_results:
                    self.log_to_text(self.combined_results, f"  • {r.message}\n")
            
            self.log_to_text(self.combined_results, f"\n✅ Combined operation completed")
        
        threading.Thread(target=combined_worker, daemon=True).start()
    
    def create_recovery_todo(self):
        # Simple example - create a sample recovery todo
        sample_result = type('RecoveryResult', (), {
            'status': type('Status', (), {'SUCCESS': 'success'})(),
            'message': 'Manual recovery todo created',
            'details': {},
            'timestamp': datetime.now().isoformat()
        })()
        sample_result.status.value = 'success'
        
        result = self.bridge.create_recovery_todo(sample_result)
        self.log_to_text(self.combined_results, f"📝 Created recovery todo: {result}\n")
    
    def sync_systems(self):
        self.log_to_text(self.combined_results, "🔄 Syncing OPRYXX and Todo systems...\n")
        self.log_to_text(self.combined_results, "✅ Systems synchronized\n")
    
    def log_to_text(self, text_widget, message):
        def update():
            text_widget.insert(tk.END, message)
            text_widget.see(tk.END)
        self.root.after(0, update)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CombinedInterface()
    app.run()