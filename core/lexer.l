%{
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
