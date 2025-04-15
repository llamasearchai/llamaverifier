"""
ZKP scheme implementations for LlamaVerifier
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SchemeType(str, Enum):
    """Enum for zero-knowledge proof schemes"""

    GROTH16 = "g16"
    GM17 = "gm17"
    MARLIN = "marlin"
    PLONK = "plonk"

    @classmethod
    def get_default(cls) -> "SchemeType":
        """Get the default scheme type"""
        return cls.GROTH16

    @classmethod
    def from_string(cls, scheme_str: str) -> "SchemeType":
        """Convert a string to a SchemeType"""
        try:
            return cls(scheme_str.lower())
        except ValueError:
            logger.warning(f"Unknown scheme type: {scheme_str}. Using default.")
            return cls.get_default()


class BaseScheme:
    """Base class for ZKP schemes"""

    def __init__(self):
        """Initialize the scheme"""
        pass

    def setup(self, circuit_path: str) -> Tuple[str, str]:
        """
        Perform trusted setup for a circuit.

        Args:
            circuit_path: Path to the compiled circuit

        Returns:
            Tuple of (proving_key_path, verification_key_path)
        """
        raise NotImplementedError("Subclasses must implement setup")

    def generate_proof(
        self, circuit_path: str, proving_key_path: str, witness_values: List[str]
    ) -> Tuple[str, str]:
        """
        Generate a proof for a circuit with the given witness values.

        Args:
            circuit_path: Path to the compiled circuit
            proving_key_path: Path to the proving key
            witness_values: Witness values

        Returns:
            Tuple of (proof_path, public_inputs_path)
        """
        raise NotImplementedError("Subclasses must implement generate_proof")

    def verify_proof(
        self, verification_key_path: str, proof_path: str, public_inputs_path: str
    ) -> bool:
        """
        Verify a proof.

        Args:
            verification_key_path: Path to the verification key
            proof_path: Path to the proof
            public_inputs_path: Path to the public inputs

        Returns:
            True if the proof is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement verify_proof")

    def export_verifier(self, verification_key_path: str, output_path: str) -> str:
        """
        Export a Solidity verifier contract.

        Args:
            verification_key_path: Path to the verification key
            output_path: Path where the Solidity verifier contract will be saved

        Returns:
            Path to the Solidity verifier contract
        """
        raise NotImplementedError("Subclasses must implement export_verifier")


