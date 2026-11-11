"""
    Defines AST Nodes for Entity Query Language
"""


from __future__ import annotations   # lets annotations reference classes defined later
from dataclasses import dataclass, field
from abc import abstractmethod

from typeinfo import *


# ============================================================
# Roots
# ============================================================
@dataclass
class Node:
    # kw_only so subclasses can still have required fields (Python 3.10+)
    line: int | None = field(default=None, kw_only=True, repr=False)
    column: int | None = field(default=None, kw_only=True, repr=False)



class Expression(Node):
    """Anything that evaluates to a value."""
    
class Statement(Node):   """Anything that can appear in a block."""
class TopLevel(Node):    """Anything that can appear at file scope."""
class TypeSuffix(Node):  """&, [N]"""
class Tag(Node):         """Qualifier keywords."""



# ============================================================
# Names
# ============================================================
# NOTE: Only ever used in declarations and struct members!
@dataclass
class Identifier(Node):          # a name being *declared*
    name: str

    def pretty(self) -> str:
        return f'"{self.name}"'
@dataclass
class VarRef(Expression):        # a name being *used*
    name: str

    def __repr__(self):
        return f'Symbol("{self.name}")'






# ============================================================
# Types
# ============================================================
@dataclass
class ReferenceFlag(TypeSuffix): pass

@dataclass
class ArraySpan(TypeSuffix):
    size: int

@dataclass
class ConstTag(Tag): pass
@dataclass
class StaticTag(Tag): pass
@dataclass
class MutTag(Tag): pass
@dataclass
class InlineTag(Tag): pass
@dataclass
class VirtualTag(Tag): pass

@dataclass
class Type(Node):
    type_id: str | None = None
    inline: bool = False
    static: bool = False
    mut: bool = False
    const: bool = False
    reference: bool = False
    array_size: int | None = None


    def pretty(self) -> str:
        qualifiers = [
            name for name in ("static", "inline", "mut", "const")
            if getattr(self, name)
        ]

        result = " ".join(qualifiers + [self.type_id or "???"])

        if self.array_size is not None:
            result += f"[{self.array_size}]"

        if self.reference:
            result += "&"

        return result

    def __repr__(self):
        return self.pretty()


        




from dataclasses import dataclass
from dataclasses import field

# symbol table entry: name, type, scope, initialized
#@dataclass
#class SymbolTableEntry:
#    name: str
#    type: Type
#    initialized: bool

# function table entry
@dataclass
class FunctionSignature:
    return_type: Type
    name: Identifier
    parameters: list[Parameter]
    decorators: list[Decorator] = field(default_factory=list)

# Function identifier table
class FunctionTable(dict[str, FunctionSignature]): pass

# Identifier -> Type
class SymbolTable(dict[str, Type]): pass

# Type -> Layout<T>
class TypeTable(dict[Type, TypeLayout]): pass

U8_MIN  = 0x00
U8_MAX  = 0xFF
U16_MIN = 0x0000
U16_MAX = 0xFFFF

U32_MIN = 0x00000000
U32_MAX = 0xFFFFFFFF

U64_MIN = 0x0000000000000000
U64_MAX = 0xFFFFFFFFFFFFFFFF

I8_MIN  = -0x80
I8_MAX  = 0x7F

I16_MIN = -0x8000
I16_MAX = 0x7FFF

I32_MIN = -0x80000000
I32_MAX = 0x7FFFFFFF

I64_MIN = -0x8000000000000000
I64_MAX = 0x7FFFFFFFFFFFFFFF


def get_func_signature(decorators: list['Decorator'], return_type: type, name: Identifier, parameters: list[Parameter]) -> str:

        result = ""

        if decorators is not None:
            for decorator in decorators:
                result += decorator.pretty() + "\t"

        result += name.name

        result += "("

        for param in parameters:
            result += f"{param.type.type_id}, " 
        
        result += ")"

        return result        

@dataclass
class Scope:
    variables: SymbolTable
    # doesn't have to be unique or set or useful, just for debugging
    debug_name: str | None
    parent: Scope | None = None

    def pretty(self):
        result = f" {self.debug_name}{str(self.variables)}"
        if self.parent is not None:
            result += " -> " + self.parent.pretty()
        return result

    def find_recursive(self, key: str):
        # Prefer locals over globals
        if key in self.variables:
            return self.variables[key]

        # Try higher-scoped symbols
        if self.parent is not None:
            return self.parent.find_recursive(key)

        return None

    def find(self, key: str):
        if key in self.variables:
            return self.variables[key]
        
        return None
            


# ============================================================
# Expressions
# ============================================================
@dataclass
class Literal(Expression):
    value: str | int | float | bool

    def pretty(self) ->str:
        if isinstance(self.value, int):
            return f"{self.value}"
        elif isinstance(self.value, float):
            return f"{self.value}f"
        elif isinstance(self.value, str):
            return f'"{self.value}"'
        elif isinstance(self.value, bool):
            if self.value:
                return "true"
            return "false"
        assert False, "Literal expression has illegal primitive type"

    def __repr__(self):
        return self.pretty()

    def type_id(self):
        if self.value is None:
            return "void"
        elif isinstance(self.value, int):
            # keep it simple
            if(self.value > 0):
                return "u32"
            
            else:
                return "i32"

        elif isinstance(self.value, float):
            return "f64"

        elif isinstance(self.value, str):
            # need one more for the null terminator
            return f"char[]"

        raise ValueError("Invalid value")


