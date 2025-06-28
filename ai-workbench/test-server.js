// Enhanced test server with detailed logging
const express = require('express');

// Create Express app with enhanced logging
console.log('Creating Express app...');
const app = express();
const port = 3001; // Changed to 3001 to avoid conflicts

// Request logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Simple route
app.get('/', (req, res) => {
  res.send('AI Workbench Test Server is running!');
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    timestamp: new Date().toISOString(),
    nodeVersion: process.version
  });
});

// Start server
app.listen(port, () => {
  console.log(`Test server running at http://localhost:${port}`);
  console.log(`Try these endpoints:`);
  console.log(`- http://localhost:${port}/`);
  console.log(`- http://localhost:${port}/health`);
});

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});
