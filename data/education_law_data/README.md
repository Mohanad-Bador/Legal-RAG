# Education Law Extraction Script

This Python script is designed to process education law documents, specifically the Egyptian Education Law No. 139 of 1981 (قانون التعليم رقم 139 لسنة 1981). It converts plain text or basic Markdown files into structured JSON format with proper hierarchical organization and cross-references between articles.

## Prerequisites

- Python 3.6 or higher
- Input file (`education_law.md`) with the raw text of the education law

## Installation

No special installation is required beyond having Python installed. The script uses only standard Python libraries (re, json).

## Usage

1. Place your `education_law.md` file in the same directory as the script.
2. Run the script:
   ```
   python education_law_extraction.py
   ```
3. The script will process the file and generate `education_law.json` with the structured output.

## Features

- **Hierarchical Structure**: Organizes the law into books, chapters, and sections
- **Article Extraction**: Properly identifies and separates individual articles
- **Metadata Enhancement**: Adds contextual metadata to each article
- **Cross-Reference Detection**: Automatically identifies references between articles
- **Empty Line Removal**: Cleans up the document by removing unnecessary whitespace

## Function Descriptions

The script includes several key functions:

### `add_headers(file_path)`
Adds hierarchical Markdown headers (# for book, ## for chapter, ### for section) to the input file.

### `remove_empty_lines(file_path)`
Removes all empty lines from the Markdown file to clean up the document.

### `read_articles_with_metadata_and_save_to_json(file_path, json_file_path)`
Reads the processed Markdown file, extracts articles with their metadata (book, chapter, section), and saves them to a JSON file.

### `extract_references(article_text, current_article_number)`
Analyzes article text to find references to other articles using various Arabic reference patterns.

### `link_article_references_from_json(json_file_path, output_json_file_path)`
Links articles with their references based on text analysis and saves the updated information.

### `extract_headers_from_markdown(file_path)`
Extracts the hierarchical structure (chapters and sections) from the Markdown file.

### `add_article_header(json_file_path)`
Enhances article details by adding context, such as specifying that it's from the Egyptian Education Law.

## Output Format

The output JSON file contains an array of article objects, each with the following structure:

```json
{
  "article_number": "123",
  "article_details": "المادة 123 من قانون التعليم المصري: [text of the article]",
  "law": "قانون التعليم رقم 139 لسنة 1981",
  "book": "[Book title]",
  "chapter": "[Chapter title]",
  "section": "[Section title]",
  "linked_definitions": {},
  "linked_articles": [124, 125]
}
```

## Example Workflow

1. Start with a raw text file of the education law
2. The script adds hierarchical headers
3. Empty lines are removed for cleaner processing
4. Articles are extracted with their metadata
5. Cross-references between articles are identified
6. Additional metadata is added for context
7. The final structured JSON is saved

## Notes

- The script is specifically designed for Arabic legal text in the format of the Egyptian Education Law
- It recognizes various Arabic reference patterns, such as "المادة 24", "المواد من (47) إلى (55)"
- Make sure your input file uses UTF-8 encoding to properly handle Arabic characters