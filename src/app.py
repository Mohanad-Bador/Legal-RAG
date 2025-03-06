import streamlit as st
import torch
import sys
import os

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import load_resources, generate_answer

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load all models and resources
embed_model, llm_model, tokenizer, collection,retriever, vector_store = load_resources(
    device_map=device,
    embedding_model_id="intfloat/multilingual-e5-large",
    llm_model_id="Qwen/Qwen2.5-3B-Instruct",
    persist_directory="data/chromadb-law",
    collection_name="labour-law"
)

# Streamlit app UI
st.title("Legal Document Retrieval with RAG")

# Display an input field for the user to enter a question
st.write("### Enter your legal question below:")
user_question = st.text_input("Ask a question:")

# Display the response when the user submits a question
if user_question:
    st.write("### Response:")
    response = generate_answer(
        question=user_question,  # Pass the user's input directly
        embed_model=embed_model,
        collection=collection,
        llm_model=llm_model,
        tokenizer=tokenizer,
        n_results=3
    )
    st.write(response["answer"])