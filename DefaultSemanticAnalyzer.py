#========Two new libraries for Enhancing the Analyzer Capability==================
from dataclasses import dataclass, field # help in defining scope record with safe default
from pprint import pformat
#======================================
from ast_nodes import (Number, Boolean, Var, UnaryOp, BinOp,
                        Let, Assign, Show, 
                        Block, If, While)




# Semantic analysis error
class SemanticError(Exception): 
    pass

# 
@dataclass
class Scope:
    name:str
    parent: 'Scope | None' = None
    symbols:dict = field(default_factory=dict)
    children: list = field(default_factory=list)

class SemanticAnalyzer:

    NUMERIC = {'integer', 'float'}

    def __init__(self):
        self.reset()

    def reset(self):
        self.global_scope = Scope('global')
        self.scopes= [self.global_scope]
        self.scope_history =[self.global_scope]
        self.next_scope_id = 0
        self.symbol_table = self.global_scope.symbols
        self.symbols= set()

    def enter_scope(self, kind ='block'):
        self.next_scope_id+=1
        parent = self.scopes[-1]
        child = Scope(f'{kind}_{self.next_scope_id}', parent=parent)
        parent.children.append(child)
        self.scope_history.append(child)
        return child

    def exit_scope(self):
        if len(self.scopes)==1:
            raise SemanticError('Cannot exit global')
        return self.scopes.pop()

    def lookup(self, name, reguire_initialized=True):
        for scope in reversed(self.scopes):
            if name in scope.symbols:
                entry = scope.symbols[name]
                if reguire_initialized and not entry['initialized']:
                    raise SemanticError(f'Variable used before initialization: {name}')
                return entry
            raise SemanticError (f'Undefined/undeclared variable: {name}')
    
    # register structured declaration
    def declare(self, name, inferred_type):
        current = self.scopes[-1]
        if name in current.symbols:
            raise SemanticError (f"'{name}' already declared in this scope '{current.name}")
        current.symbols[name] ={
                                 'type': inferred_type,
                                 'scope': current.name,
                                 'initialized':True,
                               }
        self.symbols = set(self.global_scope.symbols)

    #Expression Type Checking
    @staticmethod
    def _same_type(actual, expected, context):
        if actual !=expected:
            raise SemanticError(f'{context}:{expected}, but got {actual}')

    # NOTE: Just type checking in an expression
    #Refactoring of the check_expr() to align with semantic scoping, type checking and
    #variable shadowing
    def check_expr(self, node):
        if isinstance(node, Boolean):
            return  'boolean'

        if isinstance(node, Number):
            return  'integer' if float(node.value).is_integer() else 'float'
        

        if isinstance(node, Var):
            return  self.lookup(node.name)['type']
        
        if isinstance(node, UnaryOp):
            operand= self.check_expr(node.operand)
            if node.op =='-':
                if operand not in self.NUMERIC:
                    raise SemanticError(f"Unary '-' requires a number, but got {operand}")
                return operand
           
            if node.op == 'not':
                self._same_type(operand, 'boolean', "'not' operand")
                return 'boolean'

            raise SemanticError(f'unsupported unary operator: {node.op}')


        if isinstance(node, BinOp):
            left =  self.check_expr(node.left)
            right = self.check_expr(node.right)
            op = node.op
            if op in {'and', 'or'}:
                if left != 'boolean' or right != 'boolean':
                    raise SemanticError(f"'{op}' requires boolean operands, got {left} and {right}")
                return 'boolean'

            if op in {'+', '-', '*', '/', '%'}:
                if left not in self.NUMERIC or right not in self.NUMERIC:
                    raise SemanticError(f"'{op}' requires numeric operands, got {left} and {right}")
                if op =="%":
                    if left != 'integer' or right != 'integer':
                         raise SemanticError(f"'{op}' requires integer operands, got {left} and {right}")
                if op== "/":
                    return 'float'
                return 'float' if 'float' in {left, right} else 'integer'
            
            if op in { '<', '>', '<=', '>='}:
                if left not in self.NUMERIC or right not in self.NUMERIC:
                    raise SemanticError(f"'{op}' requires numeric operands, but got {left} and {right}")
                return 'boolean'
            
            if op in {'==', '!='}:
                if left == right or (left in  self.NUMERIC or right in self.NUMERIC):
                    return 'boolean'
                raise SemanticError(f"cannot compare {left} and {right} with {op}")
                
            
            if node.op not in ('+', '-', '*', '/', 'and', 'or', '<', '>', '<=', '>=', '==', '!='):
                raise SemanticError(f"Unsupported binary operator '{node.op}'.")
            self.check_expr(node.left); self.check_expr(node.right); return

        raise SemanticError(f"Unsupported expression type: {type(node).__name__}")

    #Validates each statement in the block and ensures that the scope is properly managed
    def check_block(self, block, kind="block"):
           self.enter_scope(kind)

           try:
               for stmt in block.statements:
                   self.check_stmt(stmt)
           finally:
               self.exit_scope()

       
   # 
    def check_stmt(self, node):
        if isinstance(node, Let):
            if node.name in self.scopes[-1].symbols:
                raise SemanticError(f"Variable '{node.name}' is already declared in scope {self.scopes[-1].name}")
            inferred = self.check_expr(node.expr)
            self.declare(node.name, inferred)
            return
  
        if isinstance(node, Assign):
            target = self.lookup(node.name)
            if target != target['type']:
                raise SemanticError(f"Cannot assign {node.expr} to variable '{node.name}' of type {target['type']}")
            target["initialized"] = True
            return
       
        if isinstance(node, Show):
            self.check_expr(node.expr); return
        
        if isinstance(node, Block):
                self.check_block(node); return
        
        if isinstance(node, If):
            self._same_type(self.check_expr(node.condition), 'boolean', 'if condition')
            self.check_block(node.then_block, "if-then")
            if node.else_block is not None:
                self.check_block(node.else_block, "if-else")
            return
            
        if isinstance(node, While):
           self._same_type(self.check_expr(node.condition), 'boolean', 'while condition')
           self.check_block(node.body, "while")
           return
        raise SemanticError(f"Unsupported statement type: {type(node).__name__}")

    def analyze(self, program):
            self.reset()
            for stmt in program:
                self.check_stmt(stmt)
            return program

    def all_scopes_table(self):
        # Return the current symbol table for debugging purposes
        return {scope.name:{name: dict(meta) for name, meta in scope.symbols.items()} for scope in self.scope_history}

