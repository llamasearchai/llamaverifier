"""
Tests for the API server module
"""
import os
import json
import tempfile
from unittest import TestCase, mock
from fastapi.testclient import TestClient

import pytest

from llamaverifier.api.server import app, VerificationRequest


class TestAPIServer(TestCase):
    """Test cases for the API server"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        
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
        self.input_data = {"input": [1, 2, 3]}
        self.input_path = os.path.join(self.temp_dir.name, "input.json")
        with open(self.input_path, "w") as f:
            json.dump(self.input_data, f)
        
        # Create a dummy output file
        self.output_data = {"output": [3, 2, 1]}
        self.output_path = os.path.join(self.temp_dir.name, "output.json")
        with open(self.output_path, "w") as f:
            json.dump(self.output_data, f)
        
        # Create a dummy circuit file
        self.circuit_path = os.path.join(self.temp_dir.name, "circuit.zok")
        with open(self.circuit_path, "w") as f:
            f.write("def main(private field a, private field b, public field c) -> bool:\n")
            f.write("    return a * b == c\n")
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome to LlamaVerifier API", response.json()["message"])
    
    def test_info_endpoint(self):
        """Test info endpoint"""
        response = self.client.get("/info")
        self.assertEqual(response.status_code, 200)
        self.assertIn("version", response.json())
        self.assertIn("system_info", response.json())
    
    @mock.patch("llamaverifier.api.server.ZKPCompiler")
    def test_compile_endpoint(self, mock_compiler_class):
        """Test compile endpoint"""
        # Mock the compiler
        mock_compiler = mock.MagicMock()
        mock_compiler.compile_model.return_value = True
        mock_compiler_class.return_value = mock_compiler
        
        # Create test files
        with open(self.model_path, "rb") as model_file:
            # Test the endpoint
            response = self.client.post(
                "/compile",
                files={
                    "model_file": ("model.txt", model_file, "text/plain")
                },
                data={
                    "model_type": "generic",
                    "optimization_level": "1"
                }
            )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn("circuit_id", response.json())
        self.assertTrue(response.json()["success"])
        
        # Check that the compiler was called
        mock_compiler.compile_model.assert_called_once()
    
    @mock.patch("llamaverifier.api.server.ProofSystem")
    def test_setup_endpoint(self, mock_proof_system_class):
        """Test setup endpoint"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.setup.return_value = ("pk.key", "vk.key")
        mock_proof_system_class.return_value = mock_proof_system
        
        # Add a circuit to the in-memory storage
        with open(self.circuit_path, "rb") as circuit_file:
            circuit_content = circuit_file.read()
        
        # Mock the circuits dictionary
        from llamaverifier.api.server import circuits
        circuit_id = "test-circuit-id"
        circuits[circuit_id] = circuit_content
        
        # Test the endpoint
        response = self.client.post(
            f"/setup/{circuit_id}",
            json={"scheme": "groth16"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn("proving_key_id", response.json())
        self.assertIn("verification_key_id", response.json())
        self.assertTrue(response.json()["success"])
        
        # Check that the proof system was called
        mock_proof_system.setup.assert_called_once()
    
    @mock.patch("llamaverifier.api.server.ProofSystem")
    def test_generate_proof_endpoint(self, mock_proof_system_class):
        """Test generate-proof endpoint"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.generate_proof.return_value = ("proof.json", "public.json")
        mock_proof_system_class.return_value = mock_proof_system
        
        # Add a circuit and proving key to the in-memory storage
        from llamaverifier.api.server import circuits, proving_keys
        circuit_id = "test-circuit-id"
        proving_key_id = "test-pk-id"
        
        with open(self.circuit_path, "rb") as circuit_file:
            circuits[circuit_id] = circuit_file.read()
        
        proving_keys[proving_key_id] = b"dummy proving key"
        
        # Test the endpoint
        response = self.client.post(
            f"/generate-proof/{circuit_id}",
            json={
                "witness": self.input_data,
                "proving_key_id": proving_key_id,
                "scheme": "groth16"
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn("proof_id", response.json())
        self.assertIn("public_inputs_id", response.json())
        self.assertTrue(response.json()["success"])
        
        # Check that the proof system was called
        mock_proof_system.generate_proof.assert_called_once()
    
    @mock.patch("llamaverifier.api.server.ProofSystem")
    def test_verify_endpoint(self, mock_proof_system_class):
        """Test verify endpoint"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.verify_proof.return_value = True
        mock_proof_system_class.return_value = mock_proof_system
        
        # Add verification key, proof, and public inputs to the in-memory storage
        from llamaverifier.api.server import verification_keys, proofs, public_inputs
        verification_key_id = "test-vk-id"
        proof_id = "test-proof-id"
        public_inputs_id = "test-public-id"
        
        verification_keys[verification_key_id] = b"dummy verification key"
        proofs[proof_id] = b'{"proof": "dummy proof"}'
        public_inputs[public_inputs_id] = b'{"c": 12}'
        
        # Test the endpoint
        response = self.client.post(
            "/verify",
            json={
                "verification_key_id": verification_key_id,
                "proof_id": proof_id,
                "public_inputs_id": public_inputs_id,
                "scheme": "groth16"
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])
        self.assertTrue(response.json()["success"])
        
        # Check that the proof system was called
        mock_proof_system.verify_proof.assert_called_once()
    
    @mock.patch("llamaverifier.api.server.ProofSystem")
    def test_export_verifier_endpoint(self, mock_proof_system_class):
        """Test export-verifier endpoint"""
        # Mock the proof system
        mock_proof_system = mock.MagicMock()
        mock_proof_system.export_verifier.return_value = "verifier.sol"
        mock_proof_system_class.return_value = mock_proof_system
        
        # Add verification key to the in-memory storage
        from llamaverifier.api.server import verification_keys
        verification_key_id = "test-vk-id"
        
        verification_keys[verification_key_id] = b"dummy verification key"
        
        # Test the endpoint
        response = self.client.post(
            f"/export-verifier/{verification_key_id}",
            json={"scheme": "groth16"}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertIn("verifier_contract", response.json())
        self.assertTrue(response.json()["success"])
        
        # Check that the proof system was called
        mock_proof_system.export_verifier.assert_called_once()
    
    @mock.patch("llamaverifier.api.server.ZKPCompiler")
    @mock.patch("llamaverifier.api.server.ProofSystem")
    def test_verify_model_endpoint(self, mock_proof_system_class, mock_compiler_class):
        """Test verify model endpoint (end-to-end)"""
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
        
        # Create the verification request
        verification_request = VerificationRequest(
            model_type="generic",
            input_data=self.input_data,
            expected_output=self.output_data,
            scheme="groth16"
        )
        
        # Test the endpoint
        with open(self.model_path, "rb") as model_file:
            response = self.client.post(
                "/verify-model",
                files={
                    "model_file": ("model.txt", model_file, "text/plain")
                },
                data={
                    "request": json.dumps(verification_request.dict())
                }
            )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["valid"])
        self.assertTrue(response.json()["success"])
        
        # Check that the compiler and proof system were called
        mock_compiler.compile_model.assert_called_once()
        mock_proof_system.setup.assert_called_once()
        mock_proof_system.generate_proof.assert_called_once()
        mock_proof_system.verify_proof.assert_called_once() 