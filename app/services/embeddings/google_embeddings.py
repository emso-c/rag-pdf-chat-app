"""
Module for initializing embeddings using Google Generative AI.

This module sets up embeddings using the Google Generative AI Embeddings 
from the LangChain library. It leverages the provided Google API key 
from the environment configuration to access the specified model for 
generating embeddings.

Embeddings Instance:
- gemini_embeddings: An instance of GoogleGenerativeAIEmbeddings configured 
  with the model and API key.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import env_config

gemini_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=env_config.google_api_key
)
