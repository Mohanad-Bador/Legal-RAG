import unittest
from data import read_articles, clean_text

class TestDataPreprocessing(unittest.TestCase):

    def test_read_articles(self):
        # Test reading articles from a CSV file
        articles = read_articles("path/to/test_csvfile.csv")
        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)

    def test_clean_text(self):
        # Test cleaning text
        raw_text = "المادة 1 من قانون العمل المصري: هذا نص المادة."
        cleaned_text = clean_text(raw_text)
        self.assertNotIn("المادة 1 من قانون العمل المصري:", cleaned_text)
        self.assertNotIn("  ", cleaned_text)

if __name__ == '__main__':
    unittest.main()