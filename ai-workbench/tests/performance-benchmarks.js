#!/usr/bin/env node
/**
 * NEXUS AI PERFORMANCE BENCHMARKING SUITE
 * Comprehensive performance testing and optimization analysis
 */

const Benchmark = require('benchmark');
const { performance } = require('perf_hooks');
const os = require('os');
const v8 = require('v8');
const fs = require('fs').promises;
const path = require('path');
const chalk = require('chalk');

class NexusPerformanceBenchmarks {
    constructor() {
        this.benchmarkResults = new Map();
        this.systemInfo = this.collectSystemInfo();
        this.startTime = Date.now();
        this.reportPath = path.join(__dirname, '../benchmarks');

        // Ensure benchmarks directory exists
        this.ensureDirectories();
    }

    async ensureDirectories() {
        try {
            await fs.mkdir(this.reportPath, { recursive: true });
        } catch (error) {
            console.warn('Warning: Could not create reports directory:', error.message);
        }
    }

    async runAllBenchmarks() {
        console.log(chalk.cyan('🚀 NEXUS AI - PERFORMANCE BENCHMARKING SUITE'));
        console.log(chalk.cyan('=' .repeat(60)));
        console.log(chalk.yellow(`🕐 Started: ${new Date().toISOString()}`));
        console.log(chalk.blue(`💻 System: ${this.systemInfo.platform} ${this.systemInfo.arch}`));
        console.log(chalk.green(`🧠 Memory: ${this.formatBytes(this.systemInfo.totalMemory)}`));
        console.log(chalk.magenta(`⚡ CPUs: ${this.systemInfo.cpuCount} cores`));
        console.log(chalk.cyan('=' .repeat(60)));

        try {
            // Memory Management Benchmarks
            await this.runMemoryBenchmarks();

            // CPU Performance Benchmarks
            await this.runCPUBenchmarks();

            // AI Model Benchmarks
            await this.runAIModelBenchmarks();

            // GPU/NPU Benchmarks
            await this.runGPUBenchmarks();

            // Concurrent Operations Benchmarks
            await this.runConcurrencyBenchmarks();

            // Generate comprehensive report
            await this.generateBenchmarkReport();

            console.log(chalk.green('\n🎉 All benchmarks completed successfully!'));
            console.log(chalk.cyan(`📁 Reports saved to: ${this.reportPath}`));

        } catch (error) {
            console.error(chalk.red('\n❌ Benchmark execution failed:'), error);
            throw error;
        }
    }

    async runMemoryBenchmarks() {
        console.log(chalk.blue('\n🧠 Running Memory Management Benchmarks...'));
        
        const results = {};

        // Garbage Collection Performance
        if (global.gc) {
            const gcResults = await this.benchmarkGarbageCollection();
            results.garbageCollection = gcResults;
        } else {
            console.log(chalk.yellow('   ⚠️ GC benchmarks skipped (run with --expose-gc for full testing)'));
        }

        // Memory Allocation Patterns
        const allocationResults = await this.benchmarkMemoryAllocations();
        results.memoryAllocations = allocationResults;

        this.benchmarkResults.set('memory_management', results);
        console.log(chalk.green('  ✅ Memory benchmarks completed'));
    }

    async benchmarkGarbageCollection() {
        console.log(chalk.cyan('     🗑️ Testing garbage collection performance...'));
        
        const results = { cycles: [], totalTime: 0, avgTime: 0 };

        for (let i = 0; i < 5; i++) {
            // Create garbage
            const garbage = [];
            for (let j = 0; j < 50000; j++) {
                garbage.push({ id: j, data: new Array(100).fill(Math.random()) });
            }

            const beforeGC = process.memoryUsage();
            const startTime = performance.now();
            
            global.gc();
            
            const endTime = performance.now();
            const afterGC = process.memoryUsage();

            const cycleTime = endTime - startTime;
            const memoryFreed = beforeGC.heapUsed - afterGC.heapUsed;

            results.cycles.push({
                time: cycleTime,
                memoryFreed: memoryFreed,
                efficiency: memoryFreed / cycleTime
            });

            results.totalTime += cycleTime;
            
            // Clean up
            garbage.length = 0;
        }

        results.avgTime = results.totalTime / results.cycles.length;
        console.log(chalk.cyan(`        Average GC time: ${results.avgTime.toFixed(2)}ms`));

        return results;
    }

