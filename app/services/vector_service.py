"""
Module for managing vector stores using LangChain and Chroma.
"""

from pathlib import Path
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings


def save_vectorstore(
    col_name: str | Path,
    documents: list[Document],
    embeddings: Embeddings,
    dir_path: str,
) -> Chroma:
    """Saves a list of documents into a Chroma vector store.

    Args:
        col_name (str | Path): The name of the collection to save the documents.
        documents (list[Document]): A list of Document objects to save.
        embeddings (Embeddings): The embedding function to use for the documents.
        dir_path (str): The directory path for persistent storage.

    Returns:
        Chroma: The Chroma vector store instance after saving the documents.
    """
    return Chroma.from_documents(
        collection_name=col_name,
        # documents=filter_complex_metadata(documents),
        documents=documents,
        embedding=embeddings,
        persist_directory=str(
            dir_path
        ),  # implicit conversion to prevnet the windowspath issue
    )


def load_vectorstore(
    col_name: str, from_dir: str | Path, use_embeddings: Embeddings
) -> Chroma:
    """Loads a Chroma vector store from a specified directory.

    Args:
        col_name (str): The name of the collection to load.
        from_dir (str | Path): The directory from which to load the vector store.
        use_embeddings (Embeddings): The embedding function to use with the vector store.

    Returns:
        Chroma: The loaded Chroma vector store instance.
    """
    vectorstore_disk = Chroma(
        collection_name=col_name,
        embedding_function=use_embeddings,
        persist_directory=str(
            from_dir
        ),  # implicit conversion to prevnet the windowspath issue
    )
    return vectorstore_disk
