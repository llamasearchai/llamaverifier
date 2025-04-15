"""
Proof System for generating and verifying zero-knowledge proofs
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..utils.file_utils import check_file_exists, ensure_directory
from ..utils.logger import get_logger
from .schemes import SchemeType, get_scheme

logger = get_logger(__name__)


class ProofSystem:
    """
    System for generating and verifying zero-knowledge proofs.

    This class provides high-level methods to:
    1. Perform trusted setup for a circuit
    2. Generate proofs for a circuit with inputs
    3. Verify proofs
    4. Export Solidity verifier contracts
    """

    def __init__(self, workspace_dir: Optional[str] = None):
        """
        Initialize the proof system.

        Args:
            workspace_dir: Directory to use for storing artifacts (optional)
        """
        self.workspace_dir = workspace_dir
        if workspace_dir:
            ensure_directory(workspace_dir)

    def setup(self, circuit_path: str, scheme: str = "g16") -> Tuple[str, str]:
        """
        Perform trusted setup for a circuit.

        Args:
            circuit_path: Path to the compiled circuit
            scheme: ZKP scheme to use (g16, gm17, etc.)

        Returns:
            Tuple of (proving_key_path, verification_key_path)
        """
        logger.info(
            f"Performing trusted setup for circuit: {circuit_path} using scheme: {scheme}"
        )

        if not check_file_exists(circuit_path):
            raise FileNotFoundError(f"Circuit file not found: {circuit_path}")

        # Determine paths for the keys
        if self.workspace_dir:
            circuit_name = os.path.basename(circuit_path).split(".")[0]
            proving_key_path = os.path.join(
                self.workspace_dir, f"{circuit_name}.{scheme}.pk"
            )
            verification_key_path = os.path.join(
                self.workspace_dir, f"{circuit_name}.{scheme}.vk"
            )
        else:
            # Create temporary files for the keys
            with tempfile.NamedTemporaryFile(
                suffix=f".{scheme}.pk", delete=False
            ) as pk_file:
                proving_key_path = pk_file.name
            with tempfile.NamedTemporaryFile(
                suffix=f".{scheme}.vk", delete=False
            ) as vk_file:
                verification_key_path = vk_file.name

        # Get the appropriate scheme implementation
        scheme_impl = get_scheme(scheme)

        # Perform setup
        try:
            pk_path, vk_path = scheme_impl.setup(circuit_path)

            # If we're using our own paths, move the keys
            if pk_path != proving_key_path:
                os.rename(pk_path, proving_key_path)
            if vk_path != verification_key_path:
                os.rename(vk_path, verification_key_path)

            logger.info(
                f"Trusted setup completed. Proving key: {proving_key_path}, Verification key: {verification_key_path}"
            )
            return proving_key_path, verification_key_path

        except Exception as e:
            logger.error(f"Error during trusted setup: {e}")
            # Clean up temporary files on error
            for path in [proving_key_path, verification_key_path]:
                if os.path.exists(path) and path.startswith(tempfile.gettempdir()):
                    os.unlink(path)
            raise

    def generate_proof(
        self,
        circuit_path: str,
        proving_key_path: str,
        witness_values: List[str],
        scheme: str = "g16",
    ) -> Tuple[str, str]:
        """
        Generate a zero-knowledge proof.

        Args:
            circuit_path: Path to the compiled circuit
            proving_key_path: Path to the proving key
            witness_values: Values for the witness variables
            scheme: ZKP scheme to use (g16, gm17, etc.)

        Returns:
            Tuple of (proof_path, public_inputs_path)
        """
        logger.info(
            f"Generating proof for circuit: {circuit_path} using scheme: {scheme}"
        )

        if not check_file_exists(circuit_path):
            raise FileNotFoundError(f"Circuit file not found: {circuit_path}")

        if not check_file_exists(proving_key_path):
            raise FileNotFoundError(f"Proving key not found: {proving_key_path}")

        # Determine paths for the proof and public inputs
        if self.workspace_dir:
            circuit_name = os.path.basename(circuit_path).split(".")[0]
            proof_path = os.path.join(
                self.workspace_dir, f"{circuit_name}.{scheme}.proof"
            )
            public_inputs_path = os.path.join(
                self.workspace_dir, f"{circuit_name}.{scheme}.public"
            )
        else:
            # Create temporary files for the proof and public inputs
            with tempfile.NamedTemporaryFile(
                suffix=f".{scheme}.proof", delete=False
            ) as proof_file:
                proof_path = proof_file.name
            with tempfile.NamedTemporaryFile(
                suffix=f".{scheme}.public", delete=False
            ) as public_file:
                public_inputs_path = public_file.name

        # Get the appropriate scheme implementation
        scheme_impl = get_scheme(scheme)

        # Generate proof
        try:
            p_path, pi_path = scheme_impl.generate_proof(
                circuit_path, proving_key_path, witness_values
            )

            # If we're using our own paths, move the files
            if p_path != proof_path:
                os.rename(p_path, proof_path)
            if pi_path != public_inputs_path:
                os.rename(pi_path, public_inputs_path)

            logger.info(
                f"Proof generation completed. Proof: {proof_path}, Public inputs: {public_inputs_path}"
            )
            return proof_path, public_inputs_path

        except Exception as e:
            logger.error(f"Error during proof generation: {e}")
            # Clean up temporary files on error
            for path in [proof_path, public_inputs_path]:
                if os.path.exists(path) and path.startswith(tempfile.gettempdir()):
                    os.unlink(path)
            raise

    def verify_proof(
        self,
        verification_key_path: str,
        proof_path: str,
        public_inputs_path: str,
        scheme: str = "g16",
    ) -> bool:
        """
        Verify a zero-knowledge proof.

        Args:
            verification_key_path: Path to the verification key
            proof_path: Path to the proof
            public_inputs_path: Path to the public inputs
            scheme: ZKP scheme to use (g16, gm17, etc.)

        Returns:
            True if the proof is valid, False otherwise
        """
        logger.info(f"Verifying proof: {proof_path} using scheme: {scheme}")

        if not check_file_exists(verification_key_path):
            raise FileNotFoundError(
                f"Verification key not found: {verification_key_path}"
            )

        if not check_file_exists(proof_path):
            raise FileNotFoundError(f"Proof not found: {proof_path}")

        if not check_file_exists(public_inputs_path):
            raise FileNotFoundError(f"Public inputs not found: {public_inputs_path}")

        # Get the appropriate scheme implementation
        scheme_impl = get_scheme(scheme)

        # Verify the proof
        try:
            result = scheme_impl.verify_proof(
                verification_key_path, proof_path, public_inputs_path
            )

            if result:
                logger.info("Proof verification successful")
            else:
                logger.warning("Proof verification failed")

            return result

        except Exception as e:
            logger.error(f"Error during proof verification: {e}")
            return False

    def export_verifier(
        self, verification_key_path: str, output_path: str, scheme: str = "g16"
    ) -> str:
        """
        Export a Solidity verifier contract.

        Args:
            verification_key_path: Path to the verification key
            output_path: Path where the Solidity verifier contract will be saved
            scheme: ZKP scheme to use (g16, gm17, etc.)

        Returns:
            Path to the Solidity verifier contract
        """
        logger.info(
            f"Exporting verifier contract for key: {verification_key_path} using scheme: {scheme}"
        )

        if not check_file_exists(verification_key_path):
            raise FileNotFoundError(
                f"Verification key not found: {verification_key_path}"
            )

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Get the appropriate scheme implementation
        scheme_impl = get_scheme(scheme)

        # Export the verifier
        try:
            result_path = scheme_impl.export_verifier(
                verification_key_path, output_path
            )

            logger.info(f"Verifier contract exported to: {result_path}")
            return result_path

        except Exception as e:
            logger.error(f"Error during verifier export: {e}")
            raise
