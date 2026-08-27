%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int line_num;
void yyerror(const char *s);

/* --- Value Representation (Int / String) --- */
typedef enum {
    VAL_INT,
    VAL_STR
} ValType;

typedef struct Value {
    ValType type;
    int num;
    char* str;
} Value;

/* --- Symbol Table Structure --- */
struct symbol {
    char* name;
    Value val;
};

#define MAX_SYMBOLS 512
struct symbol symbol_table[MAX_SYMBOLS];
int sym_count = 0;

Value get_var(const char* name) {
    for (int i = 0; i < sym_count; i++) {
        if (strcmp(symbol_table[i].name, name) == 0) {
            return symbol_table[i].val;
        }
    }
    fprintf(stderr, "Arre Bhai! '%s' namer kono variable to dhoro koro ni!\n", name);
    Value v;
    v.type = VAL_INT;
    v.num = 0;
    v.str = NULL;
    return v;
}

void set_var(const char* name, Value val) {
    for (int i = 0; i < sym_count; i++) {
        if (strcmp(symbol_table[i].name, name) == 0) {
            symbol_table[i].val = val;
            return;
        }
    }
    if (sym_count < MAX_SYMBOLS) {
        symbol_table[sym_count].name = strdup(name);
        symbol_table[sym_count].val = val;
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
    TYPE_STR,
    TYPE_ASSIGN,
    TYPE_PRINT,
    TYPE_IF,
    TYPE_WHILE,
    TYPE_BLOCK
} NodeType;

typedef struct Node {
    NodeType type;
    int val;
    char* str_val;
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

/* Function Prototypes */
Value eval(Node* n);
void execute_program(Node* root);
%}

%union {
    int num;
    char* id;
    char* str;
    struct Node* node;
}

%token <num> NUMBER
%token <str> STRING
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
    | STRING {
        $$ = create_node(TYPE_STR);
        $$->str_val = $1;
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
Value eval(Node* n) {
    Value res;
    res.type = VAL_INT;
    res.num = 0;
    res.str = NULL;

    if (!n) return res;

    switch (n->type) {
        case TYPE_NUM:
            res.type = VAL_INT;
            res.num = n->val;
            return res;

        case TYPE_STR:
            res.type = VAL_STR;
            res.str = n->str_val ? n->str_val : "";
            return res;

        case TYPE_VAR:
            return get_var(n->id);

        case TYPE_BINOP: {
            Value l = eval(n->left);
            Value r = eval(n->right);

            // Handle string operations (concatenation & comparison)
            if (l.type == VAL_STR || r.type == VAL_STR) {
                if (n->op == PLUS) {
                    char buf1[64], buf2[64];
                    const char* s1 = (l.type == VAL_STR) ? l.str : (sprintf(buf1, "%d", l.num), buf1);
                    const char* s2 = (r.type == VAL_STR) ? r.str : (sprintf(buf2, "%d", r.num), buf2);
                    char* concat = (char*)malloc(strlen(s1) + strlen(s2) + 1);
                    strcpy(concat, s1);
                    strcat(concat, s2);
                    res.type = VAL_STR;
                    res.str = concat;
                    return res;
                }
                if (n->op == EQ) {
                    res.type = VAL_INT;
                    if (l.type == VAL_STR && r.type == VAL_STR) res.num = (strcmp(l.str, r.str) == 0);
                    else res.num = 0;
                    return res;
                }
                if (n->op == NE) {
                    res.type = VAL_INT;
                    if (l.type == VAL_STR && r.type == VAL_STR) res.num = (strcmp(l.str, r.str) != 0);
                    else res.num = 1;
                    return res;
                }
            }

            int lv = l.num;
            int rv = r.num;
            res.type = VAL_INT;
            if (n->op == PLUS) res.num = lv + rv;
            else if (n->op == MINUS) res.num = lv - rv;
            else if (n->op == MUL) res.num = lv * rv;
            else if (n->op == DIV) {
                if (rv == 0) {
                    fprintf(stderr, "Arre Bhai! Shunya (0) diye vag kora jay na!\n");
                    res.num = 0;
                } else {
                    res.num = lv / rv;
                }
            }
            else if (n->op == EQ) res.num = (lv == rv);
            else if (n->op == NE) res.num = (lv != rv);
            else if (n->op == LE) res.num = (lv <= rv);
            else if (n->op == GE) res.num = (lv >= rv);
            else if (n->op == LT) res.num = (lv < rv);
            else if (n->op == GT) res.num = (lv > rv);
            return res;
        }

        case TYPE_ASSIGN:
            set_var(n->id, eval(n->left));
            return res;

        case TYPE_PRINT: {
            Value v = eval(n->left);
            if (v.type == VAL_STR) {
                printf("%s\n", v.str ? v.str : "");
            } else {
                printf("%d\n", v.num);
            }
            fflush(stdout);
            return res;
        }

        case TYPE_BLOCK: {
            Node* cur = n->left;
            while (cur) {
                eval(cur);
                cur = cur->next;
            }
            return res;
        }

        case TYPE_IF: {
            Value cond = eval(n->left);
            int is_true = (cond.type == VAL_STR) ? (cond.str && strlen(cond.str) > 0) : (cond.num != 0);
            if (is_true) {
                eval(n->right);
            } else if (n->else_part) {
                eval(n->else_part);
            }
            return res;
        }

        case TYPE_WHILE: {
            while (1) {
                Value cond = eval(n->left);
                int is_true = (cond.type == VAL_STR) ? (cond.str && strlen(cond.str) > 0) : (cond.num != 0);
                if (!is_true) break;
                eval(n->right);
            }
            return res;
        }
    }
    return res;
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
