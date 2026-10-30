"""Future milestone: semantic analysis and symbol table."""
from ast_nodes import *

class SemanticError(Exception):
    pass

"""
class ESLAnalyzer:
    def __init__(self):
        self.symbol_table = {}
    
    def check_expression(self, expr):
        if isinstance(expr, Literal):
            return

        if isinstance(expr, Identifier):
            if(expr.name) not in self.symbol_table:
                raise RuntimeError(f"Variable {expr.name} is not declared!") # semantic error
        
        if isinstance(expr, UnaryExpression):
            if expr.operator not in []:
                raise RuntimeError(f"Unsupported binary operator `{expr.operator}`")

        if isinstance(expr, BinaryExpression):
            if expr.operator not in ["+=", "-=", "*=", "/=", "%=", "=", "+=", "-=", "*=", "/=", "%="]:
                raise RuntimeError(f"Unsupported binary operator `{expr.operator}`")

        
from 
from frontend import parse
def run_semantic_tests():
    #cases = [(name, code, True) for name, code in POSITIVE.items] + \
    #[(name, code, False) for name, code in NEGATIVE.items]

    passed = 0
    
    print(" ---------- Entity Shading Language Semantic Analysis Validation Test ---------- ")

    for i, (name, code, expected) in enumerate(cases, 1):
        try:
            SemanticAnalyzer.analyse(parse(code))

            valid = True
        except SemanticError as e:
            valid = False
            reason = str(e)

        except Exception as e:
            print(f'Test {i} - {name}: Unexpected error: {e}')

        success = valid == expected

        passed += success
        print(f"{i}.{name}: {"VALID" if valid else "INVALID"} | {"PASS" if success else "FAIL"}")
    
        print("*" * 60)

        print("Result: {passed}/{len(cases)} tests passed.")

        return passed, len(cases)

        
if __name__ == "__main__":
    raise SystemExit(run_semantic_tests())
"""

