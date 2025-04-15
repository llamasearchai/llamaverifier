"""
Command-line interface commands for LlamaVerifier
"""

import os
import sys
import tempfile
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..circuits import OptimizationLevel, ZKPCompiler
from ..proofs import ProofSystem, SchemeType
from ..utils.logger import get_logger, setup_logger
from ..utils.system_utils import check_dependencies, get_system_info, is_apple_silicon

# Initialize logger
logger = get_logger(__name__)

# Initialize console for rich output
console = Console()

# Initialize Typer app
app = typer.Typer(
    name="llamaverifier",
    help="Zero-Knowledge Proof System for AI Model Verification",
    add_completion=False,
)

# Default scheme
DEFAULT_SCHEME = SchemeType.get_default().value


def print_banner():
    """Print the LlamaVerifier banner"""
    banner = """
    🦙 LlamaVerifier - Zero-Knowledge Proof System for AI Model Verification
    """
    console.print(Panel(banner, style="bold green"))


def is_apple_silicon() -> bool:
    """Check if running on Apple Silicon"""
    return sys.platform == "darwin" and os.uname().machine == "arm64"


def print_system_info():
    """Print system information"""
    info = get_system_info()

    table = Table(title="System Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in info.items():
        table.add_row(key, str(value))

    console.print(table)

    # Check dependencies
    dependencies = check_dependencies()

    dep_table = Table(title="Dependencies")
    dep_table.add_column("Dependency", style="cyan")
    dep_table.add_column("Status", style="green")

    for dep, installed in dependencies:
        status = "✅ Installed" if installed else "❌ Missing"
        style = "green" if installed else "red"
        dep_table.add_row(dep, status, style=style)

    console.print(dep_table)


@app.command()
def verify(
    model: str = typer.Argument(..., help="Path to the AI model file to verify"),
    inputs: str = typer.Argument(..., help="Path to the input data"),
    expected_output: str = typer.Argument(
        ..., help="Path to the expected output or output data"
    ),
    model_type: str = typer.Option(
        "generic", help="Type of the model (generic, llama, etc.)"
    ),
    scheme: str = typer.Option(
        DEFAULT_SCHEME, help="ZKP scheme to use (g16, gm17, etc.)"
    ),
    output_dir: Optional[str] = typer.Option(
        None, help="Directory to store the proof artifacts"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output"
    ),
):
    """
    Verify an AI model using zero-knowledge proofs.

    This command performs the entire verification process:
    1. Compiles the model to a circuit
    2. Performs trusted setup
    3. Generates a proof
    4. Verifies the proof
    """
    # Set up logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logger("llamaverifier", log_level)

    print_banner()

    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Initialize components
    compiler = ZKPCompiler(workspace_dir=output_dir)
    proof_system = ProofSystem(workspace_dir=output_dir)

    # Step 1: Compile model to circuit
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Compiling model to circuit..."),
        transient=True,
    ) as progress:
        progress.add_task("compile", total=None)

        # Create temporary file for the circuit
        circuit_path = (
            os.path.join(output_dir, "model.circuit") if output_dir else "model.circuit"
        )

        # Compile model
        success = compiler.compile_model(
            model_path=model,
            output_path=circuit_path,
            model_type=model_type,
            optimization_level=1,
        )

        if not success:
            console.print("[bold red]Error: Failed to compile model to circuit")
            sys.exit(1)

    console.print(f"[green]✓[/green] Model compiled to circuit: {circuit_path}")

    # Step 2: Perform trusted setup
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Performing trusted setup..."),
        transient=True,
    ) as progress:
        progress.add_task("setup", total=None)

        # Perform setup
        try:
            proving_key_path, verification_key_path = proof_system.setup(
                circuit_path=circuit_path, scheme=scheme
            )
        except Exception as e:
            console.print(f"[bold red]Error: Failed to perform trusted setup: {e}")
            sys.exit(1)

    console.print(f"[green]✓[/green] Trusted setup completed")
    console.print(f"  Proving key: {proving_key_path}")
    console.print(f"  Verification key: {verification_key_path}")

    # Step 3: Read inputs and expected output
    try:
        with open(inputs, "r") as f:
            input_values = [line.strip() for line in f.readlines()]

        with open(expected_output, "r") as f:
            expected_values = [line.strip() for line in f.readlines()]
    except Exception as e:
        console.print(f"[bold red]Error: Failed to read inputs or expected output: {e}")
        sys.exit(1)

    # Step 4: Generate proof
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Generating proof..."),
        transient=True,
    ) as progress:
        progress.add_task("prove", total=None)

        # Generate proof
        try:
            proof_path, public_inputs_path = proof_system.generate_proof(
                circuit_path=circuit_path,
                proving_key_path=proving_key_path,
                witness_values=input_values + expected_values,
                scheme=scheme,
            )
        except Exception as e:
            console.print(f"[bold red]Error: Failed to generate proof: {e}")
            sys.exit(1)

    console.print(f"[green]✓[/green] Proof generated")
    console.print(f"  Proof: {proof_path}")
    console.print(f"  Public inputs: {public_inputs_path}")

    # Step 5: Verify proof
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Verifying proof..."),
        transient=True,
    ) as progress:
        progress.add_task("verify", total=None)

        # Verify proof
        try:
            valid = proof_system.verify_proof(
                verification_key_path=verification_key_path,
                proof_path=proof_path,
                public_inputs_path=public_inputs_path,
                scheme=scheme,
            )
        except Exception as e:
            console.print(f"[bold red]Error: Failed to verify proof: {e}")
            sys.exit(1)

    if valid:
        console.print(
            "[bold green]✓ Verification successful! The model execution is correct.[/bold green]"
        )
    else:
        console.print(
            "[bold red]✗ Verification failed! The model execution is incorrect.[/bold red]"
        )
        sys.exit(1)


