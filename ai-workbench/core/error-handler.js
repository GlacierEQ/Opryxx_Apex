const logger = require('./logger');
const { EventEmitter } = require('events');
const os = require('os');
const util = require('util');
const { performance } = require('perf_hooks');

// Custom error classes for better error handling
class SystemError extends Error {
    constructor(message, code, context = {}) {
        super(message);
        this.name = 'SystemError';
        this.code = code || 'SYSTEM_ERROR';
        this.context = context;
        this.isOperational = true;
        Error.captureStackTrace(this, this.constructor);
    }
}

class ResourceError extends SystemError {
    constructor(resource, context = {}) {
        super(`Resource error: ${resource}`, 'RESOURCE_ERROR', context);
        this.resource = resource;
    }
}

class NetworkError extends SystemError {
    constructor(url, status, context = {}) {
        super(`Network request failed: ${url} (${status})`, 'NETWORK_ERROR', context);
        this.url = url;
        this.status = status;
    }
}

class ValidationError extends SystemError {
    constructor(field, value, context = {}) {
        super(`Validation failed for field: ${field}`, 'VALIDATION_ERROR', context);
        this.field = field;
        this.value = value;
    }
}

class RateLimitError extends SystemError {
    constructor(limit, resetTime, context = {}) {
        super(`Rate limit exceeded. Resets at ${new Date(resetTime).toISOString()}`, 'RATE_LIMIT', context);
        this.limit = limit;
        this.resetTime = resetTime;
    }
}

class ErrorHandler extends EventEmitter {
    constructor(options = {}) {
        super();
        
        // Configuration
        this.config = {
            maxRetryAttempts: options.maxRetryAttempts || 3,
            retryDelay: options.retryDelay || 1000, // ms
            enableMetrics: options.enableMetrics !== false,
            logUnhandledRejections: options.logUnhandledRejections !== false,
            logUncaughtExceptions: options.logUncaughtExceptions !== false,
            notifyOnCritical: options.notifyOnCritical !== false,
            ...options
        };
        
        // State
        this.errorTypes = new Map();
        this.recoveryStrategies = new Map();
        this.retryCounters = new Map();
        this.metrics = {
            errors: new Map(),
            lastError: null,
            errorRate: 0,
            recoveryAttempts: 0,
            recoverySuccesses: 0
        };
        
        // Initialize
        this.setupErrorTypes();
        this.setupRecoveryStrategies();
        this.setupGlobalHandlers();
        
        // Start metrics collection if enabled
        if (this.config.enableMetrics) {
            this.setupMetricsCollection();
        }
        
        logger.info('Error handler initialized', { config: this.config });
    }