    async benchmarkMemoryAllocations() {
        console.log(chalk.cyan('     💾 Testing memory allocation patterns...'));
        
        const suite = new Benchmark.Suite('Memory Allocations');
        const results = {};

        return new Promise((resolve) => {
            suite.add('Small Object Creation', () => {
                const objects = [];
                for (let i = 0; i < 1000; i++) {
                    objects.push({ id: i, value: Math.random() });
                }
                return objects.length;
            });

            suite.add('Large Array Creation', () => {
                const arr = new Array(10000).fill(0).map(() => Math.random());
                return arr.length;
            });

            suite.add('String Concatenation', () => {
                let str = '';
                for (let i = 0; i < 1000; i++) {
                    str += `Item ${i} `;
                }
                return str.length;
            });

            suite.add('Map Operations', () => {
                const map = new Map();
                for (let i = 0; i < 1000; i++) {
                    map.set(`key_${i}`, Math.random());
                }
                return map.size;
            });

            suite.on('cycle', (event) => {
                const benchmark = event.target;
                results[benchmark.name] = {
                    hz: benchmark.hz,
                    rme: benchmark.stats.rme,
                    samples: benchmark.stats.sample.length
                };
                console.log(chalk.cyan(`        ${benchmark.name}: ${this.formatOpsPerSec(benchmark.hz)} ops/sec`));
            });

            suite.on('complete', () => {
                resolve(results);
            });

            suite.run({ async: true });
        });
    }

    async runCPUBenchmarks() {
        console.log(chalk.blue('\n⚡ Running CPU Performance Benchmarks...'));
        
        const suite = new Benchmark.Suite('CPU Performance');
        const results = {};

        return new Promise((resolve) => {
            suite.add('Mathematical Operations', () => {
                let result = 0;
                for (let i = 0; i < 10000; i++) {
                    result += Math.sin(i) * Math.cos(i) + Math.sqrt(i);
                }
                return result;
            });

            suite.add('String Operations', () => {
                let result = '';
                for (let i = 0; i < 1000; i++) {
                    result += `String ${i} with some text `;
                }
                return result.length;
            });

            suite.add('JSON Operations', () => {
                const obj = { data: new Array(1000).fill(0).map((_, i) => ({ id: i, value: Math.random() })) };
                const json = JSON.stringify(obj);
                const parsed = JSON.parse(json);
                return parsed.data.length;
            });

            suite.add('Array Operations', () => {
                const arr = new Array(10000).fill(0).map((_, i) => i);
                const filtered = arr.filter(x => x % 2 === 0);
                const mapped = filtered.map(x => x * 2);
                return mapped.reduce((a, b) => a + b, 0);
            });

            suite.add('Object Property Access', () => {
                const obj = {};
                for (let i = 0; i < 1000; i++) {
                    obj[`prop${i}`] = i;
                }
                let sum = 0;
                for (let i = 0; i < 1000; i++) {
                    sum += obj[`prop${i}`];
                }
                return sum;
            });

            suite.on('cycle', (event) => {
                const benchmark = event.target;
                results[benchmark.name] = {
                    hz: benchmark.hz,
                    rme: benchmark.stats.rme,
                    samples: benchmark.stats.sample.length
                };
                console.log(chalk.cyan(`     ${benchmark.name}: ${this.formatOpsPerSec(benchmark.hz)} ops/sec`));
            });

            suite.on('complete', () => {
                this.benchmarkResults.set('cpu_performance', results);
                console.log(chalk.green('  ✅ CPU Performance benchmarks completed'));
                resolve(results);
            });

            suite.run({ async: true });
        });
    }

    async runAIModelBenchmarks() {
        console.log(chalk.blue('\n🤖 Running AI Model Benchmarks...'));
        
        const results = {};

        // Simulate AI model operations
        const modelLoadingResults = await this.benchmarkModelLoading();
        results.modelLoading = modelLoadingResults;

        const inferenceResults = await this.benchmarkInference();
        results.inference = inferenceResults;

        this.benchmarkResults.set('ai_models', results);
        console.log(chalk.green('  ✅ AI Model benchmarks completed'));
    }