@app.command()
def compile(
    model: str = typer.Argument(..., help="Path to the AI model file to compile"),
    output: str = typer.Argument(
        ..., help="Path where the compiled circuit will be saved"
    ),
    model_type: str = typer.Option(
        "generic", help="Type of the model (generic, llama, etc.)"
    ),
    optimization_level: int = typer.Option(1, help="Optimization level (0-3)"),
):
    """
    Compile an AI model into a ZKP circuit.
    """
    print_banner()

    # Initialize compiler
    compiler = ZKPCompiler()

    console.print(f"Compiling model: {model}")
    console.print(f"Model type: {model_type}")
    console.print(f"Optimization level: {optimization_level}")

    # Compile model
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Compiling..."),
        transient=True,
    ) as progress:
        progress.add_task("compile", total=None)

        success = compiler.compile_model(
            model_path=model,
            output_path=output,
            model_type=model_type,
            optimization_level=optimization_level,
        )

    if success:
        console.print(
            f"[bold green]✓ Model compiled successfully to: {output}[/bold green]"
        )
    else:
        console.print("[bold red]✗ Failed to compile model[/bold red]")
        sys.exit(1)


@app.command()
def setup(
    circuit: str = typer.Argument(..., help="Path to the compiled circuit"),
    output_dir: str = typer.Argument(
        ..., help="Directory to store the proving and verification keys"
    ),
    scheme: str = typer.Option(
        DEFAULT_SCHEME, help="ZKP scheme to use (g16, gm17, etc.)"
    ),
    participants: int = typer.Option(
        1, help="Number of participants in the MPC ceremony (not fully implemented)"
    ),
):
    """
    Perform trusted setup for a circuit.
    """
    print_banner()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize proof system
    proof_system = ProofSystem(workspace_dir=output_dir)

    console.print(f"Performing trusted setup for circuit: {circuit}")
    console.print(f"Scheme: {scheme}")

    if participants > 1:
        console.print(
            "[yellow]Warning: Multi-party computation is not fully implemented yet. Using single-party setup.[/yellow]"
        )

    # Perform setup
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Performing trusted setup..."),
        transient=True,
    ) as progress:
        progress.add_task("setup", total=None)

        try:
            proving_key_path, verification_key_path = proof_system.setup(
                circuit_path=circuit, scheme=scheme
            )
        except Exception as e:
            console.print(
                f"[bold red]Error: Failed to perform trusted setup: {e}[/bold red]"
            )
            sys.exit(1)

    console.print(f"[bold green]✓ Trusted setup completed[/bold green]")
    console.print(f"  Proving key: {proving_key_path}")
    console.print(f"  Verification key: {verification_key_path}")


