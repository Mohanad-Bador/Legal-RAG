import unittest
import json
from data import chunk_text, chunk_and_save_to_json, load_chunks_from_json

class TestDataChunking(unittest.TestCase):

    def test_chunk_text(self):
        # Test chunking text
        documents = ["This is a test document. " * 20]
        chunks = chunk_text(documents, chunk_size=50, chunk_overlap=10)
        self.assertGreater(len(chunks), 1)

    def test_chunk_and_save_to_json(self):
        # Test chunking and saving to JSON
        raw_data_csv = [{"article_details": "This is a test article."}]
        chunk_and_save_to_json(raw_data_csv, lambda x: x, output_file="test_chunks.json")
        with open("test_chunks.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        self.assertGreater(len(data), 0)

    def test_load_chunks_from_json(self):
        # Test loading chunks from JSON
        chunked_documents, chunked_metadata, chunked_ids = load_chunks_from_json("test_chunks.json")
        self.assertGreater(len(chunked_documents), 0)
        self.assertGreater(len(chunked_metadata), 0)
        self.assertGreater(len(chunked_ids), 0)

if __name__ == '__main__':
    unittest.main()