# Legal-RAG 🏛️⚖️

A state-of-the-art Retrieval-Augmented Generation (RAG) system specialized for **labor and educational law queries**, combining advanced language models with a hybrid retrieval system to provide accurate and contextually relevant answers to legal questions in these specific domains.

## 🌟 Features

- **🔍 Hybrid Retrieval**: Combines semantic search and keyword-based search for optimal document retrieval
- **🤖 Advanced Generation**: Leverages fine-tuned language models for coherent and accurate legal responses
- **⚖️ Specialized Legal Domains**: Focused on labor law and educational law queries for enhanced accuracy
- **👥 Multi-User System**: Complete user management with registration, authentication, and personalized chat history
- **💬 Interactive Chat Interface**: Clean Streamlit UI with conversation management
- **🔐 Secure Authentication**: JWT-based authentication system
- **📚 Comprehensive API**: RESTful endpoints for all system functionality
- **🗄️ Persistent Storage**: SQLite database with chat history and user management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Internet connection for model downloads

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mohanad-Bador/Legal-RAG.git
   cd Legal-RAG
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Streamlit UI: `http://localhost:8501`
   - FastAPI Docs: `http://localhost:8000/docs`

## 📁 Project Structure

```
Legal-RAG/
├── data/                    # Data storage
│   ├── chromadb-law/        # Vector database storage
│   └── docstore/            # Document storage
│   ├── labour_data/         # Labor law data and documents
│   └── education_law_data/  # Educational law data and documents
├── src/
│   ├── apis/                # FastAPI endpoints
│   │   ├── auth.py          # Authentication endpoints
│   │   └── chat.py          # Chat management endpoints
│   ├── database/            # Database models and schema
│   │   ├── models.py        # SQLAlchemy models
│   │   └── schema.py        # Pydantic schemas
│   ├── rag/                 # RAG components
│   │   ├── hybrid_retrieval.py  # Hybrid retrieval system
│   │   ├── generation.py    # Response generation
│   │   └── RAG_Pipeline.py  # Main RAG pipeline
│   └── ui/                  # Streamlit UI components
│       ├── streamlit.py     # Main UI application
│       ├── sidebar.py       # Sidebar components and navigation
│       └── api_helpers.py   # API communication helpers
├── app.py                   # Main application entry point
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## ☁️ Running on Google Colab

Perfect for testing and development without local setup:

### Step 1: Setup Environment

```python
# Clone the repository
!git clone https://YOUR_GITHUB_TOKEN@github.com/Mohanad-Bador/Legal-RAG.git
%cd Legal-RAG

# Add to Python path
import sys
sys.path.append('/content/Legal-RAG')

# Install dependencies
!pip install -r requirements.txt
```

### Step 2: Configure Model Path

```python
# Mount Google Drive for model access
from google.colab import drive
drive.mount('/content/drive')

# Update the model path in src/rag/RAG_pipeline.py
# Set finetuned_model_id to your model's path on Google Drive
```

### Step 3: Setup Public Access

```python
from pyngrok import ngrok

# Set your ngrok auth token (get from https://dashboard.ngrok.com)
ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")
ngrok.kill()  # Kill existing tunnels
```

### Step 4: Launch Application

```python
# Run the application
!python src/app.py
```

The application will provide public URLs for both the Streamlit interface and FastAPI documentation.

## 📖 Usage Guide

### 🔐 User Authentication

| Action | Description |
|--------|-------------|
| **Register** | Create a new account with username, email, and password |
| **Login** | Access your account with credentials |
| **Logout** | Securely end your session |

### 💬 Chat Interface

1. **🆕 Start New Chat**: Begin a fresh conversation
2. **❓ Ask Questions**: Submit labor or educational law queries for AI analysis
3. **📜 View History**: Browse previous conversations
4. **✏️ Rename Chats**: Organize with custom titles
5. **🗑️ Delete Chats**: Remove unwanted conversations

**Supported Legal Domains:**
- 🏭 **Labor Law**: Employment rights, workplace regulations, union laws, wage disputes
- 🎓 **Educational Law**: Student rights, institutional policies, educational compliance, academic regulations

### 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/auth/signup` | POST | User registration |
| `/auth/login` | POST | User authentication |
| `/chat/create` | POST | Create new chat |
| `/chat/list/{user_id}` | GET | Get user's chats |
| `/chat/generate` | POST | Generate AI response |
| `/chat/update` | PUT | Update chat details |
| `/chat/{chat_id}` | DELETE | Delete specific chat |

## 🏗️ System Architecture

### 🔍 Hybrid Retrieval System

Our advanced retrieval combines multiple approaches specifically trained on labor and educational law documents:

- **Dense Retrieval**: Semantic similarity using embedding models trained on legal texts
- **Sparse Retrieval**: Keyword matching with BM25 algorithm optimized for legal terminology
- **Cross-Encoder Reranking**: Final relevance scoring for optimal results in labor and educational law contexts


### 🗃️ Database Schema

| Table | Purpose |
|-------|---------|
| **users** | User accounts and authentication |
| **chats** | Conversation organization |
| **messages** | Individual message storage with context |

## 🛠️ Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Model Configuration

Update `src/rag/RAG_pipeline.py` to configure:
- Fine-tuned model path
- Embedding model selection
- Retrieval parameters
- Generation settings

## 🚨 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Import errors** | Ensure all dependencies are installed: `pip install -r requirements.txt` |
| **Model not found** | Check model path in configuration |
| **Port conflicts** | Change ports in `app.py` if 8000/8501 are in use |
| **Authentication issues** | Verify JWT secret key configuration |

### Performance Tips

- Use GPU acceleration when available
- Consider model quantization for faster inference
- Implement caching for frequently accessed documents
- Monitor memory usage with large document collections

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the user interface
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for robust API endpoints
- Uses [ChromaDB](https://www.trychroma.com/) for vector storage
- Implements [Sentence Transformers](https://www.sbert.net/) for embeddings
- Specialized for labor and educational law domains

---

⭐ **Star this repository if you find it helpful!** ⭐