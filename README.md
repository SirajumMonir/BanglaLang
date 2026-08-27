# 🇧🇩 BanglaLang (বাংলা-ল্যাং)

> **A custom Bengali-keyword-based programming language compiler, Express runtime backend engine, and dark Cyber Bento-Grid IDE.**

---

## 🚀 Overview

**BanglaLang** is an educational and functional compiler that interprets code written in Bengali transliterated keywords (`dhoro`, `bolo`, `jodi`, `nawle`, `jotokhon`). 

It is built in a modern 3-tier architecture:
1. **Core Engine**: C, Flex (Lexer), and Bison (Parser/AST Evaluator).
2. **Backend**: Express.js API managing process execution via secure child process streams.
3. **Frontend**: Standalone Cyber Bento-Grid Playground powered by Monaco Editor and Tailwind CSS.

---

## 📂 Project Architecture

```text
BanglaLang/
├── setup_project.py       # One-click automated setup & file generation script
├── .gitignore             # Git ignore rules for node_modules and C binaries
├── README.md              # Project documentation
├── core/
│   ├── lexer.l            # Flex Lexical Token Analyzer
│   ├── parser.y           # Bison Grammar Rules, AST Evaluator & Symbol Table
│   └── Makefile           # Windows/Linux compilation rules
├── backend/
│   ├── package.json       # Express & CORS dependencies
│   └── server.js          # REST API server (Port 5000)
└── frontend/
    └── index.html         # Cyber Bento UI with Monaco Editor
```

---

## 📝 Syntax & Language Features

| Feature | BanglaLang Syntax | Equivalent (C / JS) |
| :--- | :--- | :--- |
| **Variable** | `dhoro x = 10;` | `int x = 10;` / `let x = 10;` |
| **Print Output** | `bolo x + 5;` | `printf("%d\n", x + 5);` / `console.log(x + 5);` |
| **If-Else** | `jodi (x > 5) { ... } nawle { ... }` | `if (x > 5) { ... } else { ... }` |
| **While Loop** | `jotokhon (x > 0) { ... }` | `while (x > 0) { ... }` |
| **Operators** | `+`, `-`, `*`, `/`, `==`, `!=`, `<`, `>`, `<=`, `>=` | Standard arithmetic & relational |

### 💡 Example Code (Factorial Calculation)
```c
dhoro n = 5;
dhoro fact = 1;

jotokhon (n > 0) {
    dhoro fact = fact * n;
    dhoro n = n - 1;
}

bolo fact; // Output: 120
```

---

## ⚡ Quick Start

### 1. Build the Compiler (C/Flex/Bison)
```bash
cd core
make
```

### 2. Start the Backend Server
```bash
cd backend
npm install
node server.js
```
The server will run on `http://localhost:5000`.

### 3. Open the Frontend UI
Simply open `frontend/index.html` in any modern web browser or host with any static file server!

---

## 🛠️ Automated Setup
You can also generate and sync the entire project on a fresh machine with:
```bash
python setup_project.py
```
