%{
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

int show_ast_flag = 0;

void print_node_ast_json(Node* n) {
    if (!n) { printf("null"); return; }
    printf("{\"type\":\"");
    switch (n->type) {
        case TYPE_NUM: printf("Number (%d)", n->val); break;
        case TYPE_FLOAT: printf("Float (%g)", n->fval); break;
        case TYPE_STR: printf("String (\\\"%s\\\")", n->str_val ? n->str_val : ""); break;
        case TYPE_VAR: printf("Variable (%s)", n->id ? n->id : ""); break;
        case TYPE_ASSIGN: printf("Assign (%s)", n->id ? n->id : ""); break;
        case TYPE_PRINT: printf("Print (bolo)"); break;
        case TYPE_IF: printf("If-Else (jodi)"); break;
        case TYPE_WHILE: printf("While Loop (jotokhon)"); break;
        case TYPE_FOR: printf("For Loop (jonno)"); break;
        case TYPE_BLOCK: printf("Block ({})"); break;
        case TYPE_FUNC_DECL: printf("Function Decl (%s)", n->id ? n->id : ""); break;
        case TYPE_FUNC_CALL: printf("Function Call (%s)", n->id ? n->id : ""); break;
        case TYPE_RETURN: printf("Return (ferot)"); break;
        case TYPE_INPUT: printf("Input (nao)"); break;
        case TYPE_ARRAY_LITERAL: printf("Array Literal ([])"); break;
        case TYPE_ARRAY_INDEX: printf("Array Index (%s[])", n->id ? n->id : ""); break;
        case TYPE_BINOP: {
            printf("BinaryOp (");
            if (n->op == PLUS) printf("+");
            else if (n->op == MINUS) printf("-");
            else if (n->op == MUL) printf("*");
            else if (n->op == DIV) printf("/");
            else if (n->op == EQ) printf("==");
            else if (n->op == NE) printf("!=");
            else if (n->op == LE) printf("<=");
            else if (n->op == GE) printf(">=");
            else if (n->op == LT) printf("<");
            else if (n->op == GT) printf(">");
            printf(")");
            break;
        }
    }
    printf("\",\"children\":[");
    int has_child = 0;
    if (n->left) {
        print_node_ast_json(n->left);
        has_child = 1;
    }
    if (n->right) {
        if (has_child) printf(",");
        print_node_ast_json(n->right);
        has_child = 1;
    }
    if (n->else_part) {
        if (has_child) printf(",");
        print_node_ast_json(n->else_part);
        has_child = 1;
    }
    if (n->type == TYPE_FOR && n->next) {
        if (has_child) printf(",");
        print_node_ast_json(n->next);
        has_child = 1;
    }
    printf("]}");
    if (n->type != TYPE_FOR && n->next) {
        printf(",");
        print_node_ast_json(n->next);
    }
}

void print_ast_json(Node* root) {
    printf("\n---AST_JSON_START---\n{\"type\":\"Program Root\",\"children\":[");
    if (root) print_node_ast_json(root);
    printf("]}\n---AST_JSON_END---\n");
    fflush(stdout);
}

void execute_program(Node* root) {
    if (show_ast_flag) {
        print_ast_json(root);
    }
    Node* cur = root;
    while (cur && !is_returning) {
        eval(cur);
        cur = cur->next;
    }
}

void yyerror(const char *s) {
    fprintf(stderr, "Arre Bhai! Syntax-e somossa peyechi (Line %d): %s\n", line_num, s);
}

int main(int argc, char** argv) {
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--ast") == 0 || strcmp(argv[i], "-ast") == 0) {
            show_ast_flag = 1;
        }
    }
    return yyparse();
}
