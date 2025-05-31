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
            if re.match(r'^الباب\s+\S+', line):
                book = f"{line}: {lines[i + 1].strip()}" if i + 1 < len(lines) and not lines[i + 1].strip().startswith('##') else line
                file.write(f"# {book}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^الفصل\s+\S+', line):
                chapter = f"{line}: {lines[i + 1].strip()}" if i + 1 < len(lines) and not lines[i + 1].strip().startswith('###') else line
                file.write(f"## {chapter}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^الفرع\s+\S+', line):
                section = f"{line}: {lines[i + 1].strip()}" if i + 1 < len(lines) and not lines[i + 1].strip().startswith('####') else line
                file.write(f"### {section}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^المادة\s+\d+', line):
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

def remove_article_annotations(file_path):
    """
    Removes Arabic annotations like '(معدلة)' and '(مضافة)' from article titles
    and changes article numbers with 'مكررا' to decimal notation (e.g., 241 مكررا becomes 241.1).
    
    Args:
        file_path (str): Path to the markdown file
    """
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Pattern 1: Remove annotations like (معدلة) and (مضافة)
    pattern1 = r'(#### المادة \d+(?:\s+مكررا)?) \((?:معدلة|مضافة)\)'
    cleaned_text = re.sub(pattern1, r'\1', text)
    
    # Pattern 2: Change 'مكررا' to decimal notation
    pattern2 = r'#### المادة (\d+)\s+مكررا'
    
    # Replace with decimal notation
    cleaned_text = re.sub(pattern2, r'#### المادة \1.1', cleaned_text)
    
    # Write the cleaned content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_text)
    
    print(f"Article annotations removed and 'مكررا' articles renumbered in {file_path}")

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
        if re.match(r'^# الباب\s+\S+', line):
            # Remove the leading # and strip whitespace
            heading_text = line.strip().lstrip('#').strip()
            # Replace colon with space
            if ':' in heading_text:
                book = heading_text.replace(':', '')
            else:
                book = heading_text
            chapter = ""
            section = ""
        elif re.match(r'^## الفصل\s+\S+', line):
            # Remove the leading ## and strip whitespace
            heading_text = line.strip().lstrip('#').strip()
            # Replace colon with space
            if ':' in heading_text:
                chapter = heading_text.replace(':', '')
            else:
                chapter = heading_text
            section = ""
        elif re.match(r'^### الفرع\s+\S+', line):
            # Remove the leading ### and strip whitespace
            heading_text = line.strip().lstrip('#').strip()
            # Replace colon with space
            if ':' in heading_text:
                section = heading_text.replace(':', '')
            else:
                section = heading_text
        elif re.match(r'^#### المادة\s+\d+', line):
            if current_article:
                articles.append({
                    "article_number": article_number,
                    "article_details": "\n".join(current_article),
                    "law": "دستور جمهورية مصر العربية 2019",
                    "book": book,
                    "chapter": chapter,
                    "section": section,
                    "linked_definitions": {},
                    "linked_articles": []
                })
                current_article = []
            article_number = re.search(r'المادة\s+(\d+(?:\.\d+)?)', line).group(1)
            in_article = True
        elif in_article:
            current_article.append(line.strip())
        i += 1

    if current_article:
        articles.append({
            "article_number": article_number,
            "article_details": "\n".join(current_article),
            "law": "دستور جمهورية مصر العربية 2019",
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

    # First handle special format references by converting them to regular numbers (e.g., (121/ فقرة 1، 2))
    cleaned_text = re.sub(r'\((\d+)\/\s*فقرة\s*[^)]+\)', r'\1', article_text)

    # Match reference to "المادة السابقة"
    previous_article_reference = re.findall(r"المادة\s+السابقة", article_text)

    # Match comma-separated list format (e.g., فى المواد 103، 104، 105، ...)
    comma_separated_references = re.findall(r'المواد\s+([\d،\s]+(?:\d+))', cleaned_text)

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
    
    # Process comma-separated list format
    for ref_list in comma_separated_references:
        numbers = re.findall(r'\d+', ref_list)
        all_references.extend([int(num) for num in numbers if num.isdigit()])

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
        references = extract_references(article_text, float(article['article_number']))
        article['linked_articles'] = references
    
    with open(output_json_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(articles, outfile, ensure_ascii=False, indent=4)

def reformat_json_structure(input_json_path, output_json_path):
    """
    Reformats the JSON file to match the desired structure with page_content and metadata.
    
    Parameters:
        input_json_path (str): Path to the input JSON file.
        output_json_path (str): Path to save the reformatted JSON file.
    """
    with open(input_json_path, 'r', encoding='utf-8') as jsonfile:
        articles = json.load(jsonfile)
    
    reformatted_articles = []
    
    for article in articles:
        article_number = article.get("article_number", "")
        
        # Add the prefix to page_content
        original_content = article.get("article_details", "")
        prefixed_content = f"المادة {article_number} من الدستور المصري: {original_content}"
    
        reformatted_article = {
            "page_content": prefixed_content,
            "metadata": {
                "article_number": article_number,
                "law": article.get("law", ""),
                "book": article.get("book", ""),
                "chapter": article.get("chapter", ""),
                "section": article.get("section", ""),
                "linked_definitions": json.dumps(article.get("linked_definitions", {}), ensure_ascii=False),
                "linked_articles": json.dumps(article.get("linked_articles", []), ensure_ascii=False)
            }
        }
        reformatted_articles.append(reformatted_article)
    
    with open(output_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(reformatted_articles, outfile, ensure_ascii=False, indent=4)
    
    print(f"JSON file reformatted and saved to {output_json_path}")

if __name__ == "__main__":

    # First step: Add headers to the Markdown file
    add_headers("egyptian_constitution.md")

    # Second step: Remove empty lines from the Markdown file
    remove_empty_lines("egyptian_constitution.md")

    # Third step: Remove Arabic annotations from article titles
    remove_article_annotations("egyptian_constitution.md")

    # Fourth step: Read articles with metadata from the Markdown file and save to JSON
    articles = read_articles_with_metadata_and_save_to_json("egyptian_constitution.md", "egyptian_constitution.json")

    # Fifth step: Link articles with their references based on text from a JSON file
    link_article_references_from_json("egyptian_constitution.json", "egyptian_constitution.json")
    
    # Sixth step: Reformat the JSON structure
    reformat_json_structure("egyptian_constitution.json", "egyptian_constitution.json")