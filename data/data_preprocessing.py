import csv

def read_articles(file_path):
    articles = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            articles.append(row)
    return articles

def clean_text(text):
    import re
    import pyarabic.araby as araby

    # Remove article header
    text = re.sub(r'^المادة \d+ من قانون العمل المصري:', '', text)

    # Remove extra whitespace
    text = re.sub('\s+', ' ', text)

    # Normalize Arabic text
    text = re.sub("[إأٱآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    noise = re.compile(""" ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    text = re.sub(noise, '', text)
    text = re.sub(r'(.)\1+', r"\1\1", text)  # Remove elongation
    return araby.strip_tashkeel(text)