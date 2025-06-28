const { OpenAI } = require('openai');
const { Anthropic } = require('@anthropic-ai/sdk');

class AIBrain {
    constructor() {
        this.models = {
            reasoning: null,
            coding: null,
            analysis: null,
            optimization: null
        };

        this.knowledgeBase = new Map();
        this.learningHistory = [];
        this.contextMemory = new Map();

        this.init();
    }

    async init() {
        console.log('🧠 Initializing AI Brain...');

        // Try to initialize available AI models
        await this.initializeModels();

        // Load existing knowledge
        await this.loadKnowledgeBase();

        // Start continuous learning
        this.startContinuousLearning();
    }

    async initializeModels() {
        // Check for local models first (Ollama)
        try {
            const { execSync } = require('child_process');
            const models = execSync('ollama list', { encoding: 'utf8' });
            if (models.includes('codellama') || models.includes('llama2')) {
                this.models.coding = new LocalLLM('codellama');
                console.log('✅ Local coding model initialized');
            }
        } catch (e) {
            console.log('⚠️ No local models found, using built-in intelligence');
        }

        // Initialize built-in intelligence systems
        this.models.reasoning = new ReasoningEngine();
        this.models.analysis = new AnalysisEngine();
        this.models.optimization = new OptimizationEngine();
    }

    async think(prompt, context = {}) {
        const startTime = Date.now();

        // Analyze the prompt to determine best approach
        const analysis = this.analyzePrompt(prompt, context);

        // Select appropriate model/engine
        const engine = this.selectEngine(analysis);

        // Generate response with context
        const response = await engine.process(prompt, {
            ...context,
            systemState: await this.getSystemState(),
            history: this.getRelevantHistory(prompt),
            timestamp: Date.now()
        });

        // Learn from this interaction
        await this.learn(prompt, response, context);

        const thinkingTime = Date.now() - startTime;

        return {
            response,
            confidence: response.confidence || 0.8,
            thinkingTime,
            engine: engine.name,
            analysis
        };
    }

    analyzePrompt(prompt, context) {
        const analysis = {
            type: 'general',
            complexity: 'medium',
            domains: [],
            urgency: 'normal',
            requiresAction: false
        };

        // Pattern matching
        const patterns = {
            system: /system|performance|memory|cpu|disk|optimize/i,
            code: /code|script|function|debug|implement|fix/i,
            analysis: /analyze|examine|investigate|understand|explain/i,
            problem: /problem|issue|error|broken|not working/i,
            urgent: /urgent|critical|emergency|immediately|asap/i
        };

        Object.entries(patterns).forEach(([domain, pattern]) => {
            if (pattern.test(prompt)) {
                analysis.domains.push(domain);
                if (domain === 'urgent') analysis.urgency = 'high';
            }
        });

        // Determine complexity
        if (prompt.length > 200 || analysis.domains.length > 2) {
            analysis.complexity = 'high';
        }

        return analysis;
    }

    selectEngine(analysis) {
        if (analysis.domains.includes('system')) {
            return this.models.analysis;
        }
        if (analysis.domains.includes('code')) {
            return this.models.coding || this.models.reasoning;
        }
        if (analysis.domains.includes('problem')) {
            return this.models.reasoning;
        }

        return this.models.reasoning; // Default
    }

    async getSystemState() {
        const os = require('os');
        return {
            memory: {
                total: os.totalmem(),
                free: os.freemem(),
                usage: ((os.totalmem() - os.freemem()) / os.totalmem()) * 100
            },
            cpu: {
                cores: os.cpus().length,
                load: os.loadavg()[0],
                usage: await this.getCPUUsage()
            },
            uptime: os.uptime(),
            processes: await this.getProcessCount()
        };
    }

    async getCPUUsage() {
        // Simple CPU usage calculation
        return new Promise((resolve) => {
            const startUsage = process.cpuUsage();
            setTimeout(() => {
                const endUsage = process.cpuUsage(startUsage);
                const usage = (endUsage.user + endUsage.system) / 1000000; // Convert to seconds
                resolve(Math.min(100, usage * 100));
            }, 100);
        });
    }

    async getProcessCount() {
        try {
            const { execSync } = require('child_process');
            const processes = execSync('tasklist /fo csv', { encoding: 'utf8' });
            return processes.split('\n').length - 2;
        } catch {
            return 0;
        }
    }

