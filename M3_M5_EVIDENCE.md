# M3–M5 Implementation and Test Evidence

## Entity Shading Language

## Feature traceability (at least four rows)
Declaration | int x = 5; | declaration: qualified_type identifier [initializer] ";" | Type(...), Identifier(...), Initializer(...)? Declaration(Type, Identifier, Initializer?)
For loop  | for (i = 0; i < n; i = i + 1) {} | for_statement: "for" "(" [for_init] ";" [for_cond] ";" [for_step] ")" block| "for", ";" | ForStatement(ForInitializer, ForConditional, ForStep, StatementBlock)
While loop | while (x < 5) {} | while_statement: "while" "(" expression ")" | "while", "(", ")", "<" | WhileStatement(Expression, StatementBlock)
If | if (True) {}| if_statement: "if" "(" expression ")" block [else_clause] | IfStatement(Expression, StatementBlock, ElseClause)

## Token inventory and token inspection output
// Token definitions
DECIMAL_INT: /[0-9]+/
HEXADECIMAL_INT: /0[xX][0-9a-fA-F]+/
DECIMAL_FLOAT: /[0-9]+\.[0-9]+/
STRING: /"(?:\\.|[^"\\])*"/


ASSIGN_OP: "+=" | "-=" | "*=" | "/=" | "%=" | "="
COMPOUND_OP: "+=" | "-=" | "*=" | "/=" | "%="

## M4 positive tests (at least four) and negative tests (at least four)

Positives:
// global
static inline const f32& deltaTime;
static inline const f32[16] camera;
/**/
// vector type
struct Vec3 {
    f32 x = 0.0;
    f32 y;
    f32 z;
};
/**/
// quaternion type
struct Quat {
    f32 x;
    f32 y;
    f32 z;
    f32 w;
};
/**/
// transform type
struct Transform {
    Vec3 position;
    Quat rotation;
    Vec3 scale;
    f32 extra = 0.04;
};
/**/
// virtual structure test
virtual struct Person {
    // captures arrays
    char[256] contents;
    i32[2] debts_and_credits;  
};
/**/
// tests entry point decorator
@entry
void integrate(mut Transform& transform, const Velocity& velocity) {
    transform = transform + velocity;
}

/**/
@SomeMadeUpDecorator("test", 124)
void foo() {
    transform.pos.x = 0;
}
/**/

@export qsh
void main() {
    // if-else
    if(i > 20) {
        print("i is too big");
    } else {
        print("i is too small");
    }
}
/**/
// tinylang positive test translation
void tinylang_example() {
    int score = 80;
    int bonus = 5;
    print(score + bonus * 2);
    if(score >= 60) {
        print(1);
    } else {
        print(0);
    }


    while(score < 85) {
        score = score + 1;
    }
    print(score);

    // recursive call:
    f(g(x));
    // function call, no args
    f();

    // array accesses
    a = b[43];
    a = b[54 + 5]
    b[54] = 1 + a;
}


## M5 parse tree / AST evidence and structural assertions

======================== CODE BLOCK ========================

// tinylang positive test translation
void tinylang_example() {
    int score = 80;
    int bonus = 5;
    print(score + bonus * 2);
    if(score >= 60) {
        print(1);
    } else {
        print(0);
    }


    while(score < 85) {
        score = score + 1;
    }
    print(score);

    // recursive call:
    f(g(x));
    f();
    a = b[43];
}
======================== PARSE TREE ========================
start
  entry
    function_definition
      qualified_type
        typename	void
      tinylang_example
      block
        statement
          declaration
            qualified_type
              typename	int
            identifier	score
            initializer
              literal
                number_literal	80
        statement
          declaration
            qualified_type
              typename	int
            identifier	bonus
            initializer
              literal
                number_literal	5
        statement
          expression_statement
            call
              var_ref	print
              argument_list
                add
                  var_ref	score
                  multiply
                    var_ref	bonus
                    literal
                      number_literal	2
        statement
          if_statement
            greater_equal
              var_ref	score
              literal
                number_literal	60
            block
              statement
                expression_statement
                  call
                    var_ref	print
                    argument_list
                      literal
                        number_literal	1
            else_clause
              block
                statement
                  expression_statement
                    call
                      var_ref	print
                      argument_list
                        literal
                          number_literal	0
        statement
          while_statement
            less
              var_ref	score
              literal
                number_literal	85
            block
              statement
                expression_statement
                  assign
                    var_ref	score
                    =
                    add
                      var_ref	score
                      literal
                        number_literal	1
        statement
          expression_statement
            call
              var_ref	print
              argument_list
                var_ref	score
        statement
          expression_statement
            call
              var_ref	f
              argument_list
                call
                  var_ref	g
                  argument_list
                    var_ref	x
        statement
          expression_statement
            call
              var_ref	f
        statement
          expression_statement
            assign
              var_ref	a
              =
              index
                var_ref	b
                array_access
                  literal
                    number_literal	43

