import os
import sys

def create_project():
    # Detect target base path
    # If the current working directory name is already 'BanglaLang', write directly into current directory
    # Otherwise, create/use 'BanglaLang' directory.
    cwd = os.getcwd()
    if os.path.basename(os.path.abspath(cwd)).lower() == "banglalang":
        base_dir = "."
    else:
        base_dir = "BanglaLang"

    directories = [
        os.path.join(base_dir, "core"),
        os.path.join(base_dir, "backend"),
        os.path.join(base_dir, "frontend"),
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"[+] Directory ensured: {directory}")

    # =========================================================================
    # 1. CORE: lexer.l
    # =========================================================================
    lexer_content = r'''%{
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "parser.tab.h"

void yyerror(const char *s);
int line_num = 1;
%}

%option noyywrap

%%
"dhoro"         { return DHORO; }
"bolo"          { return BOLO; }
"jodi"          { return JODI; }
"nawle"         { return NAWLE; }
"jotokhon"      { return JOTOKHON; }
"kaaj"          { return KAAJ; }
"ferot"         { return FEROT; }
"nao"           { return NAO; }
"shotto"        { return SHOTTO; }
"mittha"        { return MITTHA; }
"talika"        { return TALIKA; }
"jonno"         { return JONNO; }

[0-9]+\.[0-9]+  { yylval.fnum = atof(yytext); return FLOAT_NUMBER; }
[0-9]+          { yylval.num = atoi(yytext); return NUMBER; }

\"([^\"\\]|\\.)*\" {
    int len = strlen(yytext);
    char *buf = (char *)malloc(len - 1);
    if (len > 2) {
        strncpy(buf, yytext + 1, len - 2);
        buf[len - 2] = '\0';
    } else {
        buf[0] = '\0';
    }
    yylval.str = buf;
    return STRING;
}

[a-zA-Z_][a-zA-Z0-9_]* { yylval.id = strdup(yytext); return IDENTIFIER; }

"=="            { return EQ; }
"!="            { return NE; }
"<="            { return LE; }
">="            { return GE; }
"<"             { return LT; }
">"             { return GT; }
"="             { return ASSIGN; }
"+"             { return PLUS; }
"-"             { return MINUS; }
"*"             { return MUL; }
"/"             { return DIV; }

"{"             { return LBRACE; }
"}"             { return RBRACE; }
"("             { return LPAREN; }
")"             { return RPAREN; }
";"             { return SEMICOLON; }
","             { return COMMA; }
"["             { return LBRACKET; }
"]"             { return RBRACKET; }

[ \t\r]+        { /* ignore whitespace */ }
\n              { line_num++; }

"//".*          { /* ignore single-line comments */ }

.               { fprintf(stderr, "Arre Bhai! Ota ki chilo? Unknown character (Line %d): '%s'\n", line_num, yytext); }
%%
'''

    # =========================================================================
    # 2. CORE: parser.y
    # =========================================================================
    parser_content = r'''%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int yylex();
extern int line_num;
void yyerror(const char *s);

/* --- Value Representation (Int / Float / String / Array) --- */
typedef enum {
    VAL_INT,
    VAL_FLOAT,
    VAL_STR,
    VAL_ARR
} ValType;

typedef struct Value {
    ValType type;
    int num;
    double fnum;
    char* str;
    struct Value* arr_elements;
    int arr_size;
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
    for (int i = sym_count - 1; i >= 0; i--) {
        if (strcmp(symbol_table[i].name, name) == 0) {
            return symbol_table[i].val;
        }
    }
    fprintf(stderr, "Arre Bhai! '%s' namer kono variable to dhoro koro ni!\n", name);
    Value v;
    v.type = VAL_INT;
    v.num = 0;
    v.fnum = 0.0;
    v.str = NULL;
    v.arr_elements = NULL;
    v.arr_size = 0;
    return v;
}

void set_var(const char* name, Value val) {
    for (int i = sym_count - 1; i >= 0; i--) {
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

/* --- Parameter List for Functions --- */
struct param_node {
    char* name;
    struct param_node* next;
};

/* --- AST Structure --- */
typedef enum {
    TYPE_BINOP,
    TYPE_VAR,
    TYPE_NUM,
    TYPE_FLOAT,
    TYPE_STR,
    TYPE_ASSIGN,
    TYPE_PRINT,
    TYPE_IF,
    TYPE_WHILE,
    TYPE_FOR,
    TYPE_BLOCK,
    TYPE_FUNC_DECL,
    TYPE_FUNC_CALL,
    TYPE_RETURN,
    TYPE_INPUT,
    TYPE_ARRAY_LITERAL,
    TYPE_ARRAY_INDEX
} NodeType;

typedef struct Node {
    NodeType type;
    int val;
    double fval;
    char* str_val;
    char* id;
    int op;
    struct param_node* params;
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

/* --- Function Registry --- */
struct func_symbol {
    char* name;
    struct param_node* params;
    Node* body;
};

#define MAX_FUNCS 128
struct func_symbol func_table[MAX_FUNCS];
int func_count = 0;

void add_function(const char* name, struct param_node* params, Node* body) {
    for (int i = 0; i < func_count; i++) {
        if (strcmp(func_table[i].name, name) == 0) {
            func_table[i].params = params;
            func_table[i].body = body;
            return;
        }
    }
    if (func_count < MAX_FUNCS) {
        func_table[func_count].name = strdup(name);
        func_table[func_count].params = params;
        func_table[func_count].body = body;
        func_count++;
    }
}

struct func_symbol* get_function(const char* name) {
    for (int i = 0; i < func_count; i++) {
        if (strcmp(func_table[i].name, name) == 0) return &func_table[i];
    }
    return NULL;
}

/* Function Prototypes */
Value eval(Node* n);
void execute_program(Node* root);
void print_value(Value v);

int is_returning = 0;
Value return_val;
%}

%union {
    int num;
    double fnum;
    char* id;
    char* str;
    struct Node* node;
    struct param_node* param;
}

%token <num> NUMBER
%token <fnum> FLOAT_NUMBER
%token <str> STRING
%token <id> IDENTIFIER
%token DHORO BOLO JODI NAWLE JOTOKHON KAAJ FEROT NAO SHOTTO MITTHA TALIKA JONNO
%token PLUS MINUS MUL DIV ASSIGN SEMICOLON LPAREN RPAREN LBRACE RBRACE EQ NE LE GE LT GT COMMA LBRACKET RBRACKET
%type <node> exp statement statement_list block func_def arg_list
%type <param> param_list

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
    | DHORO TALIKA IDENTIFIER ASSIGN exp SEMICOLON {
        $$ = create_node(TYPE_ASSIGN);
        $$->id = $3;
        $$->left = $5;
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
    | JONNO LPAREN statement exp SEMICOLON statement RPAREN block {
        $$ = create_node(TYPE_FOR);
        $$->left = $3;
        $$->right = $4;
        $$->else_part = $6;
        $$->next = $8;
    }
    | func_def { $$ = $1; }
    | FEROT exp SEMICOLON {
        $$ = create_node(TYPE_RETURN);
        $$->left = $2;
    }
    | exp SEMICOLON { $$ = $1; }
    | SEMICOLON { $$ = NULL; }
    ;

func_def:
    KAAJ IDENTIFIER LPAREN param_list RPAREN block {
        $$ = create_node(TYPE_FUNC_DECL);
        $$->id = $2;
        $$->params = $4;
        $$->right = $6;
    }
    | KAAJ IDENTIFIER LPAREN RPAREN block {
        $$ = create_node(TYPE_FUNC_DECL);
        $$->id = $2;
        $$->params = NULL;
        $$->right = $5;
    }
    ;

param_list:
    IDENTIFIER {
        struct param_node* p = (struct param_node*)calloc(1, sizeof(struct param_node));
        p->name = $1;
        $$ = p;
    }
    | IDENTIFIER COMMA param_list {
        struct param_node* p = (struct param_node*)calloc(1, sizeof(struct param_node));
        p->name = $1;
        p->next = $3;
        $$ = p;
    }
    ;

arg_list:
    exp {
        $$ = $1;
    }
    | exp COMMA arg_list {
        $1->next = $3;
        $$ = $1;
    }
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
    | FLOAT_NUMBER {
        $$ = create_node(TYPE_FLOAT);
        $$->fval = $1;
    }
    | STRING {
        $$ = create_node(TYPE_STR);
        $$->str_val = $1;
    }
    | SHOTTO {
        $$ = create_node(TYPE_NUM);
        $$->val = 1;
    }
    | MITTHA {
        $$ = create_node(TYPE_NUM);
        $$->val = 0;
    }
    | LBRACKET arg_list RBRACKET {
        $$ = create_node(TYPE_ARRAY_LITERAL);
        $$->left = $2;
    }
    | LBRACKET RBRACKET {
        $$ = create_node(TYPE_ARRAY_LITERAL);
        $$->left = NULL;
    }
    | IDENTIFIER LBRACKET exp RBRACKET {
        $$ = create_node(TYPE_ARRAY_INDEX);
        $$->id = $1;
        $$->left = $3;
    }
    | IDENTIFIER {
        $$ = create_node(TYPE_VAR);
        $$->id = $1;
    }
    | IDENTIFIER LPAREN arg_list RPAREN {
        $$ = create_node(TYPE_FUNC_CALL);
        $$->id = $1;
        $$->left = $3;
    }
    | IDENTIFIER LPAREN RPAREN {
        $$ = create_node(TYPE_FUNC_CALL);
        $$->id = $1;
        $$->left = NULL;
    }
    | NAO LPAREN RPAREN {
        $$ = create_node(TYPE_INPUT);
        $$->left = NULL;
    }
    | NAO LPAREN STRING RPAREN {
        $$ = create_node(TYPE_INPUT);
        $$->str_val = $3;
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

void print_value(Value v) {
    if (v.type == VAL_STR) {
        printf("%s", v.str ? v.str : "");
    } else if (v.type == VAL_FLOAT) {
        printf("%g", v.fnum);
    } else if (v.type == VAL_ARR) {
        printf("[");
        for (int i = 0; i < v.arr_size; i++) {
            print_value(v.arr_elements[i]);
            if (i < v.arr_size - 1) printf(", ");
        }
        printf("]");
    } else {
        printf("%d", v.num);
    }
}

/* --- AST Evaluator & Interpreter Runtime --- */
Value eval(Node* n) {
    Value res;
    res.type = VAL_INT;
    res.num = 0;
    res.fnum = 0.0;
    res.str = NULL;
    res.arr_elements = NULL;
    res.arr_size = 0;

    if (!n || is_returning) return res;

    switch (n->type) {
        case TYPE_NUM:
            res.type = VAL_INT;
            res.num = n->val;
            return res;

        case TYPE_FLOAT:
            res.type = VAL_FLOAT;
            res.fnum = n->fval;
            return res;

        case TYPE_STR:
            res.type = VAL_STR;
            res.str = n->str_val ? n->str_val : "";
            return res;

        case TYPE_ARRAY_LITERAL: {
            int count = 0;
            Node* cur = n->left;
            while (cur) {
                count++;
                cur = cur->next;
            }
            res.type = VAL_ARR;
            res.arr_size = count;
            if (count > 0) {
                res.arr_elements = (Value*)calloc(count, sizeof(Value));
                cur = n->left;
                int idx = 0;
                while (cur) {
                    res.arr_elements[idx++] = eval(cur);
                    cur = cur->next;
                }
            }
            return res;
        }

        case TYPE_ARRAY_INDEX: {
            Value arr = get_var(n->id);
            Value idx_val = eval(n->left);
            int idx = idx_val.num;
            if (arr.type == VAL_ARR) {
                if (idx >= 0 && idx < arr.arr_size) {
                    return arr.arr_elements[idx];
                } else {
                    fprintf(stderr, "Arre Bhai! Talika (Array) index range-er baire! Index: %d, Size: %d\n", idx, arr.arr_size);
                }
            } else {
                fprintf(stderr, "Arre Bhai! '%s' kono talika (array) noy!\n", n->id);
            }
            return res;
        }

        case TYPE_VAR:
            return get_var(n->id);

        case TYPE_FUNC_DECL:
            add_function(n->id, n->params, n->right);
            return res;

        case TYPE_RETURN:
            return_val = eval(n->left);
            is_returning = 1;
            return return_val;

        case TYPE_INPUT: {
            if (n->str_val) {
                printf("%s", n->str_val);
                fflush(stdout);
            }
            char buf[256];
            if (fgets(buf, sizeof(buf), stdin)) {
                int len = strlen(buf);
                if (len > 0 && buf[len - 1] == '\n') buf[len - 1] = '\0';
                if (strchr(buf, '.')) {
                    res.type = VAL_FLOAT;
                    res.fnum = atof(buf);
                } else if (strlen(buf) > 0 && (buf[0] >= '0' && buf[0] <= '9')) {
                    res.type = VAL_INT;
                    res.num = atoi(buf);
                } else {
                    res.type = VAL_STR;
                    res.str = strdup(buf);
                }
            }
            return res;
        }

        case TYPE_FUNC_CALL: {
            struct func_symbol* fn = get_function(n->id);
            if (!fn) {
                fprintf(stderr, "Arre Bhai! '%s' namer kono kaaj (function) to banawni!\n", n->id);
                return res;
            }

            int saved_sym_count = sym_count;
            struct param_node* p = fn->params;
            Node* arg = n->left;
            while (p && arg) {
                Value arg_val = eval(arg);
                set_var(p->name, arg_val);
                p = p->next;
                arg = arg->next;
            }

            int prev_returning = is_returning;
            is_returning = 0;
            eval(fn->body);

            Value fn_res = return_val;
            is_returning = prev_returning;
            sym_count = saved_sym_count;
            return fn_res;
        }

        case TYPE_BINOP: {
            Value l = eval(n->left);
            Value r = eval(n->right);

            if (l.type == VAL_STR || r.type == VAL_STR) {
                if (n->op == PLUS) {
                    char buf1[64], buf2[64];
                    const char* s1 = (l.type == VAL_STR) ? l.str : 
                                    (l.type == VAL_FLOAT ? (sprintf(buf1, "%g", l.fnum), buf1) : (sprintf(buf1, "%d", l.num), buf1));
                    const char* s2 = (r.type == VAL_STR) ? r.str : 
                                    (r.type == VAL_FLOAT ? (sprintf(buf2, "%g", r.fnum), buf2) : (sprintf(buf2, "%d", r.num), buf2));
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

            if (l.type == VAL_FLOAT || r.type == VAL_FLOAT) {
                double lv = (l.type == VAL_FLOAT) ? l.fnum : l.num;
                double rv = (r.type == VAL_FLOAT) ? r.fnum : r.num;
                if (n->op == PLUS) { res.type = VAL_FLOAT; res.fnum = lv + rv; }
                else if (n->op == MINUS) { res.type = VAL_FLOAT; res.fnum = lv - rv; }
                else if (n->op == MUL) { res.type = VAL_FLOAT; res.fnum = lv * rv; }
                else if (n->op == DIV) {
                    if (rv == 0.0) {
                        fprintf(stderr, "Arre Bhai! Shunya (0) diye vag kora jay na!\n");
                        res.type = VAL_FLOAT; res.fnum = 0.0;
                    } else {
                        res.type = VAL_FLOAT; res.fnum = lv / rv;
                    }
                }
                else if (n->op == EQ) { res.type = VAL_INT; res.num = (lv == rv); }
                else if (n->op == NE) { res.type = VAL_INT; res.num = (lv != rv); }
                else if (n->op == LE) { res.type = VAL_INT; res.num = (lv <= rv); }
                else if (n->op == GE) { res.type = VAL_INT; res.num = (lv >= rv); }
                else if (n->op == LT) { res.type = VAL_INT; res.num = (lv < rv); }
                else if (n->op == GT) { res.type = VAL_INT; res.num = (lv > rv); }
                return res;
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
            print_value(v);
            printf("\n");
            fflush(stdout);
            return res;
        }

        case TYPE_BLOCK: {
            Node* cur = n->left;
            while (cur && !is_returning) {
                eval(cur);
                cur = cur->next;
            }
            return res;
        }

        case TYPE_IF: {
            Value cond = eval(n->left);
            int is_true = (cond.type == VAL_STR) ? (cond.str && strlen(cond.str) > 0) : 
                          (cond.type == VAL_FLOAT ? (cond.fnum != 0.0) : (cond.num != 0));
            if (is_true) {
                eval(n->right);
            } else if (n->else_part) {
                eval(n->else_part);
            }
            return res;
        }

        case TYPE_WHILE: {
            while (!is_returning) {
                Value cond = eval(n->left);
                int is_true = (cond.type == VAL_STR) ? (cond.str && strlen(cond.str) > 0) : 
                              (cond.type == VAL_FLOAT ? (cond.fnum != 0.0) : (cond.num != 0));
                if (!is_true) break;
                eval(n->right);
            }
            return res;
        }

        case TYPE_FOR: {
            if (n->left) eval(n->left);
            while (!is_returning) {
                Value cond = eval(n->right);
                int is_true = (cond.type == VAL_STR) ? (cond.str && strlen(cond.str) > 0) : 
                              (cond.type == VAL_FLOAT ? (cond.fnum != 0.0) : (cond.num != 0));
                if (!is_true) break;
                if (n->next) eval(n->next);
                if (n->else_part) eval(n->else_part);
            }
            return res;
        }
    }
    return res;
}

void execute_program(Node* root) {
    Node* cur = root;
    while (cur && !is_returning) {
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
'''

    # =========================================================================
    # 3. CORE: Makefile (Windows compatible)
    # =========================================================================
    makefile_content = r'''CC = gcc
LEX = flex
YACC = bison
CFLAGS = -Wall

all: banglalang.exe

banglalang.exe: lex.yy.c parser.tab.c
	$(CC) $(CFLAGS) lex.yy.c parser.tab.c -o banglalang.exe

lex.yy.c: lexer.l parser.tab.h
	$(LEX) lexer.l

parser.tab.c parser.tab.h: parser.y
	$(YACC) -d parser.y

clean:
	if exist banglalang.exe del /q /f banglalang.exe
	if exist lex.yy.c del /q /f lex.yy.c
	if exist parser.tab.c del /q /f parser.tab.c
	if exist parser.tab.h del /q /f parser.tab.h
'''

    # =========================================================================
    # 4. BACKEND: package.json
    # =========================================================================
    package_json = r'''{
  "name": "banglalang-backend",
  "version": "1.0.0",
  "description": "Express Backend API for BanglaLang Compiler Engine",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "cors": "^2.8.5"
  }
}
'''

    # =========================================================================
    # 5. BACKEND: server.js
    # =========================================================================
    server_js = r'''const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json({ limit: '5mb' }));

// Locate the banglalang.exe binary with robust fallback paths
function getBinaryPath() {
    const candidates = [
        path.join(__dirname, '..', 'core', 'banglalang.exe'),
        path.join(__dirname, 'build', 'banglalang.exe'),
        path.join(__dirname, 'core', 'banglalang.exe'),
        path.join(process.cwd(), 'core', 'banglalang.exe'),
        path.join(process.cwd(), 'banglalang.exe')
    ];
    for (const p of candidates) {
        if (fs.existsSync(p)) return p;
    }
    return candidates[0]; // fallback
}

// Health check endpoint
app.get('/api/health', (req, res) => {
    const binary = getBinaryPath();
    const isCompiled = fs.existsSync(binary);
    res.json({
        status: 'online',
        compilerReady: isCompiled,
        binaryPath: binary,
        timestamp: new Date().toISOString()
    });
});

// Run Code Endpoint
app.post('/api/run', (req, res) => {
    const { code } = req.body;
    if (typeof code !== 'string') {
        return res.status(400).json({
            output: '',
            error: 'Arre Bhai! Valid code payload pathan (string required).'
        });
    }

    const BINARY_PATH = getBinaryPath();

    if (!fs.existsSync(BINARY_PATH)) {
        return res.status(500).json({
            output: '',
            error: `BanglaLang compiler binary paoa jayni at: "${BINARY_PATH}". Kripoya "core" folder-e giye "make" command run korun.`
        });
    }

    const startTime = Date.now();
    let stdoutData = '';
    let stderrData = '';
    let isFinished = false;

    // Spawn child process with direct stdin stream and --ast flag
    const child = spawn(BINARY_PATH, ['--ast'], {
        windowsHide: true
    });

    // Timeout safety (5 seconds max execution)
    const timer = setTimeout(() => {
        if (!isFinished) {
            isFinished = true;
            child.kill();
            return res.json({
                output: stdoutData,
                ast: null,
                error: 'Execution Timed Out (5s limit exceeded). Infinite loop sombhoboto!',
                executionTimeMs: Date.now() - startTime
            });
        }
    }, 5000);

    child.stdout.on('data', (data) => {
        stdoutData += data.toString('utf-8');
    });

    child.stderr.on('data', (data) => {
        stderrData += data.toString('utf-8');
    });

    child.on('error', (err) => {
        if (isFinished) return;
        isFinished = true;
        clearTimeout(timer);
        res.json({
            output: stdoutData,
            ast: null,
            error: `Compiler execution error: ${err.message}`,
            executionTimeMs: Date.now() - startTime
        });
    });

    child.on('close', (codeStatus) => {
        if (isFinished) return;
        isFinished = true;
        clearTimeout(timer);

        let astData = null;
        const astMatch = stdoutData.match(/---AST_JSON_START---\s*([\s\S]*?)\s*---AST_JSON_END---/);
        if (astMatch) {
            try {
                astData = JSON.parse(astMatch[1]);
            } catch (e) {}
            stdoutData = stdoutData.replace(/---AST_JSON_START---\s*[\s\S]*?\s*---AST_JSON_END---\s*/, '');
        }

        res.json({
            output: stdoutData,
            ast: astData,
            error: stderrData,
            exitCode: codeStatus,
            executionTimeMs: Date.now() - startTime
        });
    });

    // Write BanglaLang code into compiler stdin and close stream
    try {
        child.stdin.write(code);
        child.stdin.end();
    } catch (writeErr) {
        if (!isFinished) {
            isFinished = true;
            clearTimeout(timer);
            res.json({
                output: '',
                error: `Stdin write error: ${writeErr.message}`,
                executionTimeMs: Date.now() - startTime
            });
        }
    }
});

app.listen(PORT, () => {
    console.log(`=========================================`);
    console.log(`🚀 BanglaLang Backend running on port ${PORT}`);
    console.log(`📌 Compiler Binary: ${getBinaryPath()}`);
    console.log(`=========================================`);
});
'''

    # =========================================================================
    # 6. FRONTEND: index.html (Cyber Bento Dashboard with Monaco Editor)
    # =========================================================================
    frontend_html = r'''<!DOCTYPE html>
<html lang="bn" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BanglaLang — Cyber IDE & Playground</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Hind+Siliguri:wght@400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs/loader.min.js"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', '"Hind Siliguri"', 'sans-serif'],
                        mono: ['"Fira Code"', 'monospace'],
                        bengali: ['"Hind Siliguri"', 'sans-serif']
                    },
                    colors: {
                        cyber: {
                            bg: '#07090e',
                            card: '#0d1117',
                            border: '#1e293b',
                            accent: '#10b981',
                            glow: '#06b6d4',
                            orange: '#f97316'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-color: #05070c;
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(16, 185, 129, 0.05) 0%, transparent 40%),
                radial-gradient(circle at 85% 85%, rgba(6, 182, 212, 0.05) 0%, transparent 40%);
        }
        .bento-card {
            background: rgba(13, 17, 23, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.07);
            transition: all 0.2s ease-in-out;
        }
        .bento-card:hover {
            border-color: rgba(16, 185, 129, 0.25);
        }
        .terminal-glow {
            box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.9);
        }
        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #07090e; }
        ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #334155; }
        
        #editorContainer {
            font-family: 'Fira Code', 'Consolas', 'Courier New', monospace !important;
            letter-spacing: 0px !important;
        }
    </style>
</head>
<body class="text-slate-100 h-screen flex flex-col font-sans overflow-hidden bg-[#05070c]">
    <!-- Header -->
    <header class="h-13 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur px-5 flex items-center justify-between shrink-0 z-10">
        <div class="flex items-center gap-3">
            <button id="sidebarToggleBtn" onclick="toggleLeftSidebar()" class="px-3 py-1.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 text-slate-300 hover:text-emerald-400 font-mono text-xs transition flex items-center gap-2 shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" /></svg>
                <span id="sidebarToggleText" class="font-bold">সাইডবার বন্ধ</span>
            </button>
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500 via-teal-600 to-cyan-600 flex items-center justify-center font-bold text-white shadow-lg shadow-emerald-500/20 font-bengali text-base">
                    বাং
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-base font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">BanglaLang</h1>
                        <span class="text-[9px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">v1.0 Compiler</span>
                    </div>
                    <p class="text-[11px] text-slate-500">বাংলা প্রোগ্রামিং ল্যাঙ্গুয়েজ ক্লাউড প্লেগ্রাউন্ড</p>
                </div>
            </div>
        </div>

        <!-- Center Controls -->
        <div class="flex items-center gap-3">
            <div id="backendStatusBadge" class="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-slate-900 border border-slate-800 text-slate-400">
                <span id="statusDot" class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
                <span id="statusText">Checking Backend...</span>
            </div>
            <button id="runBtn" class="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold px-5 py-1.5 rounded-xl text-xs transition-all duration-200 flex items-center gap-2 shadow-lg shadow-emerald-500/25 active:scale-95">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                <span>কোড রান করো (Ctrl+Enter)</span>
            </button>
        </div>
    </header>

    <!-- Main Bento Split Layout -->
    <main class="flex-1 h-[calc(100vh-3.25rem)] p-3 flex items-stretch gap-3 overflow-hidden min-h-0 relative" id="mainContainer">
        <!-- Left Sidebar / Snippets & Docs Bento -->
        <div id="leftPanel" class="w-76 shrink-0 flex flex-col gap-2.5 overflow-hidden transition-all duration-200">
            <!-- Snippets Card -->
            <div class="bento-card rounded-2xl p-3 flex flex-col shrink-0">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono">কোড এক্সাম্পল</span>
                    <span class="text-[10px] text-emerald-400 font-mono">Templates</span>
                </div>
                <div class="grid grid-cols-1 gap-1.5">
                    <button onclick="loadSnippet('vars')" class="snippet-btn text-left text-xs p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">১. ভ্যারিয়েবল ও গণিত</span>
                        <span class="text-[10px] font-mono text-slate-500">dhoro / bolo</span>
                    </button>
                    <button onclick="loadSnippet('logic')" class="snippet-btn text-left text-xs p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">২. শর্ত যাচাই (If-Else)</span>
                        <span class="text-[10px] font-mono text-slate-500">jodi / nawle</span>
                    </button>
                    <button onclick="loadSnippet('loop')" class="snippet-btn text-left text-xs p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">৩. লুপ বা পুনরাবৃত্তি</span>
                        <span class="text-[10px] font-mono text-slate-500">jotokhon</span>
                    </button>
                    <button onclick="loadSnippet('complex')" class="snippet-btn text-left text-xs p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">৪. লজিক ও ফ্যাক্টোরিয়াল</span>
                        <span class="text-[10px] font-mono text-slate-500">Full Demo</span>
                    </button>
                    <button onclick="loadSnippet('func')" class="snippet-btn text-left text-xs p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">৫. ফাংশন ও ফ্লট সংখ্যা</span>
                        <span class="text-[10px] font-mono text-slate-500">kaaj / ferot</span>
                    </button>
                    <button onclick="loadSnippet('array')" class="snippet-btn text-left text-xs p-2 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">৬. তালিকা ও For-Loop</span>
                        <span class="text-[10px] font-mono text-slate-500">talika / jonno</span>
                    </button>
                </div>
            </div>

            <!-- Syntax Reference Bento -->
            <div class="bento-card rounded-2xl p-3 flex-1 overflow-y-auto min-h-0">
                <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 font-mono mb-2">সিনট্যাক্স সহায়িকা (Cheat Sheet)</div>
                <div class="space-y-2 text-xs">
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-emerald-400 font-semibold">dhoro x = 10;</div>
                        <div class="text-slate-400 text-[10px]">ভ্যারিয়েবল ডিফাইন করতে ব্যবহৃত হয়</div>
                    </div>
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-cyan-400 font-semibold">bolo x + 5;</div>
                        <div class="text-slate-400 text-[10px]">স্ক্রিনে আউটপুট প্রিন্ট করে</div>
                    </div>
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-amber-400 font-semibold">jodi (a == b) { ... } nawle { ... }</div>
                        <div class="text-slate-400 text-[10px]">শর্তাধীন লজিক্যাল ব্রাঞ্চিং</div>
                    </div>
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-indigo-400 font-semibold">jotokhon (x > 0) { ... }</div>
                        <div class="text-slate-400 text-[10px]">শর্ত পূরণ হওয়া পর্যন্ত লুপ চলে</div>
                    </div>
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-pink-400 font-semibold">kaaj fn(a, b) { ferot a + b; }</div>
                        <div class="text-slate-400 text-[10px]">কাস্টম ফাংশন ডিক্লেয়ারেশন ও রিটার্ন</div>
                    </div>
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-violet-400 font-semibold">dhoro flag = shotto;</div>
                        <div class="text-slate-400 text-[10px]">বুলিয়ান কন্সট্যান্ট (shotto/mittha)</div>
                    </div>
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-amber-400 font-semibold">dhoro talika arr = [10, 20];</div>
                        <div class="text-slate-400 text-[10px]">অ্যারে / তালিকা ডাটা স্ট্রাকচার</div>
                    </div>
                    <div class="p-1.5 px-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-emerald-400 font-semibold">jonno (dhoro i=0; i&lt;3; dhoro i=i+1;)</div>
                        <div class="text-slate-400 text-[10px]">নির্দিষ্ট লুপ / For-Loop</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Middle Workspace (Editor + Bottom Output Drawer) -->
        <div id="middleWorkspace" class="flex-1 flex flex-col min-w-0 min-h-0 overflow-hidden">
            <!-- Middle Editor Bento -->
            <div id="editorPanel" class="flex-1 flex flex-col bento-card rounded-2xl overflow-hidden min-w-[280px] min-h-[150px]">
                <!-- Editor Top Bar -->
                <div class="h-9 bg-slate-950/80 border-b border-slate-800 px-3.5 flex items-center justify-between shrink-0">
                    <div class="flex items-center gap-2">
                        <span class="w-2.5 h-2.5 rounded-full bg-red-500/80 inline-block"></span>
                        <span class="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block"></span>
                        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block"></span>
                        <span class="ml-2 font-mono text-xs text-slate-400">main.bl</span>
                    </div>
                    <button onclick="clearEditor()" class="text-[11px] text-slate-500 hover:text-slate-300 font-mono transition">রিসেট কোড</button>
                </div>
                <!-- Monaco Container -->
                <div class="flex-1 relative bg-[#090d16]">
                    <div id="editorContainer" class="absolute inset-0"></div>
                </div>
            </div>

            <!-- Bottom Resizer Splitter Bar -->
            <div id="resizerBottom" class="h-2 hover:h-2 bg-transparent hover:bg-cyan-500/30 cursor-row-resize flex items-center justify-center group shrink-0 transition-colors z-20 my-1 rounded-full" title="Drag to Resize Output Panel">
                <div class="h-1 w-12 bg-slate-800 group-hover:bg-cyan-400 rounded-full transition-colors"></div>
            </div>

            <!-- Bottom Output Panel Drawer (VS Code Style) -->
            <div id="bottomOutputPanel" class="h-[250px] shrink-0 flex flex-col gap-0 overflow-hidden min-h-[100px]">
                <!-- Unified Output Card Container -->
                <div id="outputCardContainer" class="bento-card rounded-2xl flex-1 flex flex-col overflow-hidden h-full">
                    <div class="h-9 bg-slate-950/80 border-b border-slate-800 px-3 flex items-center justify-between shrink-0">
                        <div class="flex items-center gap-2 font-mono text-xs">
                            <button id="tabTerminalBtn" onclick="switchViewTab('terminal')" class="px-2.5 py-0.5 rounded-lg bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/40 flex items-center gap-1.5 transition">
                                <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                                <span>টার্মিনাল (Console)</span>
                            </button>
                            <button id="tabAstBtn" onclick="switchViewTab('ast')" class="px-2.5 py-0.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent transition flex items-center gap-1.5">
                                <span>🌳 AST ট্রি (Diagram)</span>
                            </button>
                        </div>

                        <!-- Exec Stats Inline Summary -->
                        <div class="hidden sm:flex items-center gap-3 font-mono text-[11px] text-slate-400 bg-slate-900/60 px-3 py-0.5 rounded-lg border border-slate-800">
                            <div>TIME: <span id="execTimeVal" class="text-emerald-400 font-bold">0 ms</span></div>
                            <div class="text-slate-600">|</div>
                            <div>EXIT: <span id="exitCodeVal" class="text-slate-200 font-bold">0</span></div>
                            <div class="text-slate-600">|</div>
                            <div class="text-cyan-400 font-bold">C/Flex/Bison</div>
                        </div>

                        <!-- AST Diagram Toolbar Controls -->
                        <div id="astControls" class="hidden flex items-center gap-1 font-mono text-[11px]">
                            <button onclick="adjustAstZoom(-0.15)" title="Zoom Out" class="px-1.5 py-0.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 transition">➖</button>
                            <span id="astZoomVal" class="text-cyan-400 font-bold px-0.5 min-w-[32px] text-center">100%</span>
                            <button onclick="adjustAstZoom(0.15)" title="Zoom In" class="px-1.5 py-0.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 transition">➕</button>
                            <button onclick="autoFitAstInline()" title="Fit to Panel" class="px-1.5 py-0.5 rounded bg-cyan-950 hover:bg-cyan-900 border border-cyan-800 text-cyan-300 transition">🔍 ফিট</button>
                            <button onclick="resetAstZoom()" title="Reset Zoom" class="px-1.5 py-0.5 rounded bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-slate-200 transition">↺</button>
                            <button onclick="openAstFullscreen()" title="Fullscreen View" class="ml-1 px-2 py-0.5 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-700 text-cyan-300 flex items-center gap-1 font-bold transition">
                                <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-2V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" /></svg>
                                <span>ফুলস্ক্রিন</span>
                            </button>
                        </div>

                        <button onclick="clearTerminal()" class="text-[11px] font-mono text-slate-500 hover:text-slate-300">ক্লিয়ার</button>
                    </div>
                    <div id="terminal" class="flex-1 p-3.5 font-mono text-[12px] leading-[1.6] overflow-y-auto terminal-glow bg-[#03060a] text-slate-300 select-text">
                        <div class="text-slate-600 italic">// কোড রান করলে ফলাফল এখানে প্রদর্শিত হবে...</div>
                    </div>
                    <div id="astViewContainer" class="flex-1 overflow-auto terminal-glow bg-[#03060a] hidden relative select-none cursor-grab active:cursor-grabbing p-6">
                        <div id="astScaleWrapper" class="inline-block transition-transform duration-100 origin-top-left min-w-max">
                            <div id="astTreeContent" class="inline-block min-w-max p-4">
                                <div class="text-slate-600 italic mt-8 font-mono text-xs">// কোড রান করলে AST সিনট্যাক্স ট্রি এখানে দেখাবে...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- AST Fullscreen Modal Overlay -->
    <div id="astModal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex flex-col p-6">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-4 shrink-0">
            <div class="flex items-center gap-4">
                <span class="text-base font-bold font-mono text-cyan-400 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                    🌳 AST (Abstract Syntax Tree) Fullscreen Visualizer
                </span>
                <div class="flex items-center gap-1.5 font-mono text-xs bg-slate-900/80 px-3 py-1 rounded-xl border border-slate-800">
                    <button onclick="adjustAstZoomModal(-0.15)" title="Zoom Out" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold transition">➖</button>
                    <span id="astModalZoomVal" class="text-cyan-400 font-bold px-2 min-w-[40px] text-center">100%</span>
                    <button onclick="adjustAstZoomModal(0.15)" title="Zoom In" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold transition">➕</button>
                    <button onclick="autoFitAstModal()" title="Fit Tree to Screen" class="px-3 py-1 rounded-lg bg-cyan-950 hover:bg-cyan-900 border border-cyan-700 text-cyan-300 font-bold transition flex items-center gap-1">
                        🔍 স্ক্রিনে ফিট করো
                    </button>
                    <button onclick="resetAstZoomModal()" title="Reset to 100%" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition">↺ 100%</button>
                </div>
            </div>
            <button onclick="closeAstFullscreen()" class="px-3.5 py-1.5 rounded-xl bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 font-mono text-xs font-bold transition flex items-center gap-1.5">
                ✕ বন্ধ করুন (Esc)
            </button>
        </div>
        <div id="astModalContainer" class="flex-1 overflow-auto bg-[#03060a] rounded-2xl border border-slate-800/80 p-8 relative cursor-grab active:cursor-grabbing select-none">
            <div id="astModalScaleWrapper" class="inline-block transition-transform duration-100 origin-top-left min-w-max">
                <div id="astModalTreeContent" class="inline-block min-w-max p-4"></div>
            </div>
        </div>
    </div>

    <script>
        let editor;
        const snippets = {
            vars: `// ১. ভ্যারিয়েবল ডিক্লেয়ারেশন ও সাধারণ গণিত
dhoro a = 35;
dhoro b = 15;
dhoro sum = a + b;
dhoro sub = a - b;
dhoro mul = a * b;
dhoro div = a / b;

bolo sum;
bolo sub;
bolo mul;
bolo div;`,

            logic: `// ২. শর্ত যাচাই (If-Else) এবং স্ট্রিং আউটপুট
dhoro score = 85;

jodi (score >= 80) {
    bolo "Shabash! Pass Korecho (A+ Grade)";
} nawle {
    bolo "Fail! Aro porashona korte hobe.";
}

dhoro check = 10;
jodi (check != 5) {
    bolo "Sothik: 10 is not equal to 5";
}`,

            loop: `// ৩. লুপ বা পুনরাবৃত্তি (While Loop)
dhoro counter = 5;

jotokhon (counter > 0) {
    bolo "Countdown: " + counter;
    dhoro counter = counter - 1;
}
bolo "Dhamaka! Loop Sesh!";`,

            complex: `// ৪. জটিল লজিক ও ফ্যাক্টোরিয়াল ক্যালকুলেশন
dhoro n = 5;
dhoro fact = 1;

jotokhon (n > 0) {
    dhoro fact = fact * n;
    dhoro n = n - 1;
}

bolo "5 er Factorial holo: " + fact;`,

            func: `// ৫. কাস্টম ফাংশন, ফ্লট এবং রিটার্ন লজিক
kaaj guun(x, y) {
    ferot x * y;
}

dhoro a = 4.5;
dhoro b = 2.0;
dhoro res = guun(a, b);

bolo "Result: " + res;

dhoro test_bool = shotto;
jodi (test_bool) {
    bolo "Booleans & Functions Active!";
}`,

            array: `// ৬. তালিকা (Array) ও নির্দিষ্ট লুপ (jonno / For-Loop)
dhoro talika numbers = [10, 20, 30, 40];
bolo "প্রথমে তালিকা: " + numbers;

jonno (dhoro i = 0; i < 4; dhoro i = i + 1;) {
    bolo "Item " + i + ": " + numbers[i];
}`
        };

        // Monaco Language definition for BanglaLang
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            monaco.languages.register({ id: 'banglalang' });
            monaco.languages.setMonarchTokensProvider('banglalang', {
                keywords: ['dhoro', 'bolo', 'jodi', 'nawle', 'jotokhon', 'kaaj', 'ferot', 'nao', 'shotto', 'mittha', 'talika', 'jonno'],
                tokenizer: {
                    root: [
                        [/\b(dhoro|bolo|jodi|nawle|jotokhon|kaaj|ferot|nao|shotto|mittha|talika|jonno)\b/, 'keyword'],
                        [/"([^"\\]|\\.)*"/, 'string'],
                        [/\b[0-9]+\.[0-9]+\b/, 'number'],
                        [/\b[0-9]+\b/, 'number'],
                        [/\b[a-zA-Z_][a-zA-Z0-9_]*\b/, 'variable'],
                        [/\/\/.*$/, 'comment'],
                        [/[+\-*\/=<>!]+/, 'operator'],
                        [/[{}();,\[\]]/, 'delimiter']
                    ]
                }
            });

            monaco.editor.defineTheme('banglaCyberTheme', {
                base: 'vs-dark',
                inherit: true,
                rules: [
                    { token: 'keyword', foreground: '10B981', fontStyle: 'bold' },
                    { token: 'string', foreground: '34D399' },
                    { token: 'number', foreground: 'F59E0B' },
                    { token: 'variable', foreground: '38BDF8' },
                    { token: 'comment', foreground: '64748B', fontStyle: 'italic' },
                    { token: 'operator', foreground: 'EC4899' },
                    { token: 'delimiter', foreground: '94A3B8' }
                ],
                colors: {
                    'editor.background': '#090d16',
                    'editor.foreground': '#E2E8F0',
                    'editorLineNumber.foreground': '#334155',
                    'editorLineNumber.activeForeground': '#10B981',
                    'editor.selectionBackground': '#1E293B',
                    'editor.inactiveSelectionBackground': '#0F172A'
                }
            });

            editor = monaco.editor.create(document.getElementById('editorContainer'), {
                value: snippets.vars,
                language: 'banglalang',
                theme: 'banglaCyberTheme',
                automaticLayout: true,
                fontSize: 13.5,
                lineHeight: 21,
                fontFamily: '"Fira Code", "Consolas", "Courier New", monospace',
                fontLigatures: true,
                letterSpacing: 0,
                smoothScrolling: true,
                cursorBlinking: 'smooth',
                cursorSmoothCaretAnimation: 'on',
                renderLineHighlight: 'all',
                bracketPairColorization: { enabled: true },
                matchBrackets: 'always',
                minimap: { enabled: false },
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                padding: { top: 10, bottom: 10 }
            });

            // Re-measure fonts once web fonts finish loading asynchronously
            if (document.fonts && document.fonts.ready) {
                document.fonts.ready.then(function() {
                    if (monaco && monaco.editor) {
                        monaco.editor.remeasureFonts();
                    }
                });
            }

            // Custom Right-Arrow handler: Prevent auto line-wrap to next line when at line end
            editor.addCommand(monaco.KeyCode.RightArrow, function() {
                const position = editor.getPosition();
                const model = editor.getModel();
                if (!position || !model) return;
                const lineLength = model.getLineContent(position.lineNumber).length;
                if (position.column <= lineLength) {
                    editor.setPosition({ lineNumber: position.lineNumber, column: position.column + 1 });
                }
            }, 'editorTextFocus && !editorHasSelection');

            // Shortcut Ctrl+Enter / Cmd+Enter to Run
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, runCode);
        });

        function loadSnippet(type) {
            if (editor && snippets[type]) {
                editor.setValue(snippets[type]);
            }
        }

        function clearEditor() {
            if (editor) editor.setValue('// Notun BanglaLang Code likhun...\n');
        }

        let isLeftCollapsed = false;
        let savedLeftWidth = 320;

        function toggleLeftSidebar() {
            const leftPanel = document.getElementById('leftPanel');
            const toggleText = document.getElementById('sidebarToggleText');

            if (isLeftCollapsed) {
                leftPanel.style.width = savedLeftWidth + 'px';
                leftPanel.classList.remove('opacity-0', 'pointer-events-none', 'w-0', '-mr-3');
                toggleText.innerText = 'সাইডবার বন্ধ';
                isLeftCollapsed = false;
            } else {
                savedLeftWidth = leftPanel.offsetWidth || 320;
                leftPanel.style.width = '0px';
                leftPanel.classList.add('opacity-0', 'pointer-events-none', 'w-0', '-mr-3');
                toggleText.innerText = 'সাইডবার খুলুন';
                isLeftCollapsed = true;
            }
            setTimeout(() => {
                if (editor) editor.layout();
                if (activeTab === 'ast') autoFitAstInline();
            }, 220);
        }

        // Setup Resizable Splitters
        function initSplitResizers() {
            const bottomOutputPanel = document.getElementById('bottomOutputPanel');
            const resizerBottom = document.getElementById('resizerBottom');

            function makeVerticalResizable(resizer, bottomPanel) {
                let startY, startHeight;

                resizer.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                    startY = e.clientY;
                    startHeight = bottomPanel.offsetHeight;

                    document.body.style.cursor = 'row-resize';
                    document.body.style.userSelect = 'none';

                    function onMouseMove(moveEvent) {
                        const delta = startY - moveEvent.clientY;
                        let newHeight = Math.min(Math.max(120, startHeight + delta), 600);
                        bottomPanel.style.height = newHeight + 'px';
                        if (editor) editor.layout();
                    }

                    function onMouseUp() {
                        document.body.style.cursor = '';
                        document.body.style.userSelect = '';
                        document.removeEventListener('mousemove', onMouseMove);
                        document.removeEventListener('mouseup', onMouseUp);
                        if (editor) editor.layout();
                        if (activeTab === 'ast') autoFitAstInline();
                    }

                    document.addEventListener('mousemove', onMouseMove);
                    document.addEventListener('mouseup', onMouseUp);
                });
            }

            if (resizerBottom && bottomOutputPanel) {
                makeVerticalResizable(resizerBottom, bottomOutputPanel);
            }
        }

        window.addEventListener('load', initSplitResizers);

        let activeTab = 'terminal';
        let currentAstData = null;
        let currentZoom = 1.0;
        let modalZoom = 1.0;

        function applyScaleToWrapper(wrapperId, scale) {
            const wrapper = document.getElementById(wrapperId);
            if (!wrapper) return;
            if ('zoom' in wrapper.style) {
                wrapper.style.zoom = scale;
                wrapper.style.transform = '';
            } else {
                wrapper.style.transform = `scale(${scale})`;
                wrapper.style.transformOrigin = 'top left';
            }
        }

        function adjustAstZoom(delta) {
            currentZoom = Math.min(Math.max(0.1, currentZoom + delta), 2.5);
            const valLabel = document.getElementById('astZoomVal');
            if (valLabel) valLabel.innerText = Math.round(currentZoom * 100) + '%';
            applyScaleToWrapper('astScaleWrapper', currentZoom);
        }

        function resetAstZoom() {
            currentZoom = 1.0;
            const valLabel = document.getElementById('astZoomVal');
            if (valLabel) valLabel.innerText = '100%';
            applyScaleToWrapper('astScaleWrapper', 1.0);
        }

        function autoFitAstInline() {
            const container = document.getElementById('astViewContainer');
            const treeContent = document.getElementById('astTreeContent');
            if (!container || !treeContent) return;

            applyScaleToWrapper('astScaleWrapper', 1.0);

            const containerWidth = container.clientWidth - 32;
            const treeWidth = treeContent.scrollWidth;

            if (treeWidth > 0 && containerWidth > 0) {
                let fitScale = Math.min(1.0, containerWidth / treeWidth);
                fitScale = Math.max(0.15, fitScale);
                
                currentZoom = fitScale;
                const valLabel = document.getElementById('astZoomVal');
                if (valLabel) valLabel.innerText = Math.round(currentZoom * 100) + '%';
                applyScaleToWrapper('astScaleWrapper', currentZoom);

                setTimeout(() => {
                    container.scrollLeft = Math.max(0, (treeWidth * fitScale - containerWidth) / 2);
                    container.scrollTop = 0;
                }, 50);
            }
        }

        function adjustAstZoomModal(delta) {
            modalZoom = Math.min(Math.max(0.1, modalZoom + delta), 3.0);
            const valLabel = document.getElementById('astModalZoomVal');
            if (valLabel) valLabel.innerText = Math.round(modalZoom * 100) + '%';
            applyScaleToWrapper('astModalScaleWrapper', modalZoom);
        }

        function resetAstZoomModal() {
            modalZoom = 1.0;
            const valLabel = document.getElementById('astModalZoomVal');
            if (valLabel) valLabel.innerText = '100%';
            applyScaleToWrapper('astModalScaleWrapper', 1.0);
        }

        function autoFitAstModal() {
            const modalContainer = document.getElementById('astModalContainer');
            const treeContent = document.getElementById('astModalTreeContent');
            if (!modalContainer || !treeContent) return;

            applyScaleToWrapper('astModalScaleWrapper', 1.0);

            const containerWidth = modalContainer.clientWidth - 64;
            const treeWidth = treeContent.scrollWidth;

            if (treeWidth > 0 && containerWidth > 0) {
                let fitScale = Math.min(1.0, containerWidth / treeWidth);
                fitScale = Math.max(0.15, fitScale);
                
                modalZoom = fitScale;
                const valLabel = document.getElementById('astModalZoomVal');
                if (valLabel) valLabel.innerText = Math.round(modalZoom * 100) + '%';
                applyScaleToWrapper('astModalScaleWrapper', modalZoom);

                setTimeout(() => {
                    modalContainer.scrollLeft = Math.max(0, (treeWidth * fitScale - containerWidth) / 2);
                    modalContainer.scrollTop = 0;
                }, 50);
            }
        }

        function openAstFullscreen() {
            if (!currentAstData) return;
            const modal = document.getElementById('astModal');
            modal.classList.remove('hidden');
            document.getElementById('astModalTreeContent').innerHTML = document.getElementById('astTreeContent').innerHTML;
            
            setTimeout(autoFitAstModal, 60);
        }

        function closeAstFullscreen() {
            document.getElementById('astModal').classList.add('hidden');
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeAstFullscreen();
        });

        function switchViewTab(tab) {
            activeTab = tab;
            const termBtn = document.getElementById('tabTerminalBtn');
            const astBtn = document.getElementById('tabAstBtn');
            const astControls = document.getElementById('astControls');
            const termDiv = document.getElementById('terminal');
            const astDiv = document.getElementById('astViewContainer');

            if (tab === 'terminal') {
                termBtn.className = "px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/40 flex items-center gap-1.5 transition";
                astBtn.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent transition flex items-center gap-1.5";
                astControls.classList.add('hidden');
                termDiv.classList.remove('hidden');
                astDiv.classList.add('hidden');
            } else {
                astBtn.className = "px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-400 font-bold border border-cyan-500/40 flex items-center gap-1.5 transition";
                termBtn.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent transition flex items-center gap-1.5";
                astControls.classList.remove('hidden');
                astDiv.classList.remove('hidden');
                termDiv.classList.add('hidden');
                if (currentAstData) {
                    renderAstTree(currentAstData);
                    setTimeout(autoFitAstInline, 60);
                }
            }
        }

        function renderAstTree(data) {
            const container = document.getElementById('astTreeContent');
            if (!data) {
                container.innerHTML = '<div class="text-slate-600 italic mt-8 font-mono text-xs">// কোনো AST ডাটা পাওয়া যায়নি।</div>';
                return;
            }

            function buildHtmlNode(node) {
                if (!node) return '';
                const typeText = node.type || 'Node';
                const hasChildren = node.children && node.children.length > 0;
                
                let html = `<div class="flex flex-col items-center my-1">`;
                html += `<div class="px-3.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-slate-900/90 border border-cyan-500/50 text-cyan-300 shadow-lg shadow-cyan-500/10 hover:border-emerald-400 hover:text-emerald-300 transition cursor-default whitespace-nowrap">${typeText}</div>`;

                if (hasChildren) {
                    html += `<div class="w-0.5 h-3.5 bg-cyan-500/40"></div>`;
                    html += `<div class="flex items-start gap-4 pt-1.5 border-t border-dashed border-cyan-500/40">`;
                    for (let child of node.children) {
                        html += buildHtmlNode(child);
                    }
                    html += `</div>`;
                }
                html += `</div>`;
                return html;
            }

            container.innerHTML = `<div class="inline-block p-4 min-w-max">${buildHtmlNode(data)}</div>`;
        }

        function setupPanContainer(containerId) {
            const container = document.getElementById(containerId);
            if (!container) return;
            let isDown = false;
            let startX, startY, scrollLeft, scrollTop;

            container.addEventListener('mousedown', (e) => {
                isDown = true;
                startX = e.pageX - container.offsetLeft;
                startY = e.pageY - container.offsetTop;
                scrollLeft = container.scrollLeft;
                scrollTop = container.scrollTop;
            });

            container.addEventListener('mouseleave', () => { isDown = false; });
            container.addEventListener('mouseup', () => { isDown = false; });

            container.addEventListener('mousemove', (e) => {
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const y = e.pageY - container.offsetTop;
                const walkX = (x - startX) * 1.5;
                const walkY = (y - startY) * 1.5;
                container.scrollLeft = scrollLeft - walkX;
                container.scrollTop = scrollTop - walkY;
            });
        }

        setupPanContainer('astViewContainer');
        setupPanContainer('astModalContainer');

        function setupWheelZoom(containerId, isModal) {
            const container = document.getElementById(containerId);
            if (!container) return;

            container.addEventListener('wheel', (e) => {
                if (e.ctrlKey || isModal) {
                    e.preventDefault();
                    const delta = e.deltaY < 0 ? 0.08 : -0.08;
                    if (isModal) {
                        adjustAstZoomModal(delta);
                    } else {
                        adjustAstZoom(delta);
                    }
                }
            }, { passive: false });
        }

        setupWheelZoom('astViewContainer', false);
        setupWheelZoom('astModalContainer', true);

        function clearTerminal() {
            const terminal = document.getElementById('terminal');
            terminal.innerHTML = '<div class="text-slate-600 italic">// Terminal cleared.</div>';
            currentAstData = null;
            renderAstTree(null);
            resetAstZoom();
        }

        // Check backend health status periodically
        async function checkBackendHealth() {
            const badge = document.getElementById('backendStatusBadge');
            const dot = document.getElementById('statusDot');
            const text = document.getElementById('statusText');

            try {
                const res = await fetch('http://localhost:5000/api/health');
                const data = await res.json();
                if (data.status === 'online') {
                    dot.className = 'w-2 h-2 rounded-full bg-emerald-400';
                    text.innerText = data.compilerReady ? 'Compiler Online (Ready)' : 'Compiler Binary Missing';
                    text.className = data.compilerReady ? 'text-emerald-400 font-medium' : 'text-amber-400 font-medium';
                }
            } catch (e) {
                dot.className = 'w-2 h-2 rounded-full bg-rose-500';
                text.innerText = 'Backend Offline (:5000)';
                text.className = 'text-rose-400 font-medium';
            }
        }

        setInterval(checkBackendHealth, 4000);
        checkBackendHealth();

        async function runCode() {
            if (!editor) return;
            const code = editor.getValue();
            const terminal = document.getElementById('terminal');
            const execTimeVal = document.getElementById('execTimeVal');
            const exitCodeVal = document.getElementById('exitCodeVal');

            terminal.innerHTML = '<div class="text-emerald-400 animate-pulse font-mono">⚙️ কোড কম্পাইল ও রান হচ্ছে...</div>';

            try {
                const res = await fetch('http://localhost:5000/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });

                const data = await res.json();
                terminal.innerHTML = '';
                currentAstData = data.ast;

                execTimeVal.innerText = (data.executionTimeMs || 0) + ' ms';
                exitCodeVal.innerText = data.exitCode !== undefined ? data.exitCode : '0';

                if (data.output) {
                    const outDiv = document.createElement('div');
                    outDiv.className = 'text-emerald-300 font-mono whitespace-pre-wrap';
                    outDiv.innerText = data.output;
                    terminal.appendChild(outDiv);
                }

                if (data.error) {
                    const errDiv = document.createElement('div');
                    errDiv.className = 'mt-2 p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 font-mono whitespace-pre-wrap';
                    errDiv.innerHTML = `<span class="font-bold text-rose-400">⚠️ এরর বার্তা:</span>\n${data.error}`;
                    terminal.appendChild(errDiv);
                }

                if (!data.output && !data.error) {
                    terminal.innerHTML = '<div class="text-slate-500 italic font-mono">// কোড সফলভাবে রান হয়েছে কিন্তু কোনো আউটপুট প্রিন্ট হয়নি।</div>';
                }

                if (data.ast) {
                    renderAstTree(data.ast);
                    setTimeout(autoFitAstInline, 60);
                }
            } catch (err) {
                terminal.innerHTML = `<div class="p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-300 font-mono">
                    <div class="font-bold text-rose-400">❌ ব্যাকএন্ড সংযোগ ব্যর্থ হয়েছে!</div>
                    <div class="text-xs text-slate-400 mt-1">দয়া করে নিশ্চিত করুন যে ব্যাকএন্ড সার্ভার চালু আছে (http://localhost:5000)।</div>
                </div>`;
            }
        }

        document.getElementById('runBtn').onclick = runCode;
    </script>
</body>
</html>
'''g-[#03060a] leading-relaxed text-slate-300 select-text">
                    <div class="text-slate-600 italic">// কোড রান করলে ফলাফল এখানে প্রদর্শিত হবে...</div>
                </div>
                <div id="astViewContainer" class="flex-1 overflow-auto terminal-glow bg-[#03060a] hidden relative select-none cursor-grab active:cursor-grabbing p-6">
                    <div id="astScaleWrapper" class="inline-block transition-transform duration-100 origin-top-left min-w-max">
                        <div id="astTreeContent" class="inline-block min-w-max p-4">
                            <div class="text-slate-600 italic mt-8 font-mono text-xs">// কোড রান করলে AST সিনট্যাক্স ট্রি এখানে দেখাবে...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- AST Fullscreen Modal Overlay -->
    <div id="astModal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-md z-50 hidden flex flex-col p-6">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-4 shrink-0">
            <div class="flex items-center gap-4">
                <span class="text-base font-bold font-mono text-cyan-400 flex items-center gap-2">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                    🌳 AST (Abstract Syntax Tree) Fullscreen Visualizer
                </span>
                <div class="flex items-center gap-1.5 font-mono text-xs bg-slate-900/80 px-3 py-1 rounded-xl border border-slate-800">
                    <button onclick="adjustAstZoomModal(-0.15)" title="Zoom Out" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold transition">➖</button>
                    <span id="astModalZoomVal" class="text-cyan-400 font-bold px-2 min-w-[40px] text-center">100%</span>
                    <button onclick="adjustAstZoomModal(0.15)" title="Zoom In" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold transition">➕</button>
                    <button onclick="autoFitAstModal()" title="Fit Tree to Screen" class="px-3 py-1 rounded-lg bg-cyan-950 hover:bg-cyan-900 border border-cyan-700 text-cyan-300 font-bold transition flex items-center gap-1">
                        🔍 স্ক্রিনে ফিট করো
                    </button>
                    <button onclick="resetAstZoomModal()" title="Reset to 100%" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition">↺ 100%</button>
                </div>
            </div>
            <button onclick="closeAstFullscreen()" class="px-3.5 py-1.5 rounded-xl bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 font-mono text-xs font-bold transition flex items-center gap-1.5">
                ✕ বন্ধ করুন (Esc)
            </button>
        </div>
        <div id="astModalContainer" class="flex-1 overflow-auto bg-[#03060a] rounded-2xl border border-slate-800/80 p-8 relative cursor-grab active:cursor-grabbing select-none">
            <div id="astModalScaleWrapper" class="inline-block transition-transform duration-100 origin-top-left min-w-max">
                <div id="astModalTreeContent" class="inline-block min-w-max p-4"></div>
            </div>
        </div>
    </div>

    <script>
        let editor;
        const snippets = {
            vars: `// ১. ভ্যারিয়েবল ডিক্লেয়ারেশন ও সাধারণ গণিত
dhoro a = 35;
dhoro b = 15;
dhoro sum = a + b;
dhoro sub = a - b;
dhoro mul = a * b;
dhoro div = a / b;

bolo sum;
bolo sub;
bolo mul;
bolo div;`,

            logic: `// ২. শর্ত যাচাই (If-Else) এবং স্ট্রিং আউটপুট
dhoro score = 85;

jodi (score >= 80) {
    bolo "Shabash! Pass Korecho (A+ Grade)";
} nawle {
    bolo "Fail! Aro porashona korte hobe.";
}

dhoro check = 10;
jodi (check != 5) {
    bolo "Sothik: 10 is not equal to 5";
}`,

            loop: `// ৩. লুপ বা পুনরাবৃত্তি (While Loop)
dhoro counter = 5;

jotokhon (counter > 0) {
    bolo "Countdown: " + counter;
    dhoro counter = counter - 1;
}
bolo "Dhamaka! Loop Sesh!";`,

            complex: `// ৪. জটিল লজিক ও ফ্যাক্টোরিয়াল ক্যালকুলেশন
dhoro n = 5;
dhoro fact = 1;

jotokhon (n > 0) {
    dhoro fact = fact * n;
    dhoro n = n - 1;
}

bolo "5 er Factorial holo: " + fact;`,

            func: `// ৫. কাস্টম ফাংশন, ফ্লট এবং রিটার্ন লজিক
kaaj guun(x, y) {
    ferot x * y;
}

dhoro a = 4.5;
dhoro b = 2.0;
dhoro res = guun(a, b);

bolo "Result: " + res;

dhoro test_bool = shotto;
jodi (test_bool) {
    bolo "Booleans & Functions Active!";
}`,

            array: `// ৬. তালিকা (Array) ও নির্দিষ্ট লুপ (jonno / For-Loop)
dhoro talika numbers = [10, 20, 30, 40];
bolo "প্রথমে তালিকা: " + numbers;

jonno (dhoro i = 0; i < 4; dhoro i = i + 1;) {
    bolo "Item " + i + ": " + numbers[i];
}`
        };

        // Monaco Language definition for BanglaLang
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            monaco.languages.register({ id: 'banglalang' });
            monaco.languages.setMonarchTokensProvider('banglalang', {
                keywords: ['dhoro', 'bolo', 'jodi', 'nawle', 'jotokhon', 'kaaj', 'ferot', 'nao', 'shotto', 'mittha', 'talika', 'jonno'],
                tokenizer: {
                    root: [
                        [/\b(dhoro|bolo|jodi|nawle|jotokhon|kaaj|ferot|nao|shotto|mittha|talika|jonno)\b/, 'keyword'],
                        [/"([^"\\]|\\.)*"/, 'string'],
                        [/\b[0-9]+\.[0-9]+\b/, 'number'],
                        [/\b[0-9]+\b/, 'number'],
                        [/\b[a-zA-Z_][a-zA-Z0-9_]*\b/, 'variable'],
                        [/\/\/.*$/, 'comment'],
                        [/[+\-*\/=<>!]+/, 'operator'],
                        [/[{}();,\[\]]/, 'delimiter']
                    ]
                }
            });

            monaco.editor.defineTheme('banglaCyberTheme', {
                base: 'vs-dark',
                inherit: true,
                rules: [
                    { token: 'keyword', foreground: '10B981', fontStyle: 'bold' },
                    { token: 'string', foreground: '34D399' },
                    { token: 'number', foreground: 'F59E0B' },
                    { token: 'variable', foreground: '38BDF8' },
                    { token: 'comment', foreground: '64748B', fontStyle: 'italic' },
                    { token: 'operator', foreground: 'EC4899' },
                    { token: 'delimiter', foreground: '94A3B8' }
                ],
                colors: {
                    'editor.background': '#090d16',
                    'editor.foreground': '#E2E8F0',
                    'editorLineNumber.foreground': '#334155',
                    'editorLineNumber.activeForeground': '#10B981',
                    'editor.selectionBackground': '#1E293B',
                    'editor.inactiveSelectionBackground': '#0F172A'
                }
            });

            editor = monaco.editor.create(document.getElementById('editorContainer'), {
                value: snippets.vars,
                language: 'banglalang',
                theme: 'banglaCyberTheme',
                automaticLayout: true,
                fontSize: 14,
                lineHeight: 24,
                fontFamily: '"Fira Code", "Consolas", "Courier New", monospace',
                fontLigatures: true,
                letterSpacing: 0,
                smoothScrolling: true,
                cursorBlinking: 'smooth',
                cursorSmoothCaretAnimation: 'on',
                renderLineHighlight: 'all',
                bracketPairColorization: { enabled: true },
                matchBrackets: 'always',
                minimap: { enabled: false },
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                padding: { top: 12, bottom: 12 }
            });

            // Re-measure fonts once web fonts finish loading asynchronously
            if (document.fonts && document.fonts.ready) {
                document.fonts.ready.then(function() {
                    if (monaco && monaco.editor) {
                        monaco.editor.remeasureFonts();
                    }
                });
            }

            // Custom Right-Arrow handler: Prevent auto line-wrap to next line when at line end
            editor.addCommand(monaco.KeyCode.RightArrow, function() {
                const position = editor.getPosition();
                const model = editor.getModel();
                if (!position || !model) return;
                const lineLength = model.getLineContent(position.lineNumber).length;
                if (position.column <= lineLength) {
                    editor.setPosition({ lineNumber: position.lineNumber, column: position.column + 1 });
                }
            }, 'editorTextFocus && !editorHasSelection');

            // Shortcut Ctrl+Enter / Cmd+Enter to Run
            editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, runCode);
        });

        function loadSnippet(type) {
            if (editor && snippets[type]) {
                editor.setValue(snippets[type]);
            }
        }

        function clearEditor() {
            if (editor) editor.setValue('// Notun BanglaLang Code likhun...\n');
        }

        let isLeftCollapsed = false;
        let savedLeftWidth = 320;

        function toggleLeftSidebar() {
            const leftPanel = document.getElementById('leftPanel');
            const toggleText = document.getElementById('sidebarToggleText');
            const resizerLeft = document.getElementById('resizerLeft');

            if (isLeftCollapsed) {
                leftPanel.style.width = savedLeftWidth + 'px';
                leftPanel.classList.remove('opacity-0', 'pointer-events-none', 'w-0');
                resizerLeft.classList.remove('hidden');
                toggleText.innerText = 'সাইডবার বন্ধ';
                isLeftCollapsed = false;
            } else {
                savedLeftWidth = leftPanel.offsetWidth || 320;
                leftPanel.style.width = '0px';
                leftPanel.classList.add('opacity-0', 'pointer-events-none');
                resizerLeft.classList.add('hidden');
                toggleText.innerText = 'সাইডবার খুলুন';
                isLeftCollapsed = true;
            }
            setTimeout(() => { if (editor) editor.layout(); }, 220);
        }

        // Setup Resizable Splitters
        function initSplitResizers() {
            const leftPanel = document.getElementById('leftPanel');
            const rightPanel = document.getElementById('rightPanel');
            const resizerLeft = document.getElementById('resizerLeft');
            const resizerRight = document.getElementById('resizerRight');
            const mainContainer = document.getElementById('mainContainer');

            function makeResizable(resizer, panel, isLeft) {
                let startX, startWidth;

                resizer.addEventListener('mousedown', (e) => {
                    e.preventDefault();
                    startX = e.clientX;
                    startWidth = panel.offsetWidth;

                    document.body.style.cursor = 'col-resize';
                    document.body.style.userSelect = 'none';
                    mainContainer.style.pointerEvents = 'none';

                    function onMouseMove(moveEvent) {
                        const delta = moveEvent.clientX - startX;
                        let newWidth;
                        if (isLeft) {
                            newWidth = Math.min(Math.max(180, startWidth + delta), 500);
                        } else {
                            newWidth = Math.min(Math.max(260, startWidth - delta), 700);
                        }
                        panel.style.width = newWidth + 'px';
                        if (editor) editor.layout();
                    }

                    function onMouseUp() {
                        document.body.style.cursor = '';
                        document.body.style.userSelect = '';
                        mainContainer.style.pointerEvents = '';
                        document.removeEventListener('mousemove', onMouseMove);
                        document.removeEventListener('mouseup', onMouseUp);
                        if (editor) editor.layout();
                    }

                    document.addEventListener('mousemove', onMouseMove);
                    document.addEventListener('mouseup', onMouseUp);
                });
            }

            makeResizable(resizerLeft, leftPanel, true);
            makeResizable(resizerRight, rightPanel, false);
        }

        window.addEventListener('load', initSplitResizers);

        let activeTab = 'terminal';
        let currentAstData = null;
        let currentZoom = 1.0;
        let modalZoom = 1.0;

        function applyScaleToWrapper(wrapperId, scale) {
            const wrapper = document.getElementById(wrapperId);
            if (!wrapper) return;
            if ('zoom' in wrapper.style) {
                wrapper.style.zoom = scale;
                wrapper.style.transform = '';
            } else {
                wrapper.style.transform = `scale(${scale})`;
                wrapper.style.transformOrigin = 'top left';
            }
        }

        function adjustAstZoom(delta) {
            currentZoom = Math.min(Math.max(0.1, currentZoom + delta), 2.5);
            const valLabel = document.getElementById('astZoomVal');
            if (valLabel) valLabel.innerText = Math.round(currentZoom * 100) + '%';
            applyScaleToWrapper('astScaleWrapper', currentZoom);
        }

        function resetAstZoom() {
            currentZoom = 1.0;
            const valLabel = document.getElementById('astZoomVal');
            if (valLabel) valLabel.innerText = '100%';
            applyScaleToWrapper('astScaleWrapper', 1.0);
        }

        function autoFitAstInline() {
            const container = document.getElementById('astViewContainer');
            const treeContent = document.getElementById('astTreeContent');
            if (!container || !treeContent) return;

            applyScaleToWrapper('astScaleWrapper', 1.0);

            const containerWidth = container.clientWidth - 32;
            const treeWidth = treeContent.scrollWidth;

            if (treeWidth > 0 && containerWidth > 0) {
                let fitScale = Math.min(1.0, containerWidth / treeWidth);
                fitScale = Math.max(0.15, fitScale);
                
                currentZoom = fitScale;
                const valLabel = document.getElementById('astZoomVal');
                if (valLabel) valLabel.innerText = Math.round(currentZoom * 100) + '%';
                applyScaleToWrapper('astScaleWrapper', currentZoom);

                setTimeout(() => {
                    container.scrollLeft = Math.max(0, (treeWidth * fitScale - containerWidth) / 2);
                    container.scrollTop = 0;
                }, 50);
            }
        }

        function adjustAstZoomModal(delta) {
            modalZoom = Math.min(Math.max(0.1, modalZoom + delta), 3.0);
            const valLabel = document.getElementById('astModalZoomVal');
            if (valLabel) valLabel.innerText = Math.round(modalZoom * 100) + '%';
            applyScaleToWrapper('astModalScaleWrapper', modalZoom);
        }

        function resetAstZoomModal() {
            modalZoom = 1.0;
            const valLabel = document.getElementById('astModalZoomVal');
            if (valLabel) valLabel.innerText = '100%';
            applyScaleToWrapper('astModalScaleWrapper', 1.0);
        }

        function autoFitAstModal() {
            const modalContainer = document.getElementById('astModalContainer');
            const treeContent = document.getElementById('astModalTreeContent');
            if (!modalContainer || !treeContent) return;

            applyScaleToWrapper('astModalScaleWrapper', 1.0);

            const containerWidth = modalContainer.clientWidth - 64;
            const treeWidth = treeContent.scrollWidth;

            if (treeWidth > 0 && containerWidth > 0) {
                let fitScale = Math.min(1.0, containerWidth / treeWidth);
                fitScale = Math.max(0.15, fitScale);
                
                modalZoom = fitScale;
                const valLabel = document.getElementById('astModalZoomVal');
                if (valLabel) valLabel.innerText = Math.round(modalZoom * 100) + '%';
                applyScaleToWrapper('astModalScaleWrapper', modalZoom);

                setTimeout(() => {
                    modalContainer.scrollLeft = Math.max(0, (treeWidth * fitScale - containerWidth) / 2);
                    modalContainer.scrollTop = 0;
                }, 50);
            }
        }

        function openAstFullscreen() {
            if (!currentAstData) return;
            const modal = document.getElementById('astModal');
            modal.classList.remove('hidden');
            document.getElementById('astModalTreeContent').innerHTML = document.getElementById('astTreeContent').innerHTML;
            
            setTimeout(autoFitAstModal, 60);
        }

        function closeAstFullscreen() {
            document.getElementById('astModal').classList.add('hidden');
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeAstFullscreen();
        });

        function switchViewTab(tab) {
            activeTab = tab;
            const termBtn = document.getElementById('tabTerminalBtn');
            const astBtn = document.getElementById('tabAstBtn');
            const astControls = document.getElementById('astControls');
            const termDiv = document.getElementById('terminal');
            const astDiv = document.getElementById('astViewContainer');

            if (tab === 'terminal') {
                termBtn.className = "px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/40 flex items-center gap-1.5 transition";
                astBtn.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent transition flex items-center gap-1.5";
                astControls.classList.add('hidden');
                termDiv.classList.remove('hidden');
                astDiv.classList.add('hidden');
            } else {
                astBtn.className = "px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-400 font-bold border border-cyan-500/40 flex items-center gap-1.5 transition";
                termBtn.className = "px-2.5 py-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent transition flex items-center gap-1.5";
                astControls.classList.remove('hidden');
                astDiv.classList.remove('hidden');
                termDiv.classList.add('hidden');
                if (currentAstData) {
                    renderAstTree(currentAstData);
                    setTimeout(autoFitAstInline, 60);
                }
            }
        }

        function renderAstTree(data) {
            const container = document.getElementById('astTreeContent');
            if (!data) {
                container.innerHTML = '<div class="text-slate-600 italic mt-8 font-mono text-xs">// কোনো AST ডাটা পাওয়া যায়নি।</div>';
                return;
            }

            function buildHtmlNode(node) {
                if (!node) return '';
                const typeText = node.type || 'Node';
                const hasChildren = node.children && node.children.length > 0;
                
                let html = `<div class="flex flex-col items-center my-1">`;
                html += `<div class="px-3.5 py-1.5 rounded-xl text-xs font-mono font-bold bg-slate-900/90 border border-cyan-500/50 text-cyan-300 shadow-lg shadow-cyan-500/10 hover:border-emerald-400 hover:text-emerald-300 transition cursor-default whitespace-nowrap">${typeText}</div>`;

                if (hasChildren) {
                    html += `<div class="w-0.5 h-3.5 bg-cyan-500/40"></div>`;
                    html += `<div class="flex items-start gap-4 pt-1.5 border-t border-dashed border-cyan-500/40">`;
                    for (let child of node.children) {
                        html += buildHtmlNode(child);
                    }
                    html += `</div>`;
                }
                html += `</div>`;
                return html;
            }

            container.innerHTML = `<div class="inline-block p-4 min-w-max">${buildHtmlNode(data)}</div>`;
        }

        function setupPanContainer(containerId) {
            const container = document.getElementById(containerId);
            if (!container) return;
            let isDown = false;
            let startX, startY, scrollLeft, scrollTop;

            container.addEventListener('mousedown', (e) => {
                isDown = true;
                startX = e.pageX - container.offsetLeft;
                startY = e.pageY - container.offsetTop;
                scrollLeft = container.scrollLeft;
                scrollTop = container.scrollTop;
            });

            container.addEventListener('mouseleave', () => { isDown = false; });
            container.addEventListener('mouseup', () => { isDown = false; });

            container.addEventListener('mousemove', (e) => {
                if (!isDown) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const y = e.pageY - container.offsetTop;
                const walkX = (x - startX) * 1.5;
                const walkY = (y - startY) * 1.5;
                container.scrollLeft = scrollLeft - walkX;
                container.scrollTop = scrollTop - walkY;
            });
        }

        setupPanContainer('astViewContainer');
        setupPanContainer('astModalContainer');

        function setupWheelZoom(containerId, isModal) {
            const container = document.getElementById(containerId);
            if (!container) return;

            container.addEventListener('wheel', (e) => {
                if (e.ctrlKey || isModal) {
                    e.preventDefault();
                    const delta = e.deltaY < 0 ? 0.08 : -0.08;
                    if (isModal) {
                        adjustAstZoomModal(delta);
                    } else {
                        adjustAstZoom(delta);
                    }
                }
            }, { passive: false });
        }

        setupWheelZoom('astViewContainer', false);
        setupWheelZoom('astModalContainer', true);

        function clearTerminal() {
            const terminal = document.getElementById('terminal');
            terminal.innerHTML = '<div class="text-slate-600 italic">// Terminal cleared.</div>';
            currentAstData = null;
            renderAstTree(null);
            resetAstZoom();
        }

        // Check backend health status periodically
        async function checkBackendHealth() {
            const badge = document.getElementById('backendStatusBadge');
            const dot = document.getElementById('statusDot');
            const text = document.getElementById('statusText');

            try {
                const res = await fetch('http://localhost:5000/api/health');
                const data = await res.json();
                if (data.status === 'online') {
                    dot.className = 'w-2 h-2 rounded-full bg-emerald-400';
                    text.innerText = data.compilerReady ? 'Compiler Online (Ready)' : 'Compiler Binary Missing';
                    text.className = data.compilerReady ? 'text-emerald-400 font-medium' : 'text-amber-400 font-medium';
                }
            } catch (e) {
                dot.className = 'w-2 h-2 rounded-full bg-rose-500';
                text.innerText = 'Backend Offline (:5000)';
                text.className = 'text-rose-400 font-medium';
            }
        }

        setInterval(checkBackendHealth, 4000);
        checkBackendHealth();

        async function runCode() {
            if (!editor) return;
            const code = editor.getValue();
            const terminal = document.getElementById('terminal');
            const execTimeVal = document.getElementById('execTimeVal');
            const exitCodeVal = document.getElementById('exitCodeVal');

            terminal.innerHTML = '<div class="text-emerald-400 animate-pulse font-mono">⚙️ কোড কম্পাইল ও রান হচ্ছে...</div>';

            try {
                const res = await fetch('http://localhost:5000/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code })
                });

                const data = await res.json();
                terminal.innerHTML = '';
                currentAstData = data.ast;

                execTimeVal.innerText = (data.executionTimeMs || 0) + ' ms';
                exitCodeVal.innerText = data.exitCode !== undefined ? data.exitCode : '0';

                if (data.output) {
                    const outDiv = document.createElement('div');
                    outDiv.className = 'text-emerald-300 font-mono whitespace-pre-wrap';
                    outDiv.innerText = data.output;
                    terminal.appendChild(outDiv);
                }

                if (data.error) {
                    const errDiv = document.createElement('div');
                    errDiv.className = 'mt-2 p-3 rounded-lg bg-rose-950/40 border border-rose-800/60 text-rose-300 font-mono whitespace-pre-wrap';
                    errDiv.innerHTML = `<span class="font-bold text-rose-400">⚠️ এরর বার্তা:</span>\n${data.error}`;
                    terminal.appendChild(errDiv);
                }

                if (!data.output && !data.error) {
                    terminal.innerHTML = '<div class="text-slate-500 italic font-mono">// কোড সফলভাবে রান হয়েছে কিন্তু কোনো আউটপুট প্রিন্ট হয়নি।</div>';
                }

                if (data.ast) {
                    renderAstTree(data.ast);
                    setTimeout(autoFitAstInline, 60);
                }
            } catch (err) {
                terminal.innerHTML = `<div class="p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-300 font-mono">
                    <div class="font-bold text-rose-400">❌ ব্যাকএন্ড সংযোগ ব্যর্থ হয়েছে!</div>
                    <div class="text-xs text-slate-400 mt-1">দয়া করে নিশ্চিত করুন যে ব্যাকএন্ড সার্ভার চালু আছে (http://localhost:5000)।</div>
                </div>`;
            }
        }

        document.getElementById('runBtn').onclick = runCode;
    </script>
</body>
</html>
'''

    # File Writing mapping
    files_to_write = [
        (os.path.join(base_dir, "core", "parser.y"), parser_content),
        (os.path.join(base_dir, "core", "Makefile"), makefile_content),
        (os.path.join(base_dir, "backend", "package.json"), package_json),
        (os.path.join(base_dir, "backend", "server.js"), server_js),
        (os.path.join(base_dir, "frontend", "index.html"), frontend_html)
    ]

    print("\n[i] Writing all complete source codes...")
    for file_path, content in files_to_write:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"[✓] Successfully written: {file_path}")

    print("\n" + "=" * 60)
    print("🎉 BanglaLang Project Generated & Aligned Perfectly!")
    print("=" * 60)
    print("Next Execution Commands:")
    print(" 1. Compiler Build:   cd core && make")
    print(" 2. Run Backend:      cd backend && npm install && node server.js")
    print(" 3. Launch Frontend:  Open frontend/index.html in browser")
    print("=" * 60)

if __name__ == "__main__":
    create_project()