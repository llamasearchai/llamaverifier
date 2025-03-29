"""
Pytest configuration file for LlamaVerifier tests
"""
import os
import json
import tempfile
import shutil
from unittest import mock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def model_file(temp_dir):
    """Create a dummy model file"""
    model_path = os.path.join(temp_dir, "model.txt")
    with open(model_path, "w") as f:
        f.write("# Dummy model file\n")
        f.write("param_1=1\n")
        f.write("param_2=2\n")
    return model_path


@pytest.fixture
def input_file(temp_dir):
    """Create a dummy input file"""
    input_data = {"input": [1, 2, 3]}
    input_path = os.path.join(temp_dir, "input.json")
    with open(input_path, "w") as f:
        json.dump(input_data, f)
    return input_path, input_data


@pytest.fixture
def output_file(temp_dir):
    """Create a dummy output file"""
    output_data = {"output": [3, 2, 1]}
    output_path = os.path.join(temp_dir, "output.json")
    with open(output_path, "w") as f:
        json.dump(output_data, f)
    return output_path, output_data


@pytest.fixture
def circuit_file(temp_dir):
    """Create a dummy circuit file"""
    circuit_path = os.path.join(temp_dir, "circuit.zok")
    with open(circuit_path, "w") as f:
        f.write("def main(private field a, private field b, public field c) -> bool:\n")
        f.write("    return a * b == c\n")
    return circuit_path


@pytest.fixture
def witness_file(temp_dir):
    """Create a dummy witness file"""
    witness_data = {"a": 3, "b": 4, "c": 12}
    witness_path = os.path.join(temp_dir, "witness.json")
    with open(witness_path, "w") as f:
        json.dump(witness_data, f)
    return witness_path, witness_data


@pytest.fixture
def proving_key_file(temp_dir):
    """Create a dummy proving key file"""
    pk_path = os.path.join(temp_dir, "proving.key")
    with open(pk_path, "w") as f:
        f.write("dummy proving key")
    return pk_path


@pytest.fixture
def verification_key_file(temp_dir):
    """Create a dummy verification key file"""
    vk_path = os.path.join(temp_dir, "verification.key")
    with open(vk_path, "w") as f:
        f.write("dummy verification key")
    return vk_path


@pytest.fixture
def proof_file(temp_dir):
    """Create a dummy proof file"""
    proof_data = {
        "a": ["0x1234", "0x5678"],
        "b": [["0x9abc", "0xdef0"], ["0x1111", "0x2222"]],
        "c": ["0x3333", "0x4444"]
    }
    proof_path = os.path.join(temp_dir, "proof.json")
    with open(proof_path, "w") as f:
        json.dump(proof_data, f)
    return proof_path, proof_data


@pytest.fixture
def public_inputs_file(temp_dir):
    """Create a dummy public inputs file"""
    public_inputs_data = {"c": 12}
    public_inputs_path = os.path.join(temp_dir, "public.json")
    with open(public_inputs_path, "w") as f:
        json.dump(public_inputs_data, f)
    return public_inputs_path, public_inputs_data


@pytest.fixture
def contract_file(temp_dir):
    """Create a dummy Solidity verifier contract file"""
    contract_path = os.path.join(temp_dir, "LlamaVerifier.sol")
    with open(contract_path, "w") as f:
        f.write("""
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
        """)
    return contract_path


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run to return success"""
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        yield mock_run


@pytest.fixture
def mock_subprocess_run_failure():
    """Mock subprocess.run to return failure"""
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(
            returncode=1,
            stdout="",
            stderr="Error"
        )
        yield mock_run 