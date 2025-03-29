"""
LlamaVerifier - Zero-Knowledge Proof System for AI Model Verification
"""

__version__ = "0.1.0"
__author__ = "LlamaVerifier Contributors"
__license__ = "MIT"

from .cli import commands
from .api import server
from .circuits import compiler
from .proofs import generator
from .utils import logger 