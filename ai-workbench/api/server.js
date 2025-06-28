require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { createServer } = require('http');
const { Server } = require('socket.io');
const { errorHandler } = require('../core/error-handler');
const AIBrain = require('../core/ai-brain');

class APIServer {
    constructor() {
        this.app = express();
        this.httpServer = createServer(this.app);
        this.io = new Server(this.httpServer, {
            cors: {
                origin: process.env.FRONTEND_URL || '*',
                methods: ['GET', 'POST']
            }
        });
        
        this.aiBrain = new AIBrain();
        this.port = process.env.PORT || 3000;
        
        this.initializeMiddlewares();
        this.initializeRoutes();
        this.initializeWebSocket();
        this.initializeErrorHandling();
    }
    
    initializeMiddlewares() {
        // Security headers
        this.app.use(helmet());
        
        // CORS configuration
        this.app.use(cors({
            origin: process.env.FRONTEND_URL || '*',
            methods: ['GET', 'POST', 'PUT', 'DELETE'],
            allowedHeaders: ['Content-Type', 'Authorization']
        }));
        
        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 100 // limit each IP to 100 requests per windowMs
        });
        this.app.use(limiter);
        
        // Body parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true }));
        
        // Request logging
        this.app.use((req, res, next) => {
            console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
            next();
        });
    }
    
    initializeRoutes() {
        // Health check endpoint
        this.app.get('/health', (req, res) => {
            res.status(200).json({
                status: 'ok',
                timestamp: new Date().toISOString(),
                uptime: process.uptime()
            });
        });
        
        // AI Brain API endpoints
        const router = express.Router();
        
        // Process prompt
        router.post('/think', async (req, res, next) => {
            try {
                const { prompt, context = {} } = req.body;
                
                if (!prompt) {
                    return res.status(400).json({ 
                        error: 'Prompt is required' 
                    });
                }
                
                const result = await this.aiBrain.think(prompt, context);
                res.json(result);
                
            } catch (error) {
                next(error);
            }
        });
        
        // Get system state
        router.get('/system/state', async (req, res, next) => {
            try {
                const state = await this.aiBrain.getSystemState();
                res.json(state);
            } catch (error) {
                next(error);
            }
        });
        
        this.app.use('/api', router);
    }
    
    initializeWebSocket() {
        this.io.on('connection', (socket) => {
            console.log('Client connected:', socket.id);
            
            // Handle real-time AI thinking
            socket.on('think', async ({ prompt, context = {} }, callback) => {
                try {
                    const result = await this.aiBrain.think(prompt, context);
                    callback({ success: true, data: result });
                } catch (error) {
                    callback({ 
                        success: false, 
                        error: error.message 
                    });
                }
            });
            
            socket.on('disconnect', () => {
                console.log('Client disconnected:', socket.id);
            });
        });
    }
    
    initializeErrorHandling() {
        // 404 handler
        this.app.use((req, res) => {
            res.status(404).json({
                error: 'Not Found',
                message: `Cannot ${req.method} ${req.path}`
            });
        });
        
        // Global error handler
        this.app.use((err, req, res, next) => {
            console.error('API Error:', err);
            
            const statusCode = err.statusCode || 500;
            const message = err.message || 'Internal Server Error';
            
            res.status(statusCode).json({
                error: message,
                ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
            });
        });
    }
    
    start() {
        return new Promise((resolve, reject) => {
            this.httpServer.listen(this.port, () => {
                console.log(`🚀 API Server running on port ${this.port}`);
                console.log(`📡 WebSocket server ready at ws://localhost:${this.port}`);
                resolve();
            }).on('error', (err) => {
                console.error('Failed to start server:', err);
                reject(err);
            });
        });
    }
    
    async shutdown() {
        console.log('Shutting down server...');
        
        // Close WebSocket server
        if (this.io) {
            this.io.close();
        }
        
        // Close HTTP server
        if (this.httpServer) {
            this.httpServer.close();
        }
        
        // Perform any cleanup
        if (this.aiBrain && typeof this.aiBrain.shutdown === 'function') {
            await this.aiBrain.shutdown();
        }
        
        console.log('Server shutdown complete');
    }
}

// Handle process termination
process.on('SIGTERM', () => {
    console.log('SIGTERM received');
    server.shutdown().then(() => process.exit(0));
});

process.on('SIGINT', () => {
    console.log('SIGINT received');
    server.shutdown().then(() => process.exit(0));
});

// Start the server
const server = new APIServer();
server.start().catch(err => {
    console.error('Failed to start server:', err);
    process.exit(1);
});

module.exports = server;
