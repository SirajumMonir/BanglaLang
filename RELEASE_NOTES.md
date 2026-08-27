# 🇧🇩 BanglaLang v1.0 — Major Upgrades & Feature Release Notes

> **Detailed documentation of language features, compiler enhancements, string manipulation support, Express backend integration, and Cyber Bento IDE UX upgrades.**

---

## 📑 Overview of Upgrades

This release marks a major evolution of **BanglaLang**, transforming it into a full-featured programming language ecosystem with string manipulation support, AST-based execution, Express REST API runtime, and a Monaco-powered Cyber Bento Web IDE.

---

## 🚀 1. String Support & Advanced Language Features

### 🔤 String Data Type & Concatenation
* **String Literals**: Double-quoted strings are fully supported (e.g. `dhoro msg = "Shabash!";`).
* **String Concatenation (`+`)**: Strings can be concatenated with other strings or numbers dynamically:
  ```c
  dhoro n = 5;
  dhoro fact = 120;
  bolo n + " er Factorial holo: " + fact;
  // Output: 5 er Factorial holo: 120
  ```
* **String Comparisons (`==`, `!=`)**: String equality and inequality checks using standard C `strcmp` inside the AST evaluator.

---

## 🛠️ 2. Core Compiler Architecture (C, Flex, Bison)

### 🔹 Flex Lexer (`core/lexer.l`)
- Tokenized Bengali transliterated keywords: `dhoro`, `bolo`, `jodi`, `nawle`, `jotokhon`.
- String escape sequence parsing regex: `\"([^\"\\]|\\.)*\"`.
- Custom Bengali error reporting for unrecognized tokens.

### 🔹 Bison Parser & AST Evaluator (`core/parser.y`)
- **Dual Value Representation (`Value` struct)**: Supports both `VAL_INT` (integer) and `VAL_STR` (string) values.
- **Dynamic Symbol Table**: Variable storage supporting integer and string scope lookups (up to 512 symbols).
- **AST Node Tree (`Node` struct)**:
  - Binop nodes for arithmetic (`+`, `-`, `*`, `/`) and relational (`==`, `!=`, `<`, `>`, `<=`, `>=`) operations.
  - Statement nodes for Assignment (`TYPE_ASSIGN`), Print (`TYPE_PRINT`), If-Else (`TYPE_IF`), While loop (`TYPE_WHILE`), and Block (`TYPE_BLOCK`).
- **Memory Safety & Error Handling**: Dynamic memory allocation for strings and safe divide-by-zero runtime checks.

---

## ⚡ 3. Express Backend & Single-Port Architecture (`backend/server.js`)

* **REST API Endpoints**:
  - `GET /api/health`: Real-time health check endpoint monitoring binary readiness.
  - `POST /api/run`: Receives code payload, spawns `banglalang.exe` as a child process stream, and returns `stdout`, `stderr`, and `executionTimeMs`.
* **Unified Single-Port Hosting**: Serves static frontend assets via `express.static` directly from `http://localhost:5000`.
* **Execution Timeout Safety**: 5-second process timeout guard against infinite loops.

---

## 🎨 4. Cyber Bento Web IDE & Monaco Editor UX Upgrades (`frontend/index.html`)

* **Custom Monarch Syntax Highlighter**: Custom color tokens for keywords, strings, numbers, operators, and comments.
* **Monaco Font Measurement & Desync Fix**:
  - Applied explicit monospace CSS rules to `#editorContainer` (`font-family: 'Fira Code', 'Consolas', 'Courier New', monospace !important`).
  - Added `document.fonts.ready` web font re-measurement event handler (`monaco.editor.remeasureFonts()`) to eliminate cursor misalignment.
* **Custom Right-Arrow Handler**: Overrode `monaco.KeyCode.RightArrow` to prevent automatic line wrap/jump to the next line when cursor is at line end.
* **Smooth Movement UX**:
  - `smoothScrolling: true`
  - `lineHeight: 24`
  - `cursorSmoothCaretAnimation: 'on'`
  - `cursorBlinking: 'smooth'`
  - `bracketPairColorization: { enabled: true }`
* **Pre-built Templates**: 4 one-click code templates (Variables, Logic, Loops, Factorial Calculation).

---

## 📁 5. Project Automation & Execution Guide

* **`setup_project.py`**: Python automated setup and synchronization script.
* **`PROJECT_RUN_GUIDE.md`**: Complete execution, build instructions, and troubleshooting guide.

---

## 🛠️ Summary of Changed Files

| File Path | Description of Upgrades |
| :--- | :--- |
| [`core/lexer.l`](file:///d:/Compiler%20Design/BanglaLang/core/lexer.l) | Flex rules for String literals and Bengali keywords |
| [`core/parser.y`](file:///d:/Compiler%20Design/BanglaLang/core/parser.y) | Bison grammar, AST evaluator, Value struct, String concatenation & comparison |
| [`backend/server.js`](file:///d:/Compiler%20Design/BanglaLang/backend/server.js) | Express API server with child process execution and static frontend hosting |
| [`frontend/index.html`](file:///d:/Compiler%20Design/BanglaLang/frontend/index.html) | Monaco Editor Cyber Bento UI, font measurement fix, Right-Arrow handler & smooth scrolling |
| [`setup_project.py`](file:///d:/Compiler%20Design/BanglaLang/setup_project.py) | Automated setup script updated with all new features |
| [`PROJECT_RUN_GUIDE.md`](file:///d:/Compiler%20Design/BanglaLang/PROJECT_RUN_GUIDE.md) | Complete build, execution, and troubleshooting documentation |

---
*BanglaLang v1.0 — Empowering Bengali Programming* 🇧🇩
