"""
File utility functions for LlamaVerifier
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union

from .logger import get_logger

logger = get_logger(__name__)


def check_file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if a file exists at the specified path.

    Args:
        file_path: Path to the file

    Returns:
        True if the file exists, False otherwise
    """
    if not file_path:
        return False

    path = Path(file_path)
    return path.exists() and path.is_file()


def ensure_directory(directory_path: Union[str, Path]) -> Path:
    """
    Ensure that a directory exists at the specified path.
    Create it if it doesn't exist.

    Args:
        directory_path: Path to the directory

    Returns:
        Path object for the directory
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_temp_file(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    directory: Optional[str] = None,
    delete: bool = False,
) -> str:
    """
    Get a temporary file path.

    Args:
        suffix: File suffix (e.g., '.txt')
        prefix: File prefix
        directory: Directory to create the file in
        delete: Whether to delete the file when closed

    Returns:
        Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(
        suffix=suffix, prefix=prefix, dir=directory, delete=delete
    ) as temp:
        return temp.name


def list_files(
    directory: Union[str, Path], pattern: Optional[str] = None, recursive: bool = False
) -> List[Path]:
    """
    List files in a directory, optionally filtering by pattern and recursing.

    Args:
        directory: Directory to list files from
        pattern: Glob pattern to filter files (e.g., '*.txt')
        recursive: Whether to recursively list files in subdirectories

    Returns:
        List of Path objects for matching files
    """
    path = Path(directory)

    if not path.exists() or not path.is_dir():
        logger.warning(f"Directory does not exist: {directory}")
        return []

    if recursive:
        if pattern:
            return list(path.glob(f"**/{pattern}"))
        else:
            return [p for p in path.glob("**/*") if p.is_file()]
    else:
        if pattern:
            return list(path.glob(pattern))
        else:
            return [p for p in path.iterdir() if p.is_file()]


def copy_with_confirmation(
    src: Union[str, Path], dest: Union[str, Path], overwrite: bool = False
) -> bool:
    """
    Copy a file with confirmation if the destination exists.

    Args:
        src: Source file path
        dest: Destination file path
        overwrite: Whether to overwrite existing files without confirmation

    Returns:
        True if the file was copied, False otherwise
    """
    src_path = Path(src)
    dest_path = Path(dest)

    if not src_path.exists():
        logger.error(f"Source file does not exist: {src}")
        return False

    if dest_path.exists() and not overwrite:
        logger.warning(f"Destination file already exists: {dest}")
        return False

    try:
        shutil.copy2(src_path, dest_path)
        logger.debug(f"Copied {src} to {dest}")
        return True
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        return False
