"""
Web Interface for OPRYXX System
Flask-based web dashboard with real-time updates
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import json
from datetime import datetime

from core.performance_monitor import performance_monitor, start_performance_monitoring, stop_performance_monitoring
from core.memory_optimizer import memory_optimizer, OptimizationLevel
from core.enhanced_gpu_ops import enhanced_gpu_ops
from core.resilience_system import resilience_manager
from core.gpu_acceleration import is_gpu_available, get_compute_device

app = Flask(__name__)
app.config['SECRET_KEY'] = 'opryxx_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

class WebInterface:
    def __init__(self):
        self.monitoring_active = False
        self.setup_routes()
        self.start_background_tasks()
    
    def setup_routes(self):
        @app.route('/')
        def dashboard():
            return render_template('dashboard.html')
        
        @app.route('/api/status')
        def get_status():
            return jsonify({
                'performance_monitor': self.monitoring_active,
                'memory_optimizer': memory_optimizer.running,
                'gpu_available': is_gpu_available(),
                'active_device': get_compute_device().name,
                'timestamp': datetime.now().isoformat()
            })
        
        @app.route('/api/metrics')
        def get_metrics():
            metrics = performance_monitor.get_metrics()
            mem_metrics = memory_optimizer.get_memory_metrics()
            
            return jsonify({
                'performance': {
                    'cpu_usage': metrics.cpu_usage,
                    'memory_usage': metrics.memory_usage,
                    'gpu_usage': metrics.gpu_usage,
                    'score': metrics.score
                },
                'memory': {
                    'total_mb': mem_metrics.total_mb,
                    'available_mb': mem_metrics.available_mb,
                    'used_mb': mem_metrics.used_mb,
                    'usage_percent': mem_metrics.usage_percent
                },
                'timestamp': datetime.now().isoformat()
            })
        
        @app.route('/api/start_monitoring', methods=['POST'])
        def start_monitoring():
            start_performance_monitoring()
            self.monitoring_active = True
            return jsonify({'status': 'started'})
        
        @app.route('/api/stop_monitoring', methods=['POST'])
        def stop_monitoring():
            stop_performance_monitoring()
            self.monitoring_active = False
            return jsonify({'status': 'stopped'})
        
        @app.route('/api/optimize_memory', methods=['POST'])
        def optimize_memory():
            result = memory_optimizer.optimize_memory()
            return jsonify(result)
        
        @app.route('/api/gpu_benchmark', methods=['POST'])
        def gpu_benchmark():
            size = request.json.get('size', 1000)
            benchmarks = enhanced_gpu_ops.benchmark_operations(size)
            return jsonify(benchmarks)
        
        @app.route('/api/resilience_report')
        def resilience_report():
            report = resilience_manager.get_system_resilience_report()
            return jsonify(report)
        
        @socketio.on('connect')
        def handle_connect():
            emit('status', {'message': 'Connected to OPRYXX System'})
        
        @socketio.on('request_update')
        def handle_update_request():
            self.send_real_time_update()
    
    def start_background_tasks(self):
        def background_thread():
            while True:
                if self.monitoring_active:
                    self.send_real_time_update()
                time.sleep(2)
        
        thread = threading.Thread(target=background_thread, daemon=True)
        thread.start()
    
    def send_real_time_update(self):
        try:
            metrics = performance_monitor.get_metrics()
            mem_metrics = memory_optimizer.get_memory_metrics()
            
            data = {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'performance_score': metrics.score,
                'memory_available': mem_metrics.available_mb,
                'timestamp': datetime.now().isoformat()
            }
            
            socketio.emit('metrics_update', data)
        except Exception as e:
            print(f"Error sending update: {e}")
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        socketio.run(app, host=host, port=port, debug=debug)

# Create templates directory and files
import os
os.makedirs('templates', exist_ok=True)

dashboard_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>OPRYXX Control Center</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: #2d2d2d; padding: 20px; border-radius: 10px; border: 1px solid #444; }
        .metric-value { font-size: 2em; font-weight: bold; color: #00ff88; }
        .controls { margin: 20px 0; text-align: center; }
        button { background: #007acc; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a99; }
        .chart-container { width: 100%; height: 300px; margin: 20px 0; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-online { background: #00ff88; }
        .status-offline { background: #ff4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OPRYXX Unified Control Center</h1>
            <p>Real-time System Monitoring and Control</p>
        </div>
        
        <div class="controls">
            <button onclick="startMonitoring()">Start Monitoring</button>
            <button onclick="stopMonitoring()">Stop Monitoring</button>
            <button onclick="optimizeMemory()">Optimize Memory</button>
            <button onclick="runBenchmark()">GPU Benchmark</button>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3><span id="perf-status" class="status-indicator status-offline"></span>Performance Monitor</h3>
                <div class="metric-value" id="cpu-usage">0%</div>
                <p>CPU Usage</p>
            </div>
            
            <div class="metric-card">
                <h3>Memory Usage</h3>
                <div class="metric-value" id="memory-usage">0%</div>
                <p>System Memory</p>
            </div>
            
            <div class="metric-card">
                <h3>Performance Score</h3>
                <div class="metric-value" id="perf-score">0</div>
                <p>Overall Performance</p>
            </div>
            
            <div class="metric-card">
                <h3>Available Memory</h3>
                <div class="metric-value" id="memory-available">0 MB</div>
                <p>Free Memory</p>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="metricsChart"></canvas>
        </div>
        
        <div id="status-log" style="background: #2d2d2d; padding: 15px; border-radius: 5px; height: 200px; overflow-y: scroll; font-family: monospace;"></div>
    </div>

    <script>
        const socket = io();
        const ctx = document.getElementById('metricsChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage',
                    data: [],
                    borderColor: '#ff6b6b',
                    tension: 0.1
                }, {
                    label: 'Memory Usage',
                    data: [],
                    borderColor: '#4ecdc4',
                    tension: 0.1
                }, {
                    label: 'Performance Score',
                    data: [],
                    borderColor: '#45b7d1',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 100 }
                }
            }
        });

        socket.on('connect', function() {
            logMessage('Connected to OPRYXX System');
        });

        socket.on('metrics_update', function(data) {
            document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = data.memory_usage.toFixed(1) + '%';
            document.getElementById('perf-score').textContent = data.performance_score.toFixed(1);
            document.getElementById('memory-available').textContent = data.memory_available.toFixed(0) + ' MB';
            
            // Update chart
            const time = new Date(data.timestamp).toLocaleTimeString();
            chart.data.labels.push(time);
            chart.data.datasets[0].data.push(data.cpu_usage);
            chart.data.datasets[1].data.push(data.memory_usage);
            chart.data.datasets[2].data.push(data.performance_score);
            
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            chart.update('none');
        });

        function startMonitoring() {
            fetch('/api/start_monitoring', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    logMessage('Monitoring started');
                    document.getElementById('perf-status').className = 'status-indicator status-online';
                });
        }

        function stopMonitoring() {
            fetch('/api/stop_monitoring', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    logMessage('Monitoring stopped');
                    document.getElementById('perf-status').className = 'status-indicator status-offline';
                });
        }

        function optimizeMemory() {
            fetch('/api/optimize_memory', {method: 'POST'})
                .then(response => response.json())
                .then(data => logMessage(`Memory optimized: ${data.freed_mb.toFixed(2)} MB freed`));
        }

        function runBenchmark() {
            logMessage('Running GPU benchmark...');
            fetch('/api/gpu_benchmark', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({size: 1000})})
                .then(response => response.json())
                .then(data => {
                    logMessage(`Benchmark completed on ${data.device}`);
                    Object.entries(data).forEach(([key, value]) => {
                        if (key !== 'device') logMessage(`${key}: ${value.toFixed(2)}ms`);
                    });
                });
        }

        function logMessage(message) {
            const log = document.getElementById('status-log');
            const time = new Date().toLocaleTimeString();
            log.innerHTML += `[${time}] ${message}<br>`;
            log.scrollTop = log.scrollHeight;
        }

        // Request initial update
        socket.emit('request_update');
    </script>
</body>
</html>
'''

with open('templates/dashboard.html', 'w') as f:
    f.write(dashboard_html)

web_interface = WebInterface()

if __name__ == "__main__":
    web_interface.run(debug=True)