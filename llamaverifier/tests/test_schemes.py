"""
Tests for the schemes module
"""

import os
import tempfile
from unittest import TestCase, mock

import pytest

from llamaverifier.proofs.schemes import (
    BaseScheme,
    GM17Scheme,
    Groth16Scheme,
    MarlinScheme,
    SchemeType,
    get_scheme,
)


class TestSchemes(TestCase):
    """Test cases for the schemes module"""

    def setUp(self):
        """Set up test fixtures"""
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

    def test_scheme_type_enum(self):
        """Test SchemeType enum"""
        self.assertEqual(SchemeType.GROTH16.value, "groth16")
        self.assertEqual(SchemeType.GM17.value, "gm17")
        self.assertEqual(SchemeType.MARLIN.value, "marlin")

    def test_get_scheme(self):
        """Test get_scheme function"""
        # Test getting Groth16 scheme
        scheme = get_scheme("groth16")
        self.assertIsInstance(scheme, Groth16Scheme)

        # Test getting GM17 scheme
        scheme = get_scheme("gm17")
        self.assertIsInstance(scheme, GM17Scheme)

        # Test getting Marlin scheme
        scheme = get_scheme("marlin")
        self.assertIsInstance(scheme, MarlinScheme)

        # Test getting default scheme
        scheme = get_scheme(None)
        self.assertIsInstance(scheme, Groth16Scheme)

        # Test getting invalid scheme
        with self.assertRaises(ValueError):
            get_scheme("invalid_scheme")

    def test_base_scheme(self):
        """Test BaseScheme class"""
        # Create a BaseScheme instance
        scheme = BaseScheme()

        # Test setup method
        with self.assertRaises(NotImplementedError):
            scheme.setup(self.circuit_path)

        # Test generate_proof method
        with self.assertRaises(NotImplementedError):
            scheme.generate_proof(self.circuit_path, self.witness_path, "pk.key")

        # Test verify_proof method
        with self.assertRaises(NotImplementedError):
            scheme.verify_proof("vk.key", "proof.json", "public.json")

        # Test export_verifier method
        with self.assertRaises(NotImplementedError):
            scheme.export_verifier("vk.key")

    @mock.patch("llamaverifier.proofs.schemes.subprocess.run")
    def test_groth16_scheme(self, mock_run):
        """Test Groth16Scheme class"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(returncode=0, stdout="Success", stderr="")

        # Create a Groth16Scheme instance
        scheme = Groth16Scheme()

        # Test setup method
        pk_path, vk_path = scheme.setup(self.circuit_path)
        self.assertIsNotNone(pk_path)
        self.assertIsNotNone(vk_path)

        # Test generate_proof method
        proof_path, public_inputs_path = scheme.generate_proof(
            self.circuit_path, self.witness_path, "pk.key"
        )
        self.assertIsNotNone(proof_path)
        self.assertIsNotNone(public_inputs_path)

        # Test verify_proof method
        result = scheme.verify_proof("vk.key", "proof.json", "public.json")
        self.assertTrue(result)

        # Test export_verifier method
        verifier_path = scheme.export_verifier("vk.key")
        self.assertIsNotNone(verifier_path)

    @mock.patch("llamaverifier.proofs.schemes.subprocess.run")
    def test_gm17_scheme(self, mock_run):
        """Test GM17Scheme class"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(returncode=0, stdout="Success", stderr="")

        # Create a GM17Scheme instance
        scheme = GM17Scheme()

        # Test setup method
        pk_path, vk_path = scheme.setup(self.circuit_path)
        self.assertIsNotNone(pk_path)
        self.assertIsNotNone(vk_path)

        # Test generate_proof method
        proof_path, public_inputs_path = scheme.generate_proof(
            self.circuit_path, self.witness_path, "pk.key"
        )
        self.assertIsNotNone(proof_path)
        self.assertIsNotNone(public_inputs_path)

        # Test verify_proof method
        result = scheme.verify_proof("vk.key", "proof.json", "public.json")
        self.assertTrue(result)

        # Test export_verifier method
        verifier_path = scheme.export_verifier("vk.key")
        self.assertIsNotNone(verifier_path)

    @mock.patch("llamaverifier.proofs.schemes.subprocess.run")
    def test_marlin_scheme(self, mock_run):
        """Test MarlinScheme class"""
        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(returncode=0, stdout="Success", stderr="")

        # Create a MarlinScheme instance
        scheme = MarlinScheme()

        # Test setup method
        pk_path, vk_path = scheme.setup(self.circuit_path)
        self.assertIsNotNone(pk_path)
        self.assertIsNotNone(vk_path)

        # Test generate_proof method
        proof_path, public_inputs_path = scheme.generate_proof(
            self.circuit_path, self.witness_path, "pk.key"
        )
        self.assertIsNotNone(proof_path)
        self.assertIsNotNone(public_inputs_path)

        # Test verify_proof method
        result = scheme.verify_proof("vk.key", "proof.json", "public.json")
        self.assertTrue(result)

        # Test export_verifier method
        verifier_path = scheme.export_verifier("vk.key")
        self.assertIsNotNone(verifier_path)

    @mock.patch("llamaverifier.proofs.schemes.subprocess.run")
    def test_scheme_failure(self, mock_run):
        """Test scheme failure handling"""
        # Mock subprocess.run to return failure
        mock_run.return_value = mock.Mock(returncode=1, stdout="", stderr="Error")

        # Create a Groth16Scheme instance
        scheme = Groth16Scheme()

        # Test setup method
        with self.assertRaises(RuntimeError):
            scheme.setup(self.circuit_path)

        # Test generate_proof method
        with self.assertRaises(RuntimeError):
            scheme.generate_proof(self.circuit_path, self.witness_path, "pk.key")

        # Test verify_proof method
        self.assertFalse(scheme.verify_proof("vk.key", "proof.json", "public.json"))

        # Test export_verifier method
        with self.assertRaises(RuntimeError):
            scheme.export_verifier("vk.key")
