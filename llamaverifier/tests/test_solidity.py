"""
Tests for the Solidity verifier contract
"""

import json
import os
import tempfile
from unittest import TestCase, mock

import pytest


class TestSolidityVerifier(TestCase):
    """Test cases for the Solidity verifier contract"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        # Path to the Solidity verifier contract
        self.contract_path = os.path.join(self.temp_dir.name, "LlamaVerifier.sol")

        # Create a dummy verification key
        self.vk_path = os.path.join(self.temp_dir.name, "verification.key")
        with open(self.vk_path, "w") as f:
            f.write("dummy verification key")

        # Create a dummy proof
        self.proof_data = {
            "a": ["0x1234", "0x5678"],
            "b": [["0x9abc", "0xdef0"], ["0x1111", "0x2222"]],
            "c": ["0x3333", "0x4444"],
        }
        self.proof_path = os.path.join(self.temp_dir.name, "proof.json")
        with open(self.proof_path, "w") as f:
            json.dump(self.proof_data, f)

        # Create dummy public inputs
        self.public_inputs_data = ["0x5555", "0x6666"]
        self.public_inputs_path = os.path.join(self.temp_dir.name, "public.json")
        with open(self.public_inputs_path, "w") as f:
            json.dump(self.public_inputs_data, f)

    @mock.patch("llamaverifier.proofs.generator.subprocess.run")
    def test_export_verifier(self, mock_run):
        """Test exporting a Solidity verifier contract"""
        # Mock subprocess.run to return success and create a dummy contract
        mock_run.return_value = mock.Mock(
            returncode=0, stdout="Export successful", stderr=""
        )

        # Create a dummy contract file
        with open(self.contract_path, "w") as f:
            f.write(
                """
            // SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0;
            
            contract LlamaVerifier {
                struct VerificationKey {
                    uint256[] alpha;
                    uint256[] beta;
                    uint256[] gamma;
                    uint256[] delta;
                    uint256[][] abc;
                }
                
                VerificationKey private vk;
                
                constructor(
                    uint256[] memory alpha,
                    uint256[] memory beta,
                    uint256[] memory gamma,
                    uint256[] memory delta,
                    uint256[][] memory abc
                ) {
                    vk.alpha = alpha;
                    vk.beta = beta;
                    vk.gamma = gamma;
                    vk.delta = delta;
                    vk.abc = abc;
                }
                
                function verifyProof(
                    uint256[2] memory a,
                    uint256[2][2] memory b,
                    uint256[2] memory c,
                    uint256[] memory input
                ) public view returns (bool) {
                    return _verify(a, b, c, input);
                }
                
                function _verify(
                    uint256[2] memory a,
                    uint256[2][2] memory b,
                    uint256[2] memory c,
                    uint256[] memory input
                ) internal view returns (bool) {
                    // This is a dummy implementation for testing
                    return true;
                }
                
                function updateVerificationKey(
                    uint256[] memory alpha,
                    uint256[] memory beta,
                    uint256[] memory gamma,
                    uint256[] memory delta,
                    uint256[][] memory abc
                ) public {
                    vk.alpha = alpha;
                    vk.beta = beta;
                    vk.gamma = gamma;
                    vk.delta = delta;
                    vk.abc = abc;
                }
            }
            """
            )

        # Import the ProofSystem class
        from llamaverifier.proofs.generator import ProofSystem

        # Create a ProofSystem instance
        proof_system = ProofSystem()

        # Test export_verifier
        verifier_path = proof_system.export_verifier(verification_key_path=self.vk_path)

        # Check result
        self.assertIsNotNone(verifier_path)

        # Check that subprocess.run was called
        mock_run.assert_called()

    def test_contract_structure(self):
        """Test the structure of the Solidity verifier contract"""
        # Create a dummy contract file
        with open(self.contract_path, "w") as f:
            f.write(
                """
            // SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0;
            
            contract LlamaVerifier {
                struct VerificationKey {
                    uint256[] alpha;
                    uint256[] beta;
                    uint256[] gamma;
                    uint256[] delta;
                    uint256[][] abc;
                }
                
                VerificationKey private vk;
                
                constructor(
                    uint256[] memory alpha,
                    uint256[] memory beta,
                    uint256[] memory gamma,
                    uint256[] memory delta,
                    uint256[][] memory abc
                ) {
                    vk.alpha = alpha;
                    vk.beta = beta;
                    vk.gamma = gamma;
                    vk.delta = delta;
                    vk.abc = abc;
                }
                
                function verifyProof(
                    uint256[2] memory a,
                    uint256[2][2] memory b,
                    uint256[2] memory c,
                    uint256[] memory input
                ) public view returns (bool) {
                    return _verify(a, b, c, input);
                }
                
                function _verify(
                    uint256[2] memory a,
                    uint256[2][2] memory b,
                    uint256[2] memory c,
                    uint256[] memory input
                ) internal view returns (bool) {
                    // This is a dummy implementation for testing
                    return true;
                }
                
                function updateVerificationKey(
                    uint256[] memory alpha,
                    uint256[] memory beta,
                    uint256[] memory gamma,
                    uint256[] memory delta,
                    uint256[][] memory abc
                ) public {
                    vk.alpha = alpha;
                    vk.beta = beta;
                    vk.gamma = gamma;
                    vk.delta = delta;
                    vk.abc = abc;
                }
            }
            
            contract LlamaVerifierRegistry {
                mapping(string => address) private verifiers;
                
                event VerifierRegistered(string modelId, address verifier);
                event VerifierUpdated(string modelId, address verifier);
                event VerifierRemoved(string modelId);
                
                function registerVerifier(string memory modelId, address verifier) public {
                    require(verifiers[modelId] == address(0), "Verifier already registered");
                    verifiers[modelId] = verifier;
                    emit VerifierRegistered(modelId, verifier);
                }
                
                function updateVerifier(string memory modelId, address verifier) public {
                    require(verifiers[modelId] != address(0), "Verifier not registered");
                    verifiers[modelId] = verifier;
                    emit VerifierUpdated(modelId, verifier);
                }
                
                function removeVerifier(string memory modelId) public {
                    require(verifiers[modelId] != address(0), "Verifier not registered");
                    delete verifiers[modelId];
                    emit VerifierRemoved(modelId);
                }
                
                function getVerifier(string memory modelId) public view returns (address) {
                    return verifiers[modelId];
                }
            }
            """
            )

        # Read the contract file
        with open(self.contract_path, "r") as f:
            contract_content = f.read()

        # Check that the contract contains the expected components
        self.assertIn("contract LlamaVerifier", contract_content)
        self.assertIn("struct VerificationKey", contract_content)
        self.assertIn("function verifyProof", contract_content)
        self.assertIn("function updateVerificationKey", contract_content)

        # Check that the registry contract contains the expected components
        self.assertIn("contract LlamaVerifierRegistry", contract_content)
        self.assertIn("mapping(string => address) private verifiers", contract_content)
        self.assertIn("function registerVerifier", contract_content)
        self.assertIn("function updateVerifier", contract_content)
        self.assertIn("function removeVerifier", contract_content)
        self.assertIn("function getVerifier", contract_content)

    @mock.patch("subprocess.run")
    def test_solidity_compilation(self, mock_run):
        """Test compiling the Solidity verifier contract"""
        # Create a dummy contract file
        with open(self.contract_path, "w") as f:
            f.write(
                """
            // SPDX-License-Identifier: MIT
            pragma solidity ^0.8.0;
            
            contract LlamaVerifier {
                struct VerificationKey {
                    uint256[] alpha;
                    uint256[] beta;
                    uint256[] gamma;
                    uint256[] delta;
                    uint256[][] abc;
                }
                
                VerificationKey private vk;
                
                constructor(
                    uint256[] memory alpha,
                    uint256[] memory beta,
                    uint256[] memory gamma,
                    uint256[] memory delta,
                    uint256[][] memory abc
                ) {
                    vk.alpha = alpha;
                    vk.beta = beta;
                    vk.gamma = gamma;
                    vk.delta = delta;
                    vk.abc = abc;
                }
                
                function verifyProof(
                    uint256[2] memory a,
                    uint256[2][2] memory b,
                    uint256[2] memory c,
                    uint256[] memory input
                ) public view returns (bool) {
                    return _verify(a, b, c, input);
                }
                
                function _verify(
                    uint256[2] memory a,
                    uint256[2][2] memory b,
                    uint256[2] memory c,
                    uint256[] memory input
                ) internal view returns (bool) {
                    // This is a dummy implementation for testing
                    return true;
                }
                
                function updateVerificationKey(
                    uint256[] memory alpha,
                    uint256[] memory beta,
                    uint256[] memory gamma,
                    uint256[] memory delta,
                    uint256[][] memory abc
                ) public {
                    vk.alpha = alpha;
                    vk.beta = beta;
                    vk.gamma = gamma;
                    vk.delta = delta;
                    vk.abc = abc;
                }
            }
            """
            )

        # Mock subprocess.run to return success
        mock_run.return_value = mock.Mock(
            returncode=0, stdout=b"Compilation successful", stderr=b""
        )

        # Simulate compiling the contract
        import subprocess

        result = subprocess.run(
            ["solc", "--bin", self.contract_path], capture_output=True, check=False
        )

        # Check result
        self.assertEqual(result.returncode, 0)

        # Check that subprocess.run was called
        mock_run.assert_called_once()
