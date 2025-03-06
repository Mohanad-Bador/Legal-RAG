# Legal-RAG

This project is a Retrieval-Augmented Generation (RAG) pipeline for legal documents. It uses various NLP models and tools to process and retrieve information from legal texts.

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
   !git clone https://github.com/your-username/Legal-RAG.git
   ```

2. **Navigate to the Project Directory**

   Change the working directory to the project directory:

   ```python
   %cd Legal-RAG
   ```

3. **Install Dependencies**

   Install the required dependencies:

   ```python
   !pip install -r requirements.txt
   ```

4. **Run the RAG Pipeline**

   Create a new cell and run the following command to execute the RAG pipeline:

   ```python
   !python src/RAG_Pipeline.py
   ```

5. **Ask More Questions**

   You can ask more questions without reloading the resources by modifying the `RAG_Pipeline.py` script or creating a new script that imports the necessary functions and reuses the loaded resources.

## Notes

- Ensure that the data files are in the correct paths as expected by the code.
- Modify the paths and parameters as needed to fit your specific use case.

This should help you get started with running your project on Google Colab. If you have any issues, please refer to the project's documentation or raise an issue on the repository.