#creating postive and negative test cases for semantic analysis

POSITIVE = {
    'arithmetic and show': 'let x = 5; let y = 10; show x + y;',
    'assignment and unary': 'let x = 5; x = -x; show x;',
    'boolean, comparison, and if/else':'let x = 5; let y = 10; if (x < y) { show x; } else { show 0; }',
    'while and modulo': 'let x=0; while (x<3){ x = x + 1; show x; }',
}

NEGATIVE = {
    'undefined variable':' let x = 10; show x+y;',
    'assignment before declaration':'total =1;',
    'boolen, comparison, and if/else': 'let x = 4; if(x>= 3 and not false){ show x; } else { show 0; }',
    'self-reference': 'let total = total + 1;',
    'branch-only declaration': 'if (true) {let x = 1;} show x;',
    'loop-only declaration': 'while (true) {let x = 1;} show x;',
}

def run_semantic_tests():
    from frontend import parse_to_ast
    cases = [(name, code, True) for name, code in POSITIVE.items()] + \
            [(name, code, False) for name, code in NEGATIVE.items()]

    passed = 0
    print('My TinyLang - Semantic Analysis and Validation Tests')
    print('=' * 60)

    for i, (name, code, expected) in enumerate(cases, 1):
        analyzer = SemanticAnalyzer()
        try:
            analyzer.analyze(parse_to_ast(code))
            
            valid, reason =True,  'No semantic errors found.'
        except SemanticError as e:
            valid, reason =False, str(e)
        except Exception as e:
            print(f'Test {i} - {name}: Unexpected error: {e}')
            continue
        success = valid == expected
        passed += success

        print(f'{i}.{name}: {"VALID" if valid else "INVALID"} | {"PASS" if success else "FAIL"}' )

    print('=' * 60)

    print(f'RESULT:{passed}/{len(cases)} tests passed.')

    return passed, len(cases)

if __name__ == '__main__':
    raise SystemExit(0 if run_semantic_tests() else 1)
           