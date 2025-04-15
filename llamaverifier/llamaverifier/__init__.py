"""
LlamaVerifier - Zero-Knowledge Proof System for AI Model Verification
"""

__version__ = "0.1.0"
__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__license__ = "MIT"

from .api import server
from .circuits import compiler
from .cli import commands
from .proofs import generator
from .utils import logger