======================== AST ========================
Program
└─ entries: list
   └─ [0]: FunctionDefinition
      ├─ return_type: Type
      │  ├─ type_id: 'void'
      │  ├─ inline: False
      │  ├─ static: False
      │  ├─ mut: False
      │  ├─ const: False
      │  └─ suffix: None
      ├─ name: Identifier
      │  └─ name: 'tinylang_example'
      ├─ parameters: list (empty)
      ├─ body: StatementBlock
      │  └─ statements: list
      │     ├─ [0]: Declaration
      │     │  ├─ type: Type
      │     │  │  ├─ type_id: 'int'
      │     │  │  ├─ inline: False
      │     │  │  ├─ static: False
      │     │  │  ├─ mut: False
      │     │  │  ├─ const: False
      │     │  │  └─ suffix: None
      │     │  ├─ id: Identifier
      │     │  │  └─ name: 'score'
      │     │  └─ initializer: Initializer
      │     │     └─ expression: Literal
      │     │        └─ value: 80
      │     ├─ [1]: Declaration
      │     │  ├─ type: Type
      │     │  │  ├─ type_id: 'int'
      │     │  │  ├─ inline: False
      │     │  │  ├─ static: False
      │     │  │  ├─ mut: False
      │     │  │  ├─ const: False
      │     │  │  └─ suffix: None
      │     │  ├─ id: Identifier
      │     │  │  └─ name: 'bonus'
      │     │  └─ initializer: Initializer
      │     │     └─ expression: Literal
      │     │        └─ value: 5
      │     ├─ [2]: ExpressionStatement
      │     │  └─ expression: FuncCall
      │     │     ├─ callee: VarRef
      │     │     │  └─ name: 'print'
      │     │     └─ args: ArgumentList
      │     │        └─ args: list
      │     │           └─ [0]: BinaryExpression
      │     │              ├─ operator: '+'
      │     │              ├─ left: VarRef
      │     │              │  └─ name: 'score'
      │     │              └─ right: BinaryExpression
      │     │                 ├─ operator: '*'
      │     │                 ├─ left: VarRef
      │     │                 │  └─ name: 'bonus'
      │     │                 └─ right: Literal
      │     │                    └─ value: 2
      │     ├─ [3]: IfStatement
      │     │  ├─ condition: BinaryExpression
      │     │  │  ├─ operator: '>='
      │     │  │  ├─ left: VarRef
      │     │  │  │  └─ name: 'score'
      │     │  │  └─ right: Literal
      │     │  │     └─ value: 60
      │     │  ├─ then_block: StatementBlock
      │     │  │  └─ statements: list
      │     │  │     └─ [0]: ExpressionStatement
      │     │  │        └─ expression: FuncCall
      │     │  │           ├─ callee: VarRef
      │     │  │           │  └─ name: 'print'
      │     │  │           └─ args: ArgumentList
      │     │  │              └─ args: list
      │     │  │                 └─ [0]: Literal
      │     │  │                    └─ value: 1
      │     │  └─ else_clause: ElseClause
      │     │     └─ body: StatementBlock
      │     │        └─ statements: list
      │     │           └─ [0]: ExpressionStatement
      │     │              └─ expression: FuncCall
      │     │                 ├─ callee: VarRef
      │     │                 │  └─ name: 'print'
      │     │                 └─ args: ArgumentList
      │     │                    └─ args: list
      │     │                       └─ [0]: Literal
      │     │                          └─ value: 0
      │     ├─ [4]: WhileStatement
      │     │  ├─ condition: BinaryExpression
      │     │  │  ├─ operator: '<'
      │     │  │  ├─ left: VarRef
      │     │  │  │  └─ name: 'score'
      │     │  │  └─ right: Literal
      │     │  │     └─ value: 85
      │     │  └─ body: StatementBlock
      │     │     └─ statements: list
      │     │        └─ [0]: ExpressionStatement
      │     │           └─ expression: AssignExpression
      │     │              ├─ operator: '='
      │     │              ├─ target: VarRef
      │     │              │  └─ name: 'score'
      │     │              └─ value: BinaryExpression
      │     │                 ├─ operator: '+'
      │     │                 ├─ left: VarRef
      │     │                 │  └─ name: 'score'
      │     │                 └─ right: Literal
      │     │                    └─ value: 1
      │     ├─ [5]: ExpressionStatement
      │     │  └─ expression: FuncCall
      │     │     ├─ callee: VarRef
      │     │     │  └─ name: 'print'
      │     │     └─ args: ArgumentList
      │     │        └─ args: list
      │     │           └─ [0]: VarRef
      │     │              └─ name: 'score'
      │     ├─ [6]: ExpressionStatement
      │     │  └─ expression: FuncCall
      │     │     ├─ callee: VarRef
      │     │     │  └─ name: 'f'
      │     │     └─ args: ArgumentList
      │     │        └─ args: list
      │     │           └─ [0]: FuncCall
      │     │              ├─ callee: VarRef
      │     │              │  └─ name: 'g'
      │     │              └─ args: ArgumentList
      │     │                 └─ args: list
      │     │                    └─ [0]: VarRef
      │     │                       └─ name: 'x'
      │     ├─ [7]: ExpressionStatement
      │     │  └─ expression: FuncCall
      │     │     ├─ callee: VarRef
      │     │     │  └─ name: 'f'
      │     │     └─ args: ArgumentList
      │     │        └─ args: list (empty)
      │     └─ [8]: ExpressionStatement
      │        └─ expression: AssignExpression
      │           ├─ operator: '='
      │           ├─ target: VarRef
      │           │  └─ name: 'a'
      │           └─ value: IndexExpression
      │              ├─ target: VarRef
      │              │  └─ name: 'b'
      │              └─ index: Literal
      │                 └─ value: 43
      └─ decorators: list (empty)

## Three meaningful differences from instructor demonstration
1. structures
2. decorators
3. qualified static types

## Test commands, results, revisions and known limitations





I don't know of any limitations because I'm making a pretty complex language and the search space for semantic errors is massive. It's also 2:30 and im tired so bear with me

## Attribution and originality statement
I developed and customized this project to match my M0–M2 design. Any instructor code patterns reused are identified and explained above.
