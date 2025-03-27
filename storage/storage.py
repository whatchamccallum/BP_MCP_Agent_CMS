"""
Storage interface for the CMS.
"""

import os
from abc import ABC, abstractmethod
from typing import BinaryIO, List, Optional, Tuple


class StorageInterface(ABC):
    """Interface for storage backends."""

    @abstractmethod
    def save_file(self, file_data: BinaryIO, file_path: str) -> str:
        """
        Save a file to storage.

        Args:
            file_data: File data as a file-like object
            file_path: Path to save the file to

        Returns:
            str: Full path to the saved file
        """
        pass

    @abstractmethod
    def get_file(self, file_path: str) -> Tuple[BinaryIO, str]:
        """
        Get a file from storage.

        Args:
            file_path: Path to the file

        Returns:
            Tuple[BinaryIO, str]: File data as a file-like object and content type
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def list_files(self, directory_path: str) -> List[str]:
        """
        List files in a directory.

        Args:
            directory_path: Path to the directory

        Returns:
            List[str]: List of file paths
        """
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if the file exists, False otherwise
        """
        pass
