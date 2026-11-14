"""Future milestone: semantic analysis and symbol table."""
# all the nodes
from ast_nodes import *
from ast_nodes import SymbolTable

# type information
from type_implementation import TypeTable


from enum import Enum, auto

class ValueCategory(Enum):
    UNKNOWN = auto()
    LVALUE = auto()
    RVALUE = auto()

class SemanticError(Exception):
    ''' Semantic analysis error. '''
    pass

binary_operators = ["+", "-", "*", "/", "%", "<<", ">>", "<", "<=", ">", ">=", "==", "!=", "&", "^", "|", "&&", "||"]
assignment_operators = ["+=", "-=", "*=", "/=", "%=", "="]




def resolve_funccall():
    pass





def classify_value(functions: FunctionDefinition,expr: Expression) -> ValueCategory:

    if isinstance(expr, Literal):
        return ValueCategory.RVALUE

    if isinstance(expr, VarRef):
        return ValueCategory.LVALUE

    if isinstance(expr, MemberAccess):
        return classify_value(expr.target)

    if isinstance(expr, IndexExpression):
        return classify_value(expr.target)

    if isinstance(expr, FuncCall):
        if expr in functions:
            return_t = functions[expr].return_type
            if return_t.const: # always an rvalue
                return ValueCategory.RVALUE
            if return_t.typename == "void":
                return ValueCategory.UNKNOWN
            return ValueCategory.LVALUE
        else:
            return ValueCategory.UNKNOWN


    if isinstance(expr, BinaryExpression):
        return ValueCategory.RVALUE

    if isinstance(expr, UnaryExpression):
        return ValueCategory.RVALUE

    raise SemanticError(f"Unknown expression category: {type(expr).__name__}")


def validate_identifier(scope: Scope, symbol_id: str, typename: str) -> None:
    if(symbol_id is None):
        raise SemanticError("Identifier name was None")
    if(symbol_id == ""):
        raise SemanticError("Identifier name was empty")


    # NOTICE: Identifiers are only produced by struct member declaration and local declarations. 
    # That means we never need to check that it exists. However, we still need to ensure that
    # it only occurs once in the current scope

    # if there's a double-definition, throw
    if(scope.find(symbol_id)):
        raise SemanticError(f"Identifier {symbol_id} was declared more than once in this scope")

    # if the typename isn't registered, throw
    if typename not in all_types:
        raise SemanticError(f"invalid type: type '{typename}' has not been declared at this point of execution")

    # if register the variable
    scope.variables[symbol_id] = all_types[typename]
    

    return


def validate_varref(scope: Scope, node: VarRef) -> None:
    if not isinstance(type.typename, str):
        raise SemanticError("Identifier name was not str")
    if(node.name == ""):
        raise SemanticError("Identifier name was empty")

    # we are using it so it has to exist
    if (scope.find_recursive(node.name) is None):
        raise SemanticError(f"symbol '{node.name}' was not declared")

    return


def validate_type_node(node: Type) -> None:
    if not isinstance(node.typename, str):
        raise SemanticError("type_id was not a str")
    if node.typename == "":
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


def validate_scope_node(node: Scope) -> None:
    if not isinstance(node.variables, SymbolTable):
        raise SemanticError("variables was not a SymbolTable")

    for key, value in node.variables:
        if not isinstance(value, Type):
            raise SemanticError("variables was not a SymbolTable")

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


def validate_binary_expression(node: BinaryExpression) -> None:
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


def validate_assign_expression(scope: Scope, node: AssignExpression) -> None:

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
    value_class =  classify_value(node.target)

    if value_class == ValueCategory.UNKNOWN:
        raise SemanticError("Unknown value category")
    elif value_class == ValueCategory.RVALUE:
        raise SemanticError("Attempted to assign an rvalue")


def validate_member_access(current_scope: Scope, node: MemberAccess) -> None:
    # run of the mill shit
    if not isinstance(node.target, Expression):
        raise SemanticError("target was not an expression")

    # first, find the symbol's typename
    typename = node.target.typename(current_scope=current_scope)

    # validate the typename
    if not isinstance(typename, str):
        raise SemanticError("Invalid typename: typename was not str")

    # get the type information

    
def validate_expression(scope: Scope, node: Expression):
    match node:
        case UnaryExpression():
            validate_unary_expression(node)
        case BinaryExpression():
            validate_binary_expression(node)
        case AssignExpression():
            validate_assign_expression(scope, node)
        case MemberAccess():
            validate_member_access(scope, node)
        case IndexExpression():
            validate_index_expression(node)
        case FuncCall():
            validate_func_call(node)
            





    


    
    

