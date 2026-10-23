"""Student-owned tests: REPLACE the placeholder inputs/expectations with YOUR syntax."""
import sys
import unittest
from pathlib import Path

# add ../ to PATH (must happen before importing project modules)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import GRAMMAR_PATH, POSITIVES, NEGATIVES, SPLITTER
from frontend import create_parser
from ESLTranslator import ESLTransformer


def load_blocks(paths):
    """Read each file, split on SPLITTER, and drop empty/whitespace-only blocks."""
    blocks = []
    for path in paths:
        with open(path, "r") as source_file:
            source = source_file.read()
        blocks.extend(b for b in source.split(SPLITTER) if b.strip())
    return blocks


class TinyLangM3M5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = create_parser(GRAMMAR_PATH)
        cls.positive_blocks = load_blocks(POSITIVES)
        cls.negative_blocks = load_blocks(NEGATIVES)

    def test_customize_positive_examples(self):
        self.assertTrue(self.positive_blocks, "no positive examples found")
        for i, block in enumerate(self.positive_blocks):
            with self.subTest(block=i, preview=block.strip()[:40]):
                try:
                    self.parser.parse(block, start="start")
                except Exception as e:
                    self.fail(f"expected block to parse, but got: {e}")

    def test_customize_negative_examples(self):
        self.assertTrue(self.negative_blocks, "no negative examples found")
        for i, block in enumerate(self.negative_blocks):
            with self.subTest(block=i, preview=block.strip()[:100]):
                with self.assertRaises(Exception):
                    self.parser.parse(block, start="start")

    def test_customize_ast_structure(self):
        # Fresh transformer per block: Transformers can carry state.
        for i, block in enumerate(self.positive_blocks):
            with self.subTest(block=i, preview=block.strip()[:40]):
                tree = self.parser.parse(block, start="start")
                try:
                    ast = ESLTransformer().transform(tree)
                except Exception as e:
                    self.fail(f"AST generation failed: {e}")
                self.assertIsNotNone(ast)


if __name__ == "__main__":
    unittest.main()