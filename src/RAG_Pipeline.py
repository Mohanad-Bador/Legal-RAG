from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer
from langchain import PromptTemplate
from langchain_chroma import Chroma
from langchain.llms import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain import HuggingFacePipeline
import streamlit as st
import chromadb
import torch
import sys
import os

# Add the root directory of your project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data import read_articles, clean_text, chunk_and_save_to_json, load_chunks_from_json, embed_documents
from src import initialize_retrieval_pipeline, add_documents_to_collection, generate_answer

@st.cache_resource
def load_resources(
    device_map,
    embedding_model_id="intfloat/multilingual-e5-large",
    llm_model_id="Qwen/Qwen2.5-3B-Instruct",
    persist_directory="data/chromadb-law",
    collection_name="labour-law",
    torch_dtype=torch.bfloat16,
):
    """
    Load the necessary models and resources.
    """
    # Load embedding model
    embed_model = SentenceTransformer(embedding_model_id)

    # Load LLM model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(llm_model_id)
    llm_model = AutoModelForCausalLM.from_pretrained(
        llm_model_id,
        device_map=device_map,
        torch_dtype=torch_dtype,
    )

    # Initialize ChromaDB client and collection
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except chromadb.errors.InvalidCollectionException:
        collection = chroma_client.create_collection(name=collection_name)

    # Initialize the retrieval pipeline
    retriever, vector_store = initialize_retrieval_pipeline(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_model_id=embedding_model_id,
        top_k=5
    )

    return embed_model, llm_model, tokenizer, collection, retriever, vector_store

if __name__ == "__main__":
    # Example usage
    device_map = "auto"
    embedding_model_id = "intfloat/multilingual-e5-large"
    llm_model_id = "Qwen/Qwen2.5-3B-Instruct"
    persist_directory = "data/chromadb-law"
    collection_name = "labour-law"
    torch_dtype = torch.bfloat16

    # Load resources
    embed_model, llm_model, tokenizer, collection, retriever, vector_store = load_resources(
        device_map=device_map,
        embedding_model_id=embedding_model_id,
        llm_model_id=llm_model_id,
        persist_directory=persist_directory,
        collection_name=collection_name,
        torch_dtype=torch_dtype,
    )

    # Clear GPU memory
    torch.cuda.empty_cache()

    # # Read and preprocess articles
    # articles = read_articles("data/labour_data/labour_law_with_articles.csv")

    # # Chunk the articles and save to JSON
    # chunk_and_save_to_json(articles, clean_text, output_file="data/labour_data/chunks_with_metadata.json")

    # # Load chunks from JSON
    # chunked_documents, chunked_metadata, chunked_ids = load_chunks_from_json("data/labour_data/chunks_with_metadata.json")

    # # Embed the chunked articles
    # embeddings = embed_documents(chunked_documents)

    # # Add documents to the collection
    # add_documents_to_collection(vector_store._collection, chunked_documents, embeddings, chunked_metadata, chunked_ids)

    # Example question
    question = "س : ما هي اشتراطات المشرع المصري في بعض العقود المتصلة بقانون العمل ؟"

    # Generate response
    response = generate_answer(question, embed_model, vector_store._collection, llm_model, tokenizer)
    print(response)