    setupErrorTypes() {
        // System Errors
        this.errorTypes.set('SystemError', {
            severity: 'critical',
            recoverable: true,
            notifyUser: true,
            retryable: true,
            maxRetries: 3,
            backoff: 'exponential',
            tags: ['system', 'critical']
        });

        // Resource Errors
        this.errorTypes.set('ResourceError', {
            severity: 'high',
            recoverable: true,
            notifyUser: true,
            retryable: true,
            maxRetries: 5,
            backoff: 'exponential',
            tags: ['resource', 'high']
        });

        // Network Errors
        this.errorTypes.set('NetworkError', {
            severity: 'high',
            recoverable: true,
            notifyUser: false,
            retryable: true,
            maxRetries: 3,
            backoff: 'exponential',
            tags: ['network', 'transient']
        });

        // Validation Errors
        this.errorTypes.set('ValidationError', {
            severity: 'medium',
            recoverable: false,
            notifyUser: true,
            retryable: false,
            tags: ['validation', 'client']
        });

        // Rate Limiting
        this.errorTypes.set('RateLimitError', {
            severity: 'medium',
            recoverable: true,
            notifyUser: false,
            retryable: true,
            maxRetries: 5,
            backoff: 'fixed',
            retryAfter: (error) => error.resetTime - Date.now(),
            tags: ['rate_limit', 'transient']
        });

        // AI/ML Errors
        this.errorTypes.set('AIModelError', {
            severity: 'high',
            recoverable: true,
            notifyUser: true,
            retryable: true,
            maxRetries: 2,
            backoff: 'linear',
            tags: ['ai', 'model', 'high']
        });

        // Cache Errors
        this.errorTypes.set('CacheError', {
            severity: 'low',
            recoverable: true,
            notifyUser: false,
            retryable: true,
            maxRetries: 3,
            backoff: 'exponential',
            tags: ['cache', 'performance']
        });

        // Database Errors
        this.errorTypes.set('DatabaseError', {
            severity: 'critical',
            recoverable: true,
            notifyUser: true,
            retryable: true,
            maxRetries: 3,
            backoff: 'exponential',
            tags: ['database', 'critical']
        });

        // Authentication/Authorization Errors
        this.errorTypes.set('AuthError', {
            severity: 'high',
            recoverable: false,
            notifyUser: true,
            retryable: false,
            tags: ['security', 'auth']
        });

        // Timeout Errors
        this.errorTypes.set('TimeoutError', {
            severity: 'medium',
            recoverable: true,
            notifyUser: false,
            retryable: true,
            maxRetries: 2,
            backoff: 'exponential',
            tags: ['timeout', 'transient']
        });

        // File System Errors
        this.errorTypes.set('FileSystemError', {
            severity: 'high',
            recoverable: true,
            notifyUser: true,
            retryable: true,
            maxRetries: 3,
            backoff: 'exponential',
            tags: ['filesystem', 'high']
        });
    }

