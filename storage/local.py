"""
Local file storage implementation for the CMS.
"""

import os
import shutil
import tempfile
from typing import BinaryIO, List, Optional, Tuple
import magic

from .storage import StorageInterface


class LocalStorage(StorageInterface):
    """Local file storage implementation."""

    def __init__(self, base_dir: str):
        """
        Initialize local storage.

        Args:
            base_dir: Base directory for file storage
        """
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_full_path(self, file_path: str) -> str:
        """
        Get the full path to a file.

        Args:
            file_path: Relative path to the file

        Returns:
            str: Full path to the file
        """
        # Clean the file path to prevent directory traversal attacks
        clean_path = os.path.normpath(file_path).lstrip(os.path.sep)
        return os.path.join(self.base_dir, clean_path)

    def save_file(self, file_data: BinaryIO, file_path: str) -> str:
        """
        Save a file to local storage.

        Args:
            file_data: File data as a file-like object
            file_path: Path to save the file to

        Returns:
            str: Full path to the saved file
        """
        full_path = self._get_full_path(file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write the file
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_data, f)

        return file_path

    def get_file(self, file_path: str) -> Tuple[BinaryIO, str]:
        """
        Get a file from local storage.

        Args:
            file_path: Path to the file

        Returns:
            Tuple[BinaryIO, str]: File data as a file-like object and content type

        Raises:
            FileNotFoundError: If the file does not exist
        """
        full_path = self._get_full_path(file_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Create a temporary file to return
        temp_file = tempfile.TemporaryFile()
        with open(full_path, 'rb') as f:
            shutil.copyfileobj(f, temp_file)
        temp_file.seek(0)

        # Detect the content type
        content_type = magic.from_file(full_path, mime=True)

        return temp_file, content_type

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from local storage.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if successful, False otherwise
        """
        full_path = self._get_full_path(file_path)

        if not os.path.exists(full_path):
            return False

        try:
            os.remove(full_path)
            return True
        except OSError:
            return False

    def list_files(self, directory_path: str) -> List[str]:
        """
        List files in a directory.

        Args:
            directory_path: Path to the directory

        Returns:
            List[str]: List of file paths
        """
        full_path = self._get_full_path(directory_path)

        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return []

        files = []
        for root, _, filenames in os.walk(full_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, self.base_dir)
                files.append(rel_path)

        return files

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if the file exists, False otherwise
        """
        full_path = self._get_full_path(file_path)
        return os.path.exists(full_path) and os.path.isfile(full_path)
