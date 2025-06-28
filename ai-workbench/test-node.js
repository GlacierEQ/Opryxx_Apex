// Simple test to verify Node.js is working
console.log('Node.js test script running!');
console.log('Node.js version:', process.version);
console.log('Platform:', process.platform);
console.log('Current directory:', process.cwd());

// Test basic functionality
const testObj = { test: 'success', timestamp: new Date().toISOString() };
console.log('Test object:', JSON.stringify(testObj, null, 2));

// Test async/await
(async () => {
  try {
    const response = await Promise.resolve('Async test passed!');
    console.log(response);
  } catch (error) {
    console.error('Async test failed:', error);
  }
})();