    setupRecoveryStrategies() {
        // System Error Recovery
        this.recoveryStrategies.set('SystemError', async (error, context) => {
            const startTime = performance.now();
            const recoveryId = `sys_${Date.now()}`;
            logger.warn('Attempting system error recovery', { 
                recoveryId,
                error: error.message, 
                context,
                memoryUsage: process.memoryUsage()
            });

            try {
                // Try to free up resources
                if (global.gc) {
                    logger.debug('Running garbage collection', { recoveryId });
                    global.gc();
                }

                // Clear caches if memory is high
                const memUsage = process.memoryUsage();
                const heapRatio = memUsage.heapUsed / memUsage.heapTotal;
                
                if (heapRatio > 0.8) {
                    logger.warn('High memory usage detected, clearing caches', { 
                        recoveryId, 
                        heapRatio: heapRatio.toFixed(2) 
                    });
                    
                    // Clear require cache for non-core modules
                    this.clearModuleCaches(/node_modules/);
                    return { 
                        recovered: true, 
                        action: 'cleared_caches',
                        duration: performance.now() - startTime
                    };
                }
                
                // If we get here, recovery wasn't possible
                return { 
                    recovered: false, 
                    action: 'escalate',
                    reason: 'No recovery actions available',
                    duration: performance.now() - startTime
                };
            } catch (recoveryError) {
                logger.error('Error during system recovery', { 
                    recoveryId, 
                    error: recoveryError 
                });
                return { 
                    recovered: false, 
                    action: 'failed',
                    error: recoveryError.message,
                    duration: performance.now() - startTime
                };
            }
        });

        // AI Model Error Recovery
        this.recoveryStrategies.set('AIModelError', async (error, context) => {
            const recoveryId = `ai_${Date.now()}`;
            logger.warn('Attempting AI model error recovery', { 
                recoveryId,
                error: error.message, 
                context 
            });

            try {
                // Try fallback model if available
                if (context.fallbackModel) {
                    logger.info('Attempting fallback model', { 
                        recoveryId, 
                        fallbackModel: context.fallbackModel 
                    });
                    return { 
                        recovered: true, 
                        action: 'fallback_model', 
                        model: context.fallbackModel 
                    };
                }

                // Try reducing model parameters
                if (context.modelParams) {
                    logger.info('Reducing model parameters', { recoveryId });
                    const reducedParams = this.reduceModelParams(context.modelParams);
                    return { 
                        recovered: true, 
                        action: 'reduced_parameters',
                        params: reducedParams
                    };
                }
                
                // Last resort: disable AI temporarily
                return { 
                    recovered: false, 
                    action: 'disable_ai_temporarily',
                    reason: 'No recovery strategies available'
                };
            } catch (recoveryError) {
                logger.error('Error during AI model recovery', { 
                    recoveryId, 
                    error: recoveryError 
                });
                return { 
                    recovered: false, 
                    action: 'failed',
                    error: recoveryError.message
                };
            }
        });

        // Network Error Recovery
        this.recoveryStrategies.set('NetworkError', async (error, context) => {
            const recoveryId = `net_${Date.now()}`;
            const { url, status } = error;
            
            logger.warn('Attempting network error recovery', { 
                recoveryId,
                url,
                status,
                error: error.message 
            });

            try {
                // For rate limiting (429) or server errors (5xx), use backoff
                if (status === 429 || (status >= 500 && status < 600)) {
                    const retryAfter = this.calculateBackoff('exponential', context.retryCount || 0);
                    logger.info(`Retrying after ${retryAfter}ms`, { recoveryId, retryAfter });
                    
                    await new Promise(resolve => setTimeout(resolve, retryAfter));
                    return { 
                        recovered: true, 
                        action: 'retry',
                        retryAfter,
                        attempt: (context.retryCount || 0) + 1
                    };
                }
                
                // For 4xx client errors (except 429), don't retry
                return { 
                    recovered: false, 
                    action: 'do_not_retry',
                    reason: 'Client error, retry unlikely to help'
                };
            } catch (recoveryError) {
                logger.error('Error during network recovery', { 
                    recoveryId, 
                    error: recoveryError 
                });
                return { 
                    recovered: false, 
                    action: 'failed',
                    error: recoveryError.message
                };
            }
        });

        // Database Error Recovery
        this.recoveryStrategies.set('DatabaseError', async (error, context) => {
            const recoveryId = `db_${Date.now()}`;
            logger.warn('Attempting database error recovery', { 
                recoveryId,
                error: error.message,
                context
            });

            try {
                // Try to reconnect to database
                if (context.db && typeof context.db.reconnect === 'function') {
                    logger.info('Attempting database reconnection', { recoveryId });
                    await context.db.reconnect();
                    return { 
                        recovered: true, 
                        action: 'reconnected',
                        db: context.db.name
                    };
                }
                
                // If reconnection isn't possible, try failover
                if (context.failoverDb) {
                    logger.info('Failing over to secondary database', { recoveryId });
                    return { 
                        recovered: true, 
                        action: 'failover',
                        db: context.failoverDb.name
                    };
                }
                
                return { 
                    recovered: false, 
                    action: 'escalate',
                    reason: 'No recovery strategy available for database error'
                };
            } catch (recoveryError) {
                logger.error('Error during database recovery', { 
                    recoveryId, 
                    error: recoveryError 
                });
                return { 
                    recovered: false, 
                    action: 'failed',
                    error: recoveryError.message
                };
            }
        });

        // Cache Error Recovery
        this.recoveryStrategies.set('CacheError', async (error, context) => {
            const recoveryId = `cache_${Date.now()}`;
            logger.warn('Attempting cache error recovery', { 
                recoveryId,
                error: error.message,
                context
            });

            try {
                // Try to clear the cache
                if (context.cache && typeof context.cache.clear === 'function') {
                    logger.info('Clearing cache', { recoveryId });
                    await context.cache.clear();
                    return { 
                        recovered: true, 
                        action: 'cache_cleared'
                    };
                }
                
                // If cache is not available, continue without it
                logger.warn('Cache not available, continuing without cache', { recoveryId });
                return { 
                    recovered: true, 
                    action: 'cache_disabled',
                    warning: 'Cache is not available'
                };
            } catch (recoveryError) {
                logger.error('Error during cache recovery', { 
                    recoveryId, 
                    error: recoveryError 
                });
                return { 
                    recovered: false, 
                    action: 'failed',
                    error: recoveryError.message
                };
            }
        });
    }

