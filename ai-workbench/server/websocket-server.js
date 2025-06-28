const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const AIBrain = require('../core/ai-brain');
const SystemMonitor = require('../monitors/system-monitor');

class DashboardServer {
    constructor(port = 3000) {
        this.port = port;
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = socketIo(this.server);

        this.aiBrain = new AIBrain();
        this.systemMonitor = new SystemMonitor();

        this.setupRoutes();
        this.setupSocketHandlers();
        this.startMetricsCollection();
    }

    setupRoutes() {
        // Serve dashboard
        this.app.use(express.static(path.join(__dirname, '../dashboard')));

        // API endpoints
        this.app.get('/api/health', (req, res) => {
            res.json({ status: 'healthy', timestamp: Date.now() });
        });

        this.app.get('/api/metrics', async (req, res) => {
            const metrics = await this.systemMonitor.getAllMetrics();
            res.json(metrics);
        });
    }

    setupSocketHandlers() {
        this.io.on('connection', (socket) => {
            console.log('🔌 Dashboard connected:', socket.id);

            socket.on('ai-query', async (data) => {
                const startTime = Date.now();

                try {
                    const response = await this.aiBrain.think(data.message, {
                        socketId: socket.id,
                        timestamp: data.timestamp
                    });

                    socket.emit('ai-response', {
                        response: response.response.solution?.summary || 'I understand your query and am processing it.',
                        confidence: response.confidence,
                        responseTime: Date.now() - startTime,
                        engine: response.engine
                    });

                    // Send suggestions if available
                    if (response.response.recommendations) {
                        socket.emit('ai-suggestion', {
                            title: 'AI Recommendation',
                            description: response.response.recommendations[0] || 'System is running optimally.'
                        });
                    }

                } catch (error) {
                    socket.emit('ai-response', {
                        response: 'I encountered an error processing your request. Let me try a different approach.',
                        confidence: 0.3,
                        responseTime: Date.now() - startTime,
                        error: true
                    });
                }
            });

            socket.on('request-metrics', async () => {
                const metrics = await this.getSystemMetrics();
                socket.emit('system-metrics', metrics);
            });

            socket.on('disconnect', () => {
                console.log('🔌 Dashboard disconnected:', socket.id);
            });
        });
    }

    async getSystemMetrics() {
        const os = require('os');
        const metrics = {
            cpu: Math.round(await this.getCPUUsage()),
            memory: Math.round((1 - os.freemem() / os.totalmem()) * 100),
            disk: await this.getDiskUsage(),
            timestamp: Date.now()
        };

        return metrics;
    }

    async getCPUUsage() {
        return new Promise((resolve) => {
            const startUsage = process.cpuUsage();
            setTimeout(() => {
                const endUsage = process.cpuUsage(startUsage);
                const usage = (endUsage.user + endUsage.system) / 1000000;
                resolve(Math.min(100, usage * 10)); // Approximate percentage
            }, 100);
        });
    }

    async getDiskUsage() {
        try {
            const { execSync } = require('child_process');
            const output = execSync('wmic logicaldisk get size,freespace,caption', { encoding: 'utf8' });
            const lines = output.trim().split('\n').slice(1);
            
            const diskInfo = lines.map(line => {
                const [drive, freeSpace, totalSize] = line.trim().split(/\s+/);
                if (!drive || !freeSpace || !totalSize) return null;
                
                const free = parseInt(freeSpace);
                const total = parseInt(totalSize);
                const used = total - free;
                const percentUsed = ((used / total) * 100).toFixed(2);
                
                return {
                    drive,
                    free: formatBytes(free),
                    used: formatBytes(used),
                    total: formatBytes(total),
                    percentUsed: parseFloat(percentUsed)
                };
            }).filter(Boolean);
            
            return diskInfo;
        } catch (error) {
            console.error('Error getting disk usage:', error);
            return [];
        }
    }
    
    formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