    getRelevantHistory(prompt) {
        // Find relevant past interactions
        return this.learningHistory
            .filter(item => this.calculateSimilarity(prompt, item.prompt) > 0.3)
            .slice(-5); // Last 5 relevant interactions
    }

    calculateSimilarity(text1, text2) {
        // Simple similarity calculation
        const words1 = text1.toLowerCase().split(/\s+/);
        const words2 = text2.toLowerCase().split(/\s+/);
        const intersection = words1.filter(word => words2.includes(word));
        return intersection.length / Math.max(words1.length, words2.length);
    }

    async learn(prompt, response, context) {
        const learningEntry = {
            prompt,
            response,
            context,
            timestamp: Date.now(),
            effectiveness: await this.measureEffectiveness(response, context)
        };

        this.learningHistory.push(learningEntry);

        // Keep only last 1000 entries
        if (this.learningHistory.length > 1000) {
            this.learningHistory = this.learningHistory.slice(-1000);
        }

        // Update knowledge base
        await this.updateKnowledgeBase(learningEntry);
    }

    async measureEffectiveness(response, context) {
        // Measure how effective the response was
        // This could be enhanced with user feedback
        let effectiveness = 0.5;

        if (response.confidence > 0.8) effectiveness += 0.2;
        if (response.actionable) effectiveness += 0.2;
        if (context.systemImprovement) effectiveness += 0.3;

        return Math.min(1.0, effectiveness);
    }

    async loadKnowledgeBase() {
        const fs = require('fs');
        const knowledgePath = './ai-workbench/knowledge/knowledge-base.json';

        if (fs.existsSync(knowledgePath)) {
            try {
                const data = JSON.parse(fs.readFileSync(knowledgePath, 'utf8'));
                this.knowledgeBase = new Map(Object.entries(data));
                console.log(`📚 Loaded ${this.knowledgeBase.size} knowledge entries`);
            } catch (e) {
                console.log('⚠️ Failed to load knowledge base:', e.message);
            }
        }
    }

    async updateKnowledgeBase(learningEntry) {
        // Extract key insights from the learning entry
        const insights = this.extractInsights(learningEntry);

        insights.forEach(insight => {
            const existing = this.knowledgeBase.get(insight.key) || { count: 0, examples: [] };
            existing.count++;
            existing.examples.push({
                prompt: learningEntry.prompt,
                response: learningEntry.response,
                timestamp: learningEntry.timestamp
            });

            // Keep only top 5 examples
            existing.examples = existing.examples.slice(-5);

            this.knowledgeBase.set(insight.key, existing);
        });

        // Periodically save to disk
        if (Math.random() < 0.1) { // 10% chance
            await this.saveKnowledgeBase();
        }
    }

    extractInsights(learningEntry) {
        const insights = [];
        const { prompt, response } = learningEntry;

        // Extract key patterns
        const words = prompt.toLowerCase().split(/\s+/);
        const importantWords = words.filter(word =>
            word.length > 3 &&
            !['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'].includes(word)
        );

        importantWords.forEach(word => {
            insights.push({
                key: `word_${word}`,
                type: 'pattern',
                value: word
            });
        });

        return insights;
    }

    async saveKnowledgeBase() {
        const fs = require('fs');
        const knowledgePath = './ai-workbench/knowledge/knowledge-base.json';

        try {
            const data = Object.fromEntries(this.knowledgeBase);
            fs.writeFileSync(knowledgePath, JSON.stringify(data, null, 2));
            console.log('💾 Knowledge base saved');
        } catch (e) {
            console.log('⚠️ Failed to save knowledge base:', e.message);
        }
    }

    startContinuousLearning() {
        setInterval(async () => {
            await this.analyzeLearningPatterns();
            await this.optimizeKnowledge();
        }, 300000); // Every 5 minutes
    }

    async analyzeLearningPatterns() {
        // Analyze patterns in learning history
        const recentLearning = this.learningHistory.slice(-100);

        // Find common patterns
        const patterns = new Map();
        recentLearning.forEach(entry => {
            const key = this.categorizePrompt(entry.prompt);
            const existing = patterns.get(key) || { count: 0, avgEffectiveness: 0 };
            existing.count++;
            existing.avgEffectiveness = (existing.avgEffectiveness + entry.effectiveness) / 2;
            patterns.set(key, existing);
        });

        console.log('📊 Learning patterns:', Object.fromEntries(patterns));
    }

