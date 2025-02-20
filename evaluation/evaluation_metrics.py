from rouge_score import rouge_scorer
from bert_score import score as bert_score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rouge import Rouge
from sentence_transformers import SentenceTransformer, util

# Initialize models and scorers
vectorizer = TfidfVectorizer()
rouge = Rouge()
bert_model = SentenceTransformer('all-MiniLM-L6-v2')  # Pre-trained Sentence-BERT model

def evaluate_rouge(predictions, references):
    """
    Evaluates the ROUGE scores for the given predictions and references.

    Args:
    - predictions (list of str): The generated responses.
    - references (list of str): The reference responses.

    Returns:
    - dict: A dictionary containing the ROUGE scores.
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = [scorer.score(pred, ref) for pred, ref in zip(predictions, references)]
    return scores

def evaluate_bert(predictions, references):
    """
    Evaluates the BERTScore for the given predictions and references.

    Args:
    - predictions (list of str): The generated responses.
    - references (list of str): The reference responses.

    Returns:
    - tuple: Precision, Recall, and F1 scores.
    """
    P, R, F1 = bert_score(predictions, references, lang="en", rescale_with_baseline=True)
    return P, R, F1

def compute_bleu(references, generated_texts):
    """
    Computes the BLEU score for the given references and generated texts.

    Args:
    - references (list of str): The reference responses.
    - generated_texts (list of str): The generated responses.

    Returns:
    - float: The average BLEU score.
    """
    bleu_scores = []
    for ref, gen in zip(references, generated_texts):
        ref_tokens = ref.split()
        gen_tokens = gen.split()
        bleu = sentence_bleu([ref_tokens], gen_tokens, smoothing_function=SmoothingFunction().method1)
        bleu_scores.append(bleu)
    return np.mean(bleu_scores)

def compute_cosine_similarity(retrieved_context, actual_context):
    """
    Computes cosine similarity between retrieved and actual contexts.

    Args:
    - retrieved_context (str): The retrieved context.
    - actual_context (str): The actual context.

    Returns:
    - float: The cosine similarity score.
    """
    tfidf_matrix = vectorizer.fit_transform([retrieved_context, actual_context])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

def compute_rouge_scores(retrieved_context, actual_context):
    """
    Computes ROUGE scores between retrieved and actual contexts.

    Args:
    - retrieved_context (str): The retrieved context.
    - actual_context (str): The actual context.

    Returns:
    - dict: A dictionary containing the ROUGE scores.
    """
    return rouge.get_scores(retrieved_context, actual_context, avg=True)

def compute_bleu_score(retrieved_context, actual_context):
    """
    Computes BLEU score between retrieved and actual contexts.

    Args:
    - retrieved_context (str): The retrieved context.
    - actual_context (str): The actual context.

    Returns:
    - float: The BLEU score.
    """
    return sentence_bleu([actual_context.split()], retrieved_context.split())

def compute_bert_similarity(retrieved_context, actual_context):
    """
    Computes BERT-based similarity between retrieved and actual contexts.

    Args:
    - retrieved_context (str): The retrieved context.
    - actual_context (str): The actual context.

    Returns:
    - float: The BERT-based similarity score.
    """
    actual_embedding = bert_model.encode(actual_context, convert_to_tensor=True)
    retrieved_embedding = bert_model.encode(retrieved_context, convert_to_tensor=True)
    return util.pytorch_cos_sim(retrieved_embedding, actual_embedding).item()

def compute_bert_precision_recall(generated_texts, references):
    """
    Computes BERT-based precision, recall, and F1 scores.

    Args:
    - generated_texts (list of str): The generated responses.
    - references (list of str): The reference responses.

    Returns:
    - tuple: Precision, Recall, and F1 scores.
    """
    P, R, F1 = bert_score(generated_texts, references, lang="en", rescale_with_baseline=True)
    return P.mean().item(), R.mean().item(), F1.mean().item()