# Overview

This project is a FastAPI-based API designed to manage and process PDF documents, enabling users to chat and interact with the content through a custom RAG model, utilizing ChromaDB, Langchain and Gemini. The application also offers a basic client UI application to interact with the API.

The code is mostly written in Python and uses Black linter to ensure consisten formatting. Module and function level documentation on detailed implementation can be found in the code.

## API Endpoints

Below is a brief overview of the API endpoints implemented. X-AUTH header can be set to simulate different user interactions with the same content. See [Viewing the Application](#viewing-the-application) section for an in-depth API documentation.

### Upload PDF
- POST /v1/pdf
    - Uploads a PDF file, validates it, and processes it asynchronously.

### Get All Documents
- GET /v1/pdf/all
    - Retrieves a list of all uploaded document IDs.

### Chat with PDF
- POST /v1/chat/{pdf_id}
    - Engages in a chat about a specific PDF document, utilizing both historical context and real-time processing.

### Get Uploaded PDF File
- GET /static/{pdf_id}.pdf
    - Retrieves the uploaded document itself.

### Get Chat History
- GET /v1/history/{pdf_id}
    - Retrieves the chat history associated with a specific document.

### Delete Chat History
- DELETE /v1/history/{pdf_id}
    -Deletes the chat history for a specified document.

# Installation

- Clone the repository:

```bash
git clone <repository-url>
cd path/to/project/root
```

- Create environment files:
```bash
touch .env & touch .env.prod
```
- Provide the following keys for both environments:
  - GOOGLE_API_KEY
    - e.g. `AIzaSyX-2Bghy6kEfGdHJYVt3ZyK0pEF3klm8K`
  - REDIS_URL 
    - e.g. `redis://localhost:6379`

- Follow the steps for either production or development setups.

## For Production (recommended to inspect the application)

### Prerequisites:
  - Docker Desktop installed and running on your system. (can be installed by adhering to the instructions provided on the  [official website](https://docs.docker.com/desktop/))

### Setup
- No additional configurations are required.

### Running the application:
```bash
# Spin up the application.
docker-compose up --build -d

# View the application logs.
docker-compose logs -f

# Spin down the application.
docker-compose down
```



## For Development

### Prerequisites:
  - Python >= 3.9
  - Redis server accepting connections on `redis://localhost:6379`
    - example using docker:
        ```bash
        docker run --name redis-instance -p 6379:6379 -d redis
        ```

### Setup
- Set up the project environment.
    ```bash
    python -m venv .venv
    ```
  - Activate the environment.
    ```bash
    source .venv/bin/activate # On Linux
    # or
    .venv\Scripts\activate # On Windows
    ```
- if `ENV` variable is set in your system, unset it or make sure its value is `dev`, as the application determines which configuration to use by reading this variable.
- Install required packages for the API application
    ```bash
    pip install -r requirements.txt
    ```
- If the client application will be used, install the required packages
    ```bash
    # Another virtual environment can be used to seperate the requirements.
    pip install -r requirements.client.txt
    ```


### Running the application
- after making sure redis instance is running, use different terminals to run these commands in the following order, as they depend on each other.
```bash
# Run the celery worker
celery -A app.tasks worker -P threads

# Run the API server.
uvicorn app.main:app

# Run the streamlit client (optional).
streamlit run streamlit_app.py --server.headless true
```


## Viewing the Application
- After following the setup instructions for either development or production, API should be running on `http://localhost:8000`
- Test if the API is running, the response should be `"pong"`
  ```bash
  curl http://localhost:8000/ping
  >"pong"
  ```
- See the API documentation running on `http://localhost:8000/docs#`
- (Optional) Interact with the app using streamlit client running on `http://localhost:8501`
<br>


## Testing

### Using docker
```bash
# Build the image
docker build -t test-image -f docker\test.Dockerfile .

# Run the image
docker run -it test-image
```

### Using local terminal
```bash
# Install requirements
pip install -r requirements.test.txt

# Run tests
pytest -v
```

# Directory Structure

```bash
└─ project 
    ├── .env                                # Environment variables for configuration
    ├── .env.prod                           # Production environment variables
    ├── .gitignore                          # Files and directories to ignore in git
    ├── requirements.client.txt             # Client-specific dependencies
    ├── requirements.test.txt               # Test-specific dependencies
    ├── requirements.txt                    # Main application dependencies
    ├── main.py                             # Main application entry point for the project
    ├── client.py                           # Client-side code for interacting with the API
    ├── streamlit_app.py                    # Streamlit application for user interface
    ├── docker-compose.yml                  # Docker Compose configuration for multi-container setup
    ├── app 
    │   ├── main.py                         # Entry point for the FastAPI application
    │   ├── config.py                       # Application and environment configuration settings
    │   ├── connection.py                   # Database and other connection settings
    │   ├── exceptions.py                   # Custom exception classes for error handling
    │   ├── tasks.py                        # Asynchronous task definitions using Celery
    │   │
    │   ├── dependencies                    # Dependency management for route handlers
    │   │   └── auth.py                     # Authentication-related dependencies
    │   │
    │   ├── middlewares                     # Middleware components for request/response processing
    │   │   ├── exceptions.py               # Middleware for handling exceptions
    │   │   ├── logging.py                  # Middleware for logging requests and responses
    │   │   ├── mock_auth.py                # Mock authentication middleware
    │   │   └── not_found.py                # Middleware for handling 404 errors
    │   │      
    │   ├── models                          # Data models and schemas for requests/responses
    │   │   ├── schemas.py                  # Pydantic schemas for data validation
    │   │   └── structures.py               # Data structures for internal use
    │   │
    │   ├── routes                          # API route definitions
    │   │   ├── chat.py                     # Chat-related endpoints
    │   │   ├── document.py                 # Document management endpoints
    │   │   └── history.py                  # Chat history-related endpoints
    │   │
    │   ├── services                        # Business logic and service layers
    │   │   ├── document_service.py         # Functions for handling document uploads and processing
    │   │   ├── history_service.py          # Functions for managing chat history
    │   │   ├── qa_cache_service.py         # Caching of query-answer pairs
    │   │   ├── rag_service.py              # Retrieval-Augmented Generation logic
    │   │   ├── vector_service.py           # Functions for managing vector storage
    │   │   │
    │   │   └── embeddings                  # Module for managing embeddings
    │   │       └─ google_embeddings.py     # Google embeddings integration
    │   │
    │   └─ utils                            # Utility functions and helpers
    │       ├── file_utils.py               # File handling utilities
    │       ├── hash_utils.py               # Hashing utilities
    │       ├── logger.py                   # Logger configuration and utilities
    │       └── parse_utils.py              # Utilities for parsing data
    │
    ├── docker                              # Docker-related files
    │   ├── client.Dockerfile               # Dockerfile for the client
    │   ├── client.Dockerfile.dockerignore  # Ignore rules for the client Dockerfile
    │   ├── prod.Dockerfile                 # Dockerfile for production
    │   ├── prod.Dockerfile.dockerignore    # Ignore rules for the production Dockerfile
    │   ├── test.Dockerfile                 # Dockerfile for testing
    │   └── test.Dockerfile.dockerignore    # Ignore rules for the test Dockerfile
    │
    ├── shared                              # Shared volumes across the docker containers
    │   └─ data
    │
    └─ tests                                # Directory for unit and integration tests
            ├── mock                        # Mock data for testing
            │   ├── test_data.json          # JSON file for AI model test data
            │   ├── history                 # Mock history data
            │   └── pdf                     # Mock PDFs for testing
            │
            ├── test_api.py                 # Test suite for API endpoints
            ├── test_document_service.py    # Test suite for document service
            ├── test_file_utils.py          # Test suite for file utilities
            ├── test_hash_utils.py          # Test suite for hashing utilities
            ├── test_history_service.py     # Test suite for history service
            ├── test_model.py               # Test suite for models
            ├── test_parsing.py             # Test suite for parsing utilities
            ├── test_qa_cache_service.py    # Test suite for QA cache service
            ├── test_tasks.py               # Test suite for task definitions
            └── test_vector_service.py      # Test suite for vector service
```


# Features

### LLM Integration
- Chat with an uploaded PDF
- Utilization of langchain, ChromaDB and Gemini to build a context-aware RAG model.
- Contextualization of the user prompt to enhance response quality.

### Chat History
- Retrieve and delete chat history
- Mock user authentication to simulate different user interactions on the same document.

### Smart State Management
- Detection of uploading the same document.
- Using a file content based hashing algorithm to determine file UUID's.
- Sharing of stored files, utilizing NFS servers for cross-container data management
- Utilization of vector databases to store document metadata.

### Intelligent Extraction & Data Retrieval
- Usage of ChromaDB vector database to store documents for a faster access.
- Splitting the documents into chunks for more efficient data retrieval.
- Usage of collections to seperate different documents / document groups, preventing other uploaded document information from interfering during a specific chat session.

### Robust Configuration Management
- Single point to seamlessly manage application configuration through `config.py`
- Utilization of pydantic models to efficiently manage configuration.
- Read only variables to prevent accidental data manipulations.
- Smart determination of loaded configuration using environment variables.

### Logging
Log files can be accessed on `data/logs` for development environment and `shared/data/logs` for production environment 
- Centralized asynchronous logging facility.
- Deterministic retention policies (by file size and modification time)
- Efficient use of storage by zipping inactive logfiles.

### Performance
- Utilization of Redis and Celery to efficiently handle long-running tasks.
- Caching of frequent LLM responses.

### Scalability
- Usage of Docker to enable the app to easily scale on demand
- Centralized data storage

### Security
- Implementation of rate limiter mechanism.
- Setting up safe CORS configurations.

### Testing
- Robust unit and integration tests to ensure application consistency.
- Utilization of deepeval to evaluate the LLM model performance.

### Error Handling
- Centralized error handling through middlewares to meticulously handle and log unexpected errors

### Client Application
- Allows easy and intuitive interaction with the application.

> Disclaimer: The client app is not designed to be efficient and it may be prone to bugs and issues, proceed with caution.