from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import chromadb
import torch
# from src.rag.retrieval import initialize_retrieval_pipeline
# from src.rag.generation import generate_answer
from src.rag.hybrid_retrieval import HybridRetriever
from src.rag.generation import LegalGenerator

class RAGService:
    def __init__(self):
        self.device_map = "auto"
        self.embedding_model_id = "intfloat/multilingual-e5-large"
        self.llm_model_id = "Qwen/Qwen2.5-3B-Instruct"
        self.persist_directory = "data/chromadb-law"
        self.collection_name = "split_parents"
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

# # Initialize once
# rag_service = RAGService()

class DummyRAGService:
    def __init__(self):
        print("DummyRAGService initialized")

    def generate_response(self, question: str, k=5):
        """
        Provides a dummy response matching the structure of RAGPipeline's output.
        
        Args:
            question: User question
            k: Number of documents to retrieve (not actually used but kept for API compatibility)
            
        Returns:
            dict: Contains dummy values for retrieved contexts and generated answer
        """
        print(f"Received question: {question}")
        
        # Create dummy response with the same structure as RAGPipeline
        dummy_contexts = [
            "This is a dummy context #1 for testing purposes.",
            "This is a dummy context #2 for testing purposes."
        ]
        
        dummy_metadata = [
            {"source": "dummy_source_1", "title": "Dummy Document 1", "page": 1},
            {"source": "dummy_source_2", "title": "Dummy Document 2", "page": 2}
        ]
        
        combined_context = "\n\n".join(dummy_contexts)
        
        return {
            "answer": f"This is a dummy response to question: '{question}'.",
            "contexts": dummy_contexts,
            "combined_context": combined_context,
            "metadata": dummy_metadata
        }

# Initialize once
dummy_rag_service = DummyRAGService()


class RAGPipeline:
    def __init__(self, 
                 documents="data/labour_data/law_with_articles.json",
                 embedding_model_name="intfloat/multilingual-e5-large",
                 llm_model_id="Qwen/Qwen2.5-3B-Instruct",
                 vectorstore_path="data/chromadb-law",
                 docstore_path="data/docstore",
                 finetuned_model_id="/gdrive/MyDrive/GP//llm-finetuning2/qwen-models/Qwen2.5-3B/",
                 bm25_weight=0.5,
                 pc_weight=0.5):
        """
        Initialize the RAG Pipeline with hybrid retrieval and legal generation components.
        
        Args:
            embedding_model_name: Model name for embeddings
            llm_model_id: Base model for generation
            vectorstore_path: Path to persist vectorstore
            docstore_path: Path to persist document store
            finetuned_model_id: Path to finetuned model (optional)
            bm25_weight: Weight for BM25 retriever
            pc_weight: Weight for dense retriever
        """
        self.documents = documents
        self.embedding_model_name = embedding_model_name
        self.llm_model_id = llm_model_id
        self.vectorstore_path = vectorstore_path
        self.docstore_path = docstore_path
        self.finetuned_model_id = finetuned_model_id
        self.bm25_weight = bm25_weight
        self.pc_weight = pc_weight
        
        # Will be initialized when documents are loaded
        self.retriever = HybridRetriever(
            documents=self.documents,
            vectorstore_path=self.vectorstore_path,
            docstore_path=self.docstore_path,
            embedding_model_name=self.embedding_model_name,
            bm25_weight=self.bm25_weight,
            pc_weight=self.pc_weight
        )
        
        # Initialize generator
        self.generator = LegalGenerator(
            base_model_id=self.llm_model_id,
            finetuned_model_id=self.finetuned_model_id if self.finetuned_model_id else self.llm_model_id
        )
    
    def generate_response(self, query, k=5):
        """
        Process a query through the RAG pipeline.
        
        Args:
            query: User question
            k: Number of documents to retrieve
            
        Returns:
            dict: Contains retrieved contexts and generated answer
        """
        if not self.retriever:
            raise ValueError("Retriever has not been initialized. Call initialize_retriever with documents first.")
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve_documents(query, k=k)
        
        # Extract context from retrieved documents
        contexts = [doc.page_content for doc in retrieved_docs]
        combined_context = "\n\n".join(contexts)
        
        # Generate response using the combined context
        answer = self.generator.generate_response(query, combined_context)
        
        # Return both the retrieved contexts and the generated answer
        return {
            "answer": answer,
            "contexts": contexts,
            "metadata": [doc.metadata for doc in retrieved_docs]
        }

# Initialize once
rag_pipeline = RAGPipeline()