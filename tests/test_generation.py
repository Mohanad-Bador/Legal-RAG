import unittest
from src import generate_answer
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer

class TestGenerationPipeline(unittest.TestCase):

    def test_generate_answer(self):
        # Test generating an answer
        tokenizer = AutoTokenizer.from_pretrained("silma-ai/SILMA-9B-Instruct-v1.0")
        llm_model = AutoModelForCausalLM.from_pretrained("silma-ai/SILMA-9B-Instruct-v1.0", device_map="auto", torch_dtype=torch.bfloat16)
        embed_model = SentenceTransformer('intfloat/multilingual-e5-large')
        collection = None  # Mock or initialize your collection here
        question = "What are the labor laws regarding overtime work?"
        response = generate_answer(question, embed_model, collection, llm_model, tokenizer)
        self.assertIn("answer", response)

if __name__ == '__main__':
    unittest.main()