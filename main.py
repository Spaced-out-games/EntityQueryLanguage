from config import LANGUAGE_NAME, AUTHOR, VERSION, DESCRIPTION
from test_parser import demo_driver
from ASTTranslator import ESLTransformer


def show_project_identity() -> None:
    print(f"Welcome to {LANGUAGE_NAME} Version {VERSION}")
    print(DESCRIPTION)
    print(f"Designed by: {AUTHOR}")

global source
global parser

if __name__ == "__main__":
    show_project_identity()
    demo_driver(ESLTransformer)