    categorizePrompt(prompt) {
        if (/system|performance/i.test(prompt)) return 'system';
        if (/code|script/i.test(prompt)) return 'coding';
        if (/problem|issue/i.test(prompt)) return 'problem-solving';
        return 'general';
    }

    async optimizeKnowledge() {
        // Remove low-value knowledge entries
        const threshold = 0.3;
        let removed = 0;

        for (const [key, value] of this.knowledgeBase.entries()) {
            if (value.count < 2 && Math.random() < 0.1) {
                this.knowledgeBase.delete(key);
                removed++;
            }
        }

        if (removed > 0) {
            console.log(`🧹 Optimized knowledge base: removed ${removed} low-value entries`);
        }
    }
}

// Specialized AI Engines
class ReasoningEngine {
    constructor() {
        this.name = 'ReasoningEngine';
    }

    async process(prompt, context) {
        // Advanced reasoning logic
        const steps = this.breakDownProblem(prompt);
        const analysis = await this.analyzeEachStep(steps, context);
        const solution = this.synthesizeSolution(analysis);

        return {
            reasoning: steps,
            analysis,
            solution,
            confidence: this.calculateConfidence(analysis),
            actionable: solution.actions && solution.actions.length > 0
        };
    }

    breakDownProblem(prompt) {
        // Break complex problems into steps
        return [
            'Understand the problem',
            'Gather relevant information',
            'Identify possible solutions',
            'Evaluate solutions',
            'Recommend best approach'
        ];
    }

    async analyzeEachStep(steps, context) {
        return steps.map(step => ({
            step,
            analysis: `Analyzing: ${step}`,
            relevantData: this.getRelevantData(step, context)
        }));
    }

    getRelevantData(step, context) {
        // Extract relevant data for each step
        return {
            systemState: context.systemState,
            timestamp: context.timestamp
        };
    }

    synthesizeSolution(analysis) {
        return {
            summary: 'Based on analysis, here is the recommended approach...',
            actions: [
                'Monitor system performance',
                'Implement optimizations',
                'Verify improvements'
            ],
            priority: 'medium'
        };
    }

    calculateConfidence(analysis) {
        return 0.75; // Base confidence
    }
}

class AnalysisEngine {
    constructor() {
        this.name = 'AnalysisEngine';
    }

    async process(prompt, context) {
        const systemAnalysis = await this.analyzeSystem(context.systemState);
        const insights = this.generateInsights(systemAnalysis);
        const recommendations = this.generateRecommendations(insights);

        return {
            systemAnalysis,
            insights,
            recommendations,
            confidence: 0.85,
            actionable: true
        };
    }

    async analyzeSystem(systemState) {
        return {
            memory: {
                status: systemState.memory.usage > 80 ? 'high' : 'normal',
                recommendation: systemState.memory.usage > 80 ? 'Consider freeing memory' : 'Memory usage is normal'
            },
            cpu: {
                status: systemState.cpu.load > 2 ? 'high' : 'normal',
                recommendation: systemState.cpu.load > 2 ? 'High CPU load detected' : 'CPU load is normal'
            }
        };
    }

    generateInsights(analysis) {
        const insights = [];

        if (analysis.memory.status === 'high') {
            insights.push('Memory usage is elevated and may impact performance');
        }

        if (analysis.cpu.status === 'high') {
            insights.push('CPU load is high, system may be under stress');
        }

        return insights;
    }

    generateRecommendations(insights) {
        if (!insights || insights.length === 0) {
            return ['No recommendations available. System is operating normally.'];
        }

        const recommendations = [];
        
        insights.forEach(insight => {
            if (insight.includes('high') && insight.includes('CPU')) {
                recommendations.push('Consider optimizing CPU-intensive operations or scaling up resources.');
            } else if (insight.includes('high') && insight.includes('memory')) {
                recommendations.push('Review memory usage and consider optimizing data structures or increasing memory allocation.');
            } else if (insight.includes('disk')) {
                recommendations.push('Check disk usage and clean up unnecessary files or consider increasing storage.');
            }
        });

        return recommendations.length > 0 
            ? recommendations 
            : ['No specific recommendations available. System is operating within normal parameters.'];
    }
}
