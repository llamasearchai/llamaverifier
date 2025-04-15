# LlamaVerifier

<p align="center">
  <img src="docs/assets/logo.png" width="200" alt="LlamaVerifier Logo">
</p>

<p align="center">
  <strong>Zero-Knowledge Proof System for AI Model Verification</strong><br>
  <em>Apple Silicon Optimized | MLX Accelerated</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

## Overview

LlamaVerifier is a cutting-edge framework that enables verifiable AI through zero-knowledge proofs. It allows AI models to generate cryptographic proofs that verify the correctness of their computations without revealing the inputs or internal workings of the model.

This technology bridges the gap between AI and cryptography, addressing key challenges in AI verification, security, and privacy:

- **Correctness Verification**: Prove that an AI model executed correctly without revealing the model parameters
- **Input Privacy**: Verify model execution while keeping sensitive inputs private
- **On-chain Verification**: Deploy verifiers to blockchain networks for decentralized validation
- **Model Protection**: Share models while protecting intellectual property

## Features

- 🔒 **End-to-end verification** of AI model execution with zero-knowledge proofs
- 🦙 **Specialized support for LLaMA models** and transformers
- ⚡ **Apple Silicon optimizations** with MLX acceleration
- 🔗 **Blockchain integration** with Solidity verifier contracts
- 🔌 **API and CLI interfaces** for seamless integration
- 📊 **Benchmark tools** for optimization and performance analysis
- 🌐 **Multi-platform support** with containerized setup

## Installation

### Quick Install (macOS/Linux)

```bash
curl -sSL https://raw.githubusercontent.com/username/llamaverifier/main/scripts/install.sh | bash
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/llamaverifier.git
   cd llamaverifier
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install ZoKrates (required for ZKP):
   ```bash
   ./scripts/install_zokrates.sh
   ```

## Usage

### CLI Usage

Verify an AI model with a single command:

```bash
llamaverifier verify model.onnx inputs.txt expected_output.txt
```

Step-by-step verification is also supported:

```bash
# Compile model to circuit
llamaverifier compile model.onnx circuit.out

# Perform trusted setup
llamaverifier setup circuit.out setup_dir

# Generate proof
llamaverifier prove circuit.out setup_dir/proving_key.json witness.json proof_dir

# Verify proof
llamaverifier verify-proof setup_dir/verification_key.json proof_dir/proof.json proof_dir/public.json
```

### API Usage

Start the API server:

```bash
llamaverifier server
```

The API documentation will be available at http://localhost:8000/docs

## Architecture

LlamaVerifier consists of several key components:

- **Compiler**: Translates AI models into arithmetic circuits
- **Proof System**: Generates and verifies zero-knowledge proofs
- **CLI**: Command line interface for easy usage
- **API**: REST API for integration with applications
- **Solidity Verifier**: On-chain verification of proofs

<p align="center">
  <img src="docs/assets/architecture.png" width="600" alt="LlamaVerifier Architecture">
</p>

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory:

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
- [Circuit Compilation](docs/circuit-compilation.md)
- [Proof Generation](docs/proof-generation.md)
- [Blockchain Integration](docs/blockchain-integration.md)
- [Benchmarks](docs/benchmarks.md)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citing

If you use LlamaVerifier in your research, please cite:

```bibtex
@software{llamaverifier2023,
  author = {Your Name},
  title = {LlamaVerifier: Zero-Knowledge Proof System for AI Model Verification},
  year = {2023},
  url = {https://github.com/username/llamaverifier}
}
```

## Acknowledgments

- The ZoKrates team for their zero-knowledge proof compiler
- The MLX team for their optimization framework
- Everyone who has contributed to the project 