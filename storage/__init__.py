"""
Storage module for the CMS.
"""

import os
from typing import Optional

from .storage import StorageInterface
from .local import LocalStorage
from .s3 import S3Storage


def get_storage(storage_type: str = 'local', **kwargs) -> StorageInterface:
    """
    Get a storage implementation.

    Args:
        storage_type: Type of storage to use ('local' or 's3')
        **kwargs: Additional arguments for the storage implementation

    Returns:
        StorageInterface: Storage implementation

    Raises:
        ValueError: If the storage type is not supported
    """
    if storage_type.lower() == 'local':
        base_dir = kwargs.get('base_dir', os.path.join(os.getcwd(), 'storage_files'))
        return LocalStorage(base_dir)
    elif storage_type.lower() == 's3':
        bucket_name = kwargs.get('bucket_name')
        if not bucket_name:
            raise ValueError("Bucket name is required for S3 storage")
        
        return S3Storage(
            bucket_name=bucket_name,
            aws_access_key_id=kwargs.get('aws_access_key_id'),
            aws_secret_access_key=kwargs.get('aws_secret_access_key'),
            region_name=kwargs.get('region_name'),
            endpoint_url=kwargs.get('endpoint_url')
        )
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
