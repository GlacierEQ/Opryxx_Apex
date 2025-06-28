// Simple HTTP server with minimal dependencies
const http = require('http');

const hostname = '127.0.0.1';
const port = 3002;

const server = http.createServer((req, res) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  
  if (req.url === '/health') {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({
      status: 'ok',
      timestamp: new Date().toISOString(),
      node: process.version
    }));
    return;
  }
  
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('AI Workbench Test Server\n');
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
  console.log('Try these endpoints:');
  console.log(`- http://${hostname}:${port}/`);
  console.log(`- http://${hostname}:${port}/health`);
});

// Handle errors
server.on('error', (error) => {
  console.error('Server error:', error);
  if (error.code === 'EADDRINUSE') {
    console.error(`Port ${port} is already in use`);
  }
});

// Handle process termination
process.on('SIGTERM', () => {
  console.log('SIGTERM received');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