@app.command()
def prove(
    circuit: str = typer.Argument(..., help="Path to the compiled circuit"),
    proving_key: str = typer.Argument(..., help="Path to the proving key"),
    witness_file: str = typer.Argument(
        ..., help="Path to the file containing witness values"
    ),
    output_dir: str = typer.Argument(
        ..., help="Directory to store the proof and public inputs"
    ),
    scheme: str = typer.Option(
        DEFAULT_SCHEME, help="ZKP scheme to use (g16, gm17, etc.)"
    ),
):
    """
    Generate a proof for a circuit.
    """
    print_banner()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Initialize proof system
    proof_system = ProofSystem(workspace_dir=output_dir)

    console.print(f"Generating proof for circuit: {circuit}")
    console.print(f"Proving key: {proving_key}")
    console.print(f"Witness file: {witness_file}")
    console.print(f"Scheme: {scheme}")

    # Read witness values
    try:
        with open(witness_file, "r") as f:
            witness_values = [line.strip() for line in f.readlines()]
    except Exception as e:
        console.print(f"[bold red]Error: Failed to read witness file: {e}[/bold red]")
        sys.exit(1)

    # Generate proof
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Generating proof..."),
        transient=True,
    ) as progress:
        progress.add_task("prove", total=None)

        try:
            proof_path, public_inputs_path = proof_system.generate_proof(
                circuit_path=circuit,
                proving_key_path=proving_key,
                witness_values=witness_values,
                scheme=scheme,
            )
        except Exception as e:
            console.print(f"[bold red]Error: Failed to generate proof: {e}[/bold red]")
            sys.exit(1)

    console.print(f"[bold green]✓ Proof generated[/bold green]")
    console.print(f"  Proof: {proof_path}")
    console.print(f"  Public inputs: {public_inputs_path}")


@app.command()
def verify_proof(
    verification_key: str = typer.Argument(..., help="Path to the verification key"),
    proof: str = typer.Argument(..., help="Path to the proof file"),
    public_inputs: str = typer.Argument(..., help="Path to the public inputs file"),
    scheme: str = typer.Option(
        DEFAULT_SCHEME, help="ZKP scheme to use (g16, gm17, etc.)"
    ),
):
    """
    Verify a proof.
    """
    print_banner()

    # Initialize proof system
    proof_system = ProofSystem()

    console.print(f"Verifying proof: {proof}")
    console.print(f"Verification key: {verification_key}")
    console.print(f"Public inputs: {public_inputs}")
    console.print(f"Scheme: {scheme}")

    # Verify proof
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Verifying proof..."),
        transient=True,
    ) as progress:
        progress.add_task("verify", total=None)

        try:
            valid = proof_system.verify_proof(
                verification_key_path=verification_key,
                proof_path=proof,
                public_inputs_path=public_inputs,
                scheme=scheme,
            )
        except Exception as e:
            console.print(f"[bold red]Error: Failed to verify proof: {e}[/bold red]")
            sys.exit(1)

    if valid:
        console.print(
            "[bold green]✓ Verification successful! The proof is valid.[/bold green]"
        )
    else:
        console.print(
            "[bold red]✗ Verification failed! The proof is invalid.[/bold red]"
        )
        sys.exit(1)


