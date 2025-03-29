"""
System utility functions for LlamaVerifier
"""
import os
import platform
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

import psutil

from .logger import get_logger

logger = get_logger(__name__)


def is_apple_silicon() -> bool:
    """
    Check if the system is running on Apple Silicon (ARM64).
    
    Returns:
        True if running on Apple Silicon, False otherwise
    """
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def get_system_info() -> Dict[str, str]:
    """
    Get information about the system.
    
    Returns:
        Dictionary containing system information
    """
    info = {
        "os": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": str(os.cpu_count()),
        "processor": platform.processor() or "Unknown"
    }
    
    # Add Apple Silicon specific information
    if is_apple_silicon():
        info["processor"] = "Apple Silicon (ARM64)"
        info["mlx_accelerated"] = "Enabled" if is_mlx_available() else "Disabled"
    else:
        info["mlx_accelerated"] = "Disabled (Not Apple Silicon)"
    
    # Add memory information
    mem = psutil.virtual_memory()
    info["total_memory"] = f"{mem.total / (1024**3):.2f} GB"
    info["available_memory"] = f"{mem.available / (1024**3):.2f} GB"
    
    # Add disk information
    disk = psutil.disk_usage("/")
    info["total_disk"] = f"{disk.total / (1024**3):.2f} GB"
    info["free_disk"] = f"{disk.free / (1024**3):.2f} GB"
    
    return info


def is_mlx_available() -> bool:
    """
    Check if MLX is available on the system.
    
    Returns:
        True if MLX is available, False otherwise
    """
    if not is_apple_silicon():
        return False
    
    try:
        import mlx
        return True
    except ImportError:
        return False


def get_gpu_info() -> Dict[str, str]:
    """
    Get information about the GPU.
    
    Returns:
        Dictionary containing GPU information, or empty dict if not available
    """
    if platform.system() == "Darwin":
        try:
            # On macOS, use system_profiler
            cmd = ["system_profiler", "SPDisplaysDataType"]
            output = subprocess.check_output(cmd, universal_newlines=True)
            
            # Parse output (simplified)
            info = {}
            for line in output.split("\n"):
                line = line.strip()
                if "Chipset Model" in line:
                    info["model"] = line.split(":", 1)[1].strip()
                elif "VRAM" in line:
                    info["vram"] = line.split(":", 1)[1].strip()
            
            return info
        except Exception as e:
            logger.warning(f"Failed to get GPU info: {e}")
            return {}
    elif platform.system() == "Linux":
        try:
            # On Linux, use lspci
            cmd = ["lspci", "-v"]
            output = subprocess.check_output(cmd, universal_newlines=True)
            
            # Parse output (simplified)
            for line in output.split("\n"):
                if "VGA" in line or "3D" in line:
                    return {"model": line.split(":", 1)[1].strip()}
            
            return {}
        except Exception as e:
            logger.warning(f"Failed to get GPU info: {e}")
            return {}
    else:
        # Windows or other systems not implemented
        return {}


def check_dependencies() -> List[Tuple[str, bool]]:
    """
    Check if all required external dependencies are installed.
    
    Returns:
        List of tuples (dependency_name, is_installed)
    """
    dependencies = []
    
    # Check for ZoKrates
    try:
        output = subprocess.check_output(["zokrates", "--version"], 
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
        dependencies.append(("ZoKrates", True))
    except (subprocess.SubprocessError, FileNotFoundError):
        dependencies.append(("ZoKrates", False))
    
    # Check for Python packages
    required_packages = ["zokrates_pycrypto", "py_ecc", "typer", "rich", "fastapi", "pydantic"]
    for package in required_packages:
        try:
            __import__(package)
            dependencies.append((package, True))
        except ImportError:
            dependencies.append((package, False))
    
    return dependencies 