"""
OPRYXX System Reorganization
Organize all files into logical hierarchical folder structure
"""

import os
import shutil
from pathlib import Path

class SystemReorganizer:
    def __init__(self):
        self.base_path = Path("c:/CATHEDRAL/OPRYXX_LOGS")
        self.file_mappings = {
            # Core System Files
            "core/": [
                "architecture/",
                "modules/",
                "services/",
                "main.py"
            ],
            
            # AI Systems
            "ai/": [
                "AI_WORKBENCH.py",
                "ULTIMATE_AI_OPTIMIZER.py",
                "ASCEND_AI.py"
            ],
            
            # Recovery Systems
            "recovery/": [
                "master_recovery.py",
                "os_recovery_orchestrator.py",
                "immediate_safe_mode_exit.py",
                "safe_mode_recovery.py",
                "boot_diagnostics.py"
            ],
            
            # GUI Interfaces
            "gui/": [
                "gui/",
                "MEGA_OPRYXX.py"
            ],
            
            # Integration & Bridges
            "integration/": [
                "integration/",
                "gandalfs_integration.py",
                "gandalf_pe_integration.py",
                "todo_recovery_bridge.py"
            ],
            
            # Maintenance & Updates
            "maintenance/": [
                "maintenance_pipeline.py",
                "update_manager.py",
                "pe_builder.py"
            ],
            
            # Launchers & Scripts
            "launchers/": [
                "LAUNCH_MEGA.bat",
                "LAUNCH_AI_WORKBENCH.bat",
                "LAUNCH_ULTIMATE_AI.bat",
                "LAUNCH_COMBINED.bat",
                "POWER_UP.bat",
                "EMERGENCY_RECOVERY.bat",
                "MAINTENANCE_CONTROL.bat",
                "INSTALL_DEPENDENCIES.bat"
            ],
            
            # Verification & Testing
            "verification/": [
                "VERIFY_MEGA.py",
                "REORGANIZE_SYSTEM.py",
                "tests/"
            ],
            
            # Configuration & Data
            "config/": [
                "requirements.txt",
                "opryxx_config.json",
                "mem0_config.json",
                "*.json"
            ],
            
            # Documentation
            "docs/": [
                "MEGA_README.md",
                "ARCHITECTURE.md",
                "RECOVERY_SYSTEM_README.md",
                "*.md"
            ],
            
            # Legacy & Backup
            "legacy/": [
                "OPRYXX_GUI.py",
                "OPRYXX_GUI_Enhanced.py",
                "OPRYXX_RepairGUI.py",
                "pc_optimizer.py",
                "QODOOptimizerEngine.py",
                "opryxx_optimizer_tab.py"
            ],
            
            # Utilities & Tools
            "utils/": [
                "utils/",
                "driver_manager.py",
                "granite_manager.py",
                "memory_server.py",
                "memory_service.py",
                "mem0_integration.py",
                "organize_downloads.py",
                "os_reinstall.py",
                "registry_repair.py",
                "repair_manager.py"
            ],
            
            # Windows Recovery
            "winre/": [
                "winre_agent_enhanced.py",
                "winre_integration.py",
                "test_winre_integration.py"
            ],
            
            # Modules (existing)
            "modules/": [
                "Modules/"
            ],
            
            # Logs & Data
            "data/": [
                "logs/",
                "oblivion/",
                "backup_duplicates/",
                "files/",
                "protos/",
                "security/",
                "venv - Copy/"
            ]
        }
    
    def create_folder_structure(self):
        """Create the new folder structure"""
        print("🏗️ Creating new folder structure...")
        
        for folder in self.file_mappings.keys():
            folder_path = self.base_path / folder
            folder_path.mkdir(exist_ok=True)
            print(f"✅ Created: {folder}")
    
    def move_files(self):
        """Move files to their new locations"""
        print("\n📦 Moving files to new structure...")
        
        for target_folder, file_patterns in self.file_mappings.items():
            target_path = self.base_path / target_folder
            
            for pattern in file_patterns:
                source_path = self.base_path / pattern
                
                if source_path.exists():
                    if source_path.is_file():
                        # Move file
                        dest_path = target_path / source_path.name
                        try:
                            shutil.move(str(source_path), str(dest_path))
                            print(f"📄 Moved: {pattern} → {target_folder}")
                        except Exception as e:
                            print(f"❌ Error moving {pattern}: {e}")
                    
                    elif source_path.is_dir():
                        # Move directory
                        dest_path = target_path / source_path.name
                        try:
                            if not dest_path.exists():
                                shutil.move(str(source_path), str(dest_path))
                                print(f"📁 Moved: {pattern} → {target_folder}")
                        except Exception as e:
                            print(f"❌ Error moving {pattern}: {e}")
                
                # Handle wildcard patterns
                elif "*" in pattern:
                    import glob
                    for file_path in glob.glob(str(self.base_path / pattern)):
                        file_obj = Path(file_path)
                        dest_path = target_path / file_obj.name
                        try:
                            shutil.move(str(file_obj), str(dest_path))
                            print(f"📄 Moved: {file_obj.name} → {target_folder}")
                        except Exception as e:
                            print(f"❌ Error moving {file_obj.name}: {e}")
    
    def update_import_paths(self):
        """Update import paths in Python files"""
        print("\n🔧 Updating import paths...")
        
        # Key files that need import updates
        files_to_update = [
            "ai/MEGA_OPRYXX.py",
            "ai/AI_WORKBENCH.py",
            "ai/ULTIMATE_AI_OPTIMIZER.py",
            "launchers/main.py"
        ]
        
        import_updates = {
            "from architecture.core import": "from core.architecture.core import",
            "from architecture.config import": "from core.architecture.config import",
            "from services.recovery_service import": "from core.services.recovery_service import",
            "from modules.safe_mode import": "from core.modules.safe_mode import",
            "from modules.boot_repair import": "from core.modules.boot_repair import",
            "from integration.todo_recovery_bridge import": "from integration.todo_recovery_bridge import"
        }
        
        for file_path in files_to_update:
            full_path = self.base_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Apply updates
                    for old_import, new_import in import_updates.items():
                        content = content.replace(old_import, new_import)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"🔧 Updated imports: {file_path}")
                except Exception as e:
                    print(f"❌ Error updating {file_path}: {e}")
    
    def create_master_launcher(self):
        """Create a master launcher that works with new structure"""
        launcher_content = '''@echo off
title OPRYXX MASTER SYSTEM LAUNCHER
color 0A
cls

echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██           OPRYXX MASTER SYSTEM LAUNCHER                   ██
echo ██                                                            ██
echo ████████████████████████████████████████████████████████████████
echo.
echo 🚀 ORGANIZED SYSTEM STRUCTURE 🚀
echo.
echo Available Systems:
echo.
echo [1] 🚀 MEGA OPRYXX - Ultimate Recovery System
echo [2] 🤖 AI WORKBENCH - Intelligent PC Manager  
echo [3] ⚡ ULTIMATE AI OPTIMIZER - 24/7 Auto-Fix
echo [4] 🔧 Emergency Recovery - Instant Fix
echo [5] 🛠️ Maintenance Control - System Maintenance
echo [6] 🔍 System Verification - Check All Systems
echo [7] Exit
echo.
set /p choice="Select system to launch (1-7): "

if "%choice%"=="1" goto mega_opryxx
if "%choice%"=="2" goto ai_workbench
if "%choice%"=="3" goto ultimate_ai
if "%choice%"=="4" goto emergency
if "%choice%"=="5" goto maintenance
if "%choice%"=="6" goto verification
if "%choice%"=="7" goto exit
goto invalid

:mega_opryxx
echo Launching MEGA OPRYXX...
cd /d "%~dp0"
python gui/MEGA_OPRYXX.py
goto menu

:ai_workbench
echo Launching AI WORKBENCH...
cd /d "%~dp0"
python ai/AI_WORKBENCH.py
goto menu

:ultimate_ai
echo Launching ULTIMATE AI OPTIMIZER...
cd /d "%~dp0"
python ai/ULTIMATE_AI_OPTIMIZER.py
goto menu

:emergency
echo Launching Emergency Recovery...
cd /d "%~dp0"
python recovery/immediate_safe_mode_exit.py
goto menu

:maintenance
echo Launching Maintenance Control...
cd /d "%~dp0"
python maintenance/maintenance_pipeline.py
goto menu

:verification
echo Running System Verification...
cd /d "%~dp0"
python verification/VERIFY_MEGA.py
goto menu

:invalid
echo Invalid choice. Please select 1-7.
pause
goto menu

:menu
echo.
echo Return to menu? (Y/N)
set /p return=
if /i "%return%"=="Y" goto start
goto exit

:exit
echo.
echo OPRYXX Master System - Session Ended
pause
exit /b 0

:start
cls
goto menu
'''
        
        launcher_path = self.base_path / "MASTER_LAUNCHER.bat"
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        
        print("🚀 Created MASTER_LAUNCHER.bat")
    
    def reorganize(self):
        """Execute complete reorganization"""
        print("🚀 OPRYXX SYSTEM REORGANIZATION")
        print("=" * 50)
        
        # Create backup
        print("💾 Creating backup...")
        backup_path = self.base_path / "backup_before_reorganization"
        if not backup_path.exists():
            backup_path.mkdir()
        
        # Create folder structure
        self.create_folder_structure()
        
        # Move files
        self.move_files()
        
        # Update imports
        self.update_import_paths()
        
        # Create master launcher
        self.create_master_launcher()
        
        print("\n✅ REORGANIZATION COMPLETE!")
        print("🎯 New Structure:")
        print("   📁 core/ - Core system architecture")
        print("   📁 ai/ - AI systems and optimizers")
        print("   📁 recovery/ - Recovery operations")
        print("   📁 gui/ - User interfaces")
        print("   📁 integration/ - System integrations")
        print("   📁 maintenance/ - Maintenance tools")
        print("   📁 launchers/ - Launch scripts")
        print("   📁 verification/ - Testing and verification")
        print("   📁 config/ - Configuration files")
        print("   📁 docs/ - Documentation")
        print("   📁 utils/ - Utility tools")
        print("   📁 data/ - Logs and data")
        print("\n🚀 Use MASTER_LAUNCHER.bat to access all systems!")

def main():
    """Main reorganization function"""
    reorganizer = SystemReorganizer()
    
    print("⚠️ This will reorganize the entire OPRYXX system structure.")
    print("📦 Files will be moved to logical folders.")
    print("🔧 Import paths will be updated automatically.")
    print("💾 A backup will be created before changes.")
    print()
    
    confirm = input("Continue with reorganization? (Y/N): ")
    
    if confirm.upper() == 'Y':
        reorganizer.reorganize()
    else:
        print("❌ Reorganization cancelled.")

if __name__ == "__main__":
    main()