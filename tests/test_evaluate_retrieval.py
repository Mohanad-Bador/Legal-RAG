import os
import argparse
import json
import logging
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_recall, context_precision
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Map metric names to functions
METRIC_MAP = {
    'context_precision': context_precision,
    'context_recall': context_recall
}

from tqdm import tqdm

def evaluate_dataset(data_samples, model_name, metrics, output_file='score.csv', batch_size=10):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set it in the .env file.")
    
    os.environ["OPENAI_MODEL"] = model_name

    logging.info("Starting evaluation with model: %s", model_name)
    logging.info("Metrics to evaluate: %s", metrics)
    logging.info("Batch size: %d", batch_size)

    all_scores = []

    for i in tqdm(range(0, len(data_samples), batch_size), desc="Evaluating batches"):
        batch = data_samples[i:i + batch_size]
        try:
            dataset = Dataset.from_list(batch)
            score = evaluate(dataset, metrics=metrics)
            df_batch = score.to_pandas()
            all_scores.append(df_batch)
        except Exception as e:
            logging.warning("Batch %d-%d failed with error: %s", i, i+batch_size, str(e))
    
    if not all_scores:
        raise RuntimeError("All batches failed. No scores to save.")

    final_df = pd.concat(all_scores, ignore_index=True)

    final_df.to_csv(output_file, index=False, encoding='utf-8')
    logging.info("Results saved to %s", output_file)

    return final_df


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
    # data_sample = [data_samples[0] ] # Assuming the first sample is representative

    # Convert metric names to functions
    metrics = [METRIC_MAP[metric] for metric in args.metrics if metric in METRIC_MAP]

    # Evaluate the dataset
    df = evaluate_dataset(data_samples, args.model_name, metrics, args.output_file)
    print(f"Evaluation complete. Results saved to {args.output_file}")

if __name__ == "__main__":
    main()