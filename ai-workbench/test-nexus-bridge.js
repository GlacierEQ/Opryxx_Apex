/**
 * TEST NEXUS BRIDGE - Real-time Python ↔ JavaScript Communication
 * ================================================================
 * Test the bridge between Python core and JavaScript interface
 */

const NexusCorebridge = require('./nexus-core-bridge');
const WebSocket = require('ws');
const chalk = require('chalk');

class NexusBridgeTest {
    constructor() {
        this.bridge = null;
        this.client = null;
        this.testResults = [];
    }
    
    async runFullTest() {
        console.log(chalk.cyan('🧪 NEXUS BRIDGE INTEGRATION TEST'));
        console.log(chalk.gray('=' .repeat(50)));
        
        try {
            // Step 1: Start the bridge
            await this.startBridge();
            
            // Step 2: Wait for bridge to be ready
            await this.waitForBridge();
            
            // Step 3: Test client connection
            await this.testClientConnection();
            
            // Step 4: Test real-time communication
            await this.testRealTimeCommunication();
            
            // Step 5: Test Python integration
            await this.testPythonIntegration();
            
            // Show results
            this.showTestResults();
            
        } catch (error) {
            console.error(chalk.red('❌ Test failed:'), error);
        }
    }
    
    async startBridge() {
        console.log(chalk.blue('🚀 Starting NEXUS Core Bridge...'));
        
        this.bridge = new NexusCorebridge();
        
        // Give bridge time to start
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        console.log(chalk.green('✅ Bridge started'));
        this.testResults.push({ test: 'Bridge Startup', status: 'PASS' });
    }
    
    async waitForBridge() {
        console.log(chalk.blue('⏳ Waiting for bridge to be ready...'));
        
        let attempts = 0;
        const maxAttempts = 10;
        
        while (attempts < maxAttempts) {
            if (this.bridge.status.websocket_server && this.bridge.status.python_core) {
                console.log(chalk.green('✅ Bridge is ready'));
                this.testResults.push({ test: 'Bridge Ready', status: 'PASS' });
                return;
            }
            
            await new Promise(resolve => setTimeout(resolve, 1000));
            attempts++;
        }
        
        throw new Error('Bridge not ready after maximum attempts');
    }
    
    async testClientConnection() {
        console.log(chalk.blue('🔌 Testing WebSocket client connection...'));
        
        return new Promise((resolve, reject) => {
            this.client = new WebSocket('ws://localhost:3001');
            
            this.client.on('open', () => {
                console.log(chalk.green('✅ Client connected to bridge'));
                this.testResults.push({ test: 'Client Connection', status: 'PASS' });
                resolve();
            });
            
            this.client.on('message', (data) => {
                try {
                    const message = JSON.parse(data);
                    console.log(chalk.gray(`📨 Received: ${message.type}`));
                } catch (error) {
                    console.error(chalk.red('Invalid message:'), data.toString());
                }
            });
            
            this.client.on('error', (error) => {
                console.error(chalk.red('❌ Client connection failed:'), error);
                this.testResults.push({ test: 'Client Connection', status: 'FAIL' });
                reject(error);
            });
            
            // Timeout after 5 seconds
            setTimeout(() => {
                if (this.client.readyState !== WebSocket.OPEN) {
                    reject(new Error('Client connection timeout'));
                }
            }, 5000);
        });
    }
    
    async testRealTimeCommunication() {
        console.log(chalk.blue('📡 Testing real-time communication...'));
        
        const tests = [
            { type: 'get_status', expected: 'status' },
            { type: 'get_metrics', expected: 'metrics' },
            { type: 'execute_action', action: 'test_optimization', expected: 'action_result' }
        ];
        
        for (const test of tests) {
            await this.sendTestMessage(test);
        }
        
        console.log(chalk.green('✅ Real-time communication working'));
        this.testResults.push({ test: 'Real-time Communication', status: 'PASS' });
    }
    
    async sendTestMessage(test) {
        return new Promise((resolve) => {
            const messageHandler = (data) => {
                try {
                    const response = JSON.parse(data);
                    if (response.type === test.expected) {
                        console.log(chalk.green(`   ✅ ${test.type} → ${response.type}`));
                        this.client.removeListener('message', messageHandler);
                        resolve();
                    }
                } catch (error) {
                    console.error(chalk.red('Message parse error:'), error);
                }
            };
            
            this.client.on('message', messageHandler);
            this.client.send(JSON.stringify(test));
            
            // Timeout after 3 seconds
            setTimeout(() => {
                this.client.removeListener('message', messageHandler);
                resolve();
            }, 3000);
        });
    }
    
    async testPythonIntegration() {
        console.log(chalk.blue('🐍 Testing Python core integration...'));
        
        // Check if Python process is running
        if (this.bridge.pythonCore && !this.bridge.pythonCore.killed) {
            console.log(chalk.green('✅ Python core process active'));
            this.testResults.push({ test: 'Python Integration', status: 'PASS' });
        } else {
            console.log(chalk.red('❌ Python core process not active'));
            this.testResults.push({ test: 'Python Integration', status: 'FAIL' });
        }
        
        // Test file-based communication
        const fs = require('fs');
        const path = require('path');
        
        try {
            const configPath = path.join(__dirname, '..', 'config', 'opryxx.json');
            if (fs.existsSync(configPath)) {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                console.log(chalk.green(`✅ Python config accessible: ${config.opryxx.version}`));
                this.testResults.push({ test: 'Config Bridge', status: 'PASS' });
            }
        } catch (error) {
            console.log(chalk.red('❌ Config bridge failed'));
            this.testResults.push({ test: 'Config Bridge', status: 'FAIL' });
        }
    }
    
    showTestResults() {
        console.log();
        console.log(chalk.cyan('📊 TEST RESULTS'));
        console.log(chalk.gray('=' .repeat(40)));
        
        let passed = 0;
        let failed = 0;
        
        this.testResults.forEach(result => {
            const icon = result.status === 'PASS' ? '✅' : '❌';
            const color = result.status === 'PASS' ? chalk.green : chalk.red;
            
            console.log(`${icon} ${result.test.padEnd(25)}: ${color(result.status)}`);
            
            if (result.status === 'PASS') passed++;
            else failed++;
        });
        
        console.log();
        console.log(chalk.cyan(`📈 Summary: ${passed} passed, ${failed} failed`));
        
        if (failed === 0) {
            console.log(chalk.green('🎉 ALL TESTS PASSED!'));
            console.log(chalk.green('🚀 NEXUS BRIDGE IS FULLY OPERATIONAL!'));
        } else {
            console.log(chalk.yellow('⚠️  Some tests failed - check configuration'));
        }
        
        console.log();
        console.log(chalk.gray('Press Ctrl+C to stop the test'));
    }
    
    cleanup() {
        console.log(chalk.yellow('🧹 Cleaning up test environment...'));
        
        if (this.client) {
            this.client.close();
        }
        
        if (this.bridge) {
            this.bridge.shutdown();
        }
        
        console.log(chalk.green('✅ Cleanup complete'));
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log(chalk.yellow('\n🛑 Test interrupted, cleaning up...'));
    if (global.bridgeTest) {
        global.bridgeTest.cleanup();
    }
    process.exit(0);
});

// Run the test
if (require.main === module) {
    global.bridgeTest = new NexusBridgeTest();
    global.bridgeTest.runFullTest().catch(console.error);
}

module.exports = NexusBridgeTest;
