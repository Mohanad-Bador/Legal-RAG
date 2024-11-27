import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import streamlit as st
from RAG_Pipeline import generate_response, load_resources


device = "cuda" if torch.cuda.is_available() else "cpu"

# Load all models and resources
embed_model, llm_model, tokenizer, collection = load_resources(
    device_map=device,
    embedding_model_id="intfloat/multilingual-e5-large",
    llm_model_id="silma-ai/SILMA-9B-Instruct-v1.0",
    persist_directory="chromadb-ar-docs6",
    collection_name="laww"
)

# Streamlit app UI
st.title("Legal Document Retrieval with RAG")

# Display an input field for the user to enter a question
st.write("### Enter your legal question below:")
user_question = st.text_input("Ask a question:")

# Display the response when the user submits a question
if user_question:
    st.write("### Response:")
    response = generate_response(
        question=user_question,  # Pass the user's input directly
        llm_model=llm_model,
        tokenizer=tokenizer,
        embed_model=embed_model,
        collection=collection,
        n_results=3
    )
    st.write(response)
