"""
Module defining pydantic models that will be used
through the app to ensure data quality.
"""

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Represents metadata for a document.

    Attributes:
        document_id (str): Unique identifier for the document.
        filename (str): Name of the document file.
        page_count (int): Total number of pages in the document.
    """

    document_id: str
    filename: str
    page_count: int


class ChunkMetadata(DocumentMetadata):
    """Represents metadata for a document chunk.

    Inherits from DocumentMetadata and adds chunk-specific information.

    Attributes:
        start_index (int): The starting index of the chunk within the document.
    """

    start_index: int