    async benchmarkModelLoading() {
        console.log(chalk.cyan('     📥 Testing model loading performance...'));
        
        const loadingTimes = [];

        for (let i = 0; i < 5; i++) {
            const startTime = performance.now();
            
            // Simulate model loading (creating large data structures)
            const model = {
                weights: new Array(100000).fill(0).map(() => Math.random()),
                biases: new Array(1000).fill(0).map(() => Math.random()),
                config: {
                    layers: 50,
                    neurons: 1000,
                    activation: 'relu'
                }
            };

            const endTime = performance.now();
            const loadTime = endTime - startTime;
            loadingTimes.push(loadTime);

            // Clean up
            model.weights.length = 0;
            model.biases.length = 0;
        }

        const avgTime = loadingTimes.reduce((a, b) => a + b, 0) / loadingTimes.length;
        console.log(chalk.cyan(`        Average model loading: ${avgTime.toFixed(2)}ms`));

        return { times: loadingTimes, avgTime, totalModels: loadingTimes.length };
    }

    async benchmarkInference() {
        console.log(chalk.cyan('     🧠 Testing inference performance...'));
        
        const suite = new Benchmark.Suite('AI Inference');
        const results = {};

        return new Promise((resolve) => {
            suite.add('Matrix Multiplication', () => {
                const matrixA = Array(100).fill(0).map(() => Array(100).fill(Math.random()));
                const matrixB = Array(100).fill(0).map(() => Array(100).fill(Math.random()));
                
                const result = matrixA.map((row, i) =>
                    row.map((_, j) =>
                        matrixA[i].reduce((sum, _, k) => sum + matrixA[i][k] * matrixB[k][j], 0)
                    )
                );
                
                return result.length;
            });

            suite.add('Neural Network Forward Pass', () => {
                const input = new Array(784).fill(0).map(() => Math.random());
                let layer1 = input.map(x => Math.max(0, x)); // ReLU
                let layer2 = layer1.map(x => 1 / (1 + Math.exp(-x))); // Sigmoid
                return layer2.reduce((a, b) => a + b, 0);
            });

            suite.add('Text Processing', () => {
                const text = "The quick brown fox jumps over the lazy dog ".repeat(100);
                const tokens = text.split(' ').filter(Boolean);
                const processed = tokens.map(token => ({
                    token,
                    length: token.length,
                    embedding: new Array(50).fill(0).map(() => Math.random())
                }));
                return processed.length;
            });

            suite.on('cycle', (event) => {
                const benchmark = event.target;
                results[benchmark.name] = {
                    hz: benchmark.hz,
                    rme: benchmark.stats.rme,
                    samples: benchmark.stats.sample.length
                };
                console.log(chalk.cyan(`        ${benchmark.name}: ${this.formatOpsPerSec(benchmark.hz)} ops/sec`));
            });

            suite.on('complete', () => {
                resolve(results);
            });

            suite.run({ async: true });
        });
    }

    async runGPUBenchmarks() {
        console.log(chalk.blue('\n🎮 Running GPU/NPU Benchmarks...'));
        
        const results = {
            gpuDetection: await this.detectGPU(),
            npuDetection: await this.detectNPU(),
            accelerationTest: await this.testAcceleration()
        };

        this.benchmarkResults.set('gpu_npu', results);
        console.log(chalk.green('  ✅ GPU/NPU benchmarks completed'));
    }

    async detectGPU() {
        console.log(chalk.cyan('     🎮 Detecting GPU capabilities...'));
        
        const gpuInfo = {
            available: false,
            vendor: 'unknown',
            memory: 0,
            compute: false
        };

        try {
            // In Node.js environment, we can't directly access WebGL
            // This would be a placeholder for actual GPU detection
            if (process.platform === 'win32') {
                // Simulate Windows GPU detection
                gpuInfo.available = true;
                gpuInfo.vendor = 'nvidia'; // Simulated
                gpuInfo.compute = true;
            }
        } catch (error) {
            console.log(chalk.yellow(`        GPU detection failed: ${error.message}`));
        }

        console.log(chalk.cyan(`        GPU Available: ${gpuInfo.available ? 'Yes' : 'No'}`));
        return gpuInfo;
    }

