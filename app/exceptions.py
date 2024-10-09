"""
This module handles custom exceptions
"""


class EnvironmentException(KeyError):
    """Raised when there's an issue with the environment variables"""

    pass


class NoDocumentsException(KeyError):
    """Raised when no documents are loaded from a vector store"""

    pass
