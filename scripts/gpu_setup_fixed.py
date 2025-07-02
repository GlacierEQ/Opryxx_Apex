"""
GPU Setup and Installation Helper
Automatically installs GPU drivers and libraries
"""

import subprocess
import platform
import sys

def install_wmi():
    """Install WMI for Windows GPU detection"""
    if platform.system() == "Windows":
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'wmi'], check=True)
            print("[OK] WMI installed")
        except:
            print("[WARNING] WMI installation failed")

def install_opencl():
    """Install OpenCL support"""
    print("Installing OpenCL...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyopencl'], check=True)
        print("[OK] OpenCL installed")
    except:
        print("[WARNING] OpenCL installation failed")

def install_cuda_toolkit():
    """Install CUDA toolkit"""
    print("Installing CUDA toolkit...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'torch', 'torchvision', 'torchaudio', 
                       '--index-url', 'https://download.pytorch.org/whl/cu121'], 
                      check=True)
        print("[OK] PyTorch with CUDA installed")
    except:
        print("[WARNING] CUDA installation failed, installing CPU version")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 
                       'torch', 'torchvision', 'torchaudio'], check=True)

def main():
    print("GPU Setup and Elevation")
    print("=" * 30)
    
    install_wmi()
    install_opencl()
    install_cuda_toolkit()
    
    print("\nTesting GPU detection...")
    try:
        from core.gpu_detector import gpu_detector
        gpus = gpu_detector.detect_all_gpus()
        
        if gpus:
            print(f"[OK] Found {len(gpus)} GPU(s):")
            for gpu in gpus:
                print(f"   - {gpu.name} ({gpu.memory_mb}MB) via {gpu.backend}")
        else:
            print("[ERROR] No GPUs detected")
            print("\nTroubleshooting:")
            print("   1. Install GPU drivers")
            print("   2. Restart system")
            print("   3. Run as administrator")
    
    except Exception as e:
        print(f"[ERROR] GPU detection test failed: {e}")
    
    print("\n[OK] GPU setup complete!")

if __name__ == "__main__":
    main()