// Minimal HTTP server test
const http = require('http');

console.log('Starting minimal HTTP server test...');
console.log('Node.js version:', process.version);

const server = http.createServer((req, res) => {
  console.log('Request received:', req.method, req.url);
  
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', time: new Date().toISOString() }));
    return;
  }
  
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello, World!\n');
});

const PORT = 8080;
const HOST = '127.0.0.1';

server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}/`);
  console.log('Test with:');
  console.log(`- curl http://${HOST}:${PORT}/`);
  console.log(`- curl http://${HOST}:${PORT}/health`);
  console.log('\nPress Ctrl+C to stop the server');
});

// Keep process alive
process.stdin.resume();

// Handle process termination
process.on('SIGINT', () => {
  console.log('\nShutting down server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

console.log('Test script loaded');
