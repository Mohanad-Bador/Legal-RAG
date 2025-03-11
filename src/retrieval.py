import chromadb
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from data import read_articles, chunk_and_save_to_json, load_chunks_from_json, embed_documents


def initialize_retrieval_pipeline(persist_directory, collection_name, embedding_model_id, top_k=5):
    chroma_client = chromadb.PersistentClient(path=persist_directory)
    
    # Check if the collection exists, if not, create it
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except chromadb.errors.CollectionNotFoundError:
        collection = chroma_client.create_collection(name=collection_name)
    
    vector_store = Chroma(client=chroma_client, collection_name=collection_name, embedding_function=embedding_model_id)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
    
    return retriever, vector_store

def process_and_add_documents(collection, articles_path, clean_text_func, chunk_output_file, embedding_model_id="intfloat/multilingual-e5-large"):
    """
    Process articles by chunking, embedding, and adding them to the collection.

    Args:
    - collection: The ChromaDB collection to add documents to.
    - articles_path: Path to the articles CSV file.
    - clean_text_func: Function to clean the text.
    - chunk_output_file: Path to save the chunked articles JSON file.
    - embed_model: The embedding model to use.
    """
    embed_model = SentenceTransformer(embedding_model_id)
    # Read and preprocess articles
    articles = read_articles(articles_path)

    # Chunk the articles and save to JSON
    chunk_and_save_to_json(articles, clean_text_func, output_file=chunk_output_file)

    # Load chunks from JSON
    chunked_documents, chunked_metadata, chunked_ids = load_chunks_from_json(chunk_output_file)

    # Embed the chunked articles
    embeddings = embed_documents(chunked_documents, embed_model)

    # Add documents to the collection
    collection.add(documents=chunked_documents, embeddings=embeddings, metadatas=chunked_metadata, ids=chunked_ids)

if __name__ == "__main__":
    # Example usage
    persist_directory = "data/chromadb-law"
    collection_name = "labour-law"
    embedding_model_id = "intfloat/multilingual-e5-large"
    top_k = 5
    articles_path = "data/labour_law_articles.csv"
    chunk_output_file = "data/chunked_articles.json"

    # Load resources
    retriever, vector_store = initialize_retrieval_pipeline(
        persist_directory=persist_directory,
        collection_name=collection_name,
        embedding_model_id=embedding_model_id,
        top_k=top_k
    )

    # Process and add documents to the collection
    process_and_add_documents(
        collection=vector_store.collection,
        articles_path=articles_path,
        clean_text_func=lambda x: x,
        chunk_output_file=chunk_output_file,
        embedding_model_id=embedding_model_id
    )