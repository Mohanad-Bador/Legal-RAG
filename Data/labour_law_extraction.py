import re
import csv

def add_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    book = ""
    chapter = ""
    section = ""
    i = 0

    with open(file_path, 'w', encoding='utf-8') as file:
        while i < len(lines):
            line = lines[i]
            if re.match(r'^الكتاب\s+\S+', line):
                book = f"{line.strip()}: {lines[i + 1].strip()}" if i + 1 < len(lines) else line.strip()
                file.write(f"# {book}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^الباب\s+\S+', line):
                chapter = f"{line.strip()}: {lines[i + 1].strip()}" if i + 1 < len(lines) else line.strip()
                file.write(f"## {chapter}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^الفصل\s+\S+', line):
                section = f"{line.strip()}: {lines[i + 1].strip()}" if i + 1 < len(lines) else line.strip()
                file.write(f"### {section}\n")
                i += 1  # Skip the next line as it is already processed
            elif re.match(r'^article\s+\d+:', line):
                # file.write(f"#### {book} - {chapter} - {section}\n")
                file.write(f"#### {line.strip()}\n")
            else:
                file.write(line)
            i += 1


def add_article_metadata(csv_file_path):
    articles = read_articles_from_csv(csv_file_path)
    updated_articles = []

    for article in articles:
        article_number = article['article_number']
        article_details = article['article_details']
        updated_article_details = []

        lines = article_details.split('\n')
        for i, line in enumerate(lines):
            if i == 0:
                updated_article_details.append(f"المادة {article_number} من قانون العمل المصري: {line}")
            else:
                updated_article_details.append(line)

        article['article_details'] = '\n'.join(updated_article_details)
        updated_articles.append(article)

    save_articles_to_csv(updated_articles, csv_file_path)


def read_articles(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    i = 0
    articles = []
    current_article = []
    in_article = False

    while i < len(lines):
        line = lines[i]
        if re.match(r'^#### article\s+\d+:', line):
            if current_article:
                articles.append("\n".join(current_article))
                current_article = []
            # current_article.append(line.strip())
            in_article = True
        elif in_article:
            if not re.match(r'^(#|##|###)', line):
                current_article.append(line.strip())
        i += 1

    if current_article:
        articles.append("\n".join(current_article))

    return articles


def read_articles_with_metadata(file_path):
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
            book = line.strip().lstrip('#').strip()
            chapter = ""
            section = ""
        elif re.match(r'^## الباب\s+\S+', line):
            chapter = line.strip().lstrip('#').strip()
            section = ""
        elif re.match(r'^### الفصل\s+\S+', line):
            section = line.strip().lstrip('#').strip()
        elif re.match(r'^#### article\s+\d+:', line):
            if current_article:
                articles.append({
                    "article_number": article_number,
                    "article_details": "\n".join(current_article),
                    "book": book,
                    "chapter": chapter,
                    "section": section
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
            "book": book,
            "chapter": chapter,
            "section": section
        })

    return articles

def save_articles_to_csv(articles, csv_file_path):
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['article_number', 'article_details', 'book', 'chapter', 'section', 'linked_definitions', 'linked_articles']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for article in articles:
            writer.writerow(article)

def read_articles_from_csv(file_path):
    articles = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            articles.append(row)
    return articles

definitions = {
    "العامل": "كل شخص طبيعي يعمل لقاء أجر لدى صاحب عمل وتحت إدارته أو إشرافه",
    "صاحب العمل": "كل شخص طبيعي أو اعتباري يستخدم عاملا أو أكثر لقاء أجر.",
    "الأجر": """كل ما يحصل عليه العامل لقاء عمله ، ثابتا كان أو متغيرا ، نقدا أو عينا.
ويعتبر أجرا على الأخص ما يلى: ۱ - العمولة التي تدخل في إطار علاقة العمل.  
۲ - النسبة المئوية ، وهى ما قد يدفع للعامل مقابل ما يقوم بإنتاجه أو بيعه أو تحصيله طوال قيامة بالعمل المقرر له هذه النسبة 
۳ - العلاوات أيا كان سبب استحقاقها أو نوعها.  
٤ - المزايا العينية التي يلتزم بها صاحب العمل دون أن تستلزمها مقتضيات العمل.  
٥ - المنح : وهى ما يعطى للعامل علاوة على أجره وما يصرف له جزاء أمانته أو كفاءته متى كانت هذه المنح مقررة فى عقود العمل الفردية أو الجماعية أو في الأنظمة الأساسية للعمل ، وكذلك ما جرت العادة بمنحه متى توافرت لها صفات العمومية والدوام والثبات.  
٦ - البدل : وهو ما يعطى للعامل لقاء ظروف أو مخاطر معينة يتعرض لها في أداء عمله.  
۷ - نصيب العامل فى الأرباح.  
۸ - الوهبة التي يحصل عليها العامل إذا جرت العادة بدفعها وكانت لها قواعد تسمح بتحديدها ، وتعتبر فى حكم الوهبة النسبة المئوية التي يدفعها العملاء مقابل الخدمة فى المنشآت السياحية.  
     ويصدر قرار من الوزير المختص بالاتفاق مع المنظمة النقابية المعنية بكيفية توزيعها على العاملين وذلك بالتشاور مع الوزير المعنى.""",
    "العمل المؤقت": "العمل الذي يدخل بطبيعته فيما يزاوله صاحب العمل من نشاط وتقتضى طبيعة إنجازه مدة محددة.",
    "العمل العرضي": "العمل الذي لا يدخل بطبيعته فيما يزاوله صاحب العمل من نشاط ولا يستغرق إنجازه أكثر من ستة أشهر.",
    "العمل الموسمي": "العمل الذي يتم في مواسم دورية متعارف عليها.",
    "الليل": "الفترة ما بين غروب الشمس وشروقها.",
    "الوزير المختص": "الوزير المختص بالقوى العاملة.",
    "الوزارة المختصة": "الوزارة المختصة بشئون القوى العاملة.",
    "المنشأة": {
        "الكتاب الخامس": {
            "الباب الرابع": "كل مشروع أو مرفق يملكه أو يديره شخص من أشخاص القانون الخاص."
        },
        "default": "كل مشروع أو مرفق يملكه أو يديره شخص من أشخاص القانون العام أو الخاص."
    }
}

def find_definitions_in_articles(articles, definitions):
    """
    Search for references to definitions in each article, with specific definitions
    applied only to specific books and chapters. Falls back to default definitions
    when no book- or chapter-specific definitions are found.
    
    Parameters:
        articles (list): List of dictionaries containing article details.
        definitions (dict): Nested dictionary of terms and their definitions.
    
    Returns:
        list: List of articles with linked definitions added as metadata.
    """
    linked_articles = []
    
    for article in articles:
        article_text = article['article_details']
        article_book = article['book'].split(":")[0].strip()  # Extract main book title
        article_chapter = article['chapter'].split(":")[0].strip()  # Extract main chapter title
        linked_terms = {}
        
        for term, definition in definitions.items():
            if article['article_number'] == "1" or article['article_number'] == "202":
                continue
            # Check if the definition is specific to a book or chapter
            if isinstance(definition, dict):
                applied_definition = None  # Initialize variable for the matched definition
                
                # Check for book-specific definitions
                for book_key, book_value in definition.items():
                    if book_key == article_book:
                        if isinstance(book_value, dict):
                            # Check for chapter-specific definitions
                            for chapter_key, chapter_value in book_value.items():
                                if chapter_key == article_chapter:
                                    applied_definition = chapter_value
                        else:
                            # Apply book-wide definition except for specific chapters
                            if article_chapter != "الباب الرابع":
                                applied_definition = book_value
                
                # Fallback to default definition
                if applied_definition is None and "default" in definition:
                    applied_definition = definition["default"]
                
                # Check if the term is in the article text
                if applied_definition and re.search(rf'\b{re.escape(term)}\b', article_text):
                    linked_terms[term] = applied_definition
            else:
                # General definitions
                if re.search(rf'\b{re.escape(term)}\b', article_text):
                    linked_terms[term] = definition
        
        # Add linked terms as metadata
        article['linked_definitions'] = linked_terms
        linked_articles.append(article)
    
    return linked_articles




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

def link_article_references(articles):
    """
    Link articles with their references based on text.
    
    Parameters:
        articles (list): List of dictionaries containing article details.
    
    Returns:
        list: Updated articles with linked references.
    """
    for article in articles:
        article_text = article['article_details']
        references = extract_references(article_text, int(article['article_number']))
        article['linked_articles'] = references
    return articles


if __name__ == "__main__":

    add_article_metadata("labour_law_with_articles.csv")
    # articles = read_articles_with_metadata("labour_law.md")

    # # linked_articles = read_articles_from_csv("labour_law_linked.csv")
    # linked_articles = find_definitions_in_articles(articles, definitions)

    # referenced_articles = link_article_references(linked_articles)

    # save_articles_to_csv(referenced_articles, "labour_law.csv")
    # for article in articles_from_csv:
    #     print(article)
    #     print("\n" + "="*80 + "\n")
