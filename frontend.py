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
from lark.exceptions import UnexpectedInput

# ------------------------------------------------------------
# AST IMPORTS
# ------------------------------------------------------------
#
# Customize this import list so that it matches the AST classes
# you define in ast_nodes.py.
#
# Example AST node names are provided below.

from ast_nodes import (
    Program,
    Number,
    Boolean,
    Var,
    UnaryOp,
    BinOp,
    Declaration,
    Assignment,
    Show,
    Block,
    If,
    While,
)


# ============================================================
# 1. LOCATE grammar.lark
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
GRAMMAR_FILE = BASE_DIR / "grammar.lark"


# ============================================================
# 2. CREATE THE LARK PARSER
# ============================================================

def create_parser():
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
        str(GRAMMAR_FILE),
        parser="lalr",
        start="start",
    )


# Create one parser that can be reused.

parser = create_parser()


# ============================================================
# 3. AST TRANSFORMER
# ============================================================

class ToAST(Transformer):
    """
    Convert the Lark parse structure into TinyLang AST nodes.

    IMPORTANT:
    The method names in this class must correspond to rule
    names or aliases in YOUR grammar.lark.

    Example:

        NUMBER -> number

    can cause Lark to call:

        def number(...)

    Similarly:

        NAME -> var

    can cause Lark to call:

        def var(...)

    Therefore, grammar.lark and frontend.py must be designed
    together.
    """

    # --------------------------------------------------------
    # PROGRAM
    # --------------------------------------------------------

    def start(self, items):
        """
        Convert the start rule into a Program AST node.

        Example grammar:

            start: statement+

        The items list contains the transformed statements.
        """

        return Program(list(items))


    # ========================================================
    # LITERAL VALUES
    # ========================================================

    def number(self, items):
        """
        Convert a numeric token into a Number AST node.

        Example source:

            42
            3.14
        """

        value = float(items[0])

        return Number(value)


    def boolean(self, items):
        """
        Convert a Boolean token into a Boolean AST node.

        Example source:

            true
            false
        """

        text = str(items[0]).lower()

        value = (text == "true")

        return Boolean(value)


    # ========================================================
    # VARIABLES
    # ========================================================

    def var(self, items):
        """
        Convert an identifier into a Var AST node.

        Example:

            score

        becomes conceptually:

            Var("score")
        """

        name = str(items[0])

        return Var(name)


    # ========================================================
    # UNARY EXPRESSIONS
    # ========================================================

    def neg(self, items):
        """
        Unary numeric negation.

        Example:

            -5

        Conceptual AST:

            UnaryOp("-", Number(5))
        """

        operand = items[0]

        return UnaryOp("-", operand)


    def not_expr(self, items):
        """
        Boolean negation.

        Example:

            not ready

        Conceptual AST:

            UnaryOp("not", Var("ready"))
        """

        operand = items[0]

        return UnaryOp("not", operand)


    # ========================================================
    # BINARY-EXPRESSION HELPER
    # ========================================================

    def _fold_binary(self, items):
        """
        Convert a sequence such as:

            left operator right operator right ...

        into nested BinOp AST nodes.

        Example source:

            2 + 3 + 4

        Conceptually becomes:

            BinOp(
                "+",
                BinOp(
                    "+",
                    Number(2),
                    Number(3)
                ),
                Number(4)
            )

        This produces left-associative structure.
        """

        if len(items) == 1:
            return items[0]

        left = items[0]

        index = 1

        while index < len(items):

            operator = str(items[index])
            right = items[index + 1]

            left = BinOp(
                operator,
                left,
                right
            )

            index += 2

        return left


    # ========================================================
    # ARITHMETIC EXPRESSIONS
    # ========================================================

    def sum(self, items):
        """
        Handle addition and subtraction.

        Example grammar:

            ?sum: product (ADDOP product)*

        Example:

            x + 5 - 2
        """

        return self._fold_binary(items)


    def product(self, items):
        """
        Handle multiplication, division, and remainder.

        Example grammar:

            ?product: unary (MULOP unary)*

        Example:

            x * 5 / 2
        """

        return self._fold_binary(items)


    # ========================================================
    # COMPARISON EXPRESSIONS
    # ========================================================

    def comparison(self, items):
        """
        Handle comparison operators.

        Example grammar:

            ?comparison: sum (COMPOP sum)?

        Examples:

            score > 60

            x == y

            count <= 10
        """

        if len(items) == 1:
            return items[0]

        left = items[0]
        operator = str(items[1])
        right = items[2]

        return BinOp(
            operator,
            left,
            right
        )


    # ========================================================
    # BOOLEAN EXPRESSIONS
    # ========================================================

    def and_expr(self, items):
        """
        Handle Boolean AND expressions.

        Example:

            ready and active
        """

        if len(items) == 1:
            return items[0]

        left = items[0]

        for right in items[1:]:

            left = BinOp(
                "and",
                left,
                right
            )

        return left


    def or_expr(self, items):
        """
        Handle Boolean OR expressions.

        Example:

            ready or active
        """

        if len(items) == 1:
            return items[0]

        left = items[0]

        for right in items[1:]:

            left = BinOp(
                "or",
                left,
                right
            )

        return left


    # ========================================================
    # VARIABLE DECLARATION
    # ========================================================

    def declaration(self, items):
        """
        Convert a declaration into a Declaration AST node.

        Example source:

            let score = 80;

        Conceptual AST:

            Declaration(
                "score",
                Number(80)
            )
        """

        name = str(items[0])
        expression = items[1]

        return Declaration(
            name,
            expression
        )


    # ========================================================
    # ASSIGNMENT
    # ========================================================

    def assignment(self, items):
        """
        Convert an assignment into an Assignment AST node.

        Example:

            score = score + 5;
        """

        name = str(items[0])
        expression = items[1]

        return Assignment(
            name,
            expression
        )


    # ========================================================
    # OUTPUT / SHOW STATEMENT
    # ========================================================

    def show_stmt(self, items):
        """
        Convert the TinyLang output statement.

        Instructor example:

            show score;

        Conceptual AST:

            Show(
                Var("score")
            )

        STUDENTS:
        Your language does not have to use the keyword "show".
        Use the output syntax defined for YOUR TinyLang.
        """

        expression = items[0]

        return Show(expression)


    # ========================================================
    # BLOCK
    # ========================================================

    def block(self, items):
        """
        Convert a sequence of statements surrounded by
        block delimiters into a Block AST node.

        Instructor example:

            {
                show x;
                x = x + 1;
            }

        Conceptual AST:

            Block([
                Show(...),
                Assignment(...)
            ])
        """

        return Block(list(items))


    # ========================================================
    # IF STATEMENT
    # ========================================================

    def if_stmt(self, items):
        """
        Convert an if/else statement into an If AST node.

        Instructor example:

            if (score >= 60) {
                show score;
            }
            else {
                show 0;
            }

        Expected transformed items:

            condition
            then_block
            optional else_block
        """

        condition = items[0]
        then_block = items[1]

        else_block = None

        if len(items) > 2:
            else_block = items[2]

        return If(
            condition,
            then_block,
            else_block
        )


    # ========================================================
    # WHILE STATEMENT
    # ========================================================

    def while_stmt(self, items):
        """
        Convert a while statement into a While AST node.

        Instructor example:

            while (score < 100) {
                score = score + 1;
            }
        """

        condition = items[0]
        body = items[1]

        return While(
            condition,
            body
        )


# ============================================================
# 4. CREATE TRANSFORMER
# ============================================================

transformer = ToAST()


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


# ============================================================
# 9. DEMONSTRATION / DEVELOPMENT DRIVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("TinyLang Frontend Test")
    print("=" * 60)

    # --------------------------------------------------------
    # STUDENTS:
    #
    # Replace these instructor examples with programs written
    # using YOUR TinyLang syntax.
    # --------------------------------------------------------

    sample_program = """
    let score = 80;
    let bonus = 5;

    show score + bonus * 2;

    if (score >= 60) {
        show 1;
    }
    else {
        show 0;
    }
    """

    print("\nSOURCE PROGRAM")
    print("-" * 60)
    print(sample_program)


    # --------------------------------------------------------
    # PARSE TREE
    # --------------------------------------------------------

    try:

        tree = parse_tree(sample_program)

        print("\nPARSE TREE")
        print("-" * 60)

        print(tree.pretty())


        # ----------------------------------------------------
        # AST
        # ----------------------------------------------------

        ast = transformer.transform(tree)

        print("\nAST")
        print("-" * 60)

        print(ast)


    except UnexpectedInput as error:

        print("\nSYNTAX ERROR")
        print("-" * 60)

        print(error)