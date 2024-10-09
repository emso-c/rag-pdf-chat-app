"""
Module for implementing a Retrieval-Augmented Generation (RAG) chain.

This module sets up a RAG chain using LangChain to enhance question-answering 
capabilities for PDF documents. It leverages chromadb vector store for document 
retrieval, Google Generative AI for natural language processing, and manages 
chat history for context-aware responses. The module includes functionality 
to build and invoke the RAG chain while ensuring proper error handling 
for missing documents.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_chroma import Chroma
from app.config import app_config, env_config
from app.exceptions import NoDocumentsException
from app.services.history_service import load_history, save_history
from app.services.vector_service import load_vectorstore

from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from app.services.embeddings import gemini_embeddings
from app.utils.logger import logger
from langchain_core.runnables import Runnable


def _build_rag_chain(pdf_id: str, chat_history: list[tuple] = []):
    logger.debug(f"setting up RAG chain for: {pdf_id}")
    vectorstore: Chroma = load_vectorstore(
        col_name=pdf_id,
        from_dir=str(app_config.chroma_path),
        use_embeddings=gemini_embeddings,
    )

    if not vectorstore.get()["documents"]:
        raise NoDocumentsException

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=env_config.google_api_key,
    )

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            *chat_history[
                1:-1
            ],  # do not include the first system message and the last human input
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    qa_prompt = ChatPromptTemplate.from_messages(chat_history)
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


def invoke_rag_chain(pdf_id: str, query: str, user_id: str = None):
    chat_history = load_history(pdf_id, user_id) or app_config.default_history

    chain: Runnable = _build_rag_chain(pdf_id, chat_history)
    output: dict = chain.invoke({"input": query, "chat_history": chat_history})

    chat_history.pop(-1)
    chat_history.extend(
        [
            ("human", query),
            ("ai", output.get("answer")),
            ("human", "{input}"),
        ]
    )
    save_history(pdf_id, chat_history, user_id)

    return output  # , chat_history