@app.command()
def export(
    verification_key: str = typer.Argument(..., help="Path to the verification key"),
    output: str = typer.Argument(
        ..., help="Path where the Solidity verifier contract will be saved"
    ),
    scheme: str = typer.Option(
        DEFAULT_SCHEME, help="ZKP scheme to use (g16, gm17, etc.)"
    ),
):
    """
    Export a Solidity verifier contract.
    """
    print_banner()

    # Initialize proof system
    proof_system = ProofSystem()

    console.print(f"Exporting verifier contract")
    console.print(f"Verification key: {verification_key}")
    console.print(f"Output: {output}")
    console.print(f"Scheme: {scheme}")

    # Export verifier
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Exporting verifier contract..."),
        transient=True,
    ) as progress:
        progress.add_task("export", total=None)

        try:
            verifier_path = proof_system.export_verifier(
                verification_key_path=verification_key,
                output_path=output,
                scheme=scheme,
            )
        except Exception as e:
            console.print(
                f"[bold red]Error: Failed to export verifier contract: {e}[/bold red]"
            )
            sys.exit(1)

    console.print(
        f"[bold green]✓ Verifier contract exported to: {verifier_path}[/bold green]"
    )


@app.command()
def server(
    host: str = typer.Option("0.0.0.0", help="Host to bind the server to"),
    port: int = typer.Option(8000, help="Port to bind the server to"),
    debug: bool = typer.Option(False, help="Enable debug mode"),
):
    """
    Start the API server.
    """
    print_banner()

    console.print(f"Starting API server on {host}:{port}")

    try:
        from ..api.server import start_server

        start_server(host=host, port=port, debug=debug)
    except ImportError:
        console.print(
            "[bold red]Error: API server module not found. Make sure the API dependencies are installed.[/bold red]"
        )
        sys.exit(1)


