# Legal-RAG

A Retrieval-Augmented Generation (RAG) system specialized for legal queries, combining advanced language models with a hybrid retrieval system to provide accurate and contextually relevant answers to legal questions.

## Overview

Legal-RAG is designed to help users get precise answers to legal inquiries by combining:

- **Hybrid Retrieval**: Uses both semantic search and keyword-based search to find the most relevant legal documents
- **Advanced Generation**: Leverages state-of-the-art language models to generate coherent and accurate responses
- **Multi-User System**: Supports user registration, authentication, and personalized chat history
- **Interactive UI**: Clean Streamlit interface for easy interaction with the system

## Project Structure

```
Legal-RAG/
├── data/                    # Data storage
│   ├── chromadb-law/        # Vector database storage
│   └── docstore/            # Document storage
├── src/
│   ├── apis/                # FastAPI endpoints
│   ├── database/            # Database models and schema
│   ├── rag/                 # RAG components
│   │   ├── hybrid_retrieval.py  # Hybrid retrieval system
│   │   ├── generation.py    # Generation 
│   │   └── RAG_Pipeline.py  # Main RAG pipeline
│   └── ui/                  # Streamlit UI components
└── app.py                   # Main application entry point
```

## Requirements

The project requires Python 3.8+ and the dependencies listed in `requirements.txt`.

## Running on Google Colab

Follow these steps to run the project on Google Colab:

1. **Create a New Colab Notebook**

   Go to [Google Colab](https://colab.research.google.com/) and create a new notebook.

2. **Clone the Repository**

   ```python
   !git clone https://<YOUR_GITHUB_TOKEN>@github.com/Mohanad-Bador/Legal-RAG.git
   ```

3. **Add Project to Python Path**

   ```python
   import sys
   sys.path.append('/content/Legal-RAG')
   ```

4. **Install Dependencies**

   ```python
   !pip install -r requirements.txt
   ```


5. **Set Up Ngrok for Public Access**

   ```python
   # Install pyngrok if not already installed
   !pip install pyngrok
   
   import uvicorn
   from pyngrok import ngrok
   from threading import Thread

   # Authenticate ngrok with your authtoken (get one from https://dashboard.ngrok.com)
   ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")
   
   # Kill any existing ngrok tunnels
   ngrok.kill()
   ```

6. **Run the Application**

   ```python
   # Run the FastAPI and Streamlit application
   !python src/app.py
   ```

7. **Access the Application**

   After running the application, you'll see URLs in the output. Use these URLs to access:
   - Streamlit UI: For the user interface
   - FastAPI Docs: For API documentation at `/docs` endpoint

## Using the Application

### User Authentication

1. **Register**: Create a new account with username, email, and password
2. **Login**: Access your account with your credentials
3. **Logout**: End your session securely

### Chat Interface

1. **Start a New Chat**: Begin a new conversation with the legal assistant
2. **Ask Questions**: Type legal queries and get AI-generated responses
3. **View History**: Access your previous conversations
4. **Rename Chats**: Organize your chats with custom titles
5. **Delete Chats**: Remove unwanted conversations

### API Endpoints

The system exposes several RESTful API endpoints:

- **Authentication**: `/auth/login`, `/auth/signup`
- **Chat Management**: `/chat/create`, `/chat/list/{user_id}`, `/chat/update`, `/chat/{chat_id}`
- **Question Answering**: `/chat/generate`

## Advanced Features

### Hybrid Retrieval System

The system uses a combination of:
- **Dense Retrieval**: Semantic search using embeddings
- **Sparse Retrieval**: Keyword-based search using BM25
- **Reranking**: Cross-encoder to rerank results for maximum relevance

### Database Schema

The application uses SQLite with the following tables:
- **Users**: Store user information and credentials
- **Chats**: Organize conversations by user
- **Messages**: Store individual messages with full response context


## License

This project is licensed under the MIT License - see the LICENSE file for details.