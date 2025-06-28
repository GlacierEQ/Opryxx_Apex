#!/usr/bin/env node
/**
 * ULTIMATE MEMORY SYSTEM LAUNCHER
 * Launches comprehensive memory testing and AI integration
 */

const chalk = require('chalk');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log(chalk.cyan('🚀 ULTIMATE MEMORY SYSTEM LAUNCHER'));
console.log(chalk.cyan('=' .repeat(50)));

async function launchMemoryTests() {
    console.log(chalk.yellow('\n📋 Launching Ultimate Memory Test Suite...'));
    
    // Check if we need to expose garbage collection
    const needsGC = !global.gc;
    
    if (needsGC) {
        console.log(chalk.yellow('⚠️ Restarting with --expose-gc for full testing capabilities...'));
        
        // Restart with --expose-gc flag
        const child = spawn(process.execPath, ['--expose-gc', __filename], {
            stdio: 'inherit',
            cwd: process.cwd()
        });
        
        child.on('close', (code) => {
            process.exit(code);
        });
        
        return;
    }
    
    console.log(chalk.green('✅ Garbage collection exposed - full testing available'));
    
    // Run the test suite
    try {
        const UltimateMemoryTestSuite = require('./tests/ultimate-memory-test');
        const testSuite = new UltimateMemoryTestSuite();
        
        await testSuite.runCompleteTestSuite();
        
        console.log(chalk.green('\n🎉 Memory test suite completed successfully!'));
        
    } catch (error) {
        console.error(chalk.red('\n💥 Test suite failed:'), error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Performance monitoring
const startTime = Date.now();
const startMemory = process.memoryUsage();

process.on('exit', () => {
    const endTime = Date.now();
    const endMemory = process.memoryUsage();
    const duration = (endTime - startTime) / 1000;
    const memoryDelta = endMemory.heapUsed - startMemory.heapUsed;
    
    console.log(chalk.cyan('\n📊 Launcher Performance:'));
    console.log(chalk.white(`   Duration: ${duration.toFixed(2)}s`));
    console.log(chalk.white(`   Memory Delta: ${formatBytes(memoryDelta)}`));
    console.log(chalk.white(`   Peak Memory: ${formatBytes(endMemory.heapUsed)}`));
});

function formatBytes(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

// Launch the tests
launchMemoryTests().catch(console.error);
