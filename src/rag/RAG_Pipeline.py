from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from src.rag.hybrid_retrieval import HybridRetriever
from src.rag.generation import LegalGenerator

class DummyRAGService:
    def __init__(self):
        print("DummyRAGService initialized")
        # Initialize the hybrid retriever with default parameters
        self.retriever = HybridRetriever(
            documents="data/merged_data/documents.json",
            vectorstore_path="data/chromadb-law",
            docstore_path="data/docstore",
            embedding_model_name="intfloat/multilingual-e5-large",
            bm25_weight=0.5,
            pc_weight=0.5
        )
        # We're not loading the full LLM to keep this lightweight
        print("Hybrid retriever loaded successfully")

    def generate_response(self, question: str, k=5):
        """
        Provides a response using the hybrid retriever but with a dummy answer generator.
        
        Args:
            question: User question
            k: Number of documents to retrieve
            
        Returns:
            dict: Contains retrieved contexts from the hybrid retriever but dummy answer
        """
        print(f"Received question: {question}")
        
        # # Create dummy response with the same structure as RAGPipeline
        # contexts = [
        #     ["This is a dummy context #1 for testing purposes.", "This is another dummy context #1.", "This is yet another dummy context #1."],
        #     ["This is a dummy context #2 for testing purposes."],
        #     ["This is a dummy context #3 for testing purposes.", "This is another dummy context #3."],
        #     ["This is a dummy context #4 for testing purposes."],
        # ]
        
        # metadata = [
        #     {"source": "dummy_source_1", "title": "Dummy Document 1", "page": 1},
        #     {"source": "dummy_source_2", "title": "Dummy Document 2", "page": 2}
        # ]

        # Use the actual hybrid retriever to get relevant documents
        retrieved_docs = self.retriever.retrieve_documents(question)
        
        # Extract contexts and metadata from retrieved documents
        contexts = [doc.page_content for doc in retrieved_docs]
        metadata = [doc.metadata for doc in retrieved_docs]
        
        return {
            "answer": f"This is a dummy response to question: '{question}', but retrieved from actual documents.",
            "contexts": contexts,
            "metadata": metadata
        }

# Initialize once
# dummy_rag_service = DummyRAGService() # Uncomment this line to use the dummy service


class RAGPipeline:
    def __init__(self, 
                 documents="data/merged_data/documents.json",
                 embedding_model_name="intfloat/multilingual-e5-large",
                 llm_model_id="Qwen/Qwen2.5-3B-Instruct",
                 vectorstore_path="data/chromadb-law",
                 docstore_path="data/docstore",
                #  Update the path to finetuned model with your own path
                 finetuned_model_id="/gdrive/MyDrive/GP/llm-finetuning2/qwen-models/Qwen2.5-3B/",
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
        retrieved_docs = self.retriever.retrieve_documents(query)
        
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
rag_pipeline = RAGPipeline() # Comment this line to use the Dummy service