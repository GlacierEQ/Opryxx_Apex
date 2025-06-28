"""
Web Dashboard for Remote Monitoring
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import psutil

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head><title>NEXUS AI Dashboard</title>
            <style>
                body { background: #000; color: #0f0; font-family: monospace; }
                .metric { margin: 10px; padding: 10px; border: 1px solid #0f0; }
            </style>
            </head>
            <body>
                <h1>🤖 NEXUS AI Dashboard</h1>
                <div class="metric">CPU: <span id="cpu">Loading...</span>%</div>
                <div class="metric">Memory: <span id="memory">Loading...</span>%</div>
                <div class="metric">Status: <span id="status">Active</span></div>
                <script>
                    setInterval(() => {
                        fetch('/api/metrics').then(r => r.json()).then(data => {
                            document.getElementById('cpu').textContent = data.cpu;
                            document.getElementById('memory').textContent = data.memory;
                        });
                    }, 2000);
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
            
        elif self.path == '/api/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            metrics = {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'status': 'Active'
            }
            self.wfile.write(json.dumps(metrics).encode())

class WebDashboard:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
    
    def start(self):
        """Start web dashboard"""
        self.server = HTTPServer(('localhost', self.port), DashboardHandler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        print(f"Dashboard running at http://localhost:{self.port}")
    
    def stop(self):
        if self.server:
            self.server.shutdown()