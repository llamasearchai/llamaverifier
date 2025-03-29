"""
Circuit optimization utilities for LlamaVerifier
"""
import os
import subprocess
import tempfile
from enum import Enum, IntEnum
from pathlib import Path
from typing import Optional, Union

from ..utils.logger import get_logger

logger = get_logger(__name__)


class OptimizationLevel(IntEnum):
    """Optimization levels for circuit compilation"""
    LEVEL_0 = 0  # No optimization
    LEVEL_1 = 1  # Basic optimizations
    LEVEL_2 = 2  # Intermediate optimizations
    LEVEL_3 = 3  # Aggressive optimizations


def optimize_circuit(
    circuit_path: Union[str, Path],
    optimization_level: OptimizationLevel = OptimizationLevel.LEVEL_1
) -> str:
    """
    Apply optimizations to a compiled circuit.
    
    Args:
        circuit_path: Path to the compiled circuit
        optimization_level: Level of optimization to apply
        
    Returns:
        Path to the optimized circuit (may be the same as input if no optimizations were applied)
    """
    if optimization_level == OptimizationLevel.LEVEL_0:
        # No optimizations
        logger.info("Skipping circuit optimization (level 0)")
        return str(circuit_path)
    
    logger.info(f"Optimizing circuit with level {optimization_level.value}")
    
    # Ensure circuit file exists
    if not os.path.exists(circuit_path):
        logger.error(f"Circuit file not found: {circuit_path}")
        return str(circuit_path)
    
    # Create a temporary file for the optimized circuit
    with tempfile.NamedTemporaryFile(suffix=".out", delete=False) as temp_file:
        optimized_path = temp_file.name
    
    try:
        circuit_path_str = str(circuit_path)
        
        # Apply different optimization strategies based on the level
        if optimization_level == OptimizationLevel.LEVEL_1:
            _apply_basic_optimizations(circuit_path_str, optimized_path)
        elif optimization_level == OptimizationLevel.LEVEL_2:
            _apply_intermediate_optimizations(circuit_path_str, optimized_path)
        elif optimization_level == OptimizationLevel.LEVEL_3:
            _apply_aggressive_optimizations(circuit_path_str, optimized_path)
        
        logger.info(f"Circuit optimization completed: {optimized_path}")
        return optimized_path
    except Exception as e:
        logger.error(f"Error optimizing circuit: {e}")
        # If optimization fails, return the original circuit path
        if os.path.exists(optimized_path):
            os.unlink(optimized_path)
        return str(circuit_path)


def _apply_basic_optimizations(input_path: str, output_path: str) -> bool:
    """
    Apply basic optimizations (level 1) to a circuit.
    
    Args:
        input_path: Path to the input circuit
        output_path: Path to save the optimized circuit
        
    Returns:
        True if optimization was successful, False otherwise
    """
    try:
        # For ZoKrates circuits, use ZoKrates optimizer
        result = subprocess.run(
            ["zokrates", "optimize", "--input", input_path, "--output", output_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.debug(f"Basic optimization output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Basic optimization error: {e.stderr}")
        # Copy the original file to the output path
        with open(input_path, "rb") as src, open(output_path, "wb") as dst:
            dst.write(src.read())
        return False


def _apply_intermediate_optimizations(input_path: str, output_path: str) -> bool:
    """
    Apply intermediate optimizations (level 2) to a circuit.
    
    Args:
        input_path: Path to the input circuit
        output_path: Path to save the optimized circuit
        
    Returns:
        True if optimization was successful, False otherwise
    """
    # First apply basic optimizations
    if not _apply_basic_optimizations(input_path, output_path):
        return False
    
    try:
        # For ZoKrates circuits, use additional optimizations
        # This would typically involve more sophisticated optimization techniques
        # For demonstration, we'll just use a placeholder with additional flags
        result = subprocess.run(
            ["zokrates", "optimize", "--input", output_path, "--output", output_path, "--stage", "2"],
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.debug(f"Intermediate optimization output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Intermediate optimization error: {e.stderr}")
        return False


def _apply_aggressive_optimizations(input_path: str, output_path: str) -> bool:
    """
    Apply aggressive optimizations (level 3) to a circuit.
    
    Args:
        input_path: Path to the input circuit
        output_path: Path to save the optimized circuit
        
    Returns:
        True if optimization was successful, False otherwise
    """
    # First apply intermediate optimizations
    if not _apply_intermediate_optimizations(input_path, output_path):
        return False
    
    try:
        # For ZoKrates circuits, use the most aggressive optimizations
        # This would involve techniques like circuit flattening, common subexpression elimination, etc.
        # For demonstration, we'll just use a placeholder with additional flags
        result = subprocess.run(
            ["zokrates", "optimize", "--input", output_path, "--output", output_path, "--stage", "3", "--experimental"],
            check=True,
            capture_output=True,
            text=True
        )
        
        logger.debug(f"Aggressive optimization output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Aggressive optimization error: {e.stderr}")
        return False 