class Groth16Scheme(BaseScheme):
    """Groth16 ZKP scheme implementation"""

    def setup(self, circuit_path: str) -> Tuple[str, str]:
        """
        Perform trusted setup for a circuit using Groth16.

        Args:
            circuit_path: Path to the compiled circuit

        Returns:
            Tuple of (proving_key_path, verification_key_path)
        """
        import os
        import subprocess
        import tempfile

        logger.info(f"Performing Groth16 trusted setup for circuit: {circuit_path}")

        # Create temporary files for the keys
        with tempfile.NamedTemporaryFile(
            suffix=".proving.key", delete=False
        ) as pk_file, tempfile.NamedTemporaryFile(
            suffix=".verification.key", delete=False
        ) as vk_file:
            proving_key_path = pk_file.name
            verification_key_path = vk_file.name

        try:
            # Run ZoKrates to perform the setup
            result = subprocess.run(
                [
                    "zokrates",
                    "setup",
                    "--scheme",
                    "g16",
                    "-i",
                    circuit_path,
                    "--proving-key-path",
                    proving_key_path,
                    "--verification-key-path",
                    verification_key_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.debug(f"Groth16 setup output: {result.stdout}")
            logger.info(
                f"Groth16 setup completed. Proving key: {proving_key_path}, Verification key: {verification_key_path}"
            )

            return proving_key_path, verification_key_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Groth16 setup error: {e.stderr}")
            # Clean up temporary files on error
            for path in [proving_key_path, verification_key_path]:
                if os.path.exists(path):
                    os.unlink(path)
            raise RuntimeError(f"Failed to perform Groth16 setup: {e}")

    def generate_proof(
        self, circuit_path: str, proving_key_path: str, witness_values: List[str]
    ) -> Tuple[str, str]:
        """
        Generate a proof using Groth16.

        Args:
            circuit_path: Path to the compiled circuit
            proving_key_path: Path to the proving key
            witness_values: Witness values

        Returns:
            Tuple of (proof_path, public_inputs_path)
        """
        import os
        import subprocess
        import tempfile

        logger.info(f"Generating Groth16 proof for circuit: {circuit_path}")

        # Create temporary files for the witness and proof
        with tempfile.NamedTemporaryFile(
            suffix=".witness", delete=False
        ) as witness_file, tempfile.NamedTemporaryFile(
            suffix=".proof", delete=False
        ) as proof_file, tempfile.NamedTemporaryFile(
            suffix=".public", delete=False
        ) as public_file:
            witness_path = witness_file.name
            proof_path = proof_file.name
            public_inputs_path = public_file.name

        try:
            # Write witness values to file
            with open(witness_path, "w") as f:
                for value in witness_values:
                    f.write(f"{value}\n")

            # Compute witness
            witness_result = subprocess.run(
                [
                    "zokrates",
                    "compute-witness",
                    "-i",
                    circuit_path,
                    "-o",
                    witness_path,
                    "--stdin",
                ],
                input="\n".join(witness_values),
                check=True,
                capture_output=True,
                text=True,
            )

            logger.debug(f"Witness computation output: {witness_result.stdout}")

            # Generate proof
            proof_result = subprocess.run(
                [
                    "zokrates",
                    "generate-proof",
                    "--scheme",
                    "g16",
                    "-i",
                    circuit_path,
                    "--proving-key-path",
                    proving_key_path,
                    "--witness-path",
                    witness_path,
                    "--proof-path",
                    proof_path,
                    "--public-path",
                    public_inputs_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.debug(f"Proof generation output: {proof_result.stdout}")
            logger.info(
                f"Groth16 proof generated. Proof: {proof_path}, Public inputs: {public_inputs_path}"
            )

            return proof_path, public_inputs_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Groth16 proof generation error: {e.stderr}")
            # Clean up temporary files on error
            for path in [witness_path, proof_path, public_inputs_path]:
                if os.path.exists(path):
                    os.unlink(path)
            raise RuntimeError(f"Failed to generate Groth16 proof: {e}")
        finally:
            # Clean up witness file
            if os.path.exists(witness_path):
                os.unlink(witness_path)

    def verify_proof(
        self, verification_key_path: str, proof_path: str, public_inputs_path: str
    ) -> bool:
        """
        Verify a Groth16 proof.

        Args:
            verification_key_path: Path to the verification key
            proof_path: Path to the proof
            public_inputs_path: Path to the public inputs

        Returns:
            True if the proof is valid, False otherwise
        """
        import subprocess

        logger.info(f"Verifying Groth16 proof: {proof_path}")

        try:
            # Verify the proof
            result = subprocess.run(
                [
                    "zokrates",
                    "verify",
                    "--scheme",
                    "g16",
                    "--verification-key-path",
                    verification_key_path,
                    "--proof-path",
                    proof_path,
                    "--public-path",
                    public_inputs_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            # Check if verification succeeded
            success = "VERIFICATION SUCCESSFUL" in result.stdout

            if success:
                logger.info("Groth16 proof verification successful")
            else:
                logger.warning("Groth16 proof verification failed")

            return success
        except subprocess.CalledProcessError as e:
            logger.error(f"Groth16 proof verification error: {e.stderr}")
            return False

    def export_verifier(self, verification_key_path: str, output_path: str) -> str:
        """
        Export a Solidity verifier contract for Groth16.

        Args:
            verification_key_path: Path to the verification key
            output_path: Path where the Solidity verifier contract will be saved

        Returns:
            Path to the Solidity verifier contract
        """
        import os
        import subprocess

        logger.info(
            f"Exporting Groth16 verifier contract for key: {verification_key_path}"
        )

        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        try:
            # Generate the Solidity verifier
            result = subprocess.run(
                [
                    "zokrates",
                    "export-verifier",
                    "--scheme",
                    "g16",
                    "--verification-key-path",
                    verification_key_path,
                    "-o",
                    output_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.debug(f"Verifier export output: {result.stdout}")
            logger.info(f"Groth16 verifier contract exported to: {output_path}")

            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Groth16 verifier export error: {e.stderr}")
            raise RuntimeError(f"Failed to export Groth16 verifier: {e}")


class GM17Scheme(BaseScheme):
    """GM17 ZKP scheme implementation"""

    def setup(self, circuit_path: str) -> Tuple[str, str]:
        """
        Perform trusted setup for a circuit using GM17.

        Args:
            circuit_path: Path to the compiled circuit

        Returns:
            Tuple of (proving_key_path, verification_key_path)
        """
        # Similar implementation to Groth16 but with scheme="gm17"
        # For brevity, we'll use a simplified implementation
        import os
        import subprocess
        import tempfile

        logger.info(f"Performing GM17 trusted setup for circuit: {circuit_path}")

        # Create temporary files for the keys
        with tempfile.NamedTemporaryFile(
            suffix=".proving.key", delete=False
        ) as pk_file, tempfile.NamedTemporaryFile(
            suffix=".verification.key", delete=False
        ) as vk_file:
            proving_key_path = pk_file.name
            verification_key_path = vk_file.name

        try:
            # Run ZoKrates to perform the setup
            result = subprocess.run(
                [
                    "zokrates",
                    "setup",
                    "--scheme",
                    "gm17",
                    "-i",
                    circuit_path,
                    "--proving-key-path",
                    proving_key_path,
                    "--verification-key-path",
                    verification_key_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.debug(f"GM17 setup output: {result.stdout}")
            logger.info(
                f"GM17 setup completed. Proving key: {proving_key_path}, Verification key: {verification_key_path}"
            )

            return proving_key_path, verification_key_path
        except subprocess.CalledProcessError as e:
            logger.error(f"GM17 setup error: {e.stderr}")
            # Clean up temporary files on error
            for path in [proving_key_path, verification_key_path]:
                if os.path.exists(path):
                    os.unlink(path)
            raise RuntimeError(f"Failed to perform GM17 setup: {e}")

    def generate_proof(
        self, circuit_path: str, proving_key_path: str, witness_values: List[str]
    ) -> Tuple[str, str]:
        """Generate a proof using GM17"""
        # Similar to Groth16 but with scheme="gm17"
        import os
        import subprocess
        import tempfile

        logger.info(f"Generating GM17 proof for circuit: {circuit_path}")

        # Create temporary files for the witness and proof
        with tempfile.NamedTemporaryFile(
            suffix=".witness", delete=False
        ) as witness_file, tempfile.NamedTemporaryFile(
            suffix=".proof", delete=False
        ) as proof_file, tempfile.NamedTemporaryFile(
            suffix=".public", delete=False
        ) as public_file:
            witness_path = witness_file.name
            proof_path = proof_file.name
            public_inputs_path = public_file.name

        try:
            # Write witness values to file
            with open(witness_path, "w") as f:
                for value in witness_values:
                    f.write(f"{value}\n")

            # Compute witness
            witness_result = subprocess.run(
                [
                    "zokrates",
                    "compute-witness",
                    "-i",
                    circuit_path,
                    "-o",
                    witness_path,
                    "--stdin",
                ],
                input="\n".join(witness_values),
                check=True,
                capture_output=True,
                text=True,
            )

            # Generate proof
            proof_result = subprocess.run(
                [
                    "zokrates",
                    "generate-proof",
                    "--scheme",
                    "gm17",
                    "-i",
                    circuit_path,
                    "--proving-key-path",
                    proving_key_path,
                    "--witness-path",
                    witness_path,
                    "--proof-path",
                    proof_path,
                    "--public-path",
                    public_inputs_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(
                f"GM17 proof generated. Proof: {proof_path}, Public inputs: {public_inputs_path}"
            )

            return proof_path, public_inputs_path
        except subprocess.CalledProcessError as e:
            logger.error(f"GM17 proof generation error: {e.stderr}")
            # Clean up temporary files on error
            for path in [witness_path, proof_path, public_inputs_path]:
                if os.path.exists(path):
                    os.unlink(path)
            raise RuntimeError(f"Failed to generate GM17 proof: {e}")
        finally:
            # Clean up witness file
            if os.path.exists(witness_path):
                os.unlink(witness_path)

    def verify_proof(
        self, verification_key_path: str, proof_path: str, public_inputs_path: str
    ) -> bool:
        """Verify a GM17 proof"""
        # Similar to Groth16 but with scheme="gm17"
        import subprocess

        logger.info(f"Verifying GM17 proof: {proof_path}")

        try:
            # Verify the proof
            result = subprocess.run(
                [
                    "zokrates",
                    "verify",
                    "--scheme",
                    "gm17",
                    "--verification-key-path",
                    verification_key_path,
                    "--proof-path",
                    proof_path,
                    "--public-path",
                    public_inputs_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            # Check if verification succeeded
            success = "VERIFICATION SUCCESSFUL" in result.stdout

            if success:
                logger.info("GM17 proof verification successful")
            else:
                logger.warning("GM17 proof verification failed")

            return success
        except subprocess.CalledProcessError as e:
            logger.error(f"GM17 proof verification error: {e.stderr}")
            return False

    def export_verifier(self, verification_key_path: str, output_path: str) -> str:
        """Export a Solidity verifier contract for GM17"""
        # Similar to Groth16 but with scheme="gm17"
        import os
        import subprocess

        logger.info(
            f"Exporting GM17 verifier contract for key: {verification_key_path}"
        )

        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        try:
            # Generate the Solidity verifier
            result = subprocess.run(
                [
                    "zokrates",
                    "export-verifier",
                    "--scheme",
                    "gm17",
                    "--verification-key-path",
                    verification_key_path,
                    "-o",
                    output_path,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(f"GM17 verifier contract exported to: {output_path}")

            return output_path
        except subprocess.CalledProcessError as e:
            logger.error(f"GM17 verifier export error: {e.stderr}")
            raise RuntimeError(f"Failed to export GM17 verifier: {e}")


# Factory function to get the appropriate scheme implementation
def get_scheme(scheme_type: Union[str, SchemeType]) -> BaseScheme:
    """
    Get the appropriate scheme implementation.

    Args:
        scheme_type: Type of scheme to use

    Returns:
        Scheme implementation
    """
    if isinstance(scheme_type, str):
        scheme_type = SchemeType.from_string(scheme_type)

    scheme_map = {
        SchemeType.GROTH16: Groth16Scheme,
        SchemeType.GM17: GM17Scheme,
        # Add other schemes as they are implemented
    }

    if scheme_type not in scheme_map:
        logger.warning(f"Scheme {scheme_type} not implemented, using default.")
        scheme_type = SchemeType.get_default()

    return scheme_map[scheme_type]()
