"""
Tests for the CLI commands module
"""
import os
import tempfile
from unittest import TestCase, mock
from typer.testing import CliRunner

import pytest

from llamaverifier.cli.commands import app


class TestCLICommands(TestCase):
    """Test cases for the CLI commands"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.runner = CliRunner()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        
        # Create a dummy model file
        self.model_path = os.path.join(self.temp_dir.name, "model.txt")
        with open(self.model_path, "w") as f:
            f.write("# Dummy model file\n")
            f.write("param_1=1\n")
            f.write("param_2=2\n")
        
        # Create a dummy input file
        self.input_path = os.path.join(self.temp_dir.name, "input.json")
        with open(self.input_path, "w") as f:
            f.write('{"input": [1, 2, 3]}\n')
        
        # Create a dummy output file
        self.output_path = os.path.join(self.temp_dir.name, "output.json")
        with open(self.output_path, "w") as f:
            f.write('{"output": [3, 2, 1]}\n')
        
        # Create a dummy circuit file
        self.circuit_path = os.path.join(self.temp_dir.name, "circuit.zok")
        with open(self.circuit_path, "w") as f:
            f.write("def main(private field a, private field b, public field c) -> bool:\n")
            f.write("    return a * b == c\n")
    
    @mock.patch("llamaverifier.cli.commands.print_banner")
    @mock.patch("llamaverifier.cli.commands.print_system_info")
    def test_info_command(self, mock_print_system_info, mock_print_banner):
        """Test info command"""
        # Run the command
        result = self.runner.invoke(app, ["info"])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that the banner and system info were printed
        mock_print_banner.assert_called_once()
        mock_print_system_info.assert_called_once()
    
    @mock.patch("llamaverifier.cli.commands.ZKPCompiler")
    def test_compile_command(self, mock_compiler_class):
        """Test compile command"""
        # Mock the compiler
        mock_compiler = mock.MagicMock()
        mock_compiler.compile_model.return_value = True
        mock_compiler_class.return_value = mock_compiler
        
        # Run the command
        result = self.runner.invoke(app, [
            "compile",
            "--model", self.model_path,
            "--output", os.path.join(self.temp_dir.name, "circuit.out"),
            "--model-type", "generic",
            "--optimization", "1"
        ])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that the compiler was called
        mock_compiler.compile_model.assert_called_once()
    
    @mock.patch("llamaverifier.cli.commands.ProofSystem")
    def test_setup_command(self, mock_proof_system_class):
        """Test setup command"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.setup.return_value = ("pk.key", "vk.key")
        mock_proof_system_class.return_value = mock_proof_system
        
        # Run the command
        result = self.runner.invoke(app, [
            "setup",
            "--circuit", self.circuit_path,
            "--output-dir", self.temp_dir.name,
            "--scheme", "groth16"
        ])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that the proof system was called
        mock_proof_system.setup.assert_called_once()
    
    @mock.patch("llamaverifier.cli.commands.ProofSystem")
    def test_prove_command(self, mock_proof_system_class):
        """Test prove command"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.generate_proof.return_value = ("proof.json", "public.json")
        mock_proof_system_class.return_value = mock_proof_system
        
        # Create dummy proving key
        pk_path = os.path.join(self.temp_dir.name, "proving.key")
        with open(pk_path, "w") as f:
            f.write("dummy proving key")
        
        # Run the command
        result = self.runner.invoke(app, [
            "prove",
            "--circuit", self.circuit_path,
            "--witness", self.input_path,
            "--proving-key", pk_path,
            "--output-dir", self.temp_dir.name,
            "--scheme", "groth16"
        ])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that the proof system was called
        mock_proof_system.generate_proof.assert_called_once()
    
    @mock.patch("llamaverifier.cli.commands.ProofSystem")
    def test_verify_proof_command(self, mock_proof_system_class):
        """Test verify_proof command"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.verify_proof.return_value = True
        mock_proof_system_class.return_value = mock_proof_system
        
        # Create dummy verification key
        vk_path = os.path.join(self.temp_dir.name, "verification.key")
        with open(vk_path, "w") as f:
            f.write("dummy verification key")
        
        # Create dummy proof
        proof_path = os.path.join(self.temp_dir.name, "proof.json")
        with open(proof_path, "w") as f:
            f.write('{"proof": "dummy proof"}\n')
        
        # Create dummy public inputs
        public_inputs_path = os.path.join(self.temp_dir.name, "public.json")
        with open(public_inputs_path, "w") as f:
            f.write('{"c": 12}\n')
        
        # Run the command
        result = self.runner.invoke(app, [
            "verify-proof",
            "--verification-key", vk_path,
            "--proof", proof_path,
            "--public-inputs", public_inputs_path,
            "--scheme", "groth16"
        ])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that the proof system was called
        mock_proof_system.verify_proof.assert_called_once()
    
    @mock.patch("llamaverifier.cli.commands.ProofSystem")
    def test_export_command(self, mock_proof_system_class):
        """Test export command"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.export_verifier.return_value = "verifier.sol"
        mock_proof_system_class.return_value = mock_proof_system
        
        # Create dummy verification key
        vk_path = os.path.join(self.temp_dir.name, "verification.key")
        with open(vk_path, "w") as f:
            f.write("dummy verification key")
        
        # Run the command
        result = self.runner.invoke(app, [
            "export",
            "--verification-key", vk_path,
            "--output-dir", self.temp_dir.name,
            "--scheme", "groth16"
        ])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that the proof system was called
        mock_proof_system.export_verifier.assert_called_once()
    
    @mock.patch("llamaverifier.cli.commands.ZKPCompiler")
    @mock.patch("llamaverifier.cli.commands.ProofSystem")
    def test_verify_command(self, mock_proof_system_class, mock_compiler_class):
        """Test verify command (end-to-end)"""
        # Mock the compiler
        mock_compiler = mock.MagicMock()
        mock_compiler.compile_model.return_value = True
        mock_compiler_class.return_value = mock_compiler
        
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.setup.return_value = ("pk.key", "vk.key")
        mock_proof_system.generate_proof.return_value = ("proof.json", "public.json")
        mock_proof_system.verify_proof.return_value = True
        mock_proof_system_class.return_value = mock_proof_system
        
        # Run the command
        result = self.runner.invoke(app, [
            "verify",
            "--model", self.model_path,
            "--input", self.input_path,
            "--expected-output", self.output_path,
            "--model-type", "generic",
            "--scheme", "groth16",
            "--output-dir", self.temp_dir.name
        ])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that the compiler and proof system were called
        mock_compiler.compile_model.assert_called_once()
        mock_proof_system.setup.assert_called_once()
        mock_proof_system.generate_proof.assert_called_once()
        mock_proof_system.verify_proof.assert_called_once()
    
    @mock.patch("llamaverifier.cli.commands.uvicorn.run")
    def test_server_command(self, mock_run):
        """Test server command"""
        # Run the command
        result = self.runner.invoke(app, [
            "server",
            "--host", "127.0.0.1",
            "--port", "8000"
        ])
        
        # Check result
        self.assertEqual(result.exit_code, 0)
        
        # Check that uvicorn.run was called
        mock_run.assert_called_once() 