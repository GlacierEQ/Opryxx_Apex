// Robust HTTP server with comprehensive error handling and keep-alive
const http = require('http');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  PORT: 3005,
  HOST: '0.0.0.0',
  LOG_FILE: path.join(__dirname, 'server.log'),
  KEEP_ALIVE_TIMEOUT: 60 * 1000, // 60 seconds
  MAX_HEADERS_COUNT: 2000,
  TIMEOUT: 30 * 1000, // 30 seconds
};

// Initialize logging
const logStream = fs.createWriteStream(CONFIG.LOG_FILE, { flags: 'a' });

function log(message, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] [${level}] ${message}\n`;
  
  // Log to console
  process.stdout.write(logMessage);
  
  // Log to file
  logStream.write(logMessage, 'utf8');
}

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  log(`UNCAUGHT EXCEPTION: ${error.stack || error}`, 'ERROR');
  // Don't exit immediately, give time for logging
  setTimeout(() => process.exit(1), 100);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  log(`UNHANDLED REJECTION at: ${promise}. Reason: ${reason}`, 'ERROR');
});

// Create HTTP server
const server = http.createServer((req, res) => {
  const startTime = process.hrtime();
  
  // Log request
  log(`REQUEST: ${req.method} ${req.url} from ${req.socket.remoteAddress}`);
  
  // Set response headers
  res.setHeader('X-Powered-By', 'AI Workbench');
  res.setHeader('X-Request-ID', Date.now().toString(36));
  
  // Handle different routes
  if (req.url === '/health') {
    handleHealthCheck(req, res, startTime);
  } else if (req.url === '/') {
    handleRoot(req, res, startTime);
  } else {
    handleNotFound(req, res, startTime);
  }
});

// Configure server
server.keepAliveTimeout = CONFIG.KEEP_ALIVE_TIMEOUT;
server.maxHeadersCount = CONFIG.MAX_HEADERS_COUNT;
server.timeout = CONFIG.TIMEOUT;

// Request handlers
function handleHealthCheck(req, res, startTime) {
  const healthData = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    node: process.version,
    platform: process.platform,
    pid: process.pid,
  };
  
  sendJsonResponse(res, 200, healthData, startTime);
}

function handleRoot(req, res, startTime) {
  const response = {
    message: 'AI Workbench API',
    version: '1.0.0',
    endpoints: [
      'GET / - API Information',
      'GET /health - Health check',
    ],
  };
  
  sendJsonResponse(res, 200, response, startTime);
}

function handleNotFound(req, res, startTime) {
  const response = {
    error: 'Not Found',
    message: `Cannot ${req.method} ${req.url}`,
    status: 404,
  };
  
  sendJsonResponse(res, 404, response, startTime);
}

// Helper function to send JSON responses
function sendJsonResponse(res, statusCode, data, startTime) {
  const responseTime = process.hrtime(startTime);
  const responseTimeMs = (responseTime[0] * 1e3 + responseTime[1] / 1e6).toFixed(3);
  
  res.setHeader('Content-Type', 'application/json');
  res.statusCode = statusCode;
  
  // Add response time header
  res.setHeader('X-Response-Time', `${responseTimeMs}ms`);
  
  // Log response
  log(`RESPONSE: ${res.statusCode} in ${responseTimeMs}ms`);
  
  // Send response
  res.end(JSON.stringify(data, null, 2) + '\n');
}

// Handle server errors
server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    log(`Port ${CONFIG.PORT} is already in use`, 'ERROR');
  } else if (error.code === 'EACCES') {
    log(`Port ${CONFIG.PORT} requires elevated privileges`, 'ERROR');
  } else {
    log(`Server error: ${error.stack || error}`, 'ERROR');
  }
  
  // Don't try to restart immediately to prevent tight restart loops
  setTimeout(() => process.exit(1), 1000);
});

// Handle process termination
process.on('SIGTERM', () => {
  log('SIGTERM received - shutting down gracefully');
  shutdown();
});

process.on('SIGINT', () => {
  log('SIGINT received - shutting down gracefully');
  shutdown();
});

// Graceful shutdown function
function shutdown() {
  log('Shutting down server...');
  
  // Close server
  server.close((err) => {
    if (err) {
      log(`Error during server shutdown: ${err}`, 'ERROR');
      process.exit(1);
    }
    
    log('Server closed');
    
    // Close log file
    logStream.end('Server shutdown complete\n', 'utf8', () => {
      process.exit(0);
    });
  });
  
  // Force shutdown after 5 seconds
  setTimeout(() => {
    log('Forcing shutdown after timeout', 'WARN');
    process.exit(1);
  }, 5000);
}

// Start the server
server.listen(CONFIG.PORT, CONFIG.HOST, () => {
  const address = server.address();
  const host = address.address === '::' ? 'localhost' : address.address;
  const port = address.port;
  
  log(`Server running at http://${host}:${port}`);
  log('Available endpoints:');
  log(`- http://${host}:${port}/`);
  log(`- http://${host}:${port}/health`);
  log('Press Ctrl+C to stop the server\n');
  
  // Keep the process alive
  setInterval(() => {
    log('Server keep-alive ping');
  }, 60000); // Log every minute to keep process alive
});

// Handle uncaught exceptions in the event loop
process.on('uncaughtExceptionMonitor', (error, origin) => {
  log(`Uncaught exception in ${origin}: ${error.stack || error}`, 'ERROR');
});

// Log process start
log(`Starting server (Node.js ${process.version} on ${process.platform} ${process.arch})`);
log(`Process ID: ${process.pid}`);
log(`Working directory: ${process.cwd()}`);
log(`Server will listen on ${CONFIG.HOST}:${CONFIG.PORT}`);
