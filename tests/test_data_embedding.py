import unittest
from data import embed_documents

class TestDataEmbedding(unittest.TestCase):

    def test_embed_documents(self):
        # Test embedding documents
        documents = ["This is a test document."]
        embeddings = embed_documents(documents, model_id='intfloat/multilingual-e5-large')
        self.assertEqual(len(embeddings), len(documents))

if __name__ == '__main__':
    unittest.main()