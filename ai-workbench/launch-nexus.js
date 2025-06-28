#!/usr/bin/env node

const figlet = require('figlet');
const chalk = require('chalk');
const inquirer = require('inquirer');

// Import all our amazing components
const AIBrain = require('./core/ai-brain');
const SystemMonitor = require('./monitors/system-monitor');
const DashboardServer = require('./server/websocket-server');
const GamingMode = require('./modes/gaming-mode');
const SmartNotificationSystem = require('./core/notification-system');
const logger = require('./core/logger');

class NexusLauncher {
    constructor() {
        this.components = {};
        this.isRunning = false;
    }

    async launch() {
        // Epic startup banner
        console.clear();
        console.log(chalk.cyan(figlet.textSync('NEXUS AI', {
            font: 'Big',
            horizontalLayout: 'default',
            verticalLayout: 'default'
        })));

        console.log(chalk.magenta('🚀 Ultimate AI-Powered System Optimizer'));
        console.log(chalk.yellow('━'.repeat(60)));
        console.log();

        // Show launch options
        const choice = await inquirer.prompt([{
            type: 'list',
            name: 'mode',
            message: 'How would you like to launch NEXUS?',
            choices: [
                { name: '🚀 Full Power Mode (All Features)', value: 'full' },
                { name: '⚡ Performance Mode (Optimized)', value: 'performance' },
                { name: '🎮 Gaming Ready Mode', value: 'gaming' },
                { name: '🔧 Maintenance Mode', value: 'maintenance' },
                { name: '📊 Dashboard Only', value: 'dashboard' }
            ]
        }]);

        await this.initializeComponents(choice.mode);
        await this.startSystems();

        this.showStatus();
        this.setupGracefulShutdown();
    }

    async initializeComponents(mode) {
        console.log(chalk.blue('🔧 Initializing NEXUS components...'));

        // Always initialize core components
        this.components.notifications = new SmartNotificationSystem();
        this.components.aiBrain = new AIBrain();
        this.components.systemMonitor = new SystemMonitor();

        // Mode-specific initialization
        switch(mode) {
            case 'full':
                this.components.dashboard = new DashboardServer(3000);
                this.components.gamingMode = new GamingMode(
                    this.components.systemMonitor,
                    this.components.notifications
                );
                break;

            case 'performance':
                // Lightweight mode - no dashboard
                break;

            case 'gaming':
                this.components.gamingMode = new GamingMode(
                    this.components.systemMonitor,
                    this.components.notifications
                );
                await this.components.gamingMode.activateGamingMode(['manual']);
                break;

            case 'maintenance':
                // Focus on system cleanup and optimization
                break;

            case 'dashboard':
                this.components.dashboard = new DashboardServer(3000);
                break;
        }

        console.log(chalk.green('✅ All components initialized!'));
    }

    async startSystems() {
        console.log(chalk.blue('🚀 Starting NEXUS systems...'));

        // Start AI Brain
        await this.components.aiBrain.init();
        console.log(chalk.green('✅ AI Brain online'));

        // Start System Monitor
        this.components.systemMonitor.startMonitoring();
        console.log(chalk.green('✅ System Monitor active'));

        // Start Dashboard if available
        if (this.components.dashboard) {
            this.components.dashboard.server.listen(3000, () => {
                console.log(chalk.green('✅ Dashboard server running on http://localhost:3000'));
            });
        }

        // Welcome notification
        await this.components.notifications.successNotification(
            'NEXUS AI Activated',
            'Your ultimate system optimizer is now online and protecting your PC!'
        );

        this.isRunning = true;
    }

    showStatus() {
        console.log();
        console.log(chalk.cyan('NEXUS AI Status: Running'));
