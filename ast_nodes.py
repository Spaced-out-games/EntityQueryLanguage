"""
    Defines AST Nodes for Entity Query Language
"""
from __future__ import annotations   # lets annotations reference classes defined later
from typing import Any

from dataclasses import dataclass, field, replace
from abc import abstractmethod

# ============================================================
# Roots
# ============================================================
@dataclass
class AST_Node:
    # kw_only so subclasses can still have required fields (Python 3.10+)
    line: int | None = field(default=None, kw_only=True, repr=False)
    column: int | None = field(default=None, kw_only=True, repr=False)


class Expression(AST_Node):
    """Anything that evaluates to a value."""
    @abstractmethod
    def typename(self: Expression, **kwargs: dict[str, Any]) -> str:
        pass
class Statement(AST_Node):   """Anything that can appear in a block."""
class TopLevel(AST_Node):    """Anything that can appear at file scope."""
class TypeSuffix(AST_Node):  """&, [N]"""
class Tag(AST_Node):         """Qualifier keywords."""


# ============================================================
# Names
# ============================================================
# NOTE: Only ever used in declarations and struct members!
@dataclass
class Identifier(AST_Node):          # a name being *declared*
    name: str

    def pretty(self) -> str:
        return f'"{self.name}"'
@dataclass
class VarRef(Expression):        # a name being *used*
    name: str

    def __repr__(self: VarRef) -> str:
        return f'Symbol("{self.name}")'

    def typename(self: VarRef, **kwargs: dict[str, Any]) -> str:
        assert "current_scope" in kwargs, "VarRef::typename expected current_scope as a keyword argument"
        current_scope = kwargs["current_scope"]

        
        assert isinstance(current_scope, Scope), "VarRef::typename expected current_scope keyword argument to be a Scope"

        return current_scope.find_recursive(self.name)

        




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
class Type(AST_Node):
    typename: str | None = None
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

        result = " ".join(qualifiers + [self.typename or "???"])

        if self.array_size is not None:
            result += f"[{self.array_size}]"

        if self.reference:
            result += "&"

        return result

    def __repr__(self) -> str:
        return self.pretty()

    # Removes all type qualifications
    def decay_t(self) -> Type:
        return replace(self, inline=False, static=False, mut=False, const=False, reference=False)



from dataclasses import dataclass
from dataclasses import field

#from typeinfo import *







def get_func_signature(decorators: list['Decorator'], return_type: Type, name: Identifier, parameters: list[Parameter]) -> str:

        result = ""

        if decorators is not None:
            for decorator in decorators:
                result += decorator.pretty() + "\t"

        result += name.name

        result += "("

        for param in parameters:
            result += f"{param.type.typename}, " 
        
        result += ")"

        return result        



            


# ============================================================
# Expressions
# ============================================================
@dataclass
class Literal_Node(Expression):
    value: str | int | float | bool

    def pretty(self) -> str:
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
        assert False, "Literal_Node expression has illegal primitive type"
        return None

    def __repr__(self, **kwargs: dict[str, Any]) -> str:
        return self.pretty()


    def typename(self, **kwargs: dict[str, Any]) -> str:
        if isinstance(self.value, int):
            return "i64"
        elif isinstance(self.value, float):
            return "f64"
        elif isinstance(self.value, str):
            return f"char[{len(self.value)}]"
        elif isinstance(self.value, bool):
            return "bool"
        return "void"

@dataclass
class UnaryExpression(Expression):
    operator: str
    operand: Expression

    def __repr__(self) -> str:
        return self.operator + self.operand.__repr__()
    def typename(self, **kwargs: dict[str, Any]) -> str:
        if self.operator in ["~", "!"]:
            return "bool"
        return self.operand.typename(**kwargs)

@dataclass
class BinaryExpression(Expression):
    operator: str
    left: Expression
    right: Expression

    def __repr__(self) -> str:
        return f"({self.left} {self.operator} {self.right})" 



@dataclass
class AssignExpression(Expression):
    operator: str                 # "=", "+=", ...
    target: Expression
    value: Expression
    
    def pretty(self) -> str:
        return repr(self.target) + self.operator + repr(self.value)

@dataclass
class MemberAccess(Expression):
    target: Expression
    member: str

    def __repr__(self) -> str:

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
class ArgumentList(AST_Node):
    args: list[Expression] = field(default_factory=list)

@dataclass
class FuncCall(Expression):
    callee: Expression            # grammar allows any postfix expr, not just a name
    args: ArgumentList = field(default_factory=ArgumentList)


# ============================================================
# Statements
# ============================================================
@dataclass
class Initializer(AST_Node):
    expression: Expression

    def pretty(self) -> str:
        if self.expression is None:
            return "?"
        elif isinstance(self.expression, Literal_Node):
            return self.expression.pretty()
        else:
            return self.expression.__repr__()

    

@dataclass
class Declaration(Statement, TopLevel):      # legal in blocks and at file scope
    type: Type
    id: str
    initializer: Initializer | None = None

    def pretty(self) -> str:
        if self.initializer:
            return f"{self.type.pretty()} {self.id} = {self.initializer.pretty()}"
        return f"{self.type.pretty()} {self.id}"
        

@dataclass
class ExpressionStatement(Statement):
    expression: Expression



@dataclass
class StatementBlock(Statement):
    statements: list[Statement]
    parent: Scope
    scope: dict[str, None] = field(default_factory=dict)


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
class ForInitializer(AST_Node):
    init: Expression

@dataclass
class ForConditional(AST_Node):
    cond: Expression

@dataclass
class ForStep(AST_Node):
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
class DecoratorType(AST_Node):
    name: str

@dataclass
class DecoratorValue(AST_Node):      # @export qsh
    value: str

@dataclass
class Decorator(AST_Node):
    type: str
    args: ArgumentList | DecoratorValue | None = None

    def pretty(self) -> str:
        if isinstance(self.args, DecoratorValue):
            return f"@{self.type} {self.args.value}"
        return f"@{self.type}(...)"

    def __repr__(self) -> str:
        return f"@{self.type}" 


@dataclass
class DecoratorList(AST_Node):
    decorators: list[Decorator]


# ============================================================
# Top-level definitions
# ============================================================
@dataclass
class Parameter(AST_Node):
    type: Type
    name: Identifier

    def pretty(self) -> str:
        return f"{self.type.pretty()} {self.name.name}"

@dataclass
class ParameterList(AST_Node):
    parameters: list[Parameter]

    def pretty(self) -> str:
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
class StructMember(AST_Node):
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
class Program(AST_Node):
    entries: list[TopLevel] = field(default_factory=list)
    globals: Scope | None = None

    def children(self) -> list[TopLevel]:
        return self.entries



@dataclass
class Scope:
    variables: SymbolTable
    # doesn't have to be unique or set or useful, just for debugging
    debug_name: str
    parent: Scope | None

    def pretty(self) -> str:
        result = f" {self.debug_name}{str(self.variables)}"
        if self.parent is not None:
            result += " -> " + self.parent.pretty()
        return result

    def find_recursive(self, key: str) -> str:
        # Prefer locals over globals
        if key in self.variables:
            return self.variables[key]

        # Try higher-scoped symbols
        if self.parent is not None:
            return self.parent.find_recursive(key)

        return "void"

    def find(self, key: str) -> str:
        if key in self.variables:
            return self.variables[key]
        
        return "void"



# Non-tokens

# Local-scope
class SymbolTable(dict[str, str]):
    """ Maps Identifier -> typename, scope-local """
    pass