    /**
     * Sets up periodic metrics collection for error tracking and system health monitoring
     */
    setupMetricsCollection() {
        const METRICS_INTERVAL = 60000; // 1 minute
        
        // Initial metrics collection
        this.collectAndReportMetrics();
        
        // Set up interval for periodic collection
        this.metricsInterval = setInterval(() => {
            this.collectAndReportMetrics();
        }, METRICS_INTERVAL);
        
        // Clean up on process exit
        process.on('exit', () => {
            if (this.metricsInterval) {
                clearInterval(this.metricsInterval);
            }
        });
        
        logger.info('Metrics collection started', { interval: `${METRICS_INTERVAL}ms` });
    }
    
    /**
     * Collects and reports system and error metrics
     * @private
     */
    collectAndReportMetrics() {
        try {
            const memUsage = process.memoryUsage();
            const load = os.loadavg();
            
            const metrics = {
                timestamp: new Date().toISOString(),
                memory: {
                    rss: memUsage.rss,
                    heapTotal: memUsage.heapTotal,
                    heapUsed: memUsage.heapUsed,
                    external: memUsage.external,
                    arrayBuffers: memUsage.arrayBuffers
                },
                cpu: {
                    load1: load[0],
                    load5: load[1],
                    load15: load[2],
                    cpus: os.cpus().length
                },
                errors: {
                    total: this.metrics.errors.size,
                    lastHour: Array.from(this.metrics.errors.values())
                        .filter(e => (Date.now() - e.timestamp) < 3600000).length,
                    byType: {}
                },
                recovery: {
                    attempts: this.metrics.recoveryAttempts,
                    successes: this.metrics.recoverySuccesses,
                    successRate: this.metrics.recoveryAttempts > 0 
                        ? (this.metrics.recoverySuccesses / this.metrics.recoveryAttempts) * 100 
                        : 0
                }
            };
            
            // Count errors by type
            this.metrics.errors.forEach((error, type) => {
                metrics.errors.byType[type] = (metrics.errors.byType[type] || 0) + 1;
            });
            
            // Emit metrics for external consumers
            this.emit('metrics', metrics);
            
            // Log summary
            if (this.config.enableMetricsLogging) {
                logger.info('System metrics', {
                    memory: `${(metrics.memory.heapUsed / 1024 / 1024).toFixed(2)}MB`,
                    cpuLoad: metrics.cpu.load1.toFixed(2),
                    errors: metrics.errors.total,
                    recoveryRate: `${metrics.recovery.successRate.toFixed(1)}%`
                });
            }
            
        } catch (error) {
            logger.error('Error collecting metrics', { error: error.message });
        }
    }

    /**
     * Clears Node.js module cache, optionally excluding certain modules
     * @param {RegExp} [excludePattern] - Pattern to match against module paths to exclude from clearing
     * @returns {Object} Result with cleared and kept module counts
     */
    clearModuleCaches(excludePattern) {
        const result = {
            cleared: 0,
            kept: 0,
            errors: 0,
            clearedModules: [],
            keptModules: []
        };
        
        try {
            // Get all cached modules
            const cache = require.cache;
            
            // Clear each module's cache
            Object.keys(cache).forEach(modulePath => {
                try {
                    // Skip if module matches exclude pattern
                    if (excludePattern && excludePattern.test(modulePath)) {
                        result.kept++;
                        result.keptModules.push(modulePath);
                        return;
                    }
                    
                    // Clear module from cache
                    delete cache[modulePath];
                    result.cleared++;
                    result.clearedModules.push(modulePath);
                    
                } catch (error) {
                    result.errors++;
                    logger.warn('Error clearing module cache', { 
                        module: modulePath, 
                        error: error.message 
                    });
                }
            });
            
            // Force garbage collection if available
            if (global.gc) {
                global.gc();
                logger.debug('Garbage collection triggered after module cache clear');
            }
            
            logger.info('Module caches cleared', result);
            return result;
            
        } catch (error) {
            logger.error('Failed to clear module caches', { error: error.message });
            throw error;
        }
    }

