import ast
from lark import Transformer, Tree
from dataclasses import fields, is_dataclass
from ast_nodes import *

# debugging
from utilities import pretty_ast
class ESLSemanticError(Exception):
    """A well-formed parse that violates a language rule (expected rejection)."""




QUALIFIERS = {
    "static": (StaticTag, "static"),
    "inline": (InlineTag, "inline"),
    "const":  (ConstTag,  "const"),
    "mut":    (MutTag,    "mut"),
}
TAG_FIELD = {cls: field for cls, field in QUALIFIERS.values()}


def binop_functor(op):
    def handler(self, items):
        return BinaryExpression(op, items[0], items[1])
    return handler


def unop_functor(op):
    def handler(self, items):
        return UnaryExpression(op, items[0])
    return handler


def ident_flatten(x):
    """Normalise a declared name that may arrive as str or Identifier."""
    return x if isinstance(x, Identifier) else Identifier(str(x))


class ESLTransformer(Transformer):
    # ========================================================
    # Terminals
    # ========================================================
    def NAME(self, token):             return str(token)
    def DECIMAL_INT(self, token):      return int(token)
    def HEXADECIMAL_INT(self, token):  return int(token, 16)
    def DECIMAL_FLOAT(self, token):    return float(token)
    def STRING(self, token):           return ast.literal_eval(str(token))

    # ========================================================
    # Names
    # ========================================================
    def identifier(self, items):     return Identifier(items[0])   # declared name
    def var_ref(self, items):        return VarRef(items[0])       # used name
    def struct_name(self, items):    return Identifier(items[0])
    def function_name(self, items):  return Identifier(items[0])
    def argument_name(self, items):  return Identifier(items[0])
    def typename(self, items):       return str(items[0])

    # ========================================================
    # Literals
    # ========================================================
    def string_literal(self, items):  return Literal(items[0])
    def number_literal(self, items):  return Literal(items[0])
    def literal(self, items):         return items[0]

    # ========================================================
    # Types
    # ========================================================
    def reference(self, _):      return ReferenceFlag()
    def array_size(self, items): return ArraySpan(items[0])
    def type_suffix(self, items):
        return items[0]

    @staticmethod
    def find_node(items, cls, default=None):
        return next((item for item in items if isinstance(item, cls)), default)

    def assign_op(self, items):
        return items[0]

    def type_qualifier(self, items):
        name = str(items[0])
        try:
            return QUALIFIERS[name][0]()
        except KeyError:
            raise ESLSemanticError(f"unknown type qualifier `{name}`")

    def virtual_tag(self, _):
        return VirtualTag()

    def qualified_type(self, items):
        result = Type()

        for item in items:
            match item:
                case StaticTag():
                    if result.static:
                        raise ESLSemanticError("`static` was used more than once")
                    result.static = True

                case InlineTag():
                    if result.inline:
                        raise ESLSemanticError("`inline` was used more than once")
                    result.inline = True

                case ConstTag():
                    if result.const:
                        raise ESLSemanticError("`const` was used more than once")
                    result.const = True

                case MutTag():
                    if result.mut:
                        raise ESLSemanticError("`mut` was used more than once")
                    result.mut = True

                case VirtualTag():
                    assert False, "this should never happen"
                    pass

                case TypeSuffix():
                    assert not result.reference and result.array_size is None, "this should never happen"
                        

                    if isinstance(item, ReferenceFlag):
                        result.reference = True
                    elif isinstance(item, ArraySpan):
                        result.array_size = item.size
                

                case str():
                    result.type_id = item

        if result.const and result.mut:
            raise ESLSemanticError("`const` and `mut` are mutually exclusive")

        

        return result

    def return_type(self, items):
        return items[0]

    # ========================================================
    # Expressions
    # ========================================================
    add = binop_functor("+");           subtract = binop_functor("-")
    multiply = binop_functor("*");      divide = binop_functor("/");      modulo = binop_functor("%")
    left_shift = binop_functor("<<");   right_shift = binop_functor(">>")
    less = binop_functor("<");          less_equal = binop_functor("<=")
    greater = binop_functor(">");       greater_equal = binop_functor(">=")
    equal = binop_functor("==");        not_equal = binop_functor("!=")
    bitwise_and = binop_functor("&");   bitwise_xor = binop_functor("^");  bitwise_or = binop_functor("|")
    logical_and = binop_functor("&&");  logical_or = binop_functor("||")

    positive = unop_functor("+");       negate = unop_functor("-")
    logical_not = unop_functor("!");    bitwise_not = unop_functor("~")

    def assign(self, items):
        target, op, value = items
        return AssignExpression(str(op), target, value)

    def member(self, items):
        return MemberAccess(items[0], items[1])

    def array_access(self, items):
        return items[0]                       # just the index expression

    def index(self, items):
        return IndexExpression(items[0], items[1])

    def argument_list(self, items):
        for item in items:
            if not isinstance(item, Expression):
                raise ESLSemanticError(f"invalid argument: {item!r}")
        return ArgumentList(list(items))

    def call(self, items):
        args = items[1] if len(items) > 1 else ArgumentList()
        assert isinstance(items[0], VarRef)
        
        return FuncCall(items[0].name, args)

    # ========================================================
    # Declarations
    # ========================================================
    def initializer(self, items):
        return Initializer(items[0])

    @staticmethod
    def split_decl(items):
        type_ = next((i for i in items if isinstance(i, Type)), Type())
        id_ = next((i.name for i in items if isinstance(i, Identifier)), None)
        init = next((i for i in items if isinstance(i, Initializer)), Initializer(None))
        return type_, id_, init

    def declaration(self, items):
        return Declaration(*self.split_decl(items))

    def struct_member(self, items):
        return StructMember(*self.split_decl(items))

    # ========================================================
    # Decorators
    # ========================================================
    def decorator_type(self, items):
        return DecoratorType(items[0])

    def decorator_value(self, items):
        return DecoratorValue(items[0])

    def decorator_arguments(self, items):
        return items[0] if items else ArgumentList()    # `@foo()` has no children

    def decorator(self, items):
        type_ = next(i for i in items if isinstance(i, DecoratorType))
        args = next((i for i in items
                     if isinstance(i, (ArgumentList, DecoratorValue))), None)
        return Decorator(type_.name, args)

    def decorators(self, items):
        return DecoratorList(items)

    # ========================================================
    # Statements
    # ========================================================
    def expression_statement(self, items):
        return ExpressionStatement(items[0])

    def statement(self, items):


        return items[0]

    def block(self, items):
        scope = Scope({}, "block")


        return StatementBlock(list(items), None, scope=scope)
        

    def else_clause(self, items):
        return items[0]

    def if_statement(self, items):
        cond, then_block = items[0], items[1]
        else_clause = items[2] if len(items) > 2 and items[2] is not None else StatementBlock([], None)
        #then_block.scope.debug_name = "if_then"
        #else_clause.scope.debug_name = "if_else"

        return IfStatement(cond, then_block, else_clause)

    def while_statement(self, items):
        scope = Scope({}, "while")
        return WhileStatement(items[0], items[1], scope)

    def for_init(self, items):  return ForInitializer(items[0])
    def for_cond(self, items):  return ForConditional(items[0])
    def for_step(self, items):  return ForStep(items[0])

    def for_statement(self, items):
        init = next((i for i in items if isinstance(i, ForInitializer)), ForInitializer(None))
        condition = next((i for i in items if isinstance(i, ForConditional)), ForConditional(None))
        step = next((i for i in items if isinstance(i, ForStep)), ForStep(None))
        body = next((i for i in items if isinstance(i, StatementBlock)), StatementBlock([], None))
        body.scope.debug_name = "for_body"
        return ForStatement(init, condition, step, body)
    
    def continue_statement(self, items):
        return ContinueStatement()

    def break_statement(self, items):
        return BreakStatement()

    def return_statement(self, items):
        if items:
            return ReturnStatement(items[0])
        else:
            return None


    # ========================================================
    # Top level
    # ========================================================
    def parameter(self, items):
        pass

    def argument_declaration(self, items):
        type_, name = items
        return Parameter(type_, ident_flatten(name))

    def parameter_list(self, items):
        return ParameterList(items)

    def function_definition(self, items):
        decorators = next((i.decorators for i in items if isinstance(i, DecoratorList)), [])
        params = next((i.parameters for i in items if isinstance(i, ParameterList)), [])
        return_type = next(i for i in items if isinstance(i, Type))
        body = next(i for i in items if isinstance(i, StatementBlock))
        # the function's name is the only Identifier/str left over
        name = next(i for i in items
                    if isinstance(i, (Identifier, str)))

        body.scope.debug_name = f"fn {name}"

        return FunctionDefinition(return_type, ident_flatten(name), list(params),
                                  body, list(decorators))

    def struct_definition(self, items):
        return StructDefinition(
            name=next(i for i in items if isinstance(i, Identifier)),
            members=[i for i in items if isinstance(i, StructMember)],
            virtual=any(isinstance(i, VirtualTag) for i in items),
            decorators=list(next((i for i in items
                                  if isinstance(i, DecoratorList)), [])),
        )

    def entry(self, items):
        return items[0]

    def start(self, items):
        _globals = Scope({}, debug_name = "globals")

        program = Program(list(items), globals=_globals)

        return program

    # -------------------


    