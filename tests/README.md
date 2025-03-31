# Evaluate Script
Use evaluate.py for Generation and Retrieval evaluation using the following metrics:
- `faithfulness`
- `answer_correctness`
- `context_recall`
- `answer_relevancy`

This script evaluates a dataset using specified metrics and a chosen model.

## Arguments

- `--dataset` (required): Path to the dataset JSON file.
- `--metrics` (required): List of metrics to evaluate (e.g., `faithfulness`, `answer_correctness`, `context_recall`, `answer_relevancy`).
- `--model_name` (optional): Model name to use (default: `gpt-3.5-turbo`).
- `--output_file` (optional): Path to save the output CSV file (default: `score.csv`).

## Input

The input dataset should be a JSON file structured as:

```json
dict_keys(['question', 'answer', 'contexts', 'ground_truth'])
```

## Output

The script generates a CSV file containing evaluation results, saved to the specified ```--output_file path. ```

## Example command

```python evaluate.py --dataset ./data_samples_ragas.json --metrics answer_relevancy```

## Notes
Ensure the dataset file exists and is properly formatted.
Only metrics listed in the ```METRIC_MAP``` dictionary are supported.
Modify the ```.env``` file to include your OpenAI API key before running the script.