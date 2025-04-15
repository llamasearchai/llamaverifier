"""
API server for LlamaVerifier
"""

import os
import tempfile
from typing import Dict, List, Optional, Union

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from rich.console import Console

from ..circuits import ZKPCompiler
from ..proofs import ProofSystem
from ..utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize console for rich output
console = Console()

# Initialize FastAPI app
app = FastAPI(
    title="LlamaVerifier API",
    description="API for verifying AI models using zero-knowledge proofs",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize modules
compiler = ZKPCompiler()
proof_system = ProofSystem()


# API Models
class VerificationRequest(BaseModel):
    """Model for verification request"""

    circuit_id: str
    proof_id: str
    public_inputs_id: str


class VerificationResponse(BaseModel):
    """Model for verification response"""

    valid: bool
    message: str


class CompilationResponse(BaseModel):
    """Model for compilation response"""

    circuit_id: str
    message: str


class ProofResponse(BaseModel):
    """Model for proof generation response"""

    proof_id: str
    public_inputs_id: str
    message: str


# In-memory storage for demo purposes (would use a database in production)
circuits = {}
proofs = {}
public_inputs = {}
verification_keys = {}
proving_keys = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the LlamaVerifier API"}


@app.get("/info")
async def info():
    """Get information about the API"""
    from ..utils.system_utils import get_system_info, is_apple_silicon

    system_info = get_system_info()

    return {
        "version": "0.1.0",
        "system_info": system_info,
        "apple_silicon": is_apple_silicon(),
        "circuits": len(circuits),
        "proofs": len(proofs),
    }


@app.post("/compile", response_model=CompilationResponse)
async def compile_model(
    model_file: UploadFile = File(...),
    model_type: str = Form("generic"),
    optimization_level: int = Form(1),
):
    """
    Compile an AI model into a ZoKrates circuit
    """
    try:
        # Save uploaded model to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_model:
            temp_model_path = temp_model.name
            content = await model_file.read()
            temp_model.write(content)

        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            temp_output_path = temp_output.name

        # Compile model
        success = compiler.compile_model(
            temp_model_path, temp_output_path, model_type, optimization_level
        )

        if not success:
            raise HTTPException(status_code=500, detail="Compilation failed")

        # Store circuit in memory (would store in database in production)
        circuit_id = f"circuit_{len(circuits) + 1}"
        circuits[circuit_id] = temp_output_path

        return CompilationResponse(
            circuit_id=circuit_id, message="Model compiled successfully"
        )

    except Exception as e:
        logger.error(f"Error compiling model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary model file
        if "temp_model_path" in locals():
            try:
                os.unlink(temp_model_path)
            except:
                pass


@app.post("/setup/{circuit_id}")
async def setup_circuit(circuit_id: str, scheme: str = "g16"):
    """
    Perform trusted setup for a circuit
    """
    if circuit_id not in circuits:
        raise HTTPException(status_code=404, detail="Circuit not found")

    try:
        # Perform trusted setup
        proving_key_path, verification_key_path = proof_system.setup(
            circuits[circuit_id], scheme
        )

        # Store keys in memory
        proving_key_id = f"proving_key_{circuit_id}"
        verification_key_id = f"verification_key_{circuit_id}"

        proving_keys[proving_key_id] = proving_key_path
        verification_keys[verification_key_id] = verification_key_path

        return {
            "message": "Trusted setup completed successfully",
            "proving_key_id": proving_key_id,
            "verification_key_id": verification_key_id,
        }

    except Exception as e:
        logger.error(f"Error during trusted setup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-proof/{circuit_id}", response_model=ProofResponse)
async def generate_proof(
    circuit_id: str, witness_values: List[str], scheme: str = "g16"
):
    """
    Generate a zero-knowledge proof
    """
    if circuit_id not in circuits:
        raise HTTPException(status_code=404, detail="Circuit not found")

    proving_key_id = f"proving_key_{circuit_id}"
    if proving_key_id not in proving_keys:
        raise HTTPException(
            status_code=404, detail="Proving key not found. Run setup first."
        )

    try:
        # Generate proof
        proof_path, public_inputs_path = proof_system.generate_proof(
            circuits[circuit_id], proving_keys[proving_key_id], witness_values, scheme
        )

        # Store proof and public inputs in memory
        proof_id = f"proof_{len(proofs) + 1}"
        public_inputs_id = f"public_inputs_{len(public_inputs) + 1}"

        proofs[proof_id] = proof_path
        public_inputs[public_inputs_id] = public_inputs_path

        return ProofResponse(
            proof_id=proof_id,
            public_inputs_id=public_inputs_id,
            message="Proof generated successfully",
        )

    except Exception as e:
        logger.error(f"Error generating proof: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/verify", response_model=VerificationResponse)
async def verify_proof(request: VerificationRequest, scheme: str = "g16"):
    """
    Verify a zero-knowledge proof
    """
    try:
        if request.proof_id not in proofs:
            raise HTTPException(status_code=404, detail="Proof not found")

        if request.public_inputs_id not in public_inputs:
            raise HTTPException(status_code=404, detail="Public inputs not found")

        verification_key_id = f"verification_key_{request.circuit_id}"
        if verification_key_id not in verification_keys:
            raise HTTPException(
                status_code=404, detail="Verification key not found. Run setup first."
            )

        # Verify proof
        valid = proof_system.verify_proof(
            verification_keys[verification_key_id],
            proofs[request.proof_id],
            public_inputs[request.public_inputs_id],
            scheme,
        )

        if valid:
            return VerificationResponse(valid=True, message="Proof is valid")
        else:
            return VerificationResponse(valid=False, message="Proof is invalid")

    except Exception as e:
        logger.error(f"Error verifying proof: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export-verifier/{circuit_id}")
async def export_verifier(circuit_id: str, scheme: str = "g16"):
    """
    Export a Solidity verifier contract
    """
    verification_key_id = f"verification_key_{circuit_id}"
    if verification_key_id not in verification_keys:
        raise HTTPException(
            status_code=404, detail="Verification key not found. Run setup first."
        )

    try:
        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".sol") as temp_output:
            temp_output_path = temp_output.name

        # Export verifier
        verifier_path = proof_system.export_verifier(
            verification_keys[verification_key_id], temp_output_path, scheme
        )

        # Read verifier contract
        with open(verifier_path, "r") as f:
            verifier_code = f.read()

        return {
            "message": "Verifier contract exported successfully",
            "verifier_code": verifier_code,
        }

    except Exception as e:
        logger.error(f"Error exporting verifier: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary output file
        if "temp_output_path" in locals():
            try:
                os.unlink(temp_output_path)
            except:
                pass


def start_server(host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
    """Start the API server"""
    uvicorn.run("llamaverifier.api.server:app", host=host, port=port, reload=debug)
