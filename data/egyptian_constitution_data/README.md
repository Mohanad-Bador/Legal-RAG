# Egyptian Constitution Extraction Script

This Python script is designed to process and structure the Egyptian Constitution document (2019) from raw text into a well-organized JSON format with proper hierarchical organization and cross-references between articles.

## Overview

The script converts basic Markdown file of the Egyptian Constitution into a structured JSON format, organizing content by books, chapters, and sections while identifying and linking cross-references between articles.

## Features

- **Hierarchical Structure**: Organizes the constitution into books (باب), chapters (فصل), sections (فرع), and articles (مادة)
- **Article Extraction**: Properly identifies and separates individual articles
- **Metadata Enhancement**: Adds contextual metadata to each article
- **Cross-Reference Detection**: Automatically identifies references between articles using various Arabic reference patterns
- **Article Annotation Cleanup**: Removes annotations like (معدلة) and (مضافة) from article titles
- **Special Numbering Handling**: Converts "مكررا" notation to decimal notation (e.g., 241 مكررا → 241.1)
- **Empty Line Removal**: Cleans up the document by removing unnecessary whitespace
- **JSON Reformatting**: Structures output in a format suitable for vector databases and RAG systems

## Prerequisites

- Python 3.6 or higher
- Input file (`egyptian_constitution.md`) with the raw text of the Egyptian Constitution

## Usage

1. Place your `egyptian_constitution.md` file in the same directory as the script
2. Run the script:
   ```
   python egyptian_constitution_extraction.py
   ```
3. The script will process the file and generate `egyptian_constitution.json` with the structured output

## Processing Steps

The script processes the Egyptian Constitution in six sequential steps:

1. **Add Headers**: Adds hierarchical Markdown headers based on Arabic structural terms
2. **Remove Empty Lines**: Cleans up the document by removing whitespace
3. **Remove Article Annotations**: Cleans article titles and converts special numbering
4. **Extract Articles with Metadata**: Extracts articles and their contextual information
5. **Link Article References**: Identifies and links cross-references between articles
6. **Reformat JSON Structure**: Restructures the data for compatibility with vector databases

## Function Descriptions

### `add_headers(file_path)`
Adds hierarchical Markdown headers (# for book, ## for chapter, ### for section) to the input file.

### `remove_empty_lines(file_path)`
Removes all empty lines from the Markdown file to clean up the document.

### `remove_article_annotations(file_path)`
Removes Arabic annotations like (معدلة) and (مضافة) from article titles and converts "مكررا" notation to decimal form.

### `read_articles_with_metadata_and_save_to_json(file_path, json_file_path)`
Reads the processed Markdown file, extracts articles with their metadata (book, chapter, section), and saves them to a JSON file.

### `extract_references(article_text, current_article_number)`
Analyzes article text to find references to other articles using various Arabic reference patterns, including:
- Single references (المادة 24)
- Multiple references (المواد (76 ، 77 ، 78))
- Paired references (المادتين (17), (18))
- Range references (المواد من (192) إلى (194))
- Previous article references (المادة السابقة)

### `link_article_references_from_json(json_file_path, output_json_file_path)`
Links articles with their references based on text analysis and saves the updated information.

### `reformat_json_structure(input_json_path, output_json_path)`
Reformats the JSON file to match the desired structure with page_content and metadata fields for compatibility with vector databases and RAG systems.

## Output Format

The final JSON output includes an array of articles, each with:

```json
{
  "page_content": "المادة X من الدستور المصري: [article text]",
  "metadata": {
    "article_number": "X",
    "law": "دستور جمهورية مصر العربية 2019",
    "book": "[book title in Arabic]",
    "chapter": "[chapter title in Arabic]",
    "section": "[section title in Arabic]",
    "linked_definitions": "{}",
    "linked_articles": "[referenced article numbers]"
  }
}
```

## Notes

- The script is specifically designed for the Arabic text format of the Egyptian Constitution
- The reference extraction handles various Arabic reference patterns common in legal texts
- Unicode support (ensure_ascii=False) is used throughout to properly handle Arabic text