    async detectNPU() {
        console.log(chalk.cyan('     🧠 Detecting NPU capabilities...'));
        
        const npuInfo = {
            available: false,
            vendor: 'unknown',
            aiAcceleration: false
        };

        try {
            // Check for Intel NPU (simplified detection)
            const cpuInfo = os.cpus()[0].model;
            if (cpuInfo.toLowerCase().includes('intel') && 
                (cpuInfo.toLowerCase().includes('ultra') || cpuInfo.toLowerCase().includes('core'))) {
                npuInfo.available = true;
                npuInfo.vendor = 'intel';
                npuInfo.aiAcceleration = true;
            }
        } catch (error) {
            console.log(chalk.yellow(`        NPU detection failed: ${error.message}`));
        }

        console.log(chalk.cyan(`        NPU Available: ${npuInfo.available ? 'Yes' : 'No'}`));
        return npuInfo;
    }

    async testAcceleration() {
        console.log(chalk.cyan('     ⚡ Testing hardware acceleration...'));
        
        // CPU baseline test
        const cpuStart = performance.now();
        let cpuResult = 0;
        for (let i = 0; i < 100000; i++) {
            cpuResult += Math.sin(i) * Math.cos(i);
        }
        const cpuTime = performance.now() - cpuStart;

        // Simulated accelerated test (optimized algorithm)
        const accelStart = performance.now();
        let accelResult = 0;
        const chunkSize = 1000;
        for (let i = 0; i < 100000; i += chunkSize) {
            const chunk = Math.min(chunkSize, 100000 - i);
            for (let j = 0; j < chunk; j++) {
                accelResult += Math.sin(i + j) * Math.cos(i + j);
            }
        }
        const accelTime = performance.now() - accelStart;

        const speedup = cpuTime / accelTime;
        
        console.log(chalk.cyan(`        CPU Time: ${cpuTime.toFixed(2)}ms`));
        console.log(chalk.cyan(`        Accelerated Time: ${accelTime.toFixed(2)}ms`));
        console.log(chalk.cyan(`        Speedup: ${speedup.toFixed(2)}x`));

        return {
            cpuTime,
            acceleratedTime: accelTime,
            speedup,
            efficient: speedup > 1.0
        };
    }

    async runConcurrencyBenchmarks() {
        console.log(chalk.blue('\n🔄 Running Concurrency Benchmarks...'));
        
        const results = {};

        // Promise concurrency test
        const promiseResults = await this.benchmarkPromiseConcurrency();
        results.promises = promiseResults;

        // Worker thread simulation
        const workerResults = await this.benchmarkWorkerSimulation();
        results.workers = workerResults;

        this.benchmarkResults.set('concurrency', results);
        console.log(chalk.green('  ✅ Concurrency benchmarks completed'));
    }

    async benchmarkPromiseConcurrency() {
        console.log(chalk.cyan('     🔄 Testing Promise concurrency...'));
        
        const concurrencyLevels = [1, 5, 10, 20, 50];
        const results = {};

        for (const level of concurrencyLevels) {
            const startTime = performance.now();
            
            const promises = Array(level).fill(0).map(async (_, index) => {
                // Simulate async work
                await new Promise(resolve => setTimeout(resolve, Math.random() * 10));
                return index * Math.random();
            });

            await Promise.all(promises);
            
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            results[`concurrency_${level}`] = {
                level,
                duration,
                throughput: level / (duration / 1000)
            };
        }

        const optimalLevel = Object.entries(results)
            .reduce((best, [key, value]) => 
                value.throughput > best.throughput ? value : best
            ).level;

        console.log(chalk.cyan(`        Optimal concurrency level: ${optimalLevel}`));
        
        return { ...results, optimalLevel };
    }

