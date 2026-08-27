CC = gcc
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
