# Installation Guide

There are several ways to install LlamaVerifier:

## Using the Installer Script

The easiest way to install LlamaVerifier is to use the installer script:

```bash
curl -sSL https://raw.githubusercontent.com/username/llamaverifier/main/scripts/install.sh | bash
```

This will:
1. Check system requirements
2. Install ZoKrates (if not already installed)
3. Clone the LlamaVerifier repository
4. Install Python dependencies
5. Create a shell wrapper for easy access

## Manual Installation

### Prerequisites

- Python 3.8 or higher
- pip
- git
- ZoKrates (optional, but recommended)

### Installation Steps

1. Clone the repository:

```bash
git clone https://github.com/username/llamaverifier.git
cd llamaverifier
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:

```bash
pip install -e .
```

4. Verify the installation:

```bash
llamaverifier info
```

## Installing from PyPI

LlamaVerifier is also available on PyPI:

```bash
pip install llamaverifier
```

## Apple Silicon Optimization

LlamaVerifier includes optimizations for Apple Silicon (M1/M2) processors. If you're running on Apple Silicon, you can install the optimized dependencies:

```bash
pip install -e ".[apple]"
```

This will install MLX and other optimized libraries for Apple Silicon. 