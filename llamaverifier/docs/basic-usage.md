# Basic Usage

This guide covers the basic usage of LlamaVerifier for verifying AI model execution.

## Command-Line Interface

LlamaVerifier provides a command-line interface for easy interaction.

### Verifying a Model

The simplest way to verify a model is to use the `verify` command:

```bash
llamaverifier verify --model model.txt --input input.json --expected-output output.json
```

This will:
1. Compile the model into a ZKP circuit
2. Perform trusted setup
3. Generate a proof
4. Verify the proof

### Step-by-Step Verification

You can also perform the verification process step by step:

1. Compile the model:

```bash
llamaverifier compile --model model.txt --output circuit.out
```

2. Perform trusted setup:

```bash
llamaverifier setup --circuit circuit.out --output-dir keys/
```

3. Generate a proof:

```bash
llamaverifier prove --circuit circuit.out --proving-key keys/proving.key --witness-file witness.json --output-dir proofs/
```

4. Verify the proof:

```bash
llamaverifier verify-proof --verification-key keys/verification.key --proof proofs/proof.json --public-inputs proofs/public.json
```

### Exporting a Solidity Verifier

You can export a Solidity verifier contract for on-chain verification:

```bash
llamaverifier export --verification-key keys/verification.key --output verifier.sol
```

## API Usage

LlamaVerifier also provides a REST API for programmatic interaction.

### Starting the API Server

```bash
llamaverifier server --host 0.0.0.0 --port 8000
```

### API Endpoints

- `POST /compile`: Compile a model
- `POST /setup/{circuit_id}`: Perform trusted setup
- `POST /generate-proof/{circuit_id}`: Generate a proof
- `POST /verify`: Verify a proof
- `POST /export-verifier/{circuit_id}`: Export a Solidity verifier

See the [API Reference](api-reference.md) for more details.

## Python Library Usage

You can also use LlamaVerifier as a Python library:

```python
from llamaverifier.circuits import ZKPCompiler
from llamaverifier.proofs import ProofSystem

# Initialize components
compiler = ZKPCompiler()
proof_system = ProofSystem()

# Compile model
success = compiler.compile_model(
    model_path="model.txt",
    output_path="circuit.out",
    model_type="generic",
    optimization_level=1
)

# Perform trusted setup
proving_key_path, verification_key_path = proof_system.setup(
    circuit_path="circuit.out"
)

# Generate proof
proof_path, public_inputs_path = proof_system.generate_proof(
    circuit_path="circuit.out",
    proving_key_path=proving_key_path,
    witness_path="witness.json"
)

# Verify proof
valid = proof_system.verify_proof(
    verification_key_path=verification_key_path,
    proof_path=proof_path,
    public_inputs_path=public_inputs_path
)

print(f"Proof is {'valid' if valid else 'invalid'}")
``` 