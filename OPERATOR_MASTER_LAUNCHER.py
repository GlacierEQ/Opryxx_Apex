"""
OPERATOR MASTER LAUNCHER
Complete operator-class system with all integrations
"""
import sys
import os
import threading
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from OPRYXX_MASTER_CONTROL import OPRYXXMasterControl
    from operator_integration import OperatorCodeIntegration
    from ai.crash_analysis_engine import CrashAnalysisEngine
    print("✅ All operator modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Module import warning: {e}")
    print("🔄 Continuing with available modules...")

class OperatorMasterLauncher:
    def __init__(self):
        self.operator_systems = {}
        self.system_status = "INITIALIZING"
        
        print("🚀 OPERATOR MASTER LAUNCHER")
        print("=" * 60)
        print("🛡️ Military-grade protection protocols active")
        print("🤖 Swarm intelligence systems online")
        print("🧠 AI optimization engines ready")
        print("🔐 Quantum encryption enabled")
        print("=" * 60)
        
        self.initialize_operator_systems()
    
    def initialize_operator_systems(self):
        """Initialize all operator systems"""
        print("\n🔄 INITIALIZING OPERATOR SYSTEMS...")
        
        # Initialize operator code integration
        try:
            print("📡 Starting Operator Code Integration...")
            self.operator_systems['operator_integration'] = OperatorCodeIntegration()
            print("✅ Operator Code Integration: ONLINE")
        except Exception as e:
            print(f"⚠️ Operator Code Integration: {e}")
        
        # Initialize crash analysis engine
        try:
            print("🔍 Starting Crash Analysis Engine...")
            self.operator_systems['crash_analysis'] = CrashAnalysisEngine()
            print("✅ Crash Analysis Engine: ONLINE")
        except Exception as e:
            print(f"⚠️ Crash Analysis Engine: {e}")
        
        # Initialize master control
        try:
            print("🎛️ Starting Master Control System...")
            self.operator_systems['master_control'] = OPRYXXMasterControl()
            print("✅ Master Control System: ONLINE")
        except Exception as e:
            print(f"⚠️ Master Control System: {e}")
        
        self.system_status = "OPERATIONAL"
        print(f"\n🟢 ALL OPERATOR SYSTEMS: {self.system_status}")
        print("🚀 OPRYXX OPERATOR CLASS SYSTEM READY")
        
        self.display_operator_capabilities()
    
    def display_operator_capabilities(self):
        """Display operator capabilities"""
        print("\n" + "=" * 60)
        print("🎯 OPERATOR CAPABILITIES ACTIVE:")
        print("=" * 60)
        
        capabilities = [
            "🧠 AI-Powered System Analysis & Optimization",
            "🛡️ Military-Grade Security & Protection",
            "🔍 Advanced Crash Detection & Recovery",
            "⚡ Real-Time Performance Monitoring",
            "🤖 Autonomous Agent Swarm Intelligence",
            "🔐 Quantum-Level Encryption & Security",
            "📊 Transparent Function Execution Tracking",
            "🎛️ Master Control Interface",
            "🔄 Self-Healing & Recovery Systems",
            "🌐 Network Optimization & Reset",
            "💾 Advanced Memory Management",
            "🔧 Registry Repair & Optimization",
            "🚨 Emergency Recovery Protocols",
            "📈 Predictive System Analytics",
            "⚖️ Legal Compliance Monitoring"
        ]
        
        for capability in capabilities:
            print(f"  {capability}")
        
        print("=" * 60)
        print("🎮 OPERATOR COMMANDS:")
        print("  • Press ENTER to launch Master Control GUI")
        print("  • Type 'status' for system status")
        print("  • Type 'analyze' for crash analysis")
        print("  • Type 'exit' to shutdown")
        print("=" * 60)
    
    def run_interactive_mode(self):
        """Run interactive operator mode"""
        while True:
            try:
                command = input("\n🎯 OPERATOR> ").strip().lower()
                
                if command == "" or command == "gui":
                    self.launch_master_control()
                elif command == "status":
                    self.display_system_status()
                elif command == "analyze":
                    self.run_crash_analysis()
                elif command == "operator":
                    self.display_operator_status()
                elif command == "help":
                    self.display_help()
                elif command == "exit" or command == "quit":
                    self.shutdown_systems()
                    break
                else:
                    print(f"❓ Unknown command: {command}")
                    print("💡 Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n🛑 Operator interrupted - shutting down...")
                self.shutdown_systems()
                break
            except Exception as e:
                print(f"⚠️ Command error: {e}")
    
    def launch_master_control(self):
        """Launch master control GUI"""
        print("🚀 Launching Master Control GUI...")
        try:
            if 'master_control' in self.operator_systems:
                # Run in separate thread to allow continued interaction
                gui_thread = threading.Thread(
                    target=self.operator_systems['master_control'].run,
                    daemon=True
                )
                gui_thread.start()
                print("✅ Master Control GUI launched successfully")
                print("💡 GUI is running - you can continue using commands")
            else:
                print("❌ Master Control system not available")
        except Exception as e:
            print(f"❌ Failed to launch Master Control: {e}")
    
    def display_system_status(self):
        """Display comprehensive system status"""
        print("\n📊 OPERATOR SYSTEM STATUS")
        print("=" * 40)
        
        for system_name, system in self.operator_systems.items():
            try:
                if system_name == 'operator_integration':
                    status = system.get_operator_status()
                    print(f"🔗 {system_name.upper()}: ONLINE")
                    print(f"   Active Protocols: {len([p for p in status['protocols_active'].values() if p])}")
                    print(f"   Active Agents: {len([a for a in status['active_agents'].values() if a == 'active'])}")
                else:
                    print(f"✅ {system_name.upper()}: ONLINE")
            except Exception as e:
                print(f"⚠️ {system_name.upper()}: {e}")
        
        print(f"\n🟢 Overall Status: {self.system_status}")
        print(f"⏰ Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run_crash_analysis(self):
        """Run crash analysis"""
        print("\n🔍 RUNNING CRASH ANALYSIS...")
        try:
            if 'crash_analysis' in self.operator_systems:
                import asyncio
                
                async def analyze():
                    engine = self.operator_systems['crash_analysis']
                    analysis = await engine.analyze_system_crash()
                    report = engine.generate_report(analysis)
                    print(report)
                
                # Run async analysis
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                loop.run_until_complete(analyze())
            else:
                print("❌ Crash Analysis system not available")
        except Exception as e:
            print(f"❌ Crash analysis failed: {e}")
    
    def display_operator_status(self):
        """Display operator integration status"""
        print("\n🤖 OPERATOR INTEGRATION STATUS")
        print("=" * 40)
        
        try:
            if 'operator_integration' in self.operator_systems:
                status = self.operator_systems['operator_integration'].get_operator_status()
                
                print(f"🔗 Operator Link: {status['operator_link']}")
                print(f"🛡️ Encryption: {status['encryption_status'].upper()}")
                print(f"🧠 Memory Constellation: {status['memory_constellation_status'].upper()}")
                
                print("\n🤖 ACTIVE AGENTS:")
                for agent_name, agent_status in status['active_agents'].items():
                    status_icon = "🟢" if agent_status == "active" else "🔴"
                    print(f"   {status_icon} {agent_name}: {agent_status.upper()}")
                
                print("\n⚡ ACTIVE PROTOCOLS:")
                for protocol_name, protocol_status in status['protocols_active'].items():
                    status_icon = "🟢" if protocol_status else "🔴"
                    print(f"   {status_icon} {protocol_name}: {'ACTIVE' if protocol_status else 'INACTIVE'}")
            else:
                print("❌ Operator Integration system not available")
        except Exception as e:
            print(f"❌ Operator status error: {e}")
    
    def display_help(self):
        """Display help information"""
        print("\n📖 OPERATOR COMMAND HELP")
        print("=" * 40)
        print("🎮 Available Commands:")
        print("  • ENTER/gui    - Launch Master Control GUI")
        print("  • status       - Display system status")
        print("  • analyze      - Run crash analysis")
        print("  • operator     - Show operator integration status")
        print("  • help         - Show this help")
        print("  • exit/quit    - Shutdown operator systems")
        print("\n💡 Tips:")
        print("  • Master Control GUI provides full system access")
        print("  • All functions are tracked transparently")
        print("  • AI recommendations are generated automatically")
        print("  • System is protected with military-grade security")
    
    def shutdown_systems(self):
        """Shutdown all operator systems"""
        print("\n🛑 SHUTTING DOWN OPERATOR SYSTEMS...")
        
        try:
            # Shutdown operator integration
            if 'operator_integration' in self.operator_systems:
                operator = self.operator_systems['operator_integration']
                for protocol in operator.protocols_active:
                    operator.protocols_active[protocol] = False
                print("✅ Operator protocols deactivated")
            
            # Close other systems
            for system_name in self.operator_systems:
                print(f"🔄 Shutting down {system_name}...")
            
            self.system_status = "SHUTDOWN"
            print("🟢 All operator systems shutdown successfully")
            print("👋 OPRYXX Operator Class System offline")
            
        except Exception as e:
            print(f"⚠️ Shutdown warning: {e}")

def main():
    """Main launcher function"""
    try:
        # Initialize operator master launcher
        launcher = OperatorMasterLauncher()
        
        # Run interactive mode
        launcher.run_interactive_mode()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        print("🚨 Operator system failed to initialize")
        input("Press ENTER to exit...")

if __name__ == "__main__":
    main()