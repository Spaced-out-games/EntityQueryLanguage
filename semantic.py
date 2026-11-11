"""Future milestone: semantic analysis and symbol table."""
# all the nodes
from ast_nodes import *

from typeinfo import *

# type information


from enum import Enum, auto

class ExpressionCategory(Enum):
    UNKNOWN = auto()
    LVALUE = auto()
    RVALUE = auto()

class SemanticError(Exception):
    ''' Semantic analysis error. '''
    pass

binary_operators = ["+", "-", "*", "/", "%", "<<", ">>", "<", "<=", ">", ">=", "==", "!=", "&", "^", "|", "&&", "||"]
assignment_operators = ["+=", "-=", "*=", "/=", "%=", "="]










def classify_expression(functions: FunctionTable,expr: Expression) -> ExpressionCategory:

    if isinstance(expr, Literal):
        return ExpressionCategory.RVALUE

    if isinstance(expr, VarRef):
        return ExpressionCategory.LVALUE

    if isinstance(expr, MemberAccess):
        return classify_expression(expr.target)

    if isinstance(expr, IndexExpression):
        return classify_expression(expr.target)

    if isinstance(expr, FuncCall):
        if expr in functions:
            return_t = functions[expr].return_type
            if return_t.const or return_t.type_id == "void":
                return ExpressionCategory.RVALUE
            return ExpressionCategory.LVALUE
        else:
            return ExpressionCategory.UNKNOWN


    if isinstance(expr, BinaryExpression):
        return ExpressionCategory.RVALUE

    if isinstance(expr, UnaryExpression):
        return ExpressionCategory.RVALUE

    raise SemanticError(f"Unknown expression category: {type(expr).__name__}")



def validate_identifier(scope: Scope, node: Identifier):
    if(node.name is None):
        raise SemanticError("Identifier name was None")
    if(node.name == ""):
        raise SemanticError("Identifier name was empty")


    return


def validate_varref(scope: Scope, node: VarRef):
    if not isinstance(type.type_id, str):
        raise SemanticError("Identifier name was not str")
    if(node.name == ""):
        raise SemanticError("Identifier name was empty")

    # we are using it so it must exist
    if scope.find_recursive(node.name) is None:
        raise SemanticError(f"symbol '{node.name}' was not declared")

    return


def validate_type_node(node: Type):
    if not isinstance(node.type_id, str):
        raise SemanticError("type_id was not a str")
    if node.type_id == "":
        raise SemanticError("type_id was empty")

    if not isinstance(node.inline, bool):
        raise SemanticError("inline was not bool")
    if not isinstance(node.static, bool):
        raise SemanticError("static was not bool")
    if not isinstance(node.mut, bool):
        raise SemanticError("mut was not bool")
    if not isinstance(node.const, bool):
        raise SemanticError("const was not bool")
    if not isinstance(node.reference, bool):
        raise SemanticError("reference was not bool")

    if node.mut and node.const:
        raise SemanticError("const and mut are mutually exclusive")

    if node.array_size is not None and type(node.array_size) is not int:
        raise SemanticError("array_size was not int or None")

    if node.array_size is not None and node.reference:
        raise SemanticError("array and reference types are mutually exclusive")

    if node.array_size is not None and node.array_size <= 0:
        raise SemanticError("array types must have 1 or more elements")

def validate_scope_node(node: Scope):
    if not isinstance(node.variables, dict):
        raise SemanticError("variables was not dict")

    for symbol, symbol_type in node.variables:
        if not isinstance(symbol, Type):
            raise SemanticError("variables was not homogenously full of SymbolTableEntry")


    if not isinstance(node.debug_name, (str, None)):
        raise SemanticError("debug_name was not str or None")

    if not isinstance(node.parent, (Scope, None)):
        raise SemanticError("parent was not Scope or None")


def validate_literal_node(node: Literal):
    if node.value is None:
        raise SemanticError("Literal held no value")

    if isinstance(node.value, (str, int, float)):
        raise SemanticError("Literal held invalid value type")


def validate_unary_expression(node: UnaryExpression):

    if node.operator not in ["+", "-", "!", "~"]:
        raise SemanticError("Unsupported Unary operator")

    if node.operand is None:
        raise SemanticError("Unary operand was None")

    if not isinstance(node.operand, Expression):
        raise SemanticError("Unary operand was not an expression")

    validate_expression(node.operand)

def validate_binary_expression(node: BinaryExpression):
    if node.operator not in binary_operators:
        raise SemanticError("Unsupported Unary operator")

    if node.left is None:
        raise SemanticError("left operator was None")

    if not isinstance(node.left, Expression):
        raise SemanticError("left was not an Expression")

    if node.right is None:
        raise SemanticError("right operator was None")

    if not isinstance(node.right, Expression):
        raise SemanticError("right was not an Expression")

    validate_expression(node.left)
    validate_expression(node.right)

def validate_assign_expression(scope: Scope, node: AssignExpression):

    if node.expression is None:
        raise SemanticError("expression was None")

    if not isinstance(node.expression, Expression):
        raise SemanticError("expression was not an Expression")

    if node.target is None:
        raise SemanticError("target was None")

    if not isinstance(node.target, Expression):
        raise SemanticError("target was not an Expression")

    validate_expression(node.expression)

    validate_expression(node.target)

    # here we'd make sure node.target is an lvalue
    value_class =  classify_expression(node.target)

    if value_class == ExpressionCategory.UNKNOWN:
        pass
    elif value_class == ExpressionCategory.RVALUE:
        raise SemanticError("Attempted to assign an rvalue")

def validate_member_access(current_scope: Scope, node: MemberAccess):
    # Better be an expression
    if not isinstance(node.target, Expression):
        raise SemanticError("target was not an expression")

     # first, find the symbol
    symbol = current_scope.find_recursive(node.target)

    # make sure the member exists
    
    type_id = node.target.type_id(current_scope=current_scope)

    if type_id is None:
        raise SemanticError("")

    


def validate_expression(node: Expression):
    match node:
        case UnaryExpression():
            validate_unary_expression(node)
        case BinaryExpression():
            validate_binary_expression(node)
        case AssignExpression():
            validate_assign_expression(node)
        case MemberAccess():
            validate_member_access(node)
        case IndexExpression():
            validate_index_expression(node)
        case FuncCall():
            validate_func_call(node)
            




class SemanticAnalyzer:
    type_table = primitive_types
    current_scope: Scope = Scope({}, "globals")

