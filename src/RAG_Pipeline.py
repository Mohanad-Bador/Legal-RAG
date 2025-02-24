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

from data import read_articles, clean_text, chunk_text, chunk_and_save_to_json, load_chunks_from_json, embed_documents
from src import initialize_retrieval_pipeline, add_documents_to_collection, generate_answer

@st.cache_resource
def load_resources(
    device_map,
    embedding_model_id="intfloat/multilingual-e5-large",
    llm_model_id="silma-ai/SILMA-9B-Instruct-v1.0",
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
    collection = chroma_client.get_collection(name=collection_name)

    return embed_model, llm_model, tokenizer, collection

if __name__ == "__main__":
    # Example usage
    device_map = "auto"
    embedding_model_id = "intfloat/multilingual-e5-large"
    llm_model_id = "silma-ai/SILMA-9B-Instruct-v1.0"
    persist_directory = "data/chromadb-law"
    collection_name = "labour-law"
    torch_dtype = torch.bfloat16

    # Load resources
    embed_model, llm_model, tokenizer, collection = load_resources(
        device_map=device_map,
        embedding_model_id=embedding_model_id,
        llm_model_id=llm_model_id,
        persist_directory=persist_directory,
        collection_name=collection_name,
        torch_dtype=torch_dtype,
    )

    # Read and preprocess articles
    articles = read_articles("data/labour_data/labour_law_with_articles.csv")

    # Chunk the articles and save to JSON
    chunk_and_save_to_json(articles, clean_text, output_file="data/labour_data/chunks_with_metadata.json")

    # Load chunks from JSON
    chunked_documents, chunked_metadata, chunked_ids = load_chunks_from_json("data/labour_data/chunks_with_metadata.json")

    # Embed the chunked articles
    embeddings = embed_documents(chunked_documents)

    # Initialize the retrieval pipeline
    retriever = initialize_retrieval_pipeline(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_model_id=embedding_model_id,
        top_k=5
    )

    # Add documents to the collection
    add_documents_to_collection(retriever.vector_store.collection, chunked_documents, embeddings, chunked_metadata)

    # Example question
    question = "What are the labor laws regarding overtime work?"

    # Generate response
    response = generate_answer(question, embed_model, retriever.vector_store.collection, llm_model, tokenizer)
    print(response)