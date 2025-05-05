from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
import chromadb
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import json

class HybridRetriever:
    def __init__(self, documents, vectorstore_path=None, docstore_path=None, embedding_model_name="intfloat/multilingual-e5-large", bm25_weight=0.5, pc_weight=0.5):
        # Check if documents is a file path string
        if isinstance(documents, str):
            try:
                with open(documents, 'r', encoding='utf-8') as f:
                    raw_documents = json.load(f)
                documents = [Document(page_content=item['page_content'], metadata=item['metadata']) for item in raw_documents]
            except (FileNotFoundError, json.JSONDecodeError) as e:
                raise ValueError(f"Error loading documents from file: {e}")
        else:
            # Assume documents is already a list of dictionaries with page_content and metadata
            documents = [Document(page_content=item['page_content'], metadata=item['metadata']) for item in documents]
        
        self.documents = documents

        if (vectorstore_path and not docstore_path) or (docstore_path and not vectorstore_path):
          raise ValueError("You must provide both 'vectorstore_path' and 'docstore_path', or neither.")

        if vectorstore_path:
            self.vectorstore = self.load_vectorstore(vectorstore_path,embedding_model_name)
        else:
            self.vectorstore = self.create_vectorstore(embedding_model_name)


        self.sparse = self.create_sparse_retriever(documents)

        self.dense = self.create_dense_retriever(self.vectorstore,docstore_path)
        self.ensemble_retriever = self.create_ensemble_retriever(self.dense, self.sparse, bm25_weight, pc_weight)
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-reranker-v2-m3")
        self.model = AutoModelForSequenceClassification.from_pretrained("BAAI/bge-reranker-v2-m3")
        self.model.eval()  # Set the model to evaluation mode

    def create_vectorstore(self,embedding_model_name):
        """
        Create a vector store using Chroma and HuggingFace embeddings.

        Args:
            documents: List of documents to be embedded.
            embedding_model_name: Name of the HuggingFace model to use for embeddings.

        Returns:
            A Chroma vector store instance.
        """
        persist_directory = "data/chromadb-law"  # Path to store the vector database
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        vectorstore = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_name="split_parents",
        )
        return vectorstore

    def load_vectorstore(self,persist_directory,embedding_model_name):
        """
        Load a persisted vector store from disk.
        """
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        persist_cilent = chromadb.PersistentClient(path=persist_directory)
        vectorstore = Chroma(
            client=persist_cilent,
            collection_name="split_parents",
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        return vectorstore

    def create_sparse_retriever(self, documents, k=5):
        """
        Create a sparse retriever using BM25 algorithm.

        Args:
            documents: The documents to use for retrieval.
            k: The number of documents to retrieve.

        Returns:
            A BM25Retriever instance.
        """
        bm25_retriever = BM25Retriever.from_documents(
            documents=documents, search_kwargs={"k": k}
        )
        return bm25_retriever

    def create_dense_retriever(self, vectorstore,docstore_path):
        """
        Create a dense retriever using the provided vector store.

        Args:
            vectorstore: The vector store to use for retrieval.

        Returns:
            A ParentDocumentRetriever instance.

        """
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

        if docstore_path is not None:
            fs = LocalFileStore(docstore_path)
            store = create_kv_docstore(fs)

            retriever = ParentDocumentRetriever(
              vectorstore=vectorstore,
              parent_splitter=parent_splitter,
              child_splitter=child_splitter,
              docstore=store
            )
        else:
            fs = LocalFileStore("docstore")
            store = create_kv_docstore(fs)

            retriever = ParentDocumentRetriever(
              vectorstore=vectorstore,
              parent_splitter=parent_splitter,
              child_splitter=child_splitter,
              docstore=store
          )
            retriever.add_documents(self.documents)

        return retriever

    def create_ensemble_retriever(self, dense_retriever, sparse_retriever, bm25_weight, pc_weight):
        """
        Create an ensemble retriever that combines both dense and sparse retrievers.

        Args:
            dense_retriever: The dense retriever to use.
            sparse_retriever: The sparse retriever to use.
            bm25_weight: Weight for the BM25 retriever.
            pc_weight: Weight for the dense retriever.

        Returns:
            An EnsembleRetriever instance.
        """
        ensemble = EnsembleRetriever(
            retrievers=[dense_retriever, sparse_retriever],
            weights=[bm25_weight, pc_weight],
        )
        return ensemble

    def normalize_scores(self,scores):
        min_score = min(scores)
        max_score = max(scores)
        normalized_scores = [(score - min_score) / (max_score - min_score) if max_score > min_score else 0 for score in scores]
        return normalized_scores
    
    def rerank(self,query, documents, rank_diff_threshold=0.2, top_n=None):
        # Create (query, document) pairs using only the text content
        pairs = [[query, doc] for doc in documents]

        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            scores = self.model(**inputs, return_dict=True).logits.view(-1).float()

        # Sort documents by score descending
        scored_docs = sorted(zip(documents, scores.tolist()), key=lambda x: x[1], reverse=True)

        # Normalize the scores between 0 and 1
        document_scores = [score for doc, score in scored_docs]
        normalized_scores = self.normalize_scores(document_scores)

        # Re-assign normalized scores back to the documents
        scored_docs = [(doc, normalized_score) for (doc, score), normalized_score in zip(scored_docs, normalized_scores)]

        # Compute rank differences
        rank_diffs = [scored_docs[i][1] - scored_docs[i+1][1] for i in range(len(scored_docs)-1)]

        # Dynamically adjust top_k based on rank differences
        if top_n is None:
            top_n = len(scored_docs)

        selected_docs = []
        for i in range(top_n):
            selected_docs.append(scored_docs[i])

            # Stop if rank difference between consecutive documents is greater than the threshold
            if i < len(rank_diffs) and rank_diffs[i] > rank_diff_threshold:
                break

        return selected_docs

    def retrieve_documents(self, query, k=5):
        """
        Retrieve documents using the ensemble retriever.

        Args:
            query: The query string to search for.
            k: The number of documents to retrieve.

        Returns:
            A list of retrieved documents.
        """
        results = self.ensemble_retriever.get_relevant_documents(query)
        page_contents = [doc.page_content for doc in results]
        unique_documents_page_contents = list(set(page_contents))
        reranked = self.rerank(query, unique_documents_page_contents)
        relevant_docs = [doc for doc, score in reranked]
        return relevant_docs[:k]