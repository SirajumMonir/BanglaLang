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

    // Spawn child process with direct stdin stream (immune to Windows space in path bugs)
    const child = spawn(BINARY_PATH, [], {
        windowsHide: true
    });

    // Timeout safety (5 seconds max execution)
    const timer = setTimeout(() => {
        if (!isFinished) {
            isFinished = true;
            child.kill();
            return res.json({
                output: stdoutData,
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
            error: `Compiler execution error: ${err.message}`,
            executionTimeMs: Date.now() - startTime
        });
    });

    child.on('close', (codeStatus) => {
        if (isFinished) return;
        isFinished = true;
        clearTimeout(timer);
        res.json({
            output: stdoutData,
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
    </style>
</head>
<body class="text-slate-100 min-h-screen flex flex-col font-sans overflow-hidden">
    <!-- Header -->
    <header class="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur px-6 flex items-center justify-between shrink-0 z-10">
        <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 via-teal-600 to-cyan-600 flex items-center justify-center font-bold text-white shadow-lg shadow-emerald-500/20 font-bengali text-lg">
                বাং
            </div>
            <div>
                <div class="flex items-center gap-2">
                    <h1 class="text-lg font-extrabold tracking-tight bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">BanglaLang</h1>
                    <span class="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">v1.0 Compiler</span>
                </div>
                <p class="text-xs text-slate-500">বাংলা প্রোগ্রামিং ল্যাঙ্গুয়েজ ক্লাউড প্লেগ্রাউন্ড</p>
            </div>
        </div>

        <!-- Center Controls -->
        <div class="flex items-center gap-3">
            <div id="backendStatusBadge" class="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-slate-900 border border-slate-800 text-slate-400">
                <span id="statusDot" class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
                <span id="statusText">Checking Backend...</span>
            </div>
            <button id="runBtn" class="bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold px-6 py-2 rounded-xl text-sm transition-all duration-200 flex items-center gap-2 shadow-lg shadow-emerald-500/25 active:scale-95">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                <span>কোড রান করো (Ctrl+Enter)</span>
            </button>
        </div>
    </header>

    <!-- Main Bento Grid Layout -->
    <main class="flex-1 p-4 grid grid-cols-12 gap-4 overflow-hidden">
        <!-- Left Sidebar / Snippets & Docs Bento (Col 1-3) -->
        <div class="col-span-12 md:col-span-3 flex flex-col gap-4 overflow-hidden">
            <!-- Snippets Card -->
            <div class="bento-card rounded-2xl p-4 flex flex-col shrink-0">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">কোড এক্সাম্পল</span>
                    <span class="text-[10px] text-emerald-400 font-mono">Templates</span>
                </div>
                <div class="grid grid-cols-1 gap-2">
                    <button onclick="loadSnippet('vars')" class="snippet-btn text-left text-xs p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">১. ভ্যারিয়েবল ও গণিত</span>
                        <span class="text-[10px] font-mono text-slate-500">dhoro / bolo</span>
                    </button>
                    <button onclick="loadSnippet('logic')" class="snippet-btn text-left text-xs p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">২. শর্ত যাচাই (If-Else)</span>
                        <span class="text-[10px] font-mono text-slate-500">jodi / nawle</span>
                    </button>
                    <button onclick="loadSnippet('loop')" class="snippet-btn text-left text-xs p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">৩. লুপ বা পুনরাবৃত্তি</span>
                        <span class="text-[10px] font-mono text-slate-500">jotokhon</span>
                    </button>
                    <button onclick="loadSnippet('complex')" class="snippet-btn text-left text-xs p-2.5 rounded-xl bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-emerald-500/40 transition flex items-center justify-between">
                        <span class="font-medium text-slate-200">৪. লজিক ও ফ্যাক্টোরিয়াল</span>
                        <span class="text-[10px] font-mono text-slate-500">Full Demo</span>
                    </button>
                </div>
            </div>

            <!-- Syntax Reference Bento -->
            <div class="bento-card rounded-2xl p-4 flex-1 overflow-y-auto">
                <div class="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono mb-3">সিনট্যাক্স সহায়িকা (Cheat Sheet)</div>
                <div class="space-y-3 text-xs">
                    <div class="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-emerald-400 font-semibold">dhoro x = 10;</div>
                        <div class="text-slate-400 text-[11px]">ভ্যারিয়েবল ডিফাইন করতে ব্যবহৃত হয়</div>
                    </div>
                    <div class="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-cyan-400 font-semibold">bolo x + 5;</div>
                        <div class="text-slate-400 text-[11px]">স্ক্রিনে আউটপুট প্রিন্ট করে</div>
                    </div>
                    <div class="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-amber-400 font-semibold">jodi (a == b) { ... } nawle { ... }</div>
                        <div class="text-slate-400 text-[11px]">শর্তাধীন লজিক্যাল ব্রাঞ্চিং</div>
                    </div>
                    <div class="p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                        <div class="font-mono text-indigo-400 font-semibold">jotokhon (x > 0) { ... }</div>
                        <div class="text-slate-400 text-[11px]">শর্ত পূরণ হওয়া পর্যন্ত লুপ চলে</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Middle Editor Bento (Col 4-8) -->
        <div class="col-span-12 md:col-span-5 flex flex-col bento-card rounded-2xl overflow-hidden">
            <!-- Editor Top Bar -->
            <div class="h-10 bg-slate-950/80 border-b border-slate-800 px-4 flex items-center justify-between shrink-0">
                <div class="flex items-center gap-2">
                    <span class="w-3 h-3 rounded-full bg-red-500/80 inline-block"></span>
                    <span class="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
                    <span class="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
                    <span class="ml-2 font-mono text-xs text-slate-400">main.bl</span>
                </div>
                <button onclick="clearEditor()" class="text-[11px] text-slate-500 hover:text-slate-300 font-mono transition">রিসেট কোড</button>
            </div>
            <!-- Monaco Container -->
            <div class="flex-1 relative bg-[#090d16]">
                <div id="editorContainer" class="absolute inset-0"></div>
            </div>
        </div>

        <!-- Right Terminal & Stats Bento (Col 9-12) -->
        <div class="col-span-12 md:col-span-4 flex flex-col gap-4 overflow-hidden">
            <!-- Execution Stats Card -->
            <div class="bento-card rounded-2xl p-4 shrink-0 grid grid-cols-3 gap-2 text-center font-mono">
                <div class="p-2 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <div class="text-[10px] text-slate-500">EXEC TIME</div>
                    <div id="execTimeVal" class="text-xs font-bold text-emerald-400">0 ms</div>
                </div>
                <div class="p-2 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <div class="text-[10px] text-slate-500">EXIT CODE</div>
                    <div id="exitCodeVal" class="text-xs font-bold text-slate-300">0</div>
                </div>
                <div class="p-2 rounded-xl bg-slate-900/60 border border-slate-800/80">
                    <div class="text-[10px] text-slate-500">COMPILER</div>
                    <div class="text-xs font-bold text-cyan-400">C/Flex/Bison</div>
                </div>
            </div>

            <!-- Terminal Output Card -->
            <div class="bento-card rounded-2xl flex-1 flex flex-col overflow-hidden">
                <div class="h-10 bg-slate-950/80 border-b border-slate-800 px-4 flex items-center justify-between shrink-0">
                    <div class="flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                        <span class="text-xs font-mono font-bold text-slate-300">টার্মিনাল আউটপুট (Terminal Output)</span>
                    </div>
                    <button onclick="clearTerminal()" class="text-[11px] font-mono text-slate-500 hover:text-slate-300">ক্লিয়ার</button>
                </div>
                <div id="terminal" class="flex-1 p-4 font-mono text-xs overflow-y-auto terminal-glow bg-[#03060a] leading-relaxed text-slate-300 select-text">
                    <div class="text-slate-600 italic">// কোড রান করলে ফলাফল এখানে প্রদর্শিত হবে...</div>
                </div>
            </div>
        </div>
    </main>

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

bolo "5 er Factorial holo: " + fact;`
        };

        // Monaco Language definition for BanglaLang
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' }});
        require(['vs/editor/editor.main'], function() {
            monaco.languages.register({ id: 'banglalang' });
            monaco.languages.setMonarchTokensProvider('banglalang', {
                keywords: ['dhoro', 'bolo', 'jodi', 'nawle', 'jotokhon'],
                tokenizer: {
                    root: [
                        [/\b(dhoro|bolo|jodi|nawle|jotokhon)\b/, 'keyword'],
                        [/"([^"\\]|\\.)*"/, 'string'],
                        [/\b[0-9]+\b/, 'number'],
                        [/\b[a-zA-Z_][a-zA-Z0-9_]*\b/, 'variable'],
                        [/\/\/.*$/, 'comment'],
                        [/[+\-*\/=<>!]+/, 'operator'],
                        [/[{}();]/, 'delimiter']
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
                fontFamily: '"Fira Code", monospace',
                minimap: { enabled: false },
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                padding: { top: 12, bottom: 12 }
            });

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

        function clearTerminal() {
            const terminal = document.getElementById('terminal');
            terminal.innerHTML = '<div class="text-slate-600 italic">// Terminal cleared.</div>';
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
        (os.path.join(base_dir, "core", "lexer.l"), lexer_content),
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