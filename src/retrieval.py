import chromadb
from langchain_chroma import Chroma

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

def add_documents_to_collection(collection, documents, embeddings, metadata, ids):
    """
    Adds documents, their embeddings, and metadata to the specified collection.

    Args:
    - collection: The ChromaDB collection to add documents to.
    - documents: A list of documents to add.
    - embeddings: A list of embeddings corresponding to the documents.
    - metadata: A list of metadata corresponding to the documents.
    - ids: A list of unique IDs for the documents.
    """
    collection.add(documents=documents, embeddings=embeddings, metadatas=metadata, ids=ids)