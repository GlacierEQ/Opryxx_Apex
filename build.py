#!/usr/bin/env python3
"""
OPRYXX Build Script

This script automates the process of building the OPRYXX executable and creating an installer.
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from typing import List, Optional, Dict, Any

# Configuration
VERSION = "1.0.0"
APP_NAME = "OPRYXX"
COMPANY_NAME = "OPRYXX"
COPYRIGHT = "Copyright © 2025 OPRYXX. All rights reserved."

# Paths
ROOT_DIR = Path(__file__).parent.absolute()
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"
INSTALLER_DIR = ROOT_DIR / "installer"
ASSETS_DIR = ROOT_DIR / "assets"

# Ensure required directories exist
for directory in [BUILD_DIR, DIST_DIR, INSTALLER_DIR, ASSETS_DIR]:
    directory.mkdir(exist_ok=True)

class Builder:
    """Build system for OPRYXX."""
    
    def __init__(self, clean: bool = False, verbose: bool = False):
        """Initialize the builder."""
        self.clean = clean
        self.verbose = verbose
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()
        
        # Set up paths
        self.build_dir = BUILD_DIR / f"{self.platform}_{self.architecture}"
        self.dist_dir = DIST_DIR / f"{self.platform}_{self.architecture}"
        self.installer_dir = INSTALLER_DIR / f"{self.platform}_{self.architecture}"
        
        # Ensure directories exist
        for directory in [self.build_dir, self.dist_dir, self.installer_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def clean_build(self) -> None:
        """Clean build artifacts."""
        print("🧹 Cleaning build artifacts...")
        
        # Remove build and dist directories
        for directory in [BUILD_DIR, DIST_DIR]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"  - Removed {directory}")
        
        # Recreate directories
        for directory in [BUILD_DIR, DIST_DIR]:
            directory.mkdir(exist_ok=True)
    
    def install_dependencies(self) -> bool:
        """Install build dependencies."""
        print("📦 Installing build dependencies...")
        
        try:
            # Install PyInstaller if not already installed
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "pip", "setuptools", "wheel"
            ])
            
            # Install build tools
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--upgrade",
                "pyinstaller>=5.0",
                "pywin32>=303; platform_system=='Windows'"
            ])
            
            # Check if NSIS is installed on Windows
            if sys.platform == 'win32':
                # Try to find NSIS in common locations
                nsis_paths = [
                    os.path.expandvars(r"%ProgramFiles%\NSIS\makensis.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\NSIS\makensis.exe"),
                    r"C:\Program Files\NSIS\makensis.exe",
                    r"C:\Program Files (x86)\NSIS\makensis.exe"
                ]
                
                if not any(os.path.exists(p) for p in nsis_paths):
                    print("\n⚠️  NSIS (Nullsoft Scriptable Install System) is not installed or not in PATH.")
                    print("   Please download and install NSIS from https://nsis.sourceforge.io/Download")
                    print("   Make sure to add NSIS to your system PATH during installation.\n")
                    print("   For now, the build will continue but won't create an installer.")
                    print("   You can still build the executable using: python build.py --no-installer\n")
                    # Don't fail the build, just warn the user
                    return True
            
            # Install application dependencies
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "-r", "requirements.txt"
            ])
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def build_executable(self) -> bool:
        """Build the executable using PyInstaller."""
        print("🔨 Building executable...")
        
        try:
            # Build the spec file if it doesn't exist
            spec_file = ROOT_DIR / "opryxx.spec"
            if not spec_file.exists():
                print("  - Generating spec file...")
                subprocess.check_call([
                    sys.executable, "-m", "PyInstaller",
                    "--name", APP_NAME,
                    "--onefile",
                    "--windowed",
                    "--clean",
                    "--distpath", str(self.dist_dir),
                    "--workpath", str(self.build_dir),
                    "--specpath", str(ROOT_DIR),
                    "opryxx_launcher.py"
                ])
            
            # Build the executable
            print("  - Running PyInstaller...")
            subprocess.check_call([
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(spec_file)
            ])
            
            print(f"✅ Executable built: {self.dist_dir / f'{APP_NAME}.exe'}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build executable: {e}")
            return False
    
    def create_installer_windows(self) -> bool:
        """Create a Windows installer using NSIS."""
        print("📦 Creating Windows installer...")
        
        try:
            # Create NSIS script
            nsis_script = self._create_nsis_script()
            nsis_script_path = self.installer_dir / "installer.nsi"
            
            with open(nsis_script_path, 'w', encoding='utf-8') as f:
                f.write(nsis_script)
            
            # Run NSIS compiler
            print("  - Running NSIS compiler...")
            subprocess.check_call([
                "makensis", 
                f"/XOutFile {self.installer_dir / f'{APP_NAME}_Setup.exe'}",
                str(nsis_script_path)
            ], shell=True)
            
            print(f"✅ Installer created: {self.installer_dir / f'{APP_NAME}_Setup.exe'}")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"❌ Failed to create installer: {e}")
            print("  Make sure NSIS is installed and in your PATH")
            return False
    
    def _create_nsis_script(self) -> str:
        """Create an NSIS installer script."""
        return f"""
