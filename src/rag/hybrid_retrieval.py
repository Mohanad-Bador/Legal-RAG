from langchain.retrievers import BM25Retriever ,EnsembleRetriever
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import json

class HybridRetriever:
    def __init__(self, documents = None,vectorstore = None ,embedding_model_name="intfloat/multilingual-e5-large", bm25_weight=0.5, pc_weight=0.5):
        if vectorstore:
            self.vectorstore = vectorstore
        else:
            if not documents:
                raise ValueError("Either documents or vectorstore must be provided.")
            self.documents = [Document(page_content=item['page_content'], metadata=item['metadata']) for item in documents]
            self.vectorstore = self.create_vectorstore(documents, embedding_model_name)

        self.sparse = self.create_sparse_retriever(documents)
        self.dense = self.create_dense_retriever(self.vectorstore)
        self.ensemble_retriever = self.create_ensemble_retriever(self.dense, self.sparse,bm25_weight, pc_weight)
    

    def create_vectorstore(self,embedding_model_name="intfloat/multilingual-e5-large"):
        """
        Create a vector store using Chroma and HuggingFace embeddings.
        
        Args:
            documents: List of documents to be embedded.
            embedding_model_name: Name of the HuggingFace model to use for embeddings.
            
        Returns:
            A Chroma vector store instance.
        """
        persist_directory="data/chromadb-law"  # Path to store the vector database
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_name="split_parents",
        )
        return vectorstore
    def load_vectorstore(persist_directory="data/chromadb-law"):
        """
        Load a persisted vector store from disk.
        """
        embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_name="split_parents",
        )
        return vectorstore

    def create_sparse_retriever(self,documents, k=5):
        """
        Create a sparse retriever using BM25 algorithm.
        
        Args:
            vectorstore: The vector store to use for retrieval.
            k: The number of documents to retrieve.
            
        Returns:
            A BM25Retriever instance.
        """
        bm25_retriever = BM25Retriever.from_documents(
            documents=documents, search_kwargs={"k": k}
        )
        return bm25_retriever

    def create_dense_retriever(self,vectorstore):
        """
        Create a dense retriever using the provided vector store.
        
        Args:
            vectorstore: The vector store to use for retrieval.
            k: The number of documents to retrieve.
            
        Returns:
            A Chroma vector store instance.
        """
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size = 2000)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size = 400)
        store = InMemoryStore()
        retriever = ParentDocumentRetriever(
            vectorstore=vectorstore,
            parent_splitter=parent_splitter,
            child_splitter=child_splitter,
            docstore=store
        )
        retriever.add_documents(self.documents)
        vectorstore.persist()
        return retriever

    def create_ensemble_retriever(self,dense_retriever, sparse_retriever, bm25_weight, pc_weight):
        """
        Create an ensemble retriever that combines both dense and sparse retrievers.
        
        Args:
            dense_retriever: The dense retriever to use.
            sparse_retriever: The sparse retriever to use.
            
        Returns:
            An EnsembleRetriever instance.
        """
        ensemble = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],
            weights=[bm25_weight, pc_weight],
        )
        return ensemble
    def create_reranker(self, retriever):
        """
        Create a reranker for the retriever.
        
        Args:
            retriever: The retriever to use.
            k: The number of documents to retrieve.
            
        Returns:
            A Reranker instance.
        """
        model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-v2-m3")
        compressor = CrossEncoderReranker(model=model, top_n=3)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )
        return compression_retriever

    def retrieve_documents(self,query, k=5):
        """
        Retrieve documents using the ensemble retriever.
        
        Args:
            query: The query string to search for.
            k: The number of documents to retrieve.
            
        Returns:
            A list of retrieved documents.
        """
        reranker = self.create_reranker(self.ensemble_retriever)
        results = reranker.get_relevant_documents(query)
        return results[:k]
    

if __name__ == "__main__":

    with open('law_json.json', 'r', encoding='utf-8') as f:
        documents = json.load(f)

    retriever = HybridRetriever(documents, embedding_model_name="intfloat/multilingual-e5-large", bm25_weight=0.5, pc_weight=0.5)

    query = "ما القيود المفروضة قانونياً على انتقاص حقوق العامل في اتفاقات العمل بغض النظر عن تاريخ الاتفاق"
    results = retriever.retrieve_documents(query, k=5)
    for result in results:
        print(result.page_content)
        print(result.metadata)

    


