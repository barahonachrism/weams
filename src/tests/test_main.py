import unittest

class TestBronzeExtractor(unittest.TestCase):
    def test_initialization(self):
        """Basic sanity test to ensure standard python project structure works."""
        from extractors.bronze_extractor import extractor
        self.assertIsNotNone(extractor)

if __name__ == '__main__':
    unittest.main()
