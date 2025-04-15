"""
Tests for the __init__.py module
"""
import os
import sys
from unittest import TestCase, mock

import pytest

import llamaverifier


class TestInit(TestCase):
    """Test cases for the __init__.py module"""
    
    def test_version(self):
        """Test version attribute"""
        # Check that the version attribute exists
        self.assertTrue(hasattr(llamaverifier, "__version__"))
        
        # Check that the version is a string
        self.assertIsInstance(llamaverifier.__version__, str)
        
        # Check that the version follows semantic versioning (major.minor.patch)
        version_parts = llamaverifier.__version__.split(".")
        self.assertEqual(len(version_parts), 3)
        
        # Check that each part is a number
        for part in version_parts:
            self.assertTrue(part.isdigit())
    
    def test_author(self):
        """Test author attribute"""
        # Check that the author attribute exists
        self.assertTrue(hasattr(llamaverifier, "__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__email__ = "nikjois@llamasearch.ai""))
        
        # Check that the author is a string
        self.assertIsInstance(llamaverifier.__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__email__ = "nikjois@llamasearch.ai", str)
        
        # Check that the author is not empty
        self.assertTrue(len(llamaverifier.__author__ = "Nik Jois"
__email__ = "nikjois@llamasearch.ai" = "Nik Jois"
__email__ = "nikjois@llamasearch.ai") > 0)
    
    def test_email(self):
        """Test email attribute"""
        # Check that the email attribute exists
        self.assertTrue(hasattr(llamaverifier, "__email__"))
        
        # Check that the email is a string
        self.assertIsInstance(llamaverifier.__email__, str)
        
        # Check that the email is not empty
        self.assertTrue(len(llamaverifier.__email__) > 0)
        
        # Check that the email contains @ symbol
        self.assertIn("@", llamaverifier.__email__)
    
    def test_description(self):
        """Test description attribute"""
        # Check that the description attribute exists
        self.assertTrue(hasattr(llamaverifier, "__description__"))
        
        # Check that the description is a string
        self.assertIsInstance(llamaverifier.__description__, str)
        
        # Check that the description is not empty
        self.assertTrue(len(llamaverifier.__description__) > 0)
    
    def test_url(self):
        """Test url attribute"""
        # Check that the url attribute exists
        self.assertTrue(hasattr(llamaverifier, "__url__"))
        
        # Check that the url is a string
        self.assertIsInstance(llamaverifier.__url__, str)
        
        # Check that the url is not empty
        self.assertTrue(len(llamaverifier.__url__) > 0)
        
        # Check that the url starts with http:// or https://
        self.assertTrue(llamaverifier.__url__.startswith("http://") or 
                        llamaverifier.__url__.startswith("https://"))
    
    def test_package_structure(self):
        """Test package structure"""
        # Check that the circuits module exists
        self.assertTrue(hasattr(llamaverifier, "circuits"))
        
        # Check that the proofs module exists
        self.assertTrue(hasattr(llamaverifier, "proofs"))
        
        # Check that the cli module exists
        self.assertTrue(hasattr(llamaverifier, "cli"))
        
        # Check that the api module exists
        self.assertTrue(hasattr(llamaverifier, "api"))
    
    def test_imports(self):
        """Test imports"""
        # Check that the ZKPCompiler class is importable
        from llamaverifier.circuits import ZKPCompiler
        self.assertTrue(callable(ZKPCompiler))
        
        # Check that the ProofSystem class is importable
        from llamaverifier.proofs import ProofSystem
        self.assertTrue(callable(ProofSystem))
        
        # Check that the SchemeType enum is importable
        from llamaverifier.proofs.schemes import SchemeType
        self.assertTrue(isinstance(SchemeType, type))
        
        # Check that the app is importable
        from llamaverifier.cli import app
        self.assertTrue(hasattr(app, "__call__"))
        
        # Check that the API app is importable
        from llamaverifier.api import app
        self.assertTrue(hasattr(app, "__call__")) 