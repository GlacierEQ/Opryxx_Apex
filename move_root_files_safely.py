import os
import shutil

# A specific, hardcoded list of Python files to move
python_files_to_move = [
    "AI_OPTIMIZATION_ENGINE.py", "ARCHITECTURE_FIX.py", "BITLOCKER_RECOVERY.py",
    "BUILD_ULTIMATE.py", "CODE_CRAWLER.py", "CREATE_INSTALLER.py",
    "DELL_INSPIRON_RECOVERY.py", "ENHANCED_PERFORMANCE_AI.py", "ENHANCED_PIPELINES.py",
    "ENHANCED_ULTIMATE_AI.py", "FINAL_SYSTEM_CHECK.py", "FULL_STACK_STATUS.py",
    "FULL_STACK_VERIFICATION.py", "IMPLEMENT_IMPROVEMENTS.py", "INTEGRATION_BRIDGE.py",
    "INTEGRATION_INSTALLER.py", "LAYER_1_CORE_FIXED.py", "LAYER_1_IMPLEMENTATION.py",
    "LAYER_1_SIMPLE.py", "LOGICAL_CASCADE_IMPLEMENTATION.py", "LOGICAL_CASCADE_SIMPLE.py",
    "MAKE_EXE.py", "MAXIMUM_AI_SIMPLE.py", "OPERATOR_HOOK.py",
    "OPERATOR_MASTER_LAUNCHER.py", "OPRYXX_DEEP_REPAIR.py", "OPRYXX_FINAL.py",
    "OPRYXX_INSTALLER.py", "OPRYXX_MASTER.py", "OPRYXX_MASTER_CONTROL.py",
    "OPRYXX_ULTIMATE.py", "OPRYXX_UNIFIED.py", "OPRYXX_UNIFIED_LAUNCHER.py",
    "PROJECT_ANALYSIS.py", "PROJECT_SCANNER.py", "PROJECT_SCANNER_FIXED.py",
    "QUICK_INSTALLER.py", "RECOVERY_MASTER.py", "REORGANIZE_SYSTEM.py",
    "SIMPLE_INSTALLER.py", "STREAMLINE_ARCHITECTURE.py", "SYSTEM_VERIFICATION.py",
    "ULTIMATE_AI_LAUNCHER.py", "ULTIMATE_BOOT_RECOVERY.py", "ULTIMATE_DATA_RECOVERY.py",
    "ULTIMATE_MASTER_GUI.py", "ULTIMATE_NEXUS_AI.py", "ULTIMATE_OPERATOR_REPO_MASTER.py",
    "ULTIMATE_OPTIMIZER.py", "ULTIMATE_UNIFIED_STACK.py", "ULTIMATE_UNIFIED_SYSTEM.py",
    "UNIFIED_FULL_STACK_GUI.py", "UNIFIED_GUI.py", "UNIFIED_INTEGRATION_TEST.py",
    "UNIFIED_MASTER_LAUNCHER.py", "UNIFIED_STACK_TESTS.py", "VERIFICATION_COMPLETE.py",
    "VERIFY_FULL_STACK.py", "VERIFY_SIMPLE.py", "VERIFY_UNIFIED_STACK.py",
    "WINDOWS11_RECOVERY_MODULE.py", "add_uvx_to_path.py", "ai_context.py",
    "aifiles.py", "basic_function_test.py", "build.py", "build_exe.py",
    "cascade_integration.py", "check_imports.py", "check_ollama_repos.py",
    "ci_cd_integration.py", "cognitive_core_pb2.py", "cognitive_core_pb2_grpc.py",
    "component_integration_test.py", "deep_pc_repair.py", "fix_comprehensive_scanner.py",
    "fix_mcp_uvx_error.py", "gandalfs_integration.py", "gandalfs_maintenance.py",
    "gandalfs_update_manager.py", "github_ai_optimizer.py", "github_bulk_loader.py",
    "github_desktop_loader.py", "github_hyper_pro_loader.py", "gui_connection_tester.py",
    "gui_settings_validator.py", "healthcheck.py", "init_database.py",
    "init_db.py", "install_ollama.py", "install_ollama_binary.py",
    "install_ollama_user.py", "main_gui.py", "master_start.py",
    "memory_constellation_installer.py", "ollama_integration.py",
    "ollama_windsurf_bridge.py", "operator_integration.py", "operator_pepper_integration.py",
    "opryxx_launcher.py", "opryxx_monitor.py", "performance_benchmark.py",
    "performance_dashboard.py", "pipelines.py", "qodo_recovery_orchestrator.py",
    "quick_fix_scanner.py", "run_os_reinstall.py", "setup.py",
    "simple_ollama_verify.py", "simple_test_functions.py", "simple_verify.py",
    "start_ollama.py", "test_all_functions.py", "test_full_stack_verification.py",
    "test_launcher.py", "test_maximum_integration.py", "test_ollama_integration.py",
    "unified_system.py", "verify_ollama_hookup.py",
    "verify_stack.py", "verify_system.py", "windsurf_global_integration.py",
    "windsurf_integration.py", "windsurf_ollama_hook.py", "winre_agent_enhanced.py"
]

def move_files():
    """
    Moves Python files from the root directory to the src/ directory.
    """
    if not os.path.exists("src"):
        os.makedirs("src")

    for file_path in python_files_to_move:
        if os.path.exists(file_path):
            try:
                shutil.move(file_path, "src/")
                print(f"Moved {file_path} to src/")
            except Exception as e:
                print(f"Error moving {file_path}: {e}")

if __name__ == "__main__":
    move_files()