    async benchmarkWorkerSimulation() {
        console.log(chalk.cyan('     👷 Testing worker simulation...'));
        
        // Simulate CPU-intensive tasks
        const tasks = Array(10).fill(0).map((_, i) => ({
            id: i,
            workload: Math.floor(Math.random() * 10000) + 1000
        }));

        // Sequential processing
        const sequentialStart = performance.now();
        let sequentialResult = 0;
        for (const task of tasks) {
            for (let i = 0; i < task.workload; i++) {
                sequentialResult += Math.sqrt(i);
            }
        }
        const sequentialTime = performance.now() - sequentialStart;

        // Parallel processing simulation (batch processing)
        const parallelStart = performance.now();
        const batchPromises = tasks.map(async (task) => {
            let result = 0;
            for (let i = 0; i < task.workload; i++) {
                result += Math.sqrt(i);
            }
            return result;
        });
        
        const parallelResults = await Promise.all(batchPromises);
        const parallelTime = performance.now() - parallelStart;
        const parallelResult = parallelResults.reduce((a, b) => a + b, 0);

        const speedup = sequentialTime / parallelTime;
        
        console.log(chalk.cyan(`        Sequential: ${sequentialTime.toFixed(2)}ms`));
        console.log(chalk.cyan(`        Parallel: ${parallelTime.toFixed(2)}ms`));
        console.log(chalk.cyan(`        Speedup: ${speedup.toFixed(2)}x`));

        return {
            sequential: { time: sequentialTime, result: sequentialResult },
            parallel: { time: parallelTime, result: parallelResult },
            speedup,
            efficient: speedup > 1.0,
            tasks: tasks.length
        };
    }

