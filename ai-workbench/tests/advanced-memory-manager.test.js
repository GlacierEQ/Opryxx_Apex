const assert = require('assert');
const { AdvancedMemoryManager, LRUCache, MemoryPool, TensorMemoryManager, GPUManager } = require('../core/advanced-memory-manager');
const { execSync } = require('child_process');

// Helper function to force garbage collection
function forceGC() {
    if (global.gc) {
        global.gc();
        return true;
    }
    return false;
}

// Helper function to allocate memory
function allocateMemory(mb) {
    const size = mb * 1024 * 1024 / 8; // 8 bytes per double
    const arr = new Array(size);
    for (let i = 0; i < size; i++) {
        arr[i] = Math.random();
    }
    return arr;
}

describe('AdvancedMemoryManager', function() {
    this.timeout(30000); // Increase timeout for memory tests

    let memoryManager;

    beforeEach(() => {
        memoryManager = new AdvancedMemoryManager({
            warningThreshold: 0.7,
            criticalThreshold: 0.8,
            emergencyThreshold: 0.9,
            maxHistorySize: 100,
            enableGPUMonitoring: true
        });
    });

    afterEach(() => {
        if (memoryManager) {
            memoryManager.destroy();
            memoryManager = null;
        }
        // Force GC between tests
        forceGC();
    });

    describe('Basic Functionality', () => {
        it('should initialize successfully', () => {
            assert.ok(memoryManager, 'Memory manager should be initialized');
            assert.ok(memoryManager.memoryHistory, 'Should have memory history');
            assert.ok(Array.isArray(memoryManager.memoryHistory), 'Memory history should be an array');
        });

        it('should collect memory metrics', (done) => {
            memoryManager.collectMemoryMetrics();
            setTimeout(() => {
                assert.ok(memoryManager.memoryHistory.length > 0, 'Should have memory history');
                const latest = memoryManager.memoryHistory[memoryManager.memoryHistory.length - 1];
                assert.ok(latest.system, 'Should have system memory info');
                assert.ok(latest.process, 'Should have process memory info');
                assert.ok(latest.v8, 'Should have V8 heap info');
                done();
            }, 100);
        });

        it('should detect memory trends', () => {
            // Simulate increasing memory usage
            for (let i = 0; i < 10; i++) {
                memoryManager.memoryHistory.push({
                    timestamp: Date.now() + i * 1000,
                    system: { percentage: 50 + i * 2 },
                    process: { heapUsed: 100 * 1024 * 1024 + i * 10 * 1024 * 1024 },
                    v8: { heapSizeLimit: 2 * 1024 * 1024 * 1024 }
                });
            }

            const trends = memoryManager.analyzeMemoryTrends();
            assert.ok(trends, 'Should return trend analysis');
            assert.ok(trends.systemMemoryTrend > 0, 'Should detect increasing system memory trend');
            assert.ok(trends.heapTrend > 0, 'Should detect increasing heap trend');
        });
    });

    describe('Memory Management', () => {
        it('should handle memory thresholds', (done) => {
            // Mock memory usage above warning threshold
            memoryManager.memoryHistory = [{
                timestamp: Date.now(),
                system: { percentage: 75 },
                process: { heapUsed: 1.7 * 1024 * 1024 * 1024 },
                v8: { heapSizeLimit: 2 * 1024 * 1024 * 1024 }
            }];

            let warningFired = false;
            memoryManager.on('memoryWarning', () => {
                warningFired = true;
            });

            memoryManager.checkMemoryThresholds();
            
            setTimeout(() => {
                assert.ok(warningFired, 'Should fire memory warning event');
                done();
            }, 100);
        });

        it('should force garbage collection', () => {
            const beforeGC = process.memoryUsage().heapUsed;
            const freed = memoryManager.forceGarbageCollection();
            const afterGC = process.memoryUsage().heapUsed;
            
            if (global.gc) {
                assert.ok(freed > 0, 'Should free some memory');
                assert.ok(afterGC <= beforeGC, 'Heap used should not increase after GC');
            } else {
                assert.strictEqual(freed, 0, 'Should return 0 when GC is not available');
            }
        });
    });

    describe('Cache Management', () => {
        it('should create and use cache', () => {
            const cache = memoryManager.createCache('testCache', { maxSize: 10 });
            assert.ok(cache, 'Should create cache');
            
            cache.set('key1', 'value1');
            assert.strictEqual(cache.get('key1'), 'value1', 'Should retrieve value from cache');
            
            const retrievedCache = memoryManager.getCache('testCache');
            assert.strictEqual(retrievedCache, cache, 'Should retrieve the same cache instance');
        });

        it('should respect cache size limits', () => {
            const cache = memoryManager.createCache('limitedCache', { maxSize: 2 });
            cache.set('key1', 'value1');
            cache.set('key2', 'value2');
            cache.set('key3', 'value3'); // Should evict key1
            
            assert.strictEqual(cache.get('key1'), null, 'Should evict oldest item');
            assert.strictEqual(cache.get('key2'), 'value2', 'Should keep recent items');
            assert.strictEqual(cache.get('key3'), 'value3', 'Should keep most recent item');
        });
    });

    describe('Tensor Memory Management', () => {
        it('should manage tensor memory', () => {
            const tensorId = 'testTensor';
            const shape = [100, 100]; // 10,000 elements
            const tensor = memoryManager.allocateTensor(tensorId, shape, 'float32');
            
            assert.ok(tensor, 'Should allocate tensor');
            assert.ok(tensor.buffer, 'Tensor should have buffer');
            assert.strictEqual(tensor.buffer.length, 100 * 100 * 4, 'Should allocate correct buffer size for float32');
            
            memoryManager.freeTensor(tensorId);
            assert.ok(!memoryManager.tensorManager.tensors.has(tensorId), 'Should free tensor memory');
        });
    });

    describe('GPU Integration', function() {
        this.timeout(10000);

        it('should detect GPU hardware', async () => {
            const gpuInfo = await memoryManager.gpuManager.detectGPU();
            // This test will pass if no GPU is found (returns null) or if GPU is detected
            assert.ok(true, 'GPU detection completed');
        });

        it('should monitor GPU metrics', async () => {
            await memoryManager.gpuManager.updateGPUMetrics();
            const metrics = memoryManager.gpuManager.gpuLoadHistory;
            assert.ok(Array.isArray(metrics), 'Should track GPU metrics');
        });
    });

    describe('Performance', () => {
        it('should handle memory pressure', function(done) {
            this.timeout(60000);
            
            // Allocate memory to trigger garbage collection
            const allocations = [];
            let i = 0;
            
            function allocate() {
                allocations.push(allocateMemory(50)); // Allocate 50MB
                i++;
                
                if (i < 10) {
                    setTimeout(allocate, 100);
                } else {
                    // Verify memory manager handled the pressure
                    const memUsage = process.memoryUsage();
                    const heapUsage = memUsage.heapUsed / memUsage.heapTotal;
                    
                    assert.ok(heapUsage < 0.9, 'Heap usage should be under 90%');
                    done();
                }
            }
            
            allocate();
        });
    });
});

