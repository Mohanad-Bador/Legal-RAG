import re
import nltk
import pyarabic.araby as araby
import stanza


def setup_nlp_tools():
    nltk.download('punkt')
    stanza.download('ar')  # Download Arabic models for Stanza

    # Initialize the Stanza pipeline during setup
    global _ar_nlp
    _ar_nlp = stanza.Pipeline('ar')


# Load Stanza model once and reuse
_ar_nlp = None
def get_ar_nlp():
    global _ar_nlp
    if _ar_nlp is None:
        raise RuntimeError("Stanza pipeline is not initialized. Call setup_nlp_tools() first.")
    return _ar_nlp

def normalizeArabic(text):
    text = text.strip()
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
    text = re.sub(r'(.)\1+', r"\1\1", text) # Remove longation
    return araby.strip_tashkeel(text)


def lemmatize_text(text):
    nlp = get_ar_nlp()
    doc = nlp(text)
    lemmas = [word.lemma for sentence in doc.sentences for word in sentence.words]
    return ' '.join(lemmas)

def clean_text(text):
    # Lemmatizing
    text = lemmatize_text(text)

    # Remove Tashkeel
    text = normalizeArabic(text)

    # remove extra whitespace
    text = re.sub('\s+', ' ', text)
    return text