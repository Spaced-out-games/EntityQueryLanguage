from dataclasses import dataclass, field
from typing import Optional, Any


# ============================================================
# AST base
# ============================================================

@dataclass
class Node:
    pass


# ============================================================
# Types
# ============================================================

@dataclass
class Type:
    name: str
    array_size: int | None = None
    reference: bool = False


@dataclass
class ReferenceType(Node):
    pass


@dataclass
class ArrayType(Node):
    size: int


# ============================================================
# Declarations
# ============================================================

@dataclass
class Declaration(Node):
    type: Type
    name: str
    initializer: Optional[Node] = None
    static: bool = False
    inline: bool = False
    const: bool = False
    mut: bool = False


@dataclass
class Parameter(Node):
    type: Type
    name: str
    const: bool = False
    mut: bool = False


@dataclass
class StructMember(Node):
    type: Type
    name: str
    initializer: Optional[Node] = None
    const: bool = False


@dataclass
class StructDefinition(Node):
    name: str
    members: list[StructMember]
    virtual: bool = False


@dataclass
class FunctionDefinition(Node):
    return_type: Type
    name: str
    parameters: list[Parameter]
    body: "Block"
    decorators: list["Decorator"] = field(default_factory=list)


@dataclass
class Decorator(Node):
    type: str
    arguments: list[Node] = field(default_factory=list)


# ============================================================
# Statements
# ============================================================

@dataclass
class Block(Node):
    statements: list[Node]


@dataclass
class Assignment(Node):
    target: Node
    value: Node


@dataclass
class ExpressionStatement(Node):
    expression: Node


@dataclass
class IfStatement(Node):
    condition: Node
    then_block: Block
    else_block: Optional[Block] = None


@dataclass
class WhileStatement(Node):
    condition: Node
    body: Block


@dataclass
class ForStatement(Node):
    initializer: Node
    condition: Node
    increment: Node
    body: Block


@dataclass
class ReturnStatement(Node):
    expression: Optional[Node] = None


# ============================================================
# Expressions
# ============================================================

@dataclass
class BinaryExpression(Node):
    operator: str
    left: Node
    right: Node


@dataclass
class UnaryExpression(Node):
    operator: str
    operand: Node


@dataclass
class CastExpression(Node):
    type: Type
    expression: Node


@dataclass
class FunctionCall(Node):
    name: str
    arguments: list[Node]


# ============================================================
# Values
# ============================================================

@dataclass
class Name(Node):
    value: str


@dataclass
class IntegerLiteral(Node):
    value: int


@dataclass
class FloatLiteral(Node):
    value: float


@dataclass
class StringLiteral(Node):
    value: str


@dataclass
class MemberAccess(Node):
    object: Node
    member: str


@dataclass
class IndexAccess(Node):
    object: Node
    index: Node


@dataclass
class Parenthesized(Node):
    expression: Node






























from lark import Transformer, Token


