"""Future milestones: parser frontend and parse-tree transformation."""

# TODO M5-M6: Implement parser/frontend integration.


"""
frontend.py
COMP 265 — TinyLang Project

Purpose
-------
This module implements the frontend connection between:

    TinyLang source code
            |
            v
       grammar.lark
            |
            v
        Lark Parser
            |
            v
       Parse Tree
            |
            v
      AST Transformer
            |
            v
           AST

IMPORTANT FOR STUDENTS
----------------------
This file is a STARTING FRAMEWORK.

You must customize the Transformer methods so that they agree with:

1. YOUR grammar.lark
2. YOUR TinyLang syntax
3. YOUR AST node definitions in ast_nodes.py
4. YOUR M0/M1/M2 language-design decisions

Do NOT simply copy the instructor's example grammar or AST design.
"""

from pathlib import Path

from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput, VisitError

# ------------------------------------------------------------
# AST IMPORTS
# ------------------------------------------------------------
#
# Customize this import list so that it matches the AST classes
# you define in ast_nodes.py.
#
# Example AST node names are provided below.

from ast_nodes import *
from config import POSITIVES, NEGATIVES, SPLITTER


# ============================================================
# 1. LOCATE grammar.lark
# ============================================================

from config import GRAMMAR_PATH


# ============================================================
# 2. CREATE THE LARK PARSER
# ============================================================

def create_parser(grammar_path: str):
    """
    Create and return the Lark parser used by TinyLang.

    The parser reads grammar.lark and uses the grammar to
    determine whether TinyLang source code is syntactically
    valid.

    Students:
        If your start rule has a different name, change
        start="start" below.
    """

    return Lark.open(
        grammar_path,
        #parser="lalr",
        parser="earley",
        start="start"
    )


# Create one parser that can be reused.

parser = create_parser(GRAMMAR_PATH)

from ESLTranslator import ESLTransformer

# ============================================================
# 4. CREATE TRANSFORMER
# ============================================================

transformer = ESLTransformer()


# ============================================================
# 5. PARSE SOURCE INTO A PARSE TREE
# ============================================================

def parse_tree(source):
    """
    Parse TinyLang source and return the Lark parse tree.

    This function is useful when studying or debugging the
    grammar.

    Example:

        tree = parse_tree("show 5;")

        print(tree.pretty())
    """

    return parser.parse(source)


# ============================================================
# 6. CONVERT SOURCE DIRECTLY TO AST
# ============================================================

def parse(source):
    """
    Parse TinyLang source and transform the resulting
    structure into an AST.

    Pipeline:

        source
          |
          v
        parser
          |
          v
      parse tree
          |
          v
      transformer
          |
          v
         AST
    """

    tree = parse_tree(source)

    ast = transformer.transform(tree)

    return ast


# ============================================================
# 7. SYNTAX VALIDATION
# ============================================================

def is_valid(source):
    """
    Return True if the source is syntactically valid
    according to grammar.lark.

    Return False otherwise.

    This is particularly useful for positive and negative
    grammar tests.
    """

    try:

        parser.parse(source)

        return True

    except UnexpectedInput:

        return False


# ============================================================
# 8. FRIENDLY PARSE ERROR REPORTING
# ============================================================

def check_syntax(source):
    """
    Attempt to parse the source and print a useful syntax
    result.

    Returns True for syntactically valid input.
    Returns False for syntactically invalid input.
    """

    try:

        parser.parse(source)

        print("Syntax OK")

        return True

    except UnexpectedInput as error:

        print("Syntax Error")
        print(error)

        return False

from utilities import pretty_ast

# ============================================================
# 9. DEMONSTRATION / DEVELOPMENT DRIVER
# ============================================================

def demo_driver(parser: None, AST_transformer: Transformer, positives: list[str], negatives: list[str], splitter: str):

    # generate the test blocks
    positive_blocks: list[tuple[str, bool]]
    negative_blocks: list[tuple[str, bool]]



    for path in positives:
        with open(path, "r") as source_file:
            source = source_file.read()
            blocks = source.split(splitter)
            positive_blocks = [[block, True] for block in blocks]

    for path in negatives:
        with open(path, "r") as source_file:
            source = source_file.read()
            blocks = source.split(splitter)
            negative_blocks = [[block, False] for block in blocks]

    # merge them
    all_blocks = positive_blocks + negative_blocks

    for block, expects_pass in all_blocks:
        print("\n\n\n\n\n\n\n\n\n")
        print("======================== CODE BLOCK ========================")
        print(block)

        print("======================== TOKENS ========================")

        for token in parser.lex(block):
            print(f"{token.type:<18} {token.value!r} line={token.line} col={token.column}")

        try:
            parse_tree = parser.parse(block)
            print("======================== PARSE TREE ========================")


            print(parse_tree.pretty())

            print("======================== AST ========================")

            tree = AST_transformer.transform(parse_tree)
            print(pretty_ast(tree))
            
            # it needs to pass, so it better pass
            print("======================== STATUS ========================")
            print("PASSED!!!" if expects_pass else "FAILED!!!")
            print(f"expected: {expects_pass}; actual: True")

        except UnexpectedInput as e:
            print(None)
            print("======================== STATUS ========================")
            print("PASSED!!!" if not expects_pass else "FAILED!!!")
            print(f"expected: {expects_pass}; actual: False\n\nError:\n")
            print(e)
        except VisitError as e:
            print(e)
        print("\n\n\n\n\n\n\n\n\n")
        

if __name__ == "__main__":
    demo_driver(parser, transformer, POSITIVES, NEGATIVES, SPLITTER)