#!/usr/bin/env python3
"""
Setup script for LlamaVerifier
"""
import os

from setuptools import find_packages, setup

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

# Optional dependencies
extras_require = {
    "dev": [
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "black>=23.7.0",
        "isort>=5.12.0",
        "mypy>=1.5.0",
    ],
    "docs": [
        "mkdocs>=1.5.2",
        "mkdocs-material>=9.2.7",
    ],
    "apple": [
        "mlx>=0.0.5",
    ],
}

# Get version from package
about = {}
with open(os.path.join("llamaverifier", "__init__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

setup(
    name="llamaverifier",
    version=about["__version__"],
    author="Nik Jois" "Nik Jois" "Nik Jois" "Nik Jois" "Nik Jois",
    author_email="nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai"
    "nikjois@llamasearch.ai",
    description="Zero-Knowledge Proof System for AI Model Verification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/llamaverifier",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "llamaverifier=llamaverifier.cli.commands:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
