import unittest
from src import initialize_retrieval_pipeline, add_documents_to_collection

class TestRetrievalPipeline(unittest.TestCase):

    def test_initialize_retrieval_pipeline(self):
        # Test initializing the retrieval pipeline
        retriever = initialize_retrieval_pipeline(persist_directory="path/to/persist_directory", collection_name="test_collection", embedding_model_id="intfloat/multilingual-e5-large")
        self.assertIsNotNone(retriever)

    def test_add_documents_to_collection(self):
        # Test adding documents to the collection
        retriever = initialize_retrieval_pipeline(persist_directory="path/to/persist_directory", collection_name="test_collection", embedding_model_id="intfloat/multilingual-e5-large")
        documents = ["This is a test document."]
        embeddings = [[0.1] * 768]  # Example embedding
        metadata = [{"article_number": 1}]
        add_documents_to_collection(retriever.vector_store.collection, documents, embeddings, metadata)
        self.assertGreater(len(retriever.vector_store.collection.get_all_documents()), 0)

if __name__ == '__main__':
    unittest.main()