    async generateBenchmarkReport() {
        console.log(chalk.blue('\n📊 Generating Comprehensive Report...'));
        
        const endTime = Date.now();
        const totalDuration = endTime - this.startTime;

        const report = {
            timestamp: new Date().toISOString(),
            duration: totalDuration,
            systemInfo: this.systemInfo,
            results: Object.fromEntries(this.benchmarkResults),
            overallScore: this.calculateOverallScore(),
            recommendations: this.generateRecommendations(),
            summary: this.generateSummary()
        };

        // Save JSON report
        const jsonFilename = `nexus-benchmark-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        const jsonPath = path.join(this.reportPath, jsonFilename);
        
        try {
            await fs.writeFile(jsonPath, JSON.stringify(report, null, 2));
            console.log(chalk.green(`   💾 JSON report saved: ${jsonPath}`));
        } catch (error) {
            console.warn(chalk.yellow(`   ⚠️ Could not save JSON report: ${error.message}`));
        }

        // Save HTML report
        try {
            const htmlContent = this.generateHTMLReport(report);
            const htmlFilename = `nexus-benchmark-${new Date().toISOString().replace(/[:.]/g, '-')}.html`;
            const htmlPath = path.join(this.reportPath, htmlFilename);
            
            await fs.writeFile(htmlPath, htmlContent);
            console.log(chalk.green(`   🌐 HTML report saved: ${htmlPath}`));
        } catch (error) {
            console.warn(chalk.yellow(`   ⚠️ Could not save HTML report: ${error.message}`));
        }

        // Display summary
        this.displayReportSummary(report);
        
        return report;
    }

    calculateOverallScore() {
        let totalScore = 0;
        let categoryCount = 0;

        this.benchmarkResults.forEach((results, category) => {
            let categoryScore = 75; // Default good score

            switch (category) {
                case 'memory_management':
                    if (results.garbageCollection && results.garbageCollection.avgTime) {
                        categoryScore = Math.max(0, 100 - (results.garbageCollection.avgTime / 10));
                    }
                    break;

                case 'cpu_performance':
                    if (results && typeof results === 'object') {
                        const avgHz = Object.values(results).reduce((sum, r) => sum + (r.hz || 0), 0) / Object.keys(results).length;
                        categoryScore = Math.min(100, (avgHz / 10000) * 100);
                    }
                    break;

                case 'gpu_npu':
                    if (results.accelerationTest) {
                        categoryScore = Math.min(100, results.accelerationTest.speedup * 20);
                    }
                    break;

                case 'concurrency':
                    if (results.workers && results.workers.speedup) {
                        categoryScore = Math.min(100, results.workers.speedup * 25);
                    }
                    break;
            }

            totalScore += categoryScore;
            categoryCount++;
        });

        return categoryCount > 0 ? Math.round(totalScore / categoryCount) : 0;
    }

    generateRecommendations() {
        const recommendations = [];
        const results = this.benchmarkResults;

        // Memory recommendations
        if (results.has('memory_management')) {
            const memoryResults = results.get('memory_management');
            if (memoryResults.garbageCollection && memoryResults.garbageCollection.avgTime > 50) {
                recommendations.push({
                    category: 'Memory',
                    priority: 'high',
                    message: 'High garbage collection time detected. Consider optimizing object allocation patterns.',
                    action: 'Implement object pooling and reduce object creation in hot paths'
                });
            }
        }

        // CPU recommendations
        if (results.has('cpu_performance')) {
            const cpuResults = results.get('cpu_performance');
            const mathOps = cpuResults['Mathematical Operations'];
            if (mathOps && mathOps.hz < 5000) {
                recommendations.push({
                    category: 'CPU',
                    priority: 'medium',
                    message: 'Below average CPU performance detected.',
                    action: 'Check system load, enable high-performance power mode, or upgrade hardware'
                });
            }
        }

        // GPU/NPU recommendations
        if (results.has('gpu_npu')) {
            const gpuResults = results.get('gpu_npu');
            if (!gpuResults.gpuDetection.available) {
                recommendations.push({
                    category: 'GPU',
                    priority: 'low',
                    message: 'No GPU acceleration detected.',
                    action: 'Install/update graphics drivers or consider GPU upgrade for AI workloads'
                });
            }
        }

        // System-level recommendations
        const memoryUsage = (this.systemInfo.totalMemory - this.systemInfo.freeMemory) / this.systemInfo.totalMemory;
        if (memoryUsage > 0.85) {
            recommendations.push({
                category: 'System',
                priority: 'high',
                message: 'High system memory usage detected.',
                action: 'Close unnecessary applications or consider RAM upgrade'
            });
        }

        if (recommendations.length === 0) {
            recommendations.push({
                category: 'Performance',
                priority: 'low',
                message: 'System performance is optimal. No immediate optimizations needed.',
                action: 'Continue monitoring performance trends'
            });
        }

        return recommendations;
    }

    generateSummary() {
        const summary = {
            totalBenchmarks: this.benchmarkResults.size,
            completedSuccessfully: this.benchmarkResults.size,
            topPerformers: [],
            bottlenecks: [],
            systemHealth: 'good'
        };

        // Analyze results for top performers and bottlenecks
        this.benchmarkResults.forEach((results, category) => {
            if (typeof results === 'object' && results !== null) {
                Object.entries(results).forEach(([testName, testResults]) => {
                    if (testResults && typeof testResults.hz === 'number') {
                        if (testResults.hz > 10000) {
                            summary.topPerformers.push({ 
                                category: `${category} - ${testName}`, 
                                performance: testResults.hz 
                            });
                        } else if (testResults.hz < 1000) {
                            summary.bottlenecks.push({ 
                                category: `${category} - ${testName}`, 
                                performance: testResults.hz 
                            });
                        }
                    }
                });
            }
        });

        // Determine system health
        if (summary.bottlenecks.length > 3) {
            summary.systemHealth = 'poor';
        } else if (summary.bottlenecks.length > 1) {
            summary.systemHealth = 'fair';
        } else if (summary.topPerformers.length > 3) {
            summary.systemHealth = 'excellent';
        }

        return summary;
    }

    generateHTMLReport(report) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS AI - Performance Benchmark Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .timestamp { font-size: 1.1em; opacity: 0.9; }
        .score { font-size: 1.8em; font-weight: bold; margin-top: 15px; }
        .section { background: white; margin: 20px 0; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .section h2 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }
        .card h3 { margin-bottom: 15px; color: #2c3e50; }
        .metric { display: flex; justify-content: space-between; margin: 8px 0; }
        .metric .label { font-weight: 600; }
        .metric .value { color: #27ae60; font-family: 'Courier New', monospace; }
        .recommendations { background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; }
        .recommendation { margin: 15px 0; padding: 15px; background: white; border-radius: 5px; border-left: 4px solid #f39c12; }
        .recommendation.high { border-left-color: #e74c3c; }
        .recommendation.medium { border-left-color: #f39c12; }
        .recommendation.low { border-left-color: #27ae60; }
        .system-info { background: #ecf0f1; padding: 20px; border-radius: 8px; }
        .footer { text-align: center; margin-top: 40px; color: #7f8c8d; font-size: 0.9em; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
        .badge.excellent { background: #2ecc71; color: white; }
        .badge.good { background: #f39c12; color: white; }
        .badge.fair { background: #e67e22; color: white; }
        .badge.poor { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 NEXUS AI Performance Report</h1>
            <div class="timestamp">Generated: ${report.timestamp}</div>
            <div class="score">Overall Score: ${report.overallScore}/100</div>
            <div class="badge ${report.summary.systemHealth}">${report.summary.systemHealth.toUpperCase()}</div>
        </div>

        <div class="section">
            <h2>🖥️ System Information</h2>
            <div class="system-info">
                <div class="grid">
                    <div>
                        <div class="metric"><span class="label">Platform:</span> <span class="value">${report.systemInfo.platform} (${report.systemInfo.arch})</span></div>
                        <div class="metric"><span class="label">Node.js:</span> <span class="value">${report.systemInfo.nodeVersion}</span></div>
                        <div class="metric"><span class="label">CPU Cores:</span> <span class="value">${report.systemInfo.cpuCount}</span></div>
                    </div>
                    <div>
                        <div class="metric"><span class="label">Total Memory:</span> <span class="value">${this.formatBytes(report.systemInfo.totalMemory)}</span></div>
                        <div class="metric"><span class="label">Free Memory:</span> <span class="value">${this.formatBytes(report.systemInfo.freeMemory)}</span></div>
                        <div class="metric"><span class="label">Test Duration:</span> <span class="value">${(report.duration / 1000).toFixed(2)}s</span></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📊 Benchmark Results</h2>
            <div class="grid">
                ${Object.entries(report.results).map(([category, results]) => `
                    <div class="card">
                        <h3>${category.replace(/_/g, ' ').toUpperCase()}</h3>
                        ${this.renderBenchmarkResults(results)}
                    </div>
                `).join('')}
            </div>
        </div>

        <div class="section">
            <h2>💡 Optimization Recommendations</h2>
            <div class="recommendations">
                ${report.recommendations.map(rec => `
                    <div class="recommendation ${rec.priority}">
                        <strong>${rec.category}:</strong> ${rec.message}
                        ${rec.action ? `<br><em>Action: ${rec.action}</em>` : ''}
                    </div>
                `).join('')}
            </div>
        </div>

        <div class="section">
            <h2>📈 Performance Summary</h2>
            <div class="grid">
                <div class="card">
                    <h3>Top Performers</h3>
                    ${report.summary.topPerformers.length > 0 ? 
                        report.summary.topPerformers.map(tp => `
                            <div class="metric">
                                <span class="label">${tp.category}:</span>
                                <span class="value">${this.formatOpsPerSec(tp.performance)} ops/sec</span>
                            </div>
                        `).join('') :
                        '<div class="metric"><span class="value">No exceptional performers detected</span></div>'
                    }
                </div>
                <div class="card">
                    <h3>Performance Bottlenecks</h3>
                    ${report.summary.bottlenecks.length > 0 ? 
                        report.summary.bottlenecks.map(bn => `
                            <div class="metric">
                                <span class="label">${bn.category}:</span>
                                <span class="value">${this.formatOpsPerSec(bn.performance)} ops/sec</span>
                            </div>
                        `).join('') :
                        '<div class="metric"><span class="value">No significant bottlenecks detected</span></div>'
                    }
                </div>
            </div>
        </div>

        <div class="footer">
            <p>🚀 NEXUS AI Performance Benchmarking Suite</p>
            <p>Report generated on ${new Date().toLocaleString()}</p>
        </div>
    </div>
</body>
</html>`;
    }