    /**
     * Reduces model parameters to lower resource usage
     * @param {Object} params - Current model parameters
     * @param {Object} [options] - Reduction options
     * @param {number} [options.factor=0.5] - Reduction factor (0-1)
     * @returns {Object} Reduced parameters
     */
    reduceModelParams(params, options = {}) {
        const { factor = 0.5 } = options;
        const reducedParams = { ...params };
        
        try {
            // Reduce batch size if present
            if (reducedParams.batchSize !== undefined) {
                reducedParams.batchSize = Math.max(1, Math.floor(reducedParams.batchSize * factor));
            }
            
            // Reduce max tokens if present
            if (reducedParams.maxTokens !== undefined) {
                reducedParams.maxTokens = Math.max(32, Math.floor(reducedParams.maxTokens * factor));
            }
            
            // Reduce temperature if present and above 0.1
            if (reducedParams.temperature !== undefined && reducedParams.temperature > 0.1) {
                reducedParams.temperature = Math.max(0.1, reducedParams.temperature * factor);
            }
            
            // Reduce top_p if present and above 0.1
            if (reducedParams.topP !== undefined && reducedParams.topP > 0.1) {
                reducedParams.topP = Math.max(0.1, reducedParams.topP * factor);
            }
            
            // Handle presence_penalty and frequency_penalty
            if (reducedParams.presencePenalty !== undefined) {
                reducedParams.presencePenalty = Math.min(2, reducedParams.presencePenalty * (1 + (1 - factor)));
            }
            
            if (reducedParams.frequencyPenalty !== undefined) {
                reducedParams.frequencyPenalty = Math.min(2, reducedParams.frequencyPenalty * (1 + (1 - factor)));
            }
            
            logger.info('Model parameters reduced', { 
                original: params, 
                reduced: reducedParams,
                factor 
            });
            
            return reducedParams;
            
        } catch (error) {
            logger.error('Error reducing model parameters', { 
                error: error.message,
                params: JSON.stringify(params),
                options 
            });
            // Return original params if reduction fails
            return params;
        }
    }

    /**
     * Calculates backoff time for retry attempts
     * @param {string} type - Type of backoff ('exponential', 'linear', 'fixed')
     * @param {number} attempt - Current attempt number (1-based)
     * @param {Object} [options] - Backoff options
     * @param {number} [options.baseDelay=1000] - Base delay in milliseconds
     * @param {number} [options.maxDelay=30000] - Maximum delay in milliseconds
     * @param {number} [options.jitter=0.2] - Jitter factor (0-1) to add randomness
     * @returns {number} Time to wait in milliseconds
     */
    calculateBackoff(type, attempt, options = {}) {
        const {
            baseDelay = 1000,
            maxDelay = 30000,
            jitter = 0.2
        } = options;
        
        // Ensure attempt is at least 1
        attempt = Math.max(1, attempt);
        
        let delay;
        
        switch (type.toLowerCase()) {
            case 'exponential':
                // Exponential backoff: baseDelay * 2^(attempt-1)
                delay = Math.min(maxDelay, baseDelay * Math.pow(2, attempt - 1));
                break;
                
            case 'linear':
                // Linear backoff: baseDelay * attempt
                delay = Math.min(maxDelay, baseDelay * attempt);
                break;
                
            case 'fixed':
            default:
                // Fixed backoff: always use baseDelay
                delay = Math.min(maxDelay, baseDelay);
                break;
        }
        
        // Add jitter to prevent thundering herd problem
        if (jitter > 0) {
            const jitterAmount = delay * jitter;
            const minJitter = delay - jitterAmount;
            const maxJitter = delay + jitterAmount;
            delay = minJitter + Math.random() * (maxJitter - minJitter);
        }
        
        // Ensure delay is within bounds
        delay = Math.max(0, Math.min(maxDelay, Math.floor(delay)));
        
        logger.debug('Calculated backoff', { 
            type, 
            attempt, 
            delay,
            baseDelay,
            maxDelay,
            jitter
        });
        
        return delay;
    }

