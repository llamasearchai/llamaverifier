"""
Tests for the ZKPCompiler class
"""
import os
import tempfile
from unittest import TestCase, mock

import pytest

from llamaverifier.circuits import ZKPCompiler, ModelType, OptimizationLevel


class TestZKPCompiler(TestCase):
    """Test cases for the ZKPCompiler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.compiler = ZKPCompiler()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        
        # Create a dummy model file
        self.model_path = os.path.join(self.temp_dir.name, "model.txt")
        with open(self.model_path, "w") as f:
            f.write("# Dummy model file\n")
            f.write("param_1=1\n")
            f.write("param_2=2\n")
        
        # Output path for compiled circuit
        self.output_path = os.path.join(self.temp_dir.name, "circuit.out")
    
    def test_init(self):
        """Test initialization of ZKPCompiler"""
        compiler = ZKPCompiler()
        self.assertIsNotNone(compiler)
        
        # Test with workspace_dir
        workspace_dir = os.path.join(self.temp_dir.name, "workspace")
        compiler = ZKPCompiler(workspace_dir=workspace_dir)
        self.assertEqual(compiler.workspace_dir, workspace_dir)
    
    @mock.patch("llamaverifier.circuits.compiler.subprocess.run")
    def test_compile_model_generic(self, mock_run):
        """Test compiling a generic model"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(
            returncode=0,
            stdout="Compilation successful",
            stderr=""
        )
        
        # Test compilation
        result = self.compiler.compile_model(
            model_path=self.model_path,
            output_path=self.output_path,
            model_type="generic",
            optimization_level=1
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check that subprocess.run was called
        mock_run.assert_called()
    
    @mock.patch("llamaverifier.circuits.compiler.subprocess.run")
    def test_compile_model_llama(self, mock_run):
        """Test compiling a LLaMA model"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(
            returncode=0,
            stdout="Compilation successful",
            stderr=""
        )
        
        # Test compilation
        result = self.compiler.compile_model(
            model_path=self.model_path,
            output_path=self.output_path,
            model_type="llama",
            optimization_level=1
        )
        
        # Check result
        self.assertTrue(result)
        
        # Check that subprocess.run was called
        mock_run.assert_called()
    
    @mock.patch("llamaverifier.circuits.compiler.subprocess.run")
    def test_compile_model_failure(self, mock_run):
        """Test compilation failure"""
        # Mock subprocess.run to return failure
        mock_run.return_value = mock.Mock(
            returncode=1,
            stdout="",
            stderr="Compilation failed"
        )
        
        # Test compilation
        result = self.compiler.compile_model(
            model_path=self.model_path,
            output_path=self.output_path,
            model_type="generic",
            optimization_level=1
        )
        
        # Check result
        self.assertFalse(result)
    
    def test_compile_model_nonexistent_file(self):
        """Test compiling a nonexistent model file"""
        # Test compilation with nonexistent file
        result = self.compiler.compile_model(
            model_path="nonexistent.txt",
            output_path=self.output_path,
            model_type="generic",
            optimization_level=1
        )
        
        # Check result
        self.assertFalse(result)
    
    def test_model_type_enum(self):
        """Test ModelType enum"""
        self.assertEqual(ModelType.GENERIC.value, "generic")
        self.assertEqual(ModelType.LLAMA.value, "llama")
        self.assertEqual(ModelType.TRANSFORMER.value, "transformer")
        self.assertEqual(ModelType.ONNX.value, "onnx")
        self.assertEqual(ModelType.PYTORCH.value, "pytorch")
    
    def test_optimization_level_enum(self):
        """Test OptimizationLevel enum"""
        self.assertEqual(OptimizationLevel.LEVEL_0.value, 0)
        self.assertEqual(OptimizationLevel.LEVEL_1.value, 1)
        self.assertEqual(OptimizationLevel.LEVEL_2.value, 2)
        self.assertEqual(OptimizationLevel.LEVEL_3.value, 3) 