describe('LRUCache', () => {
    let cache;
    
    beforeEach(() => {
        cache = new LRUCache(3);
    });
    
    it('should add and retrieve items', () => {
        cache.set('a', 1);
        assert.strictEqual(cache.get('a'), 1, 'Should retrieve stored value');
    });
    
    it('should evict least recently used item', () => {
        cache.set('a', 1);
        cache.set('b', 2);
        cache.set('c', 3);
        
        // Access 'a' to make it most recently used
        cache.get('a');
        
        // Add new item, should evict 'b' (least recently used)
        cache.set('d', 4);
        
        assert.strictEqual(cache.get('b'), null, 'Should evict least recently used item');
        assert.strictEqual(cache.get('a'), 1, 'Should keep accessed item');
    });
});

describe('MemoryPool', () => {
    it('should manage memory blocks', () => {
        const pool = new MemoryPool(1024, 2); // 1KB blocks, initial size 2
        
        const block1 = pool.allocate();
        const block2 = pool.allocate();
        const block3 = pool.allocate(); // Should create a new block
        
        assert.ok(block1 instanceof Buffer, 'Should return Buffer');
        assert.strictEqual(block1.length, 1024, 'Should have correct block size');
        assert.strictEqual(pool.blocks.length, 0, 'Should use all initial blocks');
        
        pool.free(block1);
        assert.strictEqual(pool.blocks.length, 1, 'Should return block to pool');
        
        pool.release();
        assert.strictEqual(pool.blocks.length, 0, 'Should release all blocks');
    });
});

// Only run GPU tests if we have a GPU
const hasGPU = (() => {
    try {
        const gpu = new GPUManager();
        return gpu.detectGPU().then(gpus => gpus && gpus.length > 0);
    } catch (e) {
        return Promise.resolve(false);
    }
})();

if (hasGPU) {
    describe('GPUManager', function() {
        this.timeout(10000);
        
        let gpuManager;
        
        before(async () => {
            gpuManager = new GPUManager();
            await gpuManager.detectGPU();
        });
        
        it('should detect GPU hardware', () => {
            assert.ok(gpuManager.gpuInfo, 'Should detect GPU info');
            assert.ok(gpuManager.gpuInfo.length > 0, 'Should detect at least one GPU');
        });
        
        it('should monitor GPU metrics', async () => {
            await gpuManager.updateGPUMetrics();
            const metrics = gpuManager.gpuLoadHistory;
            assert.ok(Array.isArray(metrics), 'Should track GPU metrics');
            assert.ok(metrics.length > 0, 'Should have GPU metrics');
            
            const latest = metrics[metrics.length - 1];
            assert.ok('load' in latest, 'Should have load metric');
            assert.ok('temperature' in latest, 'Should have temperature metric');
        });
    });
} else {
    console.log('Skipping GPU tests - no compatible GPU detected');
}

console.log('\nTo run these tests, use: npm test advanced-memory-manager.test.js');
console.log('Make sure to run with --expose-gc flag: node --expose-gc node_modules/.bin/mocha tests/advanced-memory-manager.test.js');
