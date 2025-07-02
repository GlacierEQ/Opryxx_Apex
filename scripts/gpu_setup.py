"""
GPU Setup and Installation Helper
Automatically installs GPU drivers and libraries
"""

import subprocess
import platform
import sys
import requests
import os

def install_nvidia_drivers():
    """Install NVIDIA drivers"""
    print("Installing NVIDIA drivers...")
    
    if platform.system() == "Windows":
        # Download and install NVIDIA drivers
        try:
            subprocess.run(['winget', 'install', 'NVIDIA.GeForceExperience'], check=True)
            print("✅ NVIDIA drivers installed via winget")
        except:
            print("⚠️ Manual NVIDIA driver installation required")
            print("Visit: https://www.nvidia.com/drivers")
    
    elif platform.system() == "Linux":
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'nvidia-driver-535'], check=True)
            print("✅ NVIDIA drivers installed")
        except:
            print("⚠️ Manual NVIDIA driver installation required")

def install_cuda_toolkit():
    """Install CUDA toolkit"""
    print("Installing CUDA toolkit...")
    
    try:
        # Install PyTorch with CUDA
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'torch', 'torchvision', 'torchaudio', 
                       '--index-url', 'https://download.pytorch.org/whl/cu121'], 
                      check=True)
        print("✅ PyTorch with CUDA installed")
    except:
        print("⚠️ CUDA installation failed, installing CPU version")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'torch', 'torchvision', 'torchaudio'], check=True)

def install_opencl():
    """Install OpenCL support"""
    print("Installing OpenCL...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyopencl'], check=True)
        print("✅ OpenCL installed")
    except:
        print("⚠️ OpenCL installation failed")

def install_wmi():
    """Install WMI for Windows GPU detection"""
    if platform.system() == "Windows":
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'wmi'], check=True)
            print("✅ WMI installed")
        except:
            print("⚠️ WMI installation failed")

def main():
    print("GPU Setup and Elevation")
    print("=" * 30)
    
    # Install all GPU-related packages
    install_wmi()
    install_opencl()
    install_cuda_toolkit()
    
    # Test GPU detection
    print("\nTesting GPU detection...")
    try:
        from core.gpu_detector import gpu_detector
        gpus = gpu_detector.detect_all_gpus()
        
        if gpus:
            print(f"[OK] Found {len(gpus)} GPU(s):")
            for gpu in gpus:
                print(f"   • {gpu.name} ({gpu.memory_mb}MB) via {gpu.backend}")
        else:
            print("[ERROR] No GPUs detected")
            print("\nTroubleshooting:")
            print("   1. Install GPU drivers")
            print("   2. Restart system")
            print("   3. Run as administrator")
            
            if input("Install NVIDIA drivers? (y/n): ").lower() == 'y':
                install_nvidia_drivers()
    
    except Exception as e:
        print(f"[ERROR] GPU detection test failed: {e}")
    
    print("\n[OK] GPU setup complete!")

if __name__ == "__main__":
    main()