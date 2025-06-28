"""
Performance Dashboard - Visualization for NEXUS AI Benchmarks
"""

import json
import time
from datetime import datetime
from performance_benchmark import PerformanceBenchmark
import tkinter as tk
from tkinter import ttk

class PerformanceDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NEXUS AI Performance Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        
        self.benchmark = PerformanceBenchmark()
        self.results_history = []
        
        self.setup_dashboard()
        
    def setup_dashboard(self):
        # Title
        title = tk.Label(self.root, text="📊 NEXUS AI PERFORMANCE DASHBOARD", 
                        font=('Arial', 20, 'bold'), fg='#00ff80', bg='#1a1a1a')
        title.pack(pady=20)
        
        # Control panel
        control_frame = tk.Frame(self.root, bg='#2a2a2a', relief='raised', bd=2)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(control_frame, text="🚀 Run Benchmark", command=self.run_benchmark,
                 bg='#0066cc', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=10, pady=10)
        
        tk.Button(control_frame, text="📈 View History", command=self.show_history,
                 bg='#cc6600', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=10, pady=10)
        
        tk.Button(control_frame, text="💾 Export Results", command=self.export_results,
                 bg='#00cc66', fg='white', font=('Arial', 12, 'bold')).pack(side='left', padx=10, pady=10)
        
        # Results display
        results_frame = tk.Frame(self.root, bg='#2a2a2a', relief='raised', bd=2)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(results_frame, text="📊 BENCHMARK RESULTS", 
                font=('Arial', 16, 'bold'), fg='#00ff80', bg='#2a2a2a').pack(pady=10)
        
        self.results_text = tk.Text(results_frame, bg='#0a0a0a', fg='#00ff80', 
                                   font=('Consolas', 10), wrap='word')
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def run_benchmark(self):
        """Run performance benchmark and display results"""
        self.results_text.delete(1.0, tk.END)
        self.log("🚀 Starting NEXUS AI Performance Benchmark...")
        
        # Run benchmark
        results = self.benchmark.run_full_benchmark()
        
        # Store results
        results['timestamp'] = datetime.now().isoformat()
        self.results_history.append(results)
        
        # Display results
        self.display_results(results)
        
    def display_results(self, results):
        """Display benchmark results"""
        self.log("=" * 60)
        self.log("📊 PERFORMANCE BENCHMARK RESULTS")
        self.log("=" * 60)
        
        # Memory operations
        memory_ops = results['memory_operations']
        self.log("\n💾 MEMORY OPERATIONS:")
        for op_name, op_result in memory_ops.items():
            self.log(f"  {op_name}: {op_result['time_ms']:.2f}ms, {op_result['memory_mb']:.2f}MB")
        
        # GPU performance
        gpu_perf = results['gpu_performance']
        self.log("\n🎮 GPU PERFORMANCE:")
        if gpu_perf['gpu_available']:
            self.log(f"  Bandwidth: {gpu_perf['memory_bandwidth']:.1f} MB/s")
            self.log(f"  Score: {gpu_perf['acceleration_score']:.1f}/100")
        else:
            self.log("  GPU: Not Available")
        
        # System optimization
        sys_opt = results['system_optimization']
        self.log(f"\n🔧 SYSTEM OPTIMIZATION:")
        self.log(f"  Time: {sys_opt['optimization_time_ms']:.2f}ms")
        self.log(f"  Count: {sys_opt['optimizations_count']}")
        
        # Leak detection
        leak_det = results['leak_detection']
        self.log(f"\n🔍 LEAK DETECTION:")
        self.log(f"  Time: {leak_det['detection_time_ms']:.2f}ms")
        self.log(f"  Status: {'LEAK' if leak_det['leak_detected'] else 'CLEAN'}")
        
        # Overall score
        overall_score = self._calculate_score(results)
        self.log(f"\n🏆 OVERALL SCORE: {overall_score}/100")
        
        if overall_score >= 80:
            self.log("✅ STATUS: EXCELLENT PERFORMANCE")
        elif overall_score >= 60:
            self.log("⚡ STATUS: GOOD PERFORMANCE")
        else:
            self.log("⚠️ STATUS: NEEDS OPTIMIZATION")
    
    def show_history(self):
        """Show benchmark history"""
        self.results_text.delete(1.0, tk.END)
        
        if not self.results_history:
            self.log("No benchmark history available")
            return
        
        self.log("📈 BENCHMARK HISTORY")
        self.log("=" * 50)
        
        for i, result in enumerate(self.results_history[-10:], 1):  # Last 10 results
            timestamp = result.get('timestamp', 'Unknown')
            score = self._calculate_score(result)
            
            self.log(f"\n{i}. {timestamp}")
            self.log(f"   Score: {score}/100")
            
            # Memory average
            memory_ops = result['memory_operations']
            avg_time = sum(op['time_ms'] for op in memory_ops.values()) / len(memory_ops)
            self.log(f"   Memory Avg: {avg_time:.2f}ms")
            
            # GPU status
            gpu_available = result['gpu_performance']['gpu_available']
            self.log(f"   GPU: {'Available' if gpu_available else 'N/A'}")
    
    def export_results(self):
        """Export results to JSON file"""
        if not self.results_history:
            self.log("No results to export")
            return
        
        filename = f"nexus_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results_history, f, indent=2)
            
            self.log(f"✅ Results exported to: {filename}")
        except Exception as e:
            self.log(f"❌ Export failed: {e}")
    
    def _calculate_score(self, results):
        """Calculate overall performance score"""
        score = 0
        
        # Memory operations (40 points)
        memory_ops = results['memory_operations']
        avg_time = sum(op['time_ms'] for op in memory_ops.values()) / len(memory_ops)
        if avg_time < 10:
            score += 40
        elif avg_time < 50:
            score += 25
        else:
            score += 10
        
        # GPU performance (30 points)
        gpu_perf = results['gpu_performance']
        if gpu_perf['gpu_available']:
            gpu_score = min(30, gpu_perf['acceleration_score'] / 100 * 30)
            score += gpu_score
        
        # System optimization (20 points)
        sys_opt = results['system_optimization']
        if sys_opt['optimization_time_ms'] < 100:
            score += 20
        elif sys_opt['optimization_time_ms'] < 500:
            score += 10
        
        # Leak detection (10 points)
        leak_det = results['leak_detection']
        if leak_det['detection_time_ms'] < 1000:
            score += 10
        elif leak_det['detection_time_ms'] < 3000:
            score += 5
        
        return int(score)
    
    def log(self, message):
        """Add message to results display"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update()
    
    def run(self):
        """Start the dashboard"""
        self.root.mainloop()

def main():
    """Launch performance dashboard"""
    dashboard = PerformanceDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()