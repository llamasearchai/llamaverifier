"""
Tests for the ProofSystem class
"""

import os
import tempfile
from unittest import TestCase, mock

import pytest

from llamaverifier.proofs.generator import ProofSystem
from llamaverifier.proofs.schemes import SchemeType


class TestProofSystem(TestCase):
    """Test cases for the ProofSystem class"""

    def setUp(self):
        """Set up test fixtures"""
        self.proof_system = ProofSystem()

        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        # Create a dummy circuit file
        self.circuit_path = os.path.join(self.temp_dir.name, "circuit.zok")
        with open(self.circuit_path, "w") as f:
            f.write(
                "def main(private field a, private field b, public field c) -> bool:\n"
            )
            f.write("    return a * b == c\n")

        # Create dummy witness values
        self.witness_path = os.path.join(self.temp_dir.name, "witness.json")
        with open(self.witness_path, "w") as f:
            f.write('{"a": 3, "b": 4, "c": 12}\n')

    def test_init(self):
        """Test initialization of ProofSystem"""
        proof_system = ProofSystem()
        self.assertIsNotNone(proof_system)

        # Test with workspace_dir
        workspace_dir = os.path.join(self.temp_dir.name, "workspace")
        proof_system = ProofSystem(workspace_dir=workspace_dir)
        self.assertEqual(proof_system.workspace_dir, workspace_dir)

        # Test with scheme
        proof_system = ProofSystem(scheme="groth16")
        self.assertEqual(proof_system.scheme, "groth16")

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_setup(self, mock_run):
        """Test setup method"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(
            returncode=0, stdout="Setup successful", stderr=""
        )

        # Test setup
        pk_path, vk_path = self.proof_system.setup(circuit_path=self.circuit_path)

        # Check result
        self.assertIsNotNone(pk_path)
        self.assertIsNotNone(vk_path)

        # Check that subprocess.run was called
        mock_run.assert_called()

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_setup_failure(self, mock_run):
        """Test setup failure"""
        # Mock subprocess.run to return failure
        mock_run.return_value = mock.Mock(
            returncode=1, stdout="", stderr="Setup failed"
        )

        # Test setup
        with self.assertRaises(RuntimeError):
            self.proof_system.setup(circuit_path=self.circuit_path)

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_generate_proof(self, mock_run):
        """Test generate_proof method"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(
            returncode=0, stdout="Proof generation successful", stderr=""
        )

        # Create dummy proving key
        pk_path = os.path.join(self.temp_dir.name, "proving.key")
        with open(pk_path, "w") as f:
            f.write("dummy proving key")

        # Test generate_proof
        proof_path, public_inputs_path = self.proof_system.generate_proof(
            circuit_path=self.circuit_path,
            witness_path=self.witness_path,
            proving_key_path=pk_path,
        )

        # Check result
        self.assertIsNotNone(proof_path)
        self.assertIsNotNone(public_inputs_path)

        # Check that subprocess.run was called
        mock_run.assert_called()

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_generate_proof_failure(self, mock_run):
        """Test generate_proof failure"""
        # Mock subprocess.run to return failure
        mock_run.return_value = mock.Mock(
            returncode=1, stdout="", stderr="Proof generation failed"
        )

        # Create dummy proving key
        pk_path = os.path.join(self.temp_dir.name, "proving.key")
        with open(pk_path, "w") as f:
            f.write("dummy proving key")

        # Test generate_proof
        with self.assertRaises(RuntimeError):
            self.proof_system.generate_proof(
                circuit_path=self.circuit_path,
                witness_path=self.witness_path,
                proving_key_path=pk_path,
            )

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_verify_proof(self, mock_run):
        """Test verify_proof method"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(
            returncode=0, stdout="Verification successful", stderr=""
        )

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

        # Test verify_proof
        result = self.proof_system.verify_proof(
            verification_key_path=vk_path,
            proof_path=proof_path,
            public_inputs_path=public_inputs_path,
        )

        # Check result
        self.assertTrue(result)

        # Check that subprocess.run was called
        mock_run.assert_called()

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_verify_proof_failure(self, mock_run):
        """Test verify_proof failure"""
        # Mock subprocess.run to return failure
        mock_run.return_value = mock.Mock(
            returncode=1, stdout="", stderr="Verification failed"
        )

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

        # Test verify_proof
        result = self.proof_system.verify_proof(
            verification_key_path=vk_path,
            proof_path=proof_path,
            public_inputs_path=public_inputs_path,
        )

        # Check result
        self.assertFalse(result)

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_export_verifier(self, mock_run):
        """Test export_verifier method"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(
            returncode=0, stdout="Export successful", stderr=""
        )

        # Create dummy verification key
        vk_path = os.path.join(self.temp_dir.name, "verification.key")
        with open(vk_path, "w") as f:
            f.write("dummy verification key")

        # Test export_verifier
        verifier_path = self.proof_system.export_verifier(verification_key_path=vk_path)

        # Check result
        self.assertIsNotNone(verifier_path)

        # Check that subprocess.run was called
        mock_run.assert_called()

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_export_verifier_failure(self, mock_run):
        """Test export_verifier failure"""
        # Mock subprocess.run to return failure
        mock_run.return_value = mock.Mock(
            returncode=1, stdout="", stderr="Export failed"
        )

        # Create dummy verification key
        vk_path = os.path.join(self.temp_dir.name, "verification.key")
        with open(vk_path, "w") as f:
            f.write("dummy verification key")

        # Test export_verifier
        with self.assertRaises(RuntimeError):
            self.proof_system.export_verifier(verification_key_path=vk_path)

    def test_scheme_type_enum(self):
        """Test SchemeType enum"""
        self.assertEqual(SchemeType.GROTH16.value, "groth16")
        self.assertEqual(SchemeType.GM17.value, "gm17")
        self.assertEqual(SchemeType.MARLIN.value, "marlin")
