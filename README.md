# Legal-RAG

This project is a Retrieval-Augmented Generation (RAG) pipeline for legal inquiries. It uses various NLP models and tools to process and retrieve information from legal documents.

## Requirements

Make sure you have the following dependencies installed:

```plaintext
langchain==0.3.20
langchain_chroma==0.2.2
langchain_huggingface==0.1.2
sentence-transformers==3.4.1
transformers==4.48.3
chromadb==0.6.3
torch==2.5.1+cu124
streamlit==1.43.0
tokenizers==0.21.0
pydantic==2.10.6
langchain-community==0.3.19
nltk==3.9.1
rouge-score==0.1.2
bert-score==0.3.13
rouge==1.0.1
datasets==3.3.2
wikipedia==1.4.0
unstructured==0.16.23
stanza==1.10.1
openpyxl==3.1.5
pyarabic==0.6.15
pyngrok==7.2.3
pytest==8.3.4
```

## Running on Google Colab

Follow these steps to run the project on Google Colab:

1. **Clone the Repository**

   Open a new Colab notebook and run the following command to clone the repository:

   ```python
   !git clone https://<YOUR_GITHUB_TOKEN>@github.com/Mohanad-Bador/Legal-RAG.git
   ```

   Replace `<YOUR_GITHUB_TOKEN>` with your actual GitHub personal access token.

2. **Navigate to the Project Directory**

   Change the working directory to the project directory:

   ```python
   %cd Legal-RAG
   ```

3. **Add the Project Directory to the Python Path**

   Add the project directory to the Python path:

   ```python
   import sys
   sys.path.append('/content/Legal-RAG')
   ```

4. **Install Dependencies**

   Install the required dependencies:

   ```python
   !pip install -r requirements.txt
   ```

5. **Run FastAPI and Streamlit**

   Create a new cell and run the following commands to execute the script that runs both FastAPI and Streamlit:

   ```python
   import uvicorn
   from pyngrok import ngrok
   from threading import Thread

   # Authenticate ngrok with your authtoken
   ngrok.set_auth_token("YOUR_NGROK_AUTH_TOKEN")

   # Kill all existing ngrok tunnels
   ngrok.kill()

   # Run FastAPI and Streamlit
   !python src/app.py
   ```

6. **Access the Applications**

   After running the script, you will see the public URL for accessing the applications. Use the provided URL to access the Streamlit interface and interact with the FastAPI backend.

## Using the Application

### Streamlit Interface

- **Ask a Question**: Enter your legal question in the input field and get a response.
- **Register a User**: Register a new user by providing a username and email.
- **Get User Information**: Retrieve information about a registered user by entering the username.

### FastAPI Endpoints

- **Generate Response**: `POST /generate` - Generate a response for a given query.
- **Create User**: `POST /users` - Create a new user with a username and email.
- **Get User Info**: `GET /users/{username}` - Retrieve information about a user.
- **Get Chat History**: `GET /history/{session_id}` - Retrieve chat history for a given session.

## Notes

- Ensure that the data files are in the correct paths as expected by the code.
- Modify the paths and parameters as needed to fit your specific use case.

This should help you get started with running your project on Google Colab. If you have any issues, please refer to the project's documentation or raise an issue on the repository.