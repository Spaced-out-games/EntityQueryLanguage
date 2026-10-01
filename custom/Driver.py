from lark import Lark, UnexpectedInput
from config import POSITIVES, NEGATIVES, SPLITTER
from pprint import pprint as pprint
global source # might not need to be global
global parser
# make sure it persists past scopes its assigned in
global tree


def demo_driver():
    # create the parser
    with open("grammar.lark", "r") as grammar_file:
        parser = Lark(grammar_file.read(), start="entry", maybe_placeholders=False)

    # generate the test blocks
    positive_blocks: list[tuple[str, bool]]
    negative_blocks: list[tuple[str, bool]]

    for path in POSITIVES:
        with open(path, "r") as source_file:
            source = source_file.read()
            blocks = source.split(SPLITTER)
            positive_blocks = [[block, True] for block in blocks]

    for path in NEGATIVES:
        with open(path, "r") as source_file:
            source = source_file.read()
            blocks = source.split(SPLITTER)
            negative_blocks = [[block, False] for block in blocks]

    # merge them
    all_blocks = positive_blocks + negative_blocks

    for block, expects_pass in all_blocks:
        print("======================== BLOCK ========================")
        print(block)
        print("======================== TREE ========================")

        try:
            tree = parser.parse(block)
            # it needs to pass, so it better pass
            print(tree.pretty())

            print("======================== STATUS ========================")
            print("PASSED!!!" if expects_pass else "FAILED!!!")
            print(f"expected: {expects_pass}; actual: True")

        except UnexpectedInput as e:
            print(None)
            print("======================== STATUS ========================")
            print("PASSED!!!" if not expects_pass else "FAILED!!!")
            print(f"expected: {expects_pass}; actual: False\n\nError:\n")
            print(e)






