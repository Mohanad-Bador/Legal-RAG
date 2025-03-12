from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import chromadb
import torch
from src.rag.retrieval import initialize_retrieval_pipeline
from src.rag.generation import generate_answer

class RAGService:
    def __init__(self):
        self.device_map = "auto"
        self.embedding_model_id = "intfloat/multilingual-e5-large"
        self.llm_model_id = "Qwen/Qwen2.5-3B-Instruct"
        self.persist_directory = "data/chromadb-law"
        self.collection_name = "labour-law"
        self.torch_dtype = torch.bfloat16

        # Load embedding model
        self.embed_model = SentenceTransformer(self.embedding_model_id)

        # Load LLM model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_id)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            self.llm_model_id,
            device_map=self.device_map,
            torch_dtype=self.torch_dtype,
        )

        # Initialize ChromaDB client and collection
        self.chroma_client = chromadb.PersistentClient(path=self.persist_directory)
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
        except chromadb.errors.InvalidCollectionException:
            self.collection = self.chroma_client.create_collection(name=self.collection_name)

        # Initialize retrieval pipeline
        self.retriever, self.vector_store = initialize_retrieval_pipeline(
            persist_directory=self.persist_directory,
            collection_name=self.collection_name,
            embedding_model_id=self.embedding_model_id,
            top_k=5
        )

    def generate_response(self, question: str):
        return generate_answer(question, self.embed_model, self.vector_store._collection, self.llm_model, self.tokenizer)

# Initialize once
rag_service = RAGService()

class DummyRAGService:
    def __init__(self):
        print("DummyRAGService initialized")

    def generate_response(self, question: str):
        print(f"Received question: {question}")
        return "This is a dummy response."

# Initialize once
dummy_rag_service = DummyRAGService()