@app.command()
def benchmark(
    model_type: str = typer.Option(
        "generic", help="Type of model to benchmark (generic, llama)"
    ),
    circuit_size: str = typer.Option(
        "small", help="Size of the circuit (small, medium, large)"
    ),
    scheme: str = typer.Option(
        DEFAULT_SCHEME, help="ZKP scheme to use (g16, gm17, etc.)"
    ),
    runs: int = typer.Option(3, help="Number of benchmark runs"),
):
    """
    Run benchmarks for the ZKP system.
    """
    print_banner()

    console.print(f"Running benchmarks")
    console.print(f"Model type: {model_type}")
    console.print(f"Circuit size: {circuit_size}")
    console.print(f"Scheme: {scheme}")
    console.print(f"Runs: {runs}")

    # Create temporary directory for benchmark artifacts
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize components
        compiler = ZKPCompiler(workspace_dir=temp_dir)
        proof_system = ProofSystem(workspace_dir=temp_dir)

        # Define circuit sizes
        sizes = {
            "small": {"params": 10, "inputs": 5},
            "medium": {"params": 100, "inputs": 20},
            "large": {"params": 1000, "inputs": 50},
        }

        if circuit_size not in sizes:
            console.print(
                f"[bold red]Error: Invalid circuit size: {circuit_size}. Must be one of: {', '.join(sizes.keys())}[/bold red]"
            )
            sys.exit(1)

        size_config = sizes[circuit_size]

        # Create a temporary model file
        model_path = os.path.join(temp_dir, "benchmark_model.txt")
        with open(model_path, "w") as f:
            f.write(f"# Benchmark model\n")
            f.write(f"# Type: {model_type}\n")
            f.write(f"# Size: {circuit_size}\n")
            for i in range(size_config["params"]):
                f.write(f"param_{i}={i}\n")

        # Create a temporary input file
        input_path = os.path.join(temp_dir, "benchmark_input.txt")
        with open(input_path, "w") as f:
            for i in range(size_config["inputs"]):
                f.write(f"{i}\n")

        # Create a temporary expected output file
        output_path = os.path.join(temp_dir, "benchmark_output.txt")
        with open(output_path, "w") as f:
            f.write("1\n")  # Simple expected output

        # Run benchmarks
        results = {"compile": [], "setup": [], "prove": [], "verify": []}

        for run in range(runs):
            console.print(f"[bold]Run {run + 1}/{runs}[/bold]")

            # Benchmark compilation
            circuit_path = os.path.join(temp_dir, f"benchmark_circuit_{run}.out")
            console.print("  Benchmarking compilation...", end="")
            start_time = time.time()
            success = compiler.compile_model(
                model_path=model_path,
                output_path=circuit_path,
                model_type=model_type,
                optimization_level=1,
            )
            compile_time = time.time() - start_time
            results["compile"].append(compile_time)
            console.print(f" {compile_time:.2f}s")

            if not success:
                console.print("[bold red]  Error: Failed to compile model[/bold red]")
                continue

            # Benchmark setup
            console.print("  Benchmarking trusted setup...", end="")
            start_time = time.time()
            try:
                proving_key_path, verification_key_path = proof_system.setup(
                    circuit_path=circuit_path, scheme=scheme
                )
                setup_time = time.time() - start_time
                results["setup"].append(setup_time)
                console.print(f" {setup_time:.2f}s")
            except Exception as e:
                console.print(
                    f"[bold red]  Error: Failed to perform trusted setup: {e}[/bold red]"
                )
                continue

            # Read input values
            with open(input_path, "r") as f:
                input_values = [line.strip() for line in f.readlines()]

            # Read expected output values
            with open(output_path, "r") as f:
                expected_values = [line.strip() for line in f.readlines()]

            # Benchmark proof generation
            console.print("  Benchmarking proof generation...", end="")
            start_time = time.time()
            try:
                proof_path, public_inputs_path = proof_system.generate_proof(
                    circuit_path=circuit_path,
                    proving_key_path=proving_key_path,
                    witness_values=input_values + expected_values,
                    scheme=scheme,
                )
                prove_time = time.time() - start_time
                results["prove"].append(prove_time)
                console.print(f" {prove_time:.2f}s")
            except Exception as e:
                console.print(
                    f"[bold red]  Error: Failed to generate proof: {e}[/bold red]"
                )
                continue

            # Benchmark verification
            console.print("  Benchmarking proof verification...", end="")
            start_time = time.time()
            try:
                valid = proof_system.verify_proof(
                    verification_key_path=verification_key_path,
                    proof_path=proof_path,
                    public_inputs_path=public_inputs_path,
                    scheme=scheme,
                )
                verify_time = time.time() - start_time
                results["verify"].append(verify_time)
                console.print(f" {verify_time:.2f}s")
            except Exception as e:
                console.print(
                    f"[bold red]  Error: Failed to verify proof: {e}[/bold red]"
                )
                continue

        # Print benchmark results
        console.print("\n[bold]Benchmark Results[/bold]")

        table = Table(
            title=f"Benchmark Results ({model_type}, {circuit_size}, {scheme})"
        )
        table.add_column("Operation", style="cyan")
        table.add_column("Min (s)", style="green")
        table.add_column("Max (s)", style="yellow")
        table.add_column("Avg (s)", style="blue")

        for operation, times in results.items():
            if times:
                min_time = min(times)
                max_time = max(times)
                avg_time = sum(times) / len(times)
                table.add_row(
                    operation, f"{min_time:.2f}", f"{max_time:.2f}", f"{avg_time:.2f}"
                )
            else:
                table.add_row(operation, "N/A", "N/A", "N/A")

        console.print(table)


@app.command()
def info():
    """
    Display system information and check dependencies.
    """
    print_banner()
    print_system_info()


def main():
    """Main entry point for the CLI"""
    app()
