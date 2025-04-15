# LlamaVerifier Documentation

Welcome to the LlamaVerifier documentation. LlamaVerifier is a zero-knowledge proof system for AI model verification.

## Overview

LlamaVerifier allows you to verify AI model execution using zero-knowledge proofs, enabling trustless verification of model outputs without revealing sensitive model parameters or inputs.

## Getting Started

To get started with LlamaVerifier, follow these steps:

1. [Installation](installation.md)
2. [Basic Usage](basic-usage.md)
3. [API Reference](api-reference.md)
4. [CLI Reference](cli-reference.md)

## Features

- Compile AI models into ZKP circuits
- Generate zero-knowledge proofs for model execution
- Verify proofs on-chain or off-chain
- Export Solidity verifier contracts
- API and CLI interfaces

## Architecture

LlamaVerifier consists of several components:

- **Compiler**: Converts AI models into ZKP circuits
- **Proof System**: Generates and verifies zero-knowledge proofs
- **CLI**: Command-line interface for LlamaVerifier
- **API**: REST API for LlamaVerifier
- **Solidity Verifier**: On-chain verification of proofs 