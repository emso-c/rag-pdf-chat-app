"""
Module for file hashing and file UUID generation.
"""

import hashlib
import uuid


def get_file_hash(file_path: str) -> bytes:
    """Compute the SHA-256 hash of a file.

    Args:
        file_path (str): The path to the file for which to compute the hash.

    Returns:
        bytes: The SHA-256 hash of the file as a byte string.
    """
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).digest()


def generate_uuid_from_file(file_path: str) -> uuid.UUID:
    """Generate a UUID based on the file's hash, using the first 16 bytes.

    Args:
        file_path (str): The path to the file from which to generate the UUID.

    Returns:
        uuid.UUID: A UUID generated from the first 16 bytes of the file's hash.
    """
    file_hash = get_file_hash(file_path)
    return uuid.UUID(bytes=file_hash[:16])