# NSIS Installer Script for {APP_NAME}
# Auto-generated by build.py

# General settings
Name "{APP_NAME}"
OutFile "${{NSISDIR}}\\..\\{APP_NAME}_Setup.exe"
InstallDir "$PROGRAMFILES\\{COMPANY_NAME}\\{APP_NAME}"
InstallDirRegKey HKLM "Software\\{COMPANY_NAME}\\{APP_NAME}" "Install_Dir"
RequestExecutionLevel admin

# UI Settings
!include MUI2.nsh
!define MUI_ABORTWARNING
!define MUI_ICON "${{NSISDIR}}\\Contrib\\Graphics\\Icons\\modern-install.ico"

# Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "{ROOT_DIR / 'LICENSE'}"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

# Languages
!insertmacro MUI_LANGUAGE "English"

# Installer sections
Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite try
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    # Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\\{COMPANY_NAME}\\{APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\{COMPANY_NAME}\\{APP_NAME}\\{APP_NAME}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    CreateShortCut "$SMPROGRAMS\\{COMPANY_NAME}\\{APP_NAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    # Add files
    File /r "{self.dist_dir}\\*.*"
    
    # Write registry keys for Add/Remove Programs
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" \
        "DisplayName" "{APP_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" \
        "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" \
        "DisplayIcon" "$INSTDIR\\{APP_NAME}.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" \
        "Publisher" "{COMPANY_NAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}" \
        "DisplayVersion" "{VERSION}"
    
    # Create data directories
    CreateDirectory "$APPDATA\\{COMPANY_NAME}\\{APP_NAME}\\logs"
    CreateDirectory "$APPDATA\\{COMPANY_NAME}\\{APP_NAME}\\config"
    
    # Copy default config if it doesn't exist
    IfFileExists "$APPDATA\\{COMPANY_NAME}\\{APP_NAME}\\config\\config.yaml" +2
        File /oname=$APPDATA\\{COMPANY_NAME}\\{APP_NAME}\\config\\config.yaml "{ROOT_DIR / 'config' / 'config.default.yaml'}"
    
SectionEnd

# Uninstaller section
Section "Uninstall"
    # Remove files
    RMDir /r "$INSTDIR\\*.*"
    RMDir "$INSTDIR"
    
    # Remove shortcuts
    Delete "$SMPROGRAMS\\{COMPANY_NAME}\\{APP_NAME}\\*.*"
    RMDir "$SMPROGRAMS\\{COMPANY_NAME}\\{APP_NAME}"
    
    # Remove registry keys
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_NAME}"
    DeleteRegKey HKLM "Software\\{COMPANY_NAME}\\{APP_NAME}"
    
    # Ask to remove user data
    MessageBox MB_YESNO "Do you want to remove all user data and configuration?" IDNO NoRemoveData
        RMDir /r "$APPDATA\\{COMPANY_NAME}\\{APP_NAME}"
    NoRemoveData:
    
SectionEnd
"""

def main():
    """Main entry point for the build script."""
    parser = argparse.ArgumentParser(description=f"Build {APP_NAME} executable and installer")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts before building")
    parser.add_argument("--install-deps", action="store_true", help="Install build dependencies")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--no-installer", action="store_true", help="Skip creating an installer")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--platform", choices=["windows", "linux", "macos"], 
                       help="Target platform (default: auto-detect)")
    
    args = parser.parse_args()
    
    # Initialize builder
    builder = Builder(clean=args.clean, verbose=args.verbose)
    
    # Clean if requested
    if args.clean:
        builder.clean_build()
    
    # Install dependencies if requested
    if args.install_deps and not args.skip_deps:
        if not builder.install_dependencies():
            return 1
    
    # Build executable
    if not builder.build_executable():
        return 1
    
    # Create installer (Windows only for now)
    if platform.system().lower() == 'windows' and not args.no_installer:
        if not builder.create_installer_windows():
            print("⚠️ Installer creation failed, but the executable was built successfully")
    
    print("\n✅ Build completed successfully!")
    print(f"   - Executable: {builder.dist_dir / f'{APP_NAME}.exe'}")
    
    if platform.system().lower() == 'windows' and not args.no_installer:
        print(f"   - Installer: {builder.installer_dir / f'{APP_NAME}_Setup.exe'}")
    elif platform.system().lower() == 'windows' and args.no_installer:
        print("   - Installer creation skipped (--no-installer flag was used)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
