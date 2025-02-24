import unittest
from src import (
    evaluate_rouge, evaluate_bert, compute_bleu,
    compute_cosine_similarity, compute_rouge_scores,
    compute_bleu_score, compute_bert_similarity, compute_bert_precision_recall
)

class TestEvaluationMetrics(unittest.TestCase):

    def test_evaluate_rouge(self):
        # Test evaluating ROUGE scores
        predictions = ["The quick brown fox jumps over the lazy dog."]
        references = ["The quick brown fox leaps over the lazy dog."]
        scores = evaluate_rouge(predictions, references)
        self.assertGreater(len(scores), 0)

    def test_evaluate_bert(self):
        # Test evaluating BERTScore
        predictions = ["The quick brown fox jumps over the lazy dog."]
        references = ["The quick brown fox leaps over the lazy dog."]
        P, R, F1 = evaluate_bert(predictions, references)
        self.assertGreater(len(P), 0)

    def test_compute_bleu(self):
        # Test computing BLEU score
        references = ["The quick brown fox leaps over the lazy dog."]
        generated_texts = ["The quick brown fox jumps over the lazy dog."]
        score = compute_bleu(references, generated_texts)
        self.assertGreater(score, 0)

    def test_compute_cosine_similarity(self):
        # Test computing cosine similarity
        retrieved_context = "The quick brown fox jumps over the lazy dog."
        actual_context = "The quick brown fox leaps over the lazy dog."
        score = compute_cosine_similarity(retrieved_context, actual_context)
        self.assertGreater(score, 0)

    def test_compute_rouge_scores(self):
        # Test computing ROUGE scores
        retrieved_context = "The quick brown fox jumps over the lazy dog."
        actual_context = "The quick brown fox leaps over the lazy dog."
        scores = compute_rouge_scores(retrieved_context, actual_context)
        self.assertGreater(len(scores), 0)

    def test_compute_bleu_score(self):
        # Test computing BLEU score
        retrieved_context = "The quick brown fox jumps over the lazy dog."
        actual_context = "The quick brown fox leaps over the lazy dog."
        score = compute_bleu_score(retrieved_context, actual_context)
        self.assertGreater(score, 0)

    def test_compute_bert_similarity(self):
        # Test computing BERT-based similarity
        retrieved_context = "The quick brown fox jumps over the lazy dog."
        actual_context = "The quick brown fox leaps over the lazy dog."
        score = compute_bert_similarity(retrieved_context, actual_context)
        self.assertGreater(score, 0)

    def test_compute_bert_precision_recall(self):
        # Test computing BERT-based precision, recall, and F1 scores
        generated_texts = ["The quick brown fox jumps over the lazy dog."]
        references = ["The quick brown fox leaps over the lazy dog."]
        P, R, F1 = compute_bert_precision_recall(generated_texts, references)
        self.assertGreater(P, 0)

if __name__ == '__main__':
    unittest.main()