class ESLTransformer(Transformer):

    # ========================================================
    # Tokens
    # ========================================================

    def NAME(self, token):
        return str(token)

    def DECIMAL_INT(self, token):
        return int(token)

    def HEXADECIMAL_INT(self, token):
        return int(token, 16)

    def DECIMAL_FLOAT(self, token):
        return float(token)

    def STRING(self, token):
        # Remove surrounding quotes and decode escapes.
        import ast
        return ast.literal_eval(str(token))

    # ========================================================
    # Types
    # ========================================================

    def typename(self, items):
        return Type(items[0])

    def reference(self, _):
        return ReferenceType()

    def type_suffix(self, items):
        value = items[0]

        if isinstance(value, ReferenceType):
            return value

        return ArrayType(int(value))

    # ========================================================
    # Declarations
    # ========================================================

    def initializer(self, items):
        return items[0]

    def declaration(self, items):
        static = False
        inline = False
        const = False
        mut = False

        type_node = None
        name = None
        initializer = None

        for item in items:
            if item == "static":
                static = True
            elif item == "inline":
                inline = True
            elif item == "const":
                const = True
            elif item == "mut":
                mut = True
            elif isinstance(item, Type):
                type_node = item
            elif isinstance(item, str):
                name = item
            else:
                initializer = item

        return Declaration(
            type=type_node,
            name=name,
            initializer=initializer,
            static=static,
            inline=inline,
            const=const,
            mut=mut,
        )

    def parameter(self, items):
        const = False
        mut = False

        type_node = None
        name = None

        for item in items:
            if item == "const":
                const = True
            elif item == "mut":
                mut = True
            elif isinstance(item, Type):
                type_node = item
            elif isinstance(item, str):
                name = item

        return Parameter(
            type=type_node,
            name=name,
            const=const,
            mut=mut,
        )

    def parameter_list(self, items):
        return list(items)

    # ========================================================
    # Structs
    # ========================================================

    def virtual_modifier(self, _):
        return True

    def struct_member(self, items):
        const = False
        type_node = None
        name = None
        initializer = None

        for item in items:
            if item == "const":
                const = True
            elif isinstance(item, Type):
                type_node = item
            elif isinstance(item, str):
                name = item
            else:
                initializer = item

        return StructMember(
            type=type_node,
            name=name,
            initializer=initializer,
            const=const,
        )

    def struct_definition(self, items):
        virtual = False
        name = None
        members = []

        for item in items:
            if item is True:
                virtual = True
            elif isinstance(item, str):
                name = item
            elif isinstance(item, StructMember):
                members.append(item)

        return StructDefinition(
            name=name,
            members=members,
            virtual=virtual,
        )

    # ========================================================
    # Functions / decorators
    # ========================================================

    def function_definition(self, items):
        decorators = []
        return_type = None
        name = None
        parameters = []
        body = None

        for item in items:
            if isinstance(item, Decorator):
                decorators.append(item)
            elif isinstance(item, Type):
                return_type = item
            elif isinstance(item, str):
                name = item
            elif isinstance(item, list):
                parameters = item
            elif isinstance(item, Block):
                body = item

        return FunctionDefinition(
            return_type=return_type,
            name=name,
            parameters=parameters,
            body=body,
            decorators=decorators,
        )

    def decorator(self, items):
        decorator_type = items[0]
        arguments = items[1] if len(items) > 1 else []

        return Decorator(
            type=decorator_type,
            arguments=arguments,
        )

    def decorator_type(self, items):
        return items[0]

    def decorator_arguments(self, items):
        return items[0] if items else []

    # ========================================================
    # Statements
    # ========================================================

    def block(self, items):
        return Block(list(items))

    def assignment(self, items):
        return Assignment(
            target=items[0],
            value=items[1],
        )

    def expression_statement(self, items):
        return ExpressionStatement(items[0])

    def if_statement(self, items):
        return IfStatement(
            condition=items[0],
            then_block=items[1],
            else_block=items[2] if len(items) > 2 else None,
        )

    def else_clause(self, items):
        return items[0]

    def while_statement(self, items):
        return WhileStatement(
            condition=items[0],
            body=items[1],
        )

    def for_statement(self, items):
        return ForStatement(
            initializer=items[0],
            condition=items[1],
            increment=items[2],
            body=items[3],
        )

    def return_statement(self, items):
        return ReturnStatement(
            items[0] if items else None
        )

    # ========================================================
    # Expressions
    # ========================================================

    def comparison(self, items):
        return self._binary(items)

    def bitwise_shift(self, items):
        return self._binary(items)

    def sum(self, items):
        return self._binary(items)

    def product(self, items):
        return self._binary(items)

    def _binary(self, items):
        # Single expression gets passed through.
        if len(items) == 1:
            return items[0]

        # Grammar is left-recursive, so:
        #
        # a + b + c
        #
        # arrives as:
        #
        # [a, "+", b, "+", c]
        #
        result = items[0]

        for i in range(1, len(items), 2):
            result = BinaryExpression(
                operator=str(items[i]),
                left=result,
                right=items[i + 1],
            )

        return result

    def unary(self, items):
        if len(items) == 1:
            return items[0]

        return UnaryExpression(
            operator=str(items[0]),
            operand=items[1],
        )

    def cast(self, items):
        return CastExpression(
            type=items[0],
            expression=items[1],
        )

    # ========================================================
    # Lvalues
    # ========================================================

    def lvalue(self, items):
        if len(items) == 1:
            return Name(items[0])

        if len(items) == 2:
            return MemberAccess(
                object=items[0],
                member=items[1],
            )

        return IndexAccess(
            object=items[0],
            index=items[1],
        )

    # ========================================================
    # Rvalues
    # ========================================================

    def rvalue(self, items):
        return items[0]

    def postfix(self, items):
        if len(items) == 1:
            return items[0]

        if len(items) == 2:
            if isinstance(items[1], str):
                return MemberAccess(
                    object=items[0],
                    member=items[1],
                )

            return IndexAccess(
                object=items[0],
                index=items[1],
            )

    # ========================================================
    # Atoms
    # ========================================================

    def atom(self, items):
        item = items[0]

        if isinstance(item, str):
            return Name(item)

        return item

    def function_call(self, items):
        name = items[0]
        arguments = items[1] if len(items) > 1 else []

        return FunctionCall(
            name=name,
            arguments=arguments,
        )

    def argument_list(self, items):
        return list(items)

    # ========================================================
    # Literals
    # ========================================================

    def number_literal(self, items):
        value = items[0]

        if isinstance(value, int):
            return IntegerLiteral(value)

        return FloatLiteral(value)

    def literal(self, items):
        value = items[0]

        if isinstance(value, str):
            return StringLiteral(value)

        return value

    # ========================================================
    # Parentheses
    # ========================================================

    def expression(self, items):
        return items[0]

    def comparison(self, items):
        return self._binary(items)