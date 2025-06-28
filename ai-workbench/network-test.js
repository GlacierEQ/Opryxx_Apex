// Network test script to verify basic networking functionality
const net = require('net');
const dns = require('dns');
const os = require('os');

// Configuration
const TEST_PORT = 3003;
const TEST_HOST = '127.0.0.1';

console.log('=== Network Configuration Test ===');
console.log(`Platform: ${process.platform} ${process.arch}`);
console.log(`Node.js: ${process.version}`);
console.log(`Hostname: ${os.hostname()}`);
console.log('Network Interfaces:', JSON.stringify(os.networkInterfaces(), null, 2));

// Test DNS resolution
dns.lookup('localhost', (err, address, family) => {
  console.log(`\nDNS Test - localhost resolves to:`, { address, family });
});

// Test port availability
const testServer = net.createServer();

testServer.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.log(`❌ Port ${TEST_PORT} is already in use`);
  } else {
    console.log('Server error:', e);
  }
  process.exit(1);
});

testServer.on('listening', () => {
  console.log(`✅ Successfully bound to ${TEST_HOST}:${TEST_PORT}`);
  testServer.close(() => {
    console.log('Test completed successfully');
    process.exit(0);
  });
});

console.log(`\nAttempting to bind to ${TEST_HOST}:${TEST_PORT}...`);
testServer.listen(TEST_PORT, TEST_HOST);

// Timeout after 5 seconds
setTimeout(() => {
  console.log('Test timed out');
  process.exit(1);
}, 5000);
