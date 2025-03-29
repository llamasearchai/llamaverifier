"""
Tests for the main module
"""
import os
import sys
from unittest import TestCase, mock

import pytest

from llamaverifier.__main__ import main


class TestMain(TestCase):
    """Test cases for the main module"""
    
    @mock.patch("llamaverifier.__main__.app")
    def test_main(self, mock_app):
        """Test main function"""
        # Test main function with no arguments
        sys.argv = ["llamaverifier"]
        main()
        mock_app.assert_called_once()
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test main function with arguments
        sys.argv = ["llamaverifier", "info"]
        main()
        mock_app.assert_called_once_with(["info"])
    
    @mock.patch("llamaverifier.__main__.app")
    def test_main_with_args(self, mock_app):
        """Test main function with various arguments"""
        # Test with info command
        sys.argv = ["llamaverifier", "info"]
        main()
        mock_app.assert_called_once_with(["info"])
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test with compile command
        sys.argv = ["llamaverifier", "compile", "--model", "model.txt"]
        main()
        mock_app.assert_called_once_with(["compile", "--model", "model.txt"])
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test with setup command
        sys.argv = ["llamaverifier", "setup", "--circuit", "circuit.zok"]
        main()
        mock_app.assert_called_once_with(["setup", "--circuit", "circuit.zok"])
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test with prove command
        sys.argv = ["llamaverifier", "prove", "--circuit", "circuit.zok", "--witness", "witness.json"]
        main()
        mock_app.assert_called_once_with(["prove", "--circuit", "circuit.zok", "--witness", "witness.json"])
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test with verify-proof command
        sys.argv = ["llamaverifier", "verify-proof", "--verification-key", "vk.key", "--proof", "proof.json"]
        main()
        mock_app.assert_called_once_with(["verify-proof", "--verification-key", "vk.key", "--proof", "proof.json"])
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test with export command
        sys.argv = ["llamaverifier", "export", "--verification-key", "vk.key"]
        main()
        mock_app.assert_called_once_with(["export", "--verification-key", "vk.key"])
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test with server command
        sys.argv = ["llamaverifier", "server", "--host", "127.0.0.1", "--port", "8000"]
        main()
        mock_app.assert_called_once_with(["server", "--host", "127.0.0.1", "--port", "8000"])
        
        # Reset mock
        mock_app.reset_mock()
        
        # Test with verify command (end-to-end)
        sys.argv = ["llamaverifier", "verify", "--model", "model.txt", "--input", "input.json"]
        main()
        mock_app.assert_called_once_with(["verify", "--model", "model.txt", "--input", "input.json"])
    
    @mock.patch("llamaverifier.__main__.app")
    @mock.patch("sys.exit")
    def test_main_exception(self, mock_exit, mock_app):
        """Test main function with exception"""
        # Mock app to raise an exception
        mock_app.side_effect = Exception("Test exception")
        
        # Test main function with exception
        sys.argv = ["llamaverifier"]
        main()
        
        # Check that sys.exit was called with code 1
        mock_exit.assert_called_once_with(1)
    
    @mock.patch("llamaverifier.__main__.app")
    @mock.patch("sys.exit")
    def test_main_keyboard_interrupt(self, mock_exit, mock_app):
        """Test main function with KeyboardInterrupt"""
        # Mock app to raise a KeyboardInterrupt
        mock_app.side_effect = KeyboardInterrupt()
        
        # Test main function with KeyboardInterrupt
        sys.argv = ["llamaverifier"]
        main()
        
        # Check that sys.exit was called with code 0
        mock_exit.assert_called_once_with(0) 