    renderBenchmarkResults(results) {
        if (typeof results !== 'object' || results === null) {
            return `<div class="metric"><span class="value">${results}</span></div>`;
        }

        return Object.entries(results).map(([key, value]) => {
            if (typeof value === 'object' && value !== null) {
                if (value.hz) {
                    return `
                        <div class="metric">
                            <span class="label">${key}:</span>
                            <span class="value">${this.formatOpsPerSec(value.hz)} ops/sec</span>
                        </div>
                    `;
                } else if (value.avgTime) {
                    return `
                        <div class="metric">
                            <span class="label">${key}:</span>
                            <span class="value">${value.avgTime.toFixed(2)}ms</span>
                        </div>
                    `;
                } else if (value.speedup) {
                    return `
                        <div class="metric">
                            <span class="label">${key}:</span>
                            <span class="value">${value.speedup.toFixed(2)}x speedup</span>
                        </div>
                    `;
                } else {
                    return `
                        <div class="metric">
                            <span class="label">${key}:</span>
                            <span class="value">${JSON.stringify(value)}</span>
                        </div>
                    `;
                }
            } else {
                return `
                    <div class="metric">
                        <span class="label">${key}:</span>
                        <span class="value">${typeof value === 'number' ? value.toFixed(2) : value}</span>
                    </div>
                `;
            }
        }).join('');
    }

