from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import LocalFileStore
from langchain.storage._lc_store import create_kv_docstore
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from src.rag.preprocessing_pipline import clean_text,setup_nlp_tools,extract_article_lookup
import torch
import json
import ast
import chromadb

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
        setup_nlp_tools()
        processed_documents = self.process_dataset(documents)
        processed_documents =[Document(page_content=item['page_content'], metadata=item['metadata']) for item in processed_documents]
        
        self.documents = processed_documents

        self.doc_lookup = {
        (str(doc.metadata.get("article_number")),doc.metadata.get("law_short")): doc
        for doc in documents}

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
            collection_name="law_collection",
        )
        return vectorstore
    def process_dataset(self,documents):
      """
      Process the entire dataset by applying the clean_text function to each document.
      """
      processed_documents = []

      for document in documents:
          # Save the original text in metadata
          document.metadata['original_text'] = document.page_content

          # Apply the clean_text function to the page content
          cleaned_content = clean_text(document.page_content)

          # Create a new processed document
          processed_document = {
              'page_content': cleaned_content,
              'metadata': document.metadata
          }

          # Append the processed document to the new dataset
          processed_documents.append(processed_document)

      return processed_documents

    def load_vectorstore(self,persist_directory,embedding_model_name):
        """
        Load a persisted vector store from disk.
        """
        embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        persist_cilent = chromadb.PersistentClient(path=persist_directory)
        vectorstore = Chroma(
            client=persist_cilent,
            collection_name="law_collection",
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
    
    def rerank(self,query, documents, rank_diff_threshold=0.2):
        """
        Rerank a list of Document objects based on their relevance to the query.

        Args:
            query (str): The query string.
            documents (list[Document]): A list of Document objects to rerank.
            rank_diff_threshold (float): The threshold for rank difference to stop reranking.

        Returns:
            list[Document]: A list of reranked Document objects.
        """
        # Extract the text content from the Document objects
        document_texts = [doc.metadata["original_text"] for doc in documents]

        # Create (query, document) pairs using only the text content
        pairs = [[query, doc_text] for doc_text in document_texts]

        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
            scores = self.model(**inputs, return_dict=True).logits.view(-1).float()

        # Sort documents by raw score descending
        scored_docs = sorted(zip(documents, scores.tolist()), key=lambda x: x[1], reverse=True)

        # Normalize scores to 0-1
        raw_scores = [score for _, score in scored_docs]
        normalized_scores = self.normalize_scores(raw_scores)
        scored_docs = [(doc, norm_score) for (doc, _), norm_score in zip(scored_docs, normalized_scores)]

        # Apply filtering
        selected_docs = []
        for i in range(len(scored_docs)):
            doc, score = scored_docs[i]
            doc_with_linked_articles = self.get_linked_articles(doc)
            selected_docs.append(doc_with_linked_articles) 

            # Stop if rank difference is large
            if i < len(scored_docs) - 1:
                if score - scored_docs[i + 1][1] > rank_diff_threshold:
                    break

        return selected_docs
    
    def get_linked_articles(self,document):
        law = document.metadata.get("law_short")
        linked_articles = document.metadata.get("linked_articles")

        row = [document.metadata.get("original_text")] 
        if linked_articles:
            try:
                articles_list = ast.literal_eval(linked_articles)
                for article in articles_list:
                    article_str = str(article)
                    linked_key = (article_str,law)

                    linked_doc = self.doc_lookup.get(linked_key)
                    if linked_doc:
                        row.append(linked_doc.metadata.get("original_text"))
                    else:
                        print(f"Warning: Linked document not found for {linked_key}")

            except Exception as e:
                print(f"Error parsing linked_articles: {linked_articles}\n{e}")
        return row
     
    def retrieve_documents(self, query):
        """
        Retrieve documents using the ensemble retriever.

        Args:
            query: The query string to search for.
            k: The number of documents to retrieve.

        Returns:
            A list of retrieved documents.
        """
        result = []
        lookups = extract_article_lookup(query)
        if lookups is not None:
            for lookup in lookups:
                doc =self.doc_lookup.get(lookup)
                doc_with_linked_articles = self.get_linked_articles(doc)
                result.append(doc_with_linked_articles)
        else:
            processed_query = clean_text(query)
            results = self.ensemble_retriever.get_relevant_documents(processed_query)
            unique_documents ={doc.metadata['article_number']: doc for doc in results}.values()
            result = self.rerank(query, unique_documents)
        return result