    setupGlobalHandlers() {
        process.on('uncaughtException', (error) => {
            logger.error('Uncaught Exception', error);
            this.handleError(error, { isUncaught: true });
            
            // If it's a critical error, consider shutting down
            if (!this.errorTypes.get('SystemError')?.recoverable) {
                logger.fatal('Critical error detected, shutting down', { error: error.message });
                process.exit(1);
            }
        });

        process.on('unhandledRejection', (reason, promise) => {
            logger.error('Unhandled Rejection', { reason, promise: promise?.toString() });
            this.handleError(reason, { isUnhandledRejection: true });
        });
    }

    handleAsyncError(error) {
        const errorName = error.name || 'UnknownError';
        const errorMessage = error.message || 'No message provided';

        // Pattern matching to classify errors
        if (errorMessage.includes('ENOENT') || errorMessage.includes('file not found')) {
            return { type: 'FileSystemError', category: 'system' };
        }

        if (errorMessage.includes('memory') || errorMessage.includes('heap')) {
            return { type: 'MemoryError', category: 'system' };
        }

        if (errorMessage.includes('AI') || errorMessage.includes('model')) {
            return { type: 'AIModelError', category: 'ai' };
        }

        if (errorMessage.includes('cache')) {
            return { type: 'CacheError', category: 'performance' };
        }

        return { type: errorName, category: 'general' };
    }

    handleError(error, context = {}) {
        const errorInfo = this.analyzeError(error);
        const errorType = this.errorTypes.get(errorInfo.type) || this.errorTypes.get('SystemError');

        logger.error(`${errorInfo.type}: ${error.message}`, error, {
            context,
            severity: errorType.severity,
            recoverable: errorType.recoverable
        });

        // Attempt recovery if possible
        if (errorType.recoverable) {
            const recovery = this.attemptRecovery(error, errorInfo.type, context);
            if (recovery.recovered) {
                logger.info('Error recovery successful', {
                    errorType: errorInfo.type,
                    action: recovery.action
                });
                return { handled: true, recovery };
            }
        }

        // Notify user if required
        if (errorType.notifyUser) {
            this.notifyUser(error, errorInfo, context);
        }

        return { handled: false, errorInfo, errorType };
    }

    analyzeError(error) {
        const errorName = error.name || 'UnknownError';
        const errorMessage = error.message || 'No message provided';

        // Pattern matching to classify errors
        if (errorMessage.includes('ENOENT') || errorMessage.includes('file not found')) {
            return { type: 'FileSystemError', category: 'system' };
        }

        if (errorMessage.includes('memory') || errorMessage.includes('heap')) {
            return { type: 'MemoryError', category: 'system' };
        }

        if (errorMessage.includes('AI') || errorMessage.includes('model')) {
            return { type: 'AIModelError', category: 'ai' };
        }

        if (errorMessage.includes('cache')) {
            return { type: 'CacheError', category: 'performance' };
        }

        return { type: errorName, category: 'general' };
    }

    /**
     * Attempts to recover from an error based on its type
     * @param {Error} error - The error to recover from
     * @param {string} errorType - Type of the error
     * @param {Object} context - Additional context for recovery
     * @returns {Promise<Object>} Result of the recovery attempt
     */
    async attemptRecovery(error, errorType, context) {
        const strategy = this.recoveryStrategies.get(errorType);

        if (strategy) {
            try {
                return await strategy(error, context);
            } catch (recoveryError) {
                logger.error('Recovery strategy failed', recoveryError, {
                    originalError: error.message,
                    errorType
                });
                return { recovered: false, action: 'recovery_failed' };
            }
        }

        return { recovered: false, action: 'no_strategy' };
    }

    /**
     * Notifies users about important errors
     * @param {Error} error - The error that occurred
     * @param {Object} errorInfo - Analyzed error information
     * @param {Object} context - Additional context about the error
     */
    async notifyUser(error, errorInfo, context) {
        // In a real application, this might send notifications via various channels
        console.log(`🚨 User Notification: ${errorInfo.type} - ${error.message}`);

        // Could integrate with:
        // - Email notifications
        // - Slack/Discord webhooks
        // - Desktop notifications
        // - System tray alerts
    }

    handleCrit
