%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int line_num;
void yyerror(const char *s);

/* --- Symbol Table Structure --- */
struct symbol {
    char* name;
    int value;
};

#define MAX_SYMBOLS 512
struct symbol symbol_table[MAX_SYMBOLS];
int sym_count = 0;

int get_var(const char* name) {
    for (int i = 0; i < sym_count; i++) {
        if (strcmp(symbol_table[i].name, name) == 0) {
            return symbol_table[i].value;
        }
    }
    fprintf(stderr, "Arre Bhai! '%s' namer kono variable to dhoro koro ni!\n", name);
    return 0;
}

void set_var(const char* name, int val) {
    for (int i = 0; i < sym_count; i++) {
        if (strcmp(symbol_table[i].name, name) == 0) {
            symbol_table[i].value = val;
            return;
        }
    }
    if (sym_count < MAX_SYMBOLS) {
        symbol_table[sym_count].name = strdup(name);
        symbol_table[sym_count].value = val;
        sym_count++;
    } else {
        fprintf(stderr, "Arre Bhai! Symbol table full hoye geche!\n");
    }
}

/* --- AST Structure --- */
typedef enum {
    TYPE_BINOP,
    TYPE_VAR,
    TYPE_NUM,
    TYPE_ASSIGN,
    TYPE_PRINT,
    TYPE_IF,
    TYPE_WHILE,
    TYPE_BLOCK
} NodeType;

typedef struct Node {
    NodeType type;
    int val;
    char* id;
    int op;
    struct Node *left, *right, *next, *else_part;
} Node;

Node* create_node(NodeType type) {
    Node* n = (Node*)calloc(1, sizeof(Node));
    if (!n) {
        fprintf(stderr, "Fatal error: Memory allocation failed!\n");
        exit(1);
    }
    n->type = type;
    return n;
}

/* Function Prototype */
int eval(Node* n);
void execute_program(Node* root);
%}

%union {
    int num;
    char* id;
    struct Node* node;
}

%token <num> NUMBER
%token <id> IDENTIFIER
%token DHORO BOLO JODI NAWLE JOTOKHON
%token PLUS MINUS MUL DIV ASSIGN SEMICOLON LPAREN RPAREN LBRACE RBRACE EQ NE LE GE LT GT
%type <node> exp statement statement_list block

/* Precedence and Associativity */
%left EQ NE LE GE LT GT
%left PLUS MINUS
%left MUL DIV

%%
program:
    statement_list { execute_program($1); }
    | /* empty program */
    ;

statement_list:
    statement { $$ = $1; }
    | statement statement_list {
        if ($1) {
            $1->next = $2;
            $$ = $1;
        } else {
            $$ = $2;
        }
    }
    ;

statement:
    DHORO IDENTIFIER ASSIGN exp SEMICOLON {
        $$ = create_node(TYPE_ASSIGN);
        $$->id = $2;
        $$->left = $4;
    }
    | BOLO exp SEMICOLON {
        $$ = create_node(TYPE_PRINT);
        $$->left = $2;
    }
    | JODI LPAREN exp RPAREN block {
        $$ = create_node(TYPE_IF);
        $$->left = $3;
        $$->right = $5;
    }
    | JODI LPAREN exp RPAREN block NAWLE block {
        $$ = create_node(TYPE_IF);
        $$->left = $3;
        $$->right = $5;
        $$->else_part = $7;
    }
    | JOTOKHON LPAREN exp RPAREN block {
        $$ = create_node(TYPE_WHILE);
        $$->left = $3;
        $$->right = $5;
    }
    | SEMICOLON { $$ = NULL; }
    ;

block:
    LBRACE statement_list RBRACE {
        $$ = create_node(TYPE_BLOCK);
        $$->left = $2;
    }
    | LBRACE RBRACE {
        $$ = create_node(TYPE_BLOCK);
        $$->left = NULL;
    }
    ;

exp:
    NUMBER {
        $$ = create_node(TYPE_NUM);
        $$->val = $1;
    }
    | IDENTIFIER {
        $$ = create_node(TYPE_VAR);
        $$->id = $1;
    }
    | exp PLUS exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = PLUS;
        $$->left = $1;
        $$->right = $3;
    }
    | exp MINUS exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = MINUS;
        $$->left = $1;
        $$->right = $3;
    }
    | exp MUL exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = MUL;
        $$->left = $1;
        $$->right = $3;
    }
    | exp DIV exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = DIV;
        $$->left = $1;
        $$->right = $3;
    }
    | exp EQ exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = EQ;
        $$->left = $1;
        $$->right = $3;
    }
    | exp NE exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = NE;
        $$->left = $1;
        $$->right = $3;
    }
    | exp LE exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = LE;
        $$->left = $1;
        $$->right = $3;
    }
    | exp GE exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = GE;
        $$->left = $1;
        $$->right = $3;
    }
    | exp LT exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = LT;
        $$->left = $1;
        $$->right = $3;
    }
    | exp GT exp {
        $$ = create_node(TYPE_BINOP);
        $$->op = GT;
        $$->left = $1;
        $$->right = $3;
    }
    | LPAREN exp RPAREN {
        $$ = $2;
    }
    ;
%%

/* --- AST Evaluator & Interpreter Runtime --- */
int eval(Node* n) {
    if (!n) return 0;
    switch (n->type) {
        case TYPE_NUM:
            return n->val;
        case TYPE_VAR:
            return get_var(n->id);
        case TYPE_BINOP: {
            int l = eval(n->left);
            int r = eval(n->right);
            if (n->op == PLUS) return l + r;
            if (n->op == MINUS) return l - r;
            if (n->op == MUL) return l * r;
            if (n->op == DIV) {
                if (r == 0) {
                    fprintf(stderr, "Arre Bhai! Shunya (0) diye vag kora jay na!\n");
                    return 0;
                }
                return l / r;
            }
            if (n->op == EQ) return (l == r);
            if (n->op == NE) return (l != r);
            if (n->op == LE) return (l <= r);
            if (n->op == GE) return (l >= r);
            if (n->op == LT) return (l < r);
            if (n->op == GT) return (l > r);
            return 0;
        }
        case TYPE_ASSIGN:
            set_var(n->id, eval(n->left));
            return 0;
        case TYPE_PRINT:
            printf("%d\n", eval(n->left));
            fflush(stdout);
            return 0;
        case TYPE_BLOCK: {
            Node* cur = n->left;
            while (cur) {
                eval(cur);
                cur = cur->next;
            }
            return 0;
        }
        case TYPE_IF:
            if (eval(n->left)) {
                eval(n->right);
            } else if (n->else_part) {
                eval(n->else_part);
            }
            return 0;
        case TYPE_WHILE:
            while (eval(n->left)) {
                eval(n->right);
            }
            return 0;
    }
    return 0;
}

void execute_program(Node* root) {
    Node* cur = root;
    while (cur) {
        eval(cur);
        cur = cur->next;
    }
}

void yyerror(const char *s) {
    fprintf(stderr, "Arre Bhai! Syntax-e somossa peyechi (Line %d): %s\n", line_num, s);
}

int main() {
    return yyparse();
}
