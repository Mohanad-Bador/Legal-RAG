import os
import argparse
import json
import logging
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_correctness, context_recall, answer_relevancy
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Map metric names to functions
METRIC_MAP = {
    'faithfulness': faithfulness,
    'answer_correctness': answer_correctness,
    'context_recall': context_recall,
    'answer_relevancy': answer_relevancy
}

def evaluate_dataset(data_samples, model_name, metrics, output_file='score.csv'):
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found. Please set it in the .env file.")

    os.environ["OPENAI_MODEL"] = model_name
    dataset = Dataset.from_dict(data_samples)

    logging.info("Starting evaluation with model: %s", model_name)
    logging.info("Metrics to evaluate: %s", metrics)

    # Evaluate the dataset
    score = evaluate(dataset, metrics=metrics)

    # Assuming score contains loss or other relevant information
    logging.info("Evaluation completed. Score: %s", score)

    df = score.to_pandas()
    df.to_csv(output_file, index=False)
    logging.info("Results saved to %s", output_file)

    return df

def main():
    load_dotenv()  # Load environment variables from .env file

    parser = argparse.ArgumentParser(description="Evaluate a dataset using specified metrics.")
    parser.add_argument('--dataset', type=str, required=True, help='Path to the dataset JSON file.')
    parser.add_argument('--metrics', type=str, nargs='+', required=True, help='List of metrics to evaluate.')
    parser.add_argument('--model_name', type=str, default='gpt-3.5-turbo', help='Name of the model to use.')
    parser.add_argument('--output_file', type=str, default='score.csv', help='Output CSV file for scores.')

    args = parser.parse_args()

    # Load the dataset from the JSON file
    with open(args.dataset, 'r', encoding='utf-8') as f:
        data_samples = json.load(f)

    # Convert metric names to functions
    metrics = [METRIC_MAP[metric] for metric in args.metrics if metric in METRIC_MAP]

    # Evaluate the dataset
    df = evaluate_dataset(data_samples, args.model_name, metrics, args.output_file)
    print(f"Evaluation complete. Results saved to {args.output_file}")

if __name__ == "__main__":
    main()