// Minimal HTTP server with enhanced error handling
const http = require('http');

const PORT = 3004;
const HOST = '0.0.0.0'; // Listen on all interfaces

console.log('Starting minimal HTTP server...');
console.log(`Node.js version: ${process.version}`);
console.log(`Platform: ${process.platform} ${process.arch}`);
console.log(`Current directory: ${process.cwd()}`);

const server = http.createServer((req, res) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.url}`);
  
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      timestamp,
      node: process.version,
      platform: process.platform,
      memory: process.memoryUsage()
    }, null, 2));
    return;
  }
  
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('AI Workbench Minimal HTTP Server\n');
});

// Handle server errors
server.on('error', (error) => {
  console.error('Server error:', error);
  if (error.code === 'EACCES') {
    console.error(`Port ${PORT} requires elevated privileges`);
  } else if (error.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use`);
  }
  process.exit(1);
});

// Start the server
server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}`);
  console.log('Try these endpoints:');
  console.log(`- http://localhost:${PORT}/`);
  console.log(`- http://localhost:${PORT}/health`);
});

// Handle process termination
const shutdown = () => {
  console.log('\nShutting down server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
};

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

console.log('Press Ctrl+C to stop the server');
