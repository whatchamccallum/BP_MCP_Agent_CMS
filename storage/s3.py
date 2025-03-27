"""
S3-compatible storage implementation for the CMS.
"""

import os
import tempfile
from typing import BinaryIO, List, Optional, Tuple
import boto3
import magic
from botocore.exceptions import ClientError

from .storage import StorageInterface


class S3Storage(StorageInterface):
    """S3-compatible storage implementation."""

    def __init__(self, bucket_name: str, aws_access_key_id: Optional[str] = None,
                aws_secret_access_key: Optional[str] = None, region_name: Optional[str] = None,
                endpoint_url: Optional[str] = None):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            aws_access_key_id: AWS access key ID (optional if using instance profile)
            aws_secret_access_key: AWS secret access key (optional if using instance profile)
            region_name: AWS region name (optional)
            endpoint_url: S3-compatible endpoint URL (optional, for non-AWS S3)
        """
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url
        )

        # Ensure the bucket exists
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            # If the bucket doesn't exist, create it
            if e.response['Error']['Code'] == '404':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                raise

    def save_file(self, file_data: BinaryIO, file_path: str) -> str:
        """
        Save a file to S3 storage.

        Args:
            file_data: File data as a file-like object
            file_path: Path to save the file to

        Returns:
            str: Full path to the saved file
        """
        # Clean the file path to prevent issues
        clean_path = file_path.lstrip('/')

        # Upload the file
        self.s3.upload_fileobj(file_data, self.bucket_name, clean_path)

        return clean_path

    def get_file(self, file_path: str) -> Tuple[BinaryIO, str]:
        """
        Get a file from S3 storage.

        Args:
            file_path: Path to the file

        Returns:
            Tuple[BinaryIO, str]: File data as a file-like object and content type

        Raises:
            FileNotFoundError: If the file does not exist
        """
        # Clean the file path
        clean_path = file_path.lstrip('/')

        # Check if the file exists
        try:
            head = self.s3.head_object(Bucket=self.bucket_name, Key=clean_path)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise FileNotFoundError(f"File not found: {file_path}")
            else:
                raise

        # Get the content type from head or detect it after downloading
        content_type = head.get('ContentType', 'application/octet-stream')

        # Download the file to a temporary file
        temp_file = tempfile.TemporaryFile()
        self.s3.download_fileobj(self.bucket_name, clean_path, temp_file)
        temp_file.seek(0)

        # If content type is generic, try to detect it
        if content_type == 'application/octet-stream':
            # Create another temporary file for magic to use
            with tempfile.NamedTemporaryFile(delete=False) as named_temp:
                temp_file.seek(0)
                named_temp.write(temp_file.read())
                named_temp.close()
                
                try:
                    content_type = magic.from_file(named_temp.name, mime=True)
                finally:
                    os.unlink(named_temp.name)
                    temp_file.seek(0)

        return temp_file, content_type

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from S3 storage.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if successful, False otherwise
        """
        # Clean the file path
        clean_path = file_path.lstrip('/')

        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=clean_path)
            return True
        except ClientError:
            return False

    def list_files(self, directory_path: str) -> List[str]:
        """
        List files in a directory.

        Args:
            directory_path: Path to the directory

        Returns:
            List[str]: List of file paths
        """
        # Clean the directory path
        clean_path = directory_path.lstrip('/').rstrip('/') + '/' if directory_path else ''

        try:
            paginator = self.s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=clean_path)

            files = []
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append(obj['Key'])

            return files
        except ClientError:
            return []

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to the file

        Returns:
            bool: True if the file exists, False otherwise
        """
        # Clean the file path
        clean_path = file_path.lstrip('/')

        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=clean_path)
            return True
        except ClientError:
            return False