@dataclass
class UnaryExpression(Expression):
    operator: str
    operand: Expression

    def __repr__(self):
        return self.operator + self.operand.__repr__()
    def type_id(self, **kwargs):
        if self.operator in ["~", "!"]:
            return "bool"
        return self.operand.type_id(kwargs)

@dataclass
class BinaryExpression(Expression):
    operator: str
    left: Expression
    right: Expression

    def __repr__(self):
        return f"({self.left} {self.operator} {self.right})" 



@dataclass
class AssignExpression(Expression):
    operator: str                 # "=", "+=", ...
    target: Expression
    value: Expression
    
    def pretty(self):
        return repr(self.target) + self.operator + repr(self.value)



@dataclass
class MemberAccess(Expression):
    target: Expression
    member: str

    def __repr__(self):

        if isinstance(self.target, MemberAccess):
            return f"{self.target}.{self.member}"
        elif isinstance(self.target, VarRef):
            return f"{self.target.name}.{self.member}"
        elif isinstance(self.target, FuncCall):
            return f"{self.target.callee}"
        else:
            return "BadMemberAccess"
        assert False
        return ""

@dataclass
class IndexExpression(Expression):
    target: Expression
    index: Expression

@dataclass
class ArgumentList(Node):
    args: list[Expression] = field(default_factory=list)

@dataclass
class FuncCall(Expression):
    callee: Expression            # grammar allows any postfix expr, not just a name
    args: ArgumentList = field(default_factory=ArgumentList)


# ============================================================
# Statements
# ============================================================
@dataclass
class Initializer(Node):
    expression: Expression

    def pretty(self):
        if self.expression is None:
            return "?"
        elif isinstance(self.expression, Literal):
            return self.expression.pretty()
        else:
            return self.expression.__repr__()

    

@dataclass
class Declaration(Statement, TopLevel):      # legal in blocks and at file scope
    type: Type
    id: str
    initializer: Initializer | None = None

    def pretty(self) -> str:
        # .pretty()
        return f"{self.type.pretty()} {self.id} = {self.initializer.pretty()}"

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

# Not an AST node - a helper
#@dataclass
class TypeInitializerPair(Node):
    type: Type
    init: Initializer

@dataclass
class StatementBlock(Statement):
    statements: list[Statement]
    parent: Scope # pointer upwards
    scope: Scope # this scope


@dataclass
class ContinueStatement(Statement):
    pass

@dataclass
class BreakStatement(Statement):
    pass


@dataclass
class IfStatement(Statement):
    condition: Expression
    then_block: StatementBlock
    else_clause: StatementBlock



@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: StatementBlock
    locals: Scope | None = None # forwarding link; non-owning reference to the scope of the body block, for semantic analysis



@dataclass
class ForInitializer(Node):
    init: Expression

@dataclass
class ForConditional(Node):
    cond: Expression

@dataclass
class ForStep(Node):
    step: Statement

@dataclass
class ForStatement(Statement):
    init: ForInitializer
    condition: ForConditional
    step: ForStep
    body: StatementBlock


@dataclass
class ReturnStatement(Statement):
    value: Expression | None = None


# ============================================================
# Decorators
# ============================================================
@dataclass
class DecoratorType(Node):
    name: str

@dataclass
class DecoratorValue(Node):      # @export qsh
    value: str

@dataclass
class Decorator(Node):
    type: str
    args: ArgumentList | DecoratorValue | None = None

    def pretty(self):
        if isinstance(self.args, DecoratorValue):
            return f"@{self.type} {self.args.value}"
        return f"@{self.type}(...)"

    def __repr__(self):
        return f"@{self.type}" 


@dataclass
class DecoratorList(Node):
    decorators: list[Decorator]


# ============================================================
# Top-level definitions
# ============================================================
@dataclass
class Parameter(Node):
    type: Type
    name: Identifier

    def pretty(self):
        return f"{self.type.pretty()} {self.name.name}"

@dataclass
class ParameterList(Node):
    parameters: list[Parameter]

    def pretty(self):
        result = '('
        for param in self.parameters:
            result += f"{param.type.pretty()} {param.name.name}, "

        return result + ')'



@dataclass
class FunctionDefinition(TopLevel):
    return_type: Type
    name: Identifier
    parameters: list[Parameter]
    body: StatementBlock
    decorators: list[Decorator] = field(default_factory=list)


    


@dataclass
class StructMember(Node):
    type: Type
    id: Identifier
    initializer: Initializer | None = None

    def pretty(self) -> str:
        return f"{self.type.pretty()} {self.id} = {self.initializer.pretty() if self.initializer is not None else "?"}"

@dataclass
class StructDefinition(TopLevel):
    name: Identifier
    members: list[StructMember]
    virtual: bool = False
    decorators: list[Decorator] = field(default_factory=list)

    

        

@dataclass
class Program(Node):
    entries: list[TopLevel] = field(default_factory=list)
    globals: Scope= field(default_factory=list)

    def children(self):
        return self.entries





def get_expression_type(symbols: SymbolTable, layouts: TypeTable, scope: Scope, node: Node):
    match node:
        case Literal():
            type_name = node.type_id()
            return type_table[type_name] if type_name in type_table else None

        case Identifier():
            type_name = scope.find_recursive(node.name)
            return type_table[type_name] if type_name in type_table else None

        case VarRef():
            type_name = scope.find_recursive(node.name)
            return type_table[type_name] if type_name in type_table else None

        case MemberAccess():
            type_name = scope.find_recursive(node.target)
            type_info = type_table[type_name] if type_name in type_table else None

            if type_info is None:
                return None
            
            return type_info.members[node.member].type if node.member in type_table else None

        case IndexExpression():
            return get_expression_type(node.target)

        
