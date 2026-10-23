"""M3 template: adapt this to YOUR grammar, source and token categories."""

msg = "For the sake of development simplicity, inspect_tokens functionality has been integrated into frontend.demo_driver. It lists source, then tokens, then parse tree then AST."

from frontend import demo_driver, create_parser
from ESLTranslator import ESLTransformer
from config import NEGATIVES, POSITIVES, SPLITTER

print(msg)

demo_driver(create_parser(), ESLTransformer(), POSITIVES, NEGATIVES, SPLITTER)