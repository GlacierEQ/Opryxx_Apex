#!/usr/bin/env node
/**
 * NEXUS PERFORMANCE BENCHMARK LAUNCHER
 * Quick launcher for the comprehensive performance testing suite
 */

const chalk = require('chalk');
const { spawn } = require('child_process');

console.log(chalk.cyan('🚀 NEXUS PERFORMANCE BENCHMARK LAUNCHER'));
console.log(chalk.cyan('=' .repeat(50)));

async function launchPerformanceTests() {
    console.log(chalk.yellow('\n📊 Launching Performance Benchmark Suite...'));
    
    // Check if we need to expose garbage collection
    const needsGC = !global.gc;
    
    if (needsGC) {
        console.log(chalk.yellow('⚠️ Restarting with --expose-gc for full testing capabilities...'));
        
        // Restart with --expose-gc flag
        const child = spawn(process.execPath, [
            '--expose-gc', 
            'tests/performance-benchmarks.js'
        ], {
            stdio: 'inherit',
            cwd: process.cwd()
        });
        
        child.on('close', (code) => {
            if (code === 0) {
                console.log(chalk.green('\n🎉 Performance tests completed successfully!'));
            } else {
                console.log(chalk.red('\n❌ Performance tests failed with code:', code));
            }
            process.exit(code);
        });
        
        return;
    }
    
    console.log(chalk.green('✅ Garbage collection exposed - full testing available'));
    
    // Run the test suite directly
    try {
        const NexusPerformanceBenchmarks = require('./tests/performance-benchmarks');
        const benchmarks = new NexusPerformanceBenchmarks();
        
        await benchmarks.runAllBenchmarks();
        
        console.log(chalk.green('\n🎉 Performance benchmark suite completed successfully!'));
        
    } catch (error) {
        console.error(chalk.red('\n💥 Benchmark suite failed:'), error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Performance monitoring
const startTime = Date.now();

process.on('exit', () => {
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    console.log(chalk.cyan('\n📊 Launcher Stats:'));
    console.log(chalk.white(`   Total Duration: ${duration.toFixed(2)}s`));
    console.log(chalk.white(`   Memory Usage: ${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)}MB`));
});

// Launch the tests
launchPerformanceTests().catch(console.error);
