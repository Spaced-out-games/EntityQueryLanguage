"""
    Defines AST Nodes for Entity Query Language
"""


from __future__ import annotations   # lets annotations reference classes defined later
from dataclasses import dataclass, field


# ============================================================
# Roots
# ============================================================
@dataclass
class Node:
    # kw_only so subclasses can still have required fields (Python 3.10+)
    line: int | None = field(default=None, kw_only=True, repr=False)
    column: int | None = field(default=None, kw_only=True, repr=False)


class Expression(Node):  """Anything that evaluates to a value."""
class Statement(Node):   """Anything that can appear in a block."""
class TopLevel(Node):    """Anything that can appear at file scope."""
class TypeSuffix(Node):  """&, [N]"""
class Tag(Node):         """Qualifier keywords."""


# ============================================================
# Names
# ============================================================
@dataclass
class Identifier(Node):          # a name being *declared*
    name: str

@dataclass
class VarRef(Expression):        # a name being *used*
    name: str


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
    suffix: TypeSuffix | None = None


# ============================================================
# Expressions
# ============================================================
@dataclass
class Literal(Expression):
    value: str | int | float

@dataclass
class UnaryExpression(Expression):
    operator: str
    operand: Expression

@dataclass
class BinaryExpression(Expression):
    operator: str
    left: Expression
    right: Expression

@dataclass
class AssignExpression(Expression):
    operator: str                 # "=", "+=", ...
    target: Expression
    value: Expression

@dataclass
class MemberAccess(Expression):
    target: Expression
    member: str

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

@dataclass
class Declaration(Statement, TopLevel):      # legal in blocks and at file scope
    type: Type
    id: Identifier
    initializer: Initializer | None = None

@dataclass
class ExpressionStatement(Statement):
    expression: Expression

@dataclass
class StatementBlock(Statement):
    statements: list[Statement] = field(default_factory=list)


@dataclass
class ContinueStatement(Statement):
    pass

@dataclass
class BreakStatement(Statement):
    pass

@dataclass
class ElseClause(Node):
    body: IfStatement | StatementBlock

@dataclass
class IfStatement(Statement):
    condition: Expression
    then_block: StatementBlock
    else_clause: ElseClause | None = None

@dataclass
class WhileStatement(Statement):
    condition: Expression
    body: StatementBlock



@dataclass
class ForInitializer(Node):
    init: Statement

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
    type: DecoratorType
    args: ArgumentList | DecoratorValue | None = None

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

@dataclass
class ParameterList(Node):
    decorators: list[Decorator]

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

@dataclass
class StructDefinition(TopLevel):
    name: Identifier
    members: list[StructMember]
    virtual: bool = False
    decorators: list[Decorator] = field(default_factory=list)

@dataclass
class Program(Node):
    entries: list[TopLevel] = field(default_factory=list)


@dataclass
class Scope(Node):
    variables: dict[str, Type]