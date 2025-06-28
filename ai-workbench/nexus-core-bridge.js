/**
 * NEXUS CORE BRIDGE
 * ==================
 * JavaScript bridge to Python core infrastructure
 * Enables real-time communication between Python backend and JS frontend
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const WebSocket = require('ws');
const chalk = require('chalk');

class NexusCorebridge {
    constructor() {
        this.name = 'NEXUS-CORE-BRIDGE';
        this.version = '3.0.0';
        this.pythonCore = null;
        this.wsServer = null;
        this.clients = new Set();
        this.status = {
            python_core: false,
            websocket_server: false,
            api_bridge: false,
            total_connections: 0
        };
        
        this.initializeBridge();
    }
    
    async initializeBridge() {
        console.log(chalk.cyan('🚀 NEXUS CORE BRIDGE INITIALIZING...'));
        console.log(chalk.gray('=' .repeat(50)));
        
        try {
            // 1. Start Python core
            await this.startPythonCore();
            
            // 2. Setup WebSocket server
            await this.setupWebSocketServer();
            
            // 3. Setup API bridge
            await this.setupAPIBridge();
            
            // 4. Start monitoring
            this.startMonitoring();
            
            console.log(chalk.green('✅ NEXUS CORE BRIDGE READY!'));
            this.showStatus();
            
        } catch (error) {
            console.error(chalk.red('❌ Bridge initialization failed:'), error);
        }
    }
    
    async startPythonCore() {
        console.log(chalk.blue('🐍 Starting Python Core...'));
        
        return new Promise((resolve, reject) => {
            // Start Python core process
            this.pythonCore = spawn('python', ['../LAYER_1_CORE_FIXED.py'], {
                cwd: __dirname,
                stdio: ['pipe', 'pipe', 'pipe']
            });
            
            this.pythonCore.stdout.on('data', (data) => {
                const output = data.toString().trim();
                if (output.includes('[OK]')) {
                    console.log(chalk.green(`   ${output}`));
                }
                
                if (output.includes('PYTHON CORE READY')) {
                    this.status.python_core = true;
                    resolve();
                }
            });
            
            this.pythonCore.stderr.on('data', (data) => {
                console.error(chalk.red('Python Error:'), data.toString());
            });
            
            this.pythonCore.on('close', (code) => {
                if (code !== 0) {
                    console.error(chalk.red(`Python core exited with code ${code}`));
                    this.status.python_core = false;
                }
            });
            
            // Timeout after 10 seconds
            setTimeout(() => {
                if (!this.status.python_core) {
                    reject(new Error('Python core startup timeout'));
                }
            }, 10000);
        });
    }
    
    async setupWebSocketServer() {
        console.log(chalk.blue('🌐 Setting up WebSocket server...'));
        
        return new Promise((resolve) => {
            this.wsServer = new WebSocket.Server({ 
                port: 3001,
                clientTracking: true
            });
            
            this.wsServer.on('connection', (ws, req) => {
                console.log(chalk.green(`📱 New client connected: ${req.socket.remoteAddress}`));
                
                this.clients.add(ws);
                this.status.total_connections = this.clients.size;
                
                // Send welcome message
                ws.send(JSON.stringify({
                    type: 'welcome',
                    message: 'Connected to NEXUS Core Bridge',
                    timestamp: new Date().toISOString()
                }));
                
                // Handle messages
                ws.on('message', (message) => {
                    try {
                        const data = JSON.parse(message);
                        this.handleClientMessage(ws, data);
                    } catch (error) {
                        console.error(chalk.red('Invalid message from client:'), error);
                    }
                });
                
                // Handle disconnection
                ws.on('close', () => {
                    this.clients.delete(ws);
                    this.status.total_connections = this.clients.size;
                    console.log(chalk.yellow('📱 Client disconnected'));
                });
                
                ws.on('error', (error) => {
                    console.error(chalk.red('WebSocket error:'), error);
                    this.clients.delete(ws);
                    this.status.total_connections = this.clients.size;
                });
            });
            
            this.wsServer.on('listening', () => {
                console.log(chalk.green('   ✅ WebSocket server listening on port 3001'));
                this.status.websocket_server = true;
                resolve();
            });
        });
    }
    
    async setupAPIBridge() {
        console.log(chalk.blue('🔗 Setting up API bridge...'));
        
        // Create API endpoints configuration
        const apiConfig = {
            endpoints: {
                status: '/api/system/status',
                metrics: '/api/metrics',
                events: '/api/events',
                actions: '/api/actions'
            },
            python_bridge: {
                enabled: true,
                communication_method: 'websocket',
                fallback_method: 'file_system'
            },
            real_time: {
                enabled: true,
                update_interval: 1000,
                batch_size: 100
            }
        };
        
        // Save API configuration
        const apiDir = path.join(__dirname, '..', 'api');
        if (!fs.existsSync(apiDir)) {
            fs.mkdirSync(apiDir, { recursive: true });
        }
        
        fs.writeFileSync(
            path.join(apiDir, 'bridge-config.json'),
            JSON.stringify(apiConfig, null, 2)
        );
        
        console.log(chalk.green('   ✅ API bridge configuration saved'));
        this.status.api_bridge = true;
    }
    
    handleClientMessage(ws, data) {
        console.log(chalk.blue(`📨 Message from client: ${data.type}`));
        
        switch (data.type) {
            case 'get_status':
                this.sendStatus(ws);
                break;
                
            case 'get_metrics':
                this.sendMetrics(ws);
                break;
                
            case 'execute_action':
                this.executeAction(ws, data.action);
                break;
                
            default:
                ws.send(JSON.stringify({
                    type: 'error',
                    message: `Unknown message type: ${data.type}`
                }));
        }
    }
    
    sendStatus(ws) {
        const systemStatus = {
            type: 'status',
            data: {
                bridge: this.status,
                system: {
                    uptime: process.uptime(),
                    memory: process.memoryUsage(),
                    platform: process.platform,
                    node_version: process.version
                },
                timestamp: new Date().toISOString()
            }
        };
        
        ws.send(JSON.stringify(systemStatus));
    }
    
    sendMetrics(ws) {
        // Simulate system metrics (in real implementation, get from Python core)
        const metrics = {
            type: 'metrics',
            data: {
                cpu_usage: Math.random() * 100,
                memory_usage: Math.random() * 100,
                health_score: Math.floor(Math.random() * 30) + 70,
                intelligence_level: 85,
                active_optimizations: Math.floor(Math.random() * 10),
                timestamp: new Date().toISOString()
            }
        };
        
        ws.send(JSON.stringify(metrics));
    }
    
    executeAction(ws, action) {
        console.log(chalk.yellow(`🔧 Executing action: ${action}`));
        
        // Simulate action execution
        setTimeout(() => {
            ws.send(JSON.stringify({
                type: 'action_result',
                action: action,
                success: true,
                message: `Action ${action} completed successfully`,
                timestamp: new Date().toISOString()
            }));
        }, 1000);
    }
    
    startMonitoring() {
        console.log(chalk.blue('📊 Starting system monitoring...'));
        
        // Monitor and broadcast system status every 5 seconds
        setInterval(() => {
            if (this.clients.size > 0) {
                this.broadcastToClients({
                    type: 'system_update',
                    data: {
                        timestamp: new Date().toISOString(),
                        active_clients: this.clients.size,
                        python_core_status: this.status.python_core,
                        uptime: process.uptime()
                    }
                });
            }
        }, 5000);
    }
    
    broadcastToClients(message) {
        const messageStr = JSON.stringify(message);
        
        this.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(messageStr);
            }
        });
    }
    
    showStatus() {
        console.log();
        console.log(chalk.cyan('📊 NEXUS CORE BRIDGE STATUS'));
        console.log(chalk.gray('=' .repeat(40)));
        
        const statusItems = [
            ['Python Core', this.status.python_core ? '🟢 ONLINE' : '🔴 OFFLINE'],
            ['WebSocket Server', this.status.websocket_server ? '🟢 ONLINE' : '🔴 OFFLINE'],
            ['API Bridge', this.status.api_bridge ? '🟢 READY' : '🔴 NOT READY'],
            ['Active Connections', this.status.total_connections.toString()],
            ['Bridge Version', this.version],
            ['WebSocket Port', '3001']
        ];
        
        statusItems.forEach(([label, value]) => {
            const emoji = value.includes('🟢') || value === this.version || !isNaN(value) ? '✅' : '❌';
            console.log(`${emoji} ${label.padEnd(20)}: ${value}`);
        });
        
        console.log();
        console.log(chalk.green('🚀 Ready for OPRYXX integration!'));
        console.log(chalk.gray('Connect via WebSocket: ws://localhost:3001'));
    }
    
    shutdown() {
        console.log(chalk.yellow('🛑 Shutting down NEXUS Core Bridge...'));
        
        // Close WebSocket server
        if (this.wsServer) {
            this.wsServer.close();
        }
        
        // Kill Python process
        if (this.pythonCore) {
            this.pythonCore.kill();
        }
        
        console.log(chalk.green('✅ Shutdown complete'));
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log(chalk.yellow('\n🛑 Received SIGINT, shutting down...'));
    if (global.nexusBridge) {
        global.nexusBridge.shutdown();
    }
    process.exit(0);
});

// Start the bridge
if (require.main === module) {
    global.nexusBridge = new NexusCorebridge();
}

module.exports = NexusCorebridge;
