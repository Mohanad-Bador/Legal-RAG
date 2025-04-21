# Synthetic Data QnA

This directory contains synthetic QnA data categorized by difficulty levels (Easy, Mid, etc.) and a cleaning pipeline to ensure the quality and validity of the data.

## Overview

The synthetic QnA data is organized into subdirectories based on difficulty levels:
- **Easy/**
- **Mid/**

Each directory contains raw and processed data files for QnA tasks.

## Cleaning Pipeline

The cleaning pipeline is designed to:
1. Validate the data.
2. Remove duplicate entries.
3. Fix issues in the data.

The pipeline ensures that the data is clean and ready for use in downstream tasks.

## Directory Structure

### Ready-to-Use Data
- The cleaned and validated data is stored under each difficulty directory with the naming convention:
  `valid_questions_{difficulty_level}.json`

### Cleaned Output
- The `cleaned_output/` directory contains:
  - Invalid entries that were removed during the cleaning process.
  - Unmentioned citations that do not have corresponding questions.
  - Logs generated during the cleaning process.
  - Visualizations of the data for better understanding and analysis.

## Additional Notes
- Ensure to run the cleaning pipeline before using the raw data for any tasks.
- The logs and visualizations in the `cleaned_output/` directory can help identify patterns or issues in the data.

Feel free to explore the data and use it for your QnA-related projects.