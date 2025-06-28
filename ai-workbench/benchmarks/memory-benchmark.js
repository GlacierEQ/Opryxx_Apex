#!/usr/bin/env node

/**
 * AdvancedMemoryManager Performance Benchmark Suite
 * 
 * This script provides comprehensive performance benchmarks for the AdvancedMemoryManager,
 * including memory allocation, garbage collection, caching, and GPU acceleration metrics.
 */

const { performance, PerformanceObserver } = require('perf_hooks');
const { promisify } = require('util');
const { writeFile } = require('fs').promises;
const path = require('path');
const os = require('os');
const { AdvancedMemoryManager } = require('../core/advanced-memory-manager');

// Configuration
const CONFIG = {
    iterations: 1000,           // Number of iterations for each benchmark
    warmupRuns: 5,             // Number of warmup runs
    outputDir: './benchmark-results',
    maxMemoryMB: 1024,         // Maximum memory to use for stress tests (MB)
    gcBeforeEach: false        // Run GC before each benchmark
};

// Benchmark results storage
const results = {
    metadata: {
        timestamp: new Date().toISOString(),
        platform: process.platform,
        arch: process.arch,
        nodeVersion: process.version,
        cpus: os.cpus().length,
        totalMemory: os.totalmem(),
        freeMemory: os.freemem()
    },
    benchmarks: {}
};

// Performance measurement utilities
class Benchmark {
    constructor(name) {
        this.name = name;
        this.startTime = 0;
        this.memoryBefore = 0;
        this.memoryAfter = 0;
        this.runs = [];
        this.currentRun = null;
    }

    start() {
        if (CONFIG.gcBeforeEach && global.gc) global.gc();
        this.memoryBefore = process.memoryUsage().heapUsed;
        this.startTime = performance.now();
        this.currentRun = { start: this.startTime };
    }

    end() {
        const endTime = performance.now();
        this.memoryAfter = process.memoryUsage().heapUsed;
        
        if (this.currentRun) {
            this.currentRun.duration = endTime - this.startTime;
            this.currentRun.memoryUsed = this.memoryAfter - this.memoryBefore;
            this.runs.push(this.currentRun);
            this.currentRun = null;
        }
        
        return this.runs[this.runs.length - 1];
    }

    getStats() {
        if (this.runs.length === 0) return null;
        
        const durations = this.runs.map(r => r.duration);
        const memoryUsed = this.runs.map(r => r.memoryUsed);
        
        const sum = arr => arr.reduce((a, b) => a + b, 0);
        const avg = arr => sum(arr) / arr.length;
        const min = arr => Math.min(...arr);
        const max = arr => Math.max(...arr);
        const std = (arr, mean) => {
            const squareDiffs = arr.map(value => Math.pow(value - mean, 2));
            return Math.sqrt(avg(squareDiffs));
        };
        
        const avgDuration = avg(durations);
        const avgMemory = avg(memoryUsed);
        
        return {
            name: this.name,
            runs: this.runs.length,
            duration: {
                avg: avgDuration,
                min: min(durations),
                max: max(durations),
                std: std(durations, avgDuration),
                unit: 'ms'
            },
            memory: {
                avg: avgMemory,
                min: min(memoryUsed),
                max: max(memoryUsed),
                std: std(memoryUsed, avgMemory),
                unit: 'bytes'
            }
        };
    }
}

// Benchmark suite
class BenchmarkSuite {
    constructor() {
        this.benchmarks = new Map();
        this.memoryManager = new AdvancedMemoryManager({
            enableGPUMonitoring: true,
            maxHistorySize: 1000
        });
    }

    async run() {
        console.log('🚀 Starting AdvancedMemoryManager Benchmark Suite');
        console.log('==============================================');
        console.log(`Platform: ${os.platform()} ${os.arch()}`);
        console.log(`Node.js: ${process.version}`);
        console.log(`CPUs: ${os.cpus().length}`);
        console.log(`Total Memory: ${(os.totalmem() / (1024 * 1024)).toFixed(2)} MB`);
        console.log('==============================================\n');

        // Run benchmarks
        await this.runBenchmark('memoryAllocation', this.benchmarkMemoryAllocation.bind(this));
        await this.runBenchmark('garbageCollection', this.benchmarkGarbageCollection.bind(this));
        await this.runBenchmark('cachePerformance', this.benchmarkCachePerformance.bind(this));
        await this.runBenchmark('tensorOperations', this.benchmarkTensorOperations.bind(this));
        await this.runBenchmark('stressTest', this.benchmarkStressTest.bind(this));
        
        // GPU benchmarks if available
        if (this.memoryManager.gpuInfo && this.memoryManager.gpuInfo.length > 0) {
            await this.runBenchmark('gpuOperations', this.benchmarkGPUOperations.bind(this));
        }

        // Save results
        await this.saveResults();
        
        // Print summary
        this.printSummary();
        
        // Clean up
        this.memoryManager.destroy();
    }

    async runBenchmark(name, benchmarkFn) {
        console.log(`\n🔍 Running benchmark: ${name}`);
        console.log('='.repeat(name.length + 20));
        
        const benchmark = new Benchmark(name);
        
        // Warmup
        console.log('  Warming up...');
        for (let i = 0; i < CONFIG.warmupRuns; i++) {
            await benchmarkFn(benchmark, true);
        }
        
        // Actual benchmark
        console.log(`  Running ${CONFIG.iterations} iterations...`);
        for (let i = 0; i < CONFIG.iterations; i++) {
            if (i > 0 && i % 100 === 0) process.stdout.write(`  ${i}/${CONFIG.iterations}\r`);
            await benchmarkFn(benchmark, false);
        }
        
        // Store results
        const stats = benchmark.getStats();
        results.benchmarks[name] = stats;
        
        // Print stats
        console.log('\n  Results:');
        console.log(`  - Runs: ${stats.runs}`);
        console.log(`  - Duration: ${stats.duration.avg.toFixed(2)}ms ±${stats.duration.std.toFixed(2)}ms`);
        console.log(`  - Memory: ${(stats.memory.avg / 1024).toFixed(2)} KB`);
        
        return stats;
    }

    // Benchmark implementations
    async benchmarkMemoryAllocation(benchmark) {
        const sizes = [64, 256, 1024, 4096]; // KB
        
        benchmark.start();
        
        // Test different allocation sizes
        const allocations = [];
        for (const size of sizes) {
            const buffer = Buffer.alloc(size * 1024);
            allocations.push(buffer);
        }
        
        // Force cleanup
        allocations.length = 0;
        if (global.gc) global.gc();
        
        benchmark.end();
    }

    async benchmarkGarbageCollection(benchmark) {
        benchmark.start();
        
        // Create and release memory pressure
        const createObjects = (count) => {
            const objs = [];
            for (let i = 0; i < count; i++) {
                objs.push({ id: i, data: Buffer.alloc(1024) });
            }
            return objs;
        };
        
        const objects = createObjects(10000);
        
        // Force GC and measure
        if (global.gc) {
            const before = process.memoryUsage().heapUsed;
            global.gc();
            const after = process.memoryUsage().heapUsed;
            benchmark.currentRun.memoryFreed = before - after;
        }
        
        benchmark.end();
    }

    async benchmarkCachePerformance(benchmark) {
        const cache = this.memoryManager.createCache('benchmark', { maxSize: 1000 });
        const keys = Array.from({ length: 1000 }, (_, i) => `key${i}`);
        
        benchmark.start();
        
        // Fill cache
        for (const key of keys) {
            cache.set(key, { data: Buffer.alloc(1024) });
        }
        
        // Random access
        for (let i = 0; i < 10000; i++) {
            const key = keys[Math.floor(Math.random() * keys.length)];
            cache.get(key);
        }
        
        benchmark.end();
    }

    async benchmarkTensorOperations(benchmark) {
        benchmark.start();
        
        // Simulate tensor operations
        const tensorId = 'benchmark-tensor';
        const shape = [100, 100];
        
        // Allocate and use tensor
        const tensor = this.memoryManager.allocateTensor(tensorId, shape, 'float32');
        if (tensor && tensor.buffer) {
            // Simulate some computation
            for (let i = 0; i < tensor.buffer.length; i++) {
                tensor.buffer[i] = Math.random();
            }
        }
        
        // Clean up
        this.memoryManager.freeTensor(tensorId);
        
        benchmark.end();
    }

    async benchmarkGPUOperations(benchmark) {
        if (!this.memoryManager.gpuInfo) {
            console.log('  No GPU detected, skipping GPU benchmark');
            return;
        }
        
        benchmark.start();
        
        try {
            // Simulate GPU operations
            await this.memoryManager.gpuManager.updateGPUMetrics();
            const metrics = this.memoryManager.gpuManager.gpuLoadHistory;
            benchmark.currentRun.gpuMetrics = metrics[metrics.length - 1];
        } catch (error) {
            console.error('  GPU benchmark failed:', error.message);
        }
        
        benchmark.end();
    }

    async benchmarkStressTest(benchmark) {
        benchmark.start();
        
        // Create memory pressure
        const chunkSize = 10 * 1024 * 1024; // 10MB chunks
        const maxChunks = (CONFIG.maxMemoryMB * 1024 * 1024) / chunkSize;
        const chunks = [];
        
        // Allocate until we hit the limit
        try {
            for (let i = 0; i < maxChunks; i++) {
                chunks.push(Buffer.alloc(chunkSize));
                // Simulate some work
                for (let j = 0; j < chunkSize; j += 4096) {
                    chunks[i][j] = Math.random() * 256;
                }
            }
        } catch (error) {
            console.log(`  Memory limit reached at ${(chunks.length * chunkSize) / (1024 * 1024)}MB`);
        }
        
        // Clean up
        chunks.length = 0;
        if (global.gc) global.gc();
        
        benchmark.end();
    }

    // Result handling
    async saveResults() {
        try {
            const fs = require('fs');
            if (!fs.existsSync(CONFIG.outputDir)) {
                fs.mkdirSync(CONFIG.outputDir, { recursive: true });
            }
            
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `memory-benchmark-${timestamp}.json`;
            const filepath = path.join(CONFIG.outputDir, filename);
            
            await writeFile(filepath, JSON.stringify(results, null, 2));
            console.log(`\n✅ Benchmark results saved to: ${filepath}`);
        } catch (error) {
            console.error('Failed to save benchmark results:', error);
        }
    }

    printSummary() {
        console.log('\n📊 Benchmark Summary');
        console.log('===================');
        
        for (const [name, stats] of Object.entries(results.benchmarks)) {
            console.log(`\n${name}:`);
            console.log(`  Duration: ${stats.duration.avg.toFixed(2)}ms ±${stats.duration.std.toFixed(2)}ms`);
            console.log(`  Memory: ${(stats.memory.avg / 1024).toFixed(2)} KB`);
            if (stats.gpuMetrics) {
                console.log('  GPU Metrics:', JSON.stringify(stats.gpuMetrics, null, 2));
            }
        }
    }
}

// Run the benchmark suite
(async () => {
    try {
        const suite = new BenchmarkSuite();
        await suite.run();
    } catch (error) {
        console.error('Benchmark failed:', error);
        process.exit(1);
    }
})();