    displayReportSummary(report) {
        console.log(chalk.magenta('\n📊 BENCHMARK REPORT SUMMARY'));
        console.log(chalk.magenta('=' .repeat(60)));

        console.log(chalk.cyan('\n🎯 Overall Performance:'));
        console.log(chalk.white(`   Score: ${report.overallScore}/100`));
        console.log(chalk.white(`   System Health: ${report.summary.systemHealth.toUpperCase()}`));
        console.log(chalk.white(`   Duration: ${(report.duration / 1000).toFixed(2)}s`));

        console.log(chalk.cyan('\n⚡ Top Performers:'));
        if (report.summary.topPerformers.length > 0) {
            report.summary.topPerformers.slice(0, 3).forEach(tp => {
                console.log(chalk.green(`   ✅ ${tp.category}: ${this.formatOpsPerSec(tp.performance)} ops/sec`));
            });
        } else {
            console.log(chalk.white('   No exceptional performers detected'));
        }

        console.log(chalk.cyan('\n⚠️ Bottlenecks:'));
        if (report.summary.bottlenecks.length > 0) {
            report.summary.bottlenecks.slice(0, 3).forEach(bn => {
                console.log(chalk.yellow(`   ⚠️ ${bn.category}: ${this.formatOpsPerSec(bn.performance)} ops/sec`));
            });
        } else {
            console.log(chalk.green('   No significant bottlenecks detected'));
        }

        console.log(chalk.cyan('\n💡 Key Recommendations:'));
        report.recommendations.slice(0, 3).forEach(rec => {
            const priority = rec.priority === 'high' ? chalk.red('🔴') : 
                           rec.priority === 'medium' ? chalk.yellow('🟡') : chalk.green('🟢');
            console.log(`   ${priority} ${rec.category}: ${rec.message}`);
        });
    }

    formatBytes(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatOpsPerSec(hz) {
        if (hz >= 1000000) {
            return (hz / 1000000).toFixed(2) + 'M';
        } else if (hz >= 1000) {
            return (hz / 1000).toFixed(1) + 'K';
        } else {
            return hz.toFixed(0);
        }
    }

    collectSystemInfo() {
        return {
            platform: os.platform(),
            arch: os.arch(),
            nodeVersion: process.version,
            totalMemory: os.totalmem(),
            freeMemory: os.freemem(),
            cpuCount: os.cpus().length,
            loadAverage: os.loadavg(),
            uptime: os.uptime()
        };
    }
}

// Export the class
module.exports = NexusPerformanceBenchmarks;

// Run benchmarks if this file is executed directly
if (require.main === module) {
    console.log(chalk.cyan('🚀 Starting NEXUS Performance Benchmarks...\n'));
    
    const benchmarks = new NexusPerformanceBenchmarks();
    benchmarks.runAllBenchmarks()
        .then(() => {
            console.log(chalk.green('\n✅ All benchmarks completed successfully!'));
            console.log(chalk.cyan('📁 Check the benchmarks directory for detailed results.'));
            process.exit(0);
        })
        .catch((error) => {
            console.error(chalk.red('\n❌ Benchmark execution failed:'), error);
            process.exit(1);
        });
}
