import re
import json

# Function to add headers to the Markdown file
def add_headers(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    book = ""
    chapter = ""
    section = ""
    i = 0
    with open(file_path, 'w', encoding='utf-8') as file:
        while i < len(lines):
            line = lines[i].strip()
            if re.match(r'^الكتاب\s+\S+', line):
                book = f"{line}: {lines[i + 1].strip()}" if i + 1 < len(lines) and not lines[i + 1].strip().startswith('##') else line
                file.write(f"# {book}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^الباب\s+\S+', line):
                chapter = f"{line}: {lines[i + 1].strip()}" if i + 1 < len(lines) and not lines[i + 1].strip().startswith('###') else line
                file.write(f"## {chapter}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^الفصل\s+\S+', line):
                section = f"{line}: {lines[i + 1].strip()}" if i + 1 < len(lines) and not lines[i + 1].strip().startswith('####') else line
                file.write(f"### {section}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^مادة\s+\d+:', line):  # Changed to match without colon
                file.write(f"#### {line}\n")
            else:
                file.write(lines[i])
            i += 1

# Function to remove empty lines from the Markdown file
def remove_empty_lines(file_path):
    """
    Removes all empty lines from a Markdown file.
    
    Parameters:
        file_path (str): Path to the Markdown file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Filter out empty lines (lines that are just whitespace)
    non_empty_lines = [line for line in lines if line.strip()]
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(non_empty_lines)
    
    print(f"Empty lines removed from {file_path}")

# Function to read articles with metadata from the Markdown file and save to JSON
def read_articles_with_metadata_and_save_to_json(file_path, json_file_path):
    """
    Reads articles from a Markdown file, extracts metadata, and saves them to a JSON file.

    Parameters:
        file_path (str): Path to the Markdown file.
        json_file_path (str): Path to save the JSON file.

    Returns:
        None
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    book = ""
    chapter = ""
    section = ""
    i = 0
    articles = []
    current_article = []
    in_article = False
    article_number = ""

    while i < len(lines):
        line = lines[i]
        if re.match(r'^# الكتاب\s+\S+', line):
            book = line.strip().lstrip('#').strip().rstrip(':')
            chapter = ""
            section = ""
        elif re.match(r'^## الباب\s+\S+', line):
            chapter = line.strip().lstrip('#').strip().rstrip(':')
            section = ""
        elif re.match(r'^### الفصل\s+\S+', line):
            section = line.strip().lstrip('#').strip().rstrip(':')
        elif re.match(r'^#### مادة\s+\d+:', line):
            if current_article:
                articles.append({
                    "article_number": article_number,
                    "article_details": "\n".join(current_article),
                    "law": "قانون التعليم رقم 139 لسنة 1981",
                    "book": book,
                    "chapter": chapter,
                    "section": section,
                    "linked_definitions": {},
                    "linked_articles": []
                })
                current_article = []
            article_number = re.search(r'\d+', line).group()
            in_article = True
        elif in_article:
            current_article.append(line.strip())
        i += 1

    if current_article:
        articles.append({
            "article_number": article_number,
            "article_details": "\n".join(current_article),
            "law": "قانون التعليم رقم 139 لسنة 1981",
            "book": book,
            "chapter": chapter,
            "section": section,
            "linked_definitions": {},
            "linked_articles": []
        })

    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(articles, jsonfile, ensure_ascii=False, indent=4)

# Function to extract references from article text
def extract_references(article_text, current_article_number):
    """
    Extract references to other articles from the article text.
    
    Parameters:
        article_text (str): Text of the article.
    
    Returns:
        list: List of referenced article numbers.
    """
    # Match explicit ranges or lists (e.g., المواد (76 ، 77 ، 78 ، ...))
    multiple_references = re.findall(r"المواد\s*\(\s*([^()]+(?:\([^()]*\)[^()]*)*)\s*\)", article_text)
    
    # Match single references (e.g., المادة 24)
    single_references = re.findall(r"المادة\s*\(?\s*(\d+)\s*\)?", article_text)

    # Match single references with "للمادة" (e.g., طبقا للمادة (140))
    according_to_single_references = re.findall(r"للمادة\s*\(?\s*(\d+)\s*\)?", article_text)

    # Match paired references (e.g., المادتين (17), (18))
    paired_references = re.findall(r"المادتين\s*\(?\s*(\d+)\s*\)?\s*،\s*\(?\s*(\d+)\s*\)?", article_text)
    
    # Match ranges (e.g., المواد من (192) إلى (194))
    range_references = re.findall(r"المواد\s+من\s*\(?\s*(\d+)\s*\)?\s*إلى\s*\(?\s*(\d+)\s*\)?", article_text)
    
    # Match multiple ranges (e.g., المواد من (47) إلى (55) ومن (80) إلى (87))
    multiple_range_references = re.findall(r"المواد\s+من\s*\(?\s*(\d+)\s*\)?\s*إلى\s*\(?\s*(\d+)\s*\)?(?:\s+ومن\s*\(?\s*(\d+)\s*\)?\s*إلى\s*\(?\s*(\d+)\s*\)?)?", article_text)
    
    # Match ranges with hyphen (e.g., بالمواد من (196 - 200))
    hyphen_range_references = re.findall(r"بالمواد\s+من\s*\(?\s*(\d+)\s*-\s*(\d+)\s*\)?", article_text)
    
    # Match reference to "المادة السابقة"
    previous_article_reference = re.findall(r"المادة\s+السابقة", article_text)

    # Flatten and clean references
    all_references = []
    
    # Process multiple references
    for ref in multiple_references:
        # Remove any non-numeric text (e.g., (فقرة ثانية)) and split by commas
        cleaned_ref = re.sub(r'\([^)]*\)', '', ref)  # Remove all nested parentheses (like فقرة ثانية)
        # Split the remaining string by commas or spaces, ensuring only numeric references are included
        all_references.extend([int(num.strip()) for num in re.split(r'[،\s]+', cleaned_ref) if num.strip().isdigit()])
    
    # Process single references
    all_references.extend([int(num) for num in single_references if num.isdigit()])

    # Process according to single references
    all_references.extend([int(num) for num in according_to_single_references if num.isdigit()])

    # Process paired references
    for ref1, ref2 in paired_references:
        if ref1.isdigit() and ref2.isdigit():
            all_references.extend([int(ref1), int(ref2)])
    
    # Process range references
    for start, end in range_references:
        if start.isdigit() and end.isdigit():
            all_references.extend(range(int(start), int(end) + 1))
    
    # Process multiple range references
    for start1, end1, start2, end2 in multiple_range_references:
        if start1.isdigit() and end1.isdigit():
            all_references.extend(range(int(start1), int(end1) + 1))
        if start2 and end2 and start2.isdigit() and end2.isdigit():
            all_references.extend(range(int(start2), int(end2) + 1))
    
    # Process hyphen range references
    for start, end in hyphen_range_references:
        if start.isdigit() and end.isdigit():
            all_references.extend(range(int(start), int(end) + 1))
    
    # Process reference to "المادة السابقة"
    if previous_article_reference:
        previous_article_number = current_article_number - 1
        all_references.append(previous_article_number)

    # Remove duplicates and sort
    return sorted(set(all_references))

# Function to link articles with their references based on text from a JSON file
def link_article_references_from_json(json_file_path, output_json_file_path):
    """
    Link articles with their references based on text from a JSON file and save the updated articles to a new JSON file.
    
    Parameters:
        json_file_path (str): Path to the JSON file containing article details.
        output_json_file_path (str): Path to save the updated JSON file with linked references.
    """
    with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
        articles = json.load(jsonfile)
    
    for article in articles:
        article_text = article['article_details']
        references = extract_references(article_text, int(article['article_number']))
        article['linked_articles'] = references
    
    with open(output_json_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(articles, outfile, ensure_ascii=False, indent=4)

# Function to extract chapters and sections from the Markdown file
def extract_headers_from_markdown(file_path):
    """
    Extract chapters and sections from the Markdown file.
    
    Parameters:
        file_path (str): Path to the Markdown file.
    
    Returns:
        dict: Dictionary with chapters as keys and sections as lists.
    """
    chapters = {}
    current_chapter = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            chapter_match = re.match(r'^## (الباب .+)$', line.strip())
            section_match = re.match(r'^### (.+)$', line.strip())
            
            if chapter_match:
                current_chapter = chapter_match.group(1)
                if current_chapter not in chapters:
                    chapters[current_chapter] = []
            elif section_match and current_chapter:
                current_section = section_match.group(1)
                if current_section not in chapters[current_chapter]:
                    chapters[current_chapter].append(current_section)
    
    return chapters

# Function to add header to articles in a JSON file
def add_article_header(json_file_path):
    """
    Add metadata to articles in a JSON file.

    Parameters:
        json_file_path (str): Path to the JSON file containing articles.

    Returns:
        None
    """
    with open(json_file_path, 'r', encoding='utf-8') as jsonfile:
        articles = json.load(jsonfile)

    updated_articles = []

    for article in articles:
        article_number = article['article_number']
        article_details = article['article_details']
        updated_article_details = []

        lines = article_details.split('\n')
        for i, line in enumerate(lines):
            if i == 0:
                updated_article_details.append(f"المادة {article_number} من قانون التعليم المصري: {line}")
            else:
                updated_article_details.append(line)

        article['article_details'] = '\n'.join(updated_article_details)
        updated_articles.append(article)

    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(updated_articles, jsonfile, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    # First step: Add headers to the Markdown file
    add_headers("education_law.md")

    # Second step: Remove empty lines from the Markdown file
    remove_empty_lines("education_law.md")

    # Third step: Read articles with metadata from the Markdown file and save to JSON
    articles = read_articles_with_metadata_and_save_to_json("education_law.md", "education_law.json")

    # Fourth step: Link articles with their references based on text from a JSON file
    link_article_references_from_json("education_law.json", "education_law.json")
    
    # Fifth step: Add header to articles in a JSON file
    add_article_header("education_law.json")

    # # Check for chapters and sections in the Markdown file
    # chapters_sections = extract_headers_from_markdown("education_law.md")
    # for chapter, sections in chapters_sections.items():
    #     print(f"Chapter: {chapter}")
    #     for section in sections:
    #         print(f"  Section: {section}")
    #     print("\n" + "="*80 + "\n")