# 🇧🇩 BanglaLang — Complete Project Execution & Troubleshooting Guide

> **A step-by-step developer guide for building, running, and troubleshooting the BanglaLang compiler, Express backend API, and Cyber Bento Web IDE.**

---

## 📑 Table of Contents
1. [Project Overview & Architecture](#-project-overview--architecture)
2. [Prerequisites & System Requirements](#-prerequisites--system-requirements)
3. [Step-by-Step Execution Guide](#-step-by-step-execution-guide)
   - [Step 1: Build the C Compiler Binary](#step-1-build-the-c-compiler-binary)
   - [Step 2: Start the Backend Server & Web IDE](#step-2-start-the-backend-server--web-ide)
   - [Step 3: Open the Web Playground](#step-3-open-the-web-playground)
4. [How to Stop / Deactivate the Server](#-how-to-stop--deactivate-the-server)
5. [Troubleshooting & Common Issues](#-troubleshooting--common-issues)
   - [Issue 1: Compiler Binary Missing](#issue-1-compiler-binary-missing-banglalangexe-not-found)
   - [Issue 2: 'node' Command Not Recognized](#issue-2-node-command-is-not-recognized-in-powershell)
   - [Issue 3: Port 5000 Already in Use (EADDRINUSE)](#issue-3-port-5000-already-in-use-eaddrinuse)
   - [Issue 4: Code Execution Timeout](#issue-4-code-execution-timeout-5s-limit)
6. [Quick Cheat-Sheet of Commands](#-quick-cheat-sheet-of-commands)

---

## 🏗️ Project Overview & Architecture

**BanglaLang** operates in a 3-tier architecture:

```text
BanglaLang/
├── core/                  # Layer 1: C Compiler Engine (Flex + Bison)
│   ├── lexer.l            # Lexical rules (Tokens)
│   ├── parser.y           # Syntax grammar rules + AST Evaluator
│   ├── Makefile           # Windows/Linux compilation rules
│   └── banglalang.exe     # Compiled binary engine
├── backend/               # Layer 2: Express.js REST API Server
│   ├── package.json       # Node.js dependencies (express, cors)
│   └── server.js          # REST API + Static Frontend Server (Port 5000)
├── frontend/              # Layer 3: Cyber Bento Web IDE
│   └── index.html         # Monaco Editor UI + Bengali Syntax Rules
└── PROJECT_RUN_GUIDE.md   # Project Execution Guide (This file)
```

---

## 📋 Prerequisites & System Requirements

Before running the project, make sure you have the following installed:

1. **GCC Compiler & Make Tools**:
   - MinGW / GCC (`gcc`)
   - Flex (`flex` or `win_flex`)
   - Bison (`bison` or `win_bison`)
   - `make` utility
2. **Node.js** (v18.x or v20.x or higher)
3. **Web Browser** (Google Chrome, Microsoft Edge, Brave, or Firefox)

---

## 🚀 Step-by-Step Execution Guide

### Step 1: Build the C Compiler Binary

Open PowerShell or Terminal and navigate to the `core/` folder to compile the language engine:

```powershell
cd "d:\Compiler Design\BanglaLang\core"
make
```

> **What this does:** `make` runs Flex on `lexer.l`, Bison on `parser.y`, and compiles `lex.yy.c` and `parser.tab.c` into `banglalang.exe`.

---

### Step 2: Start the Backend Server & Web IDE

Navigate to the `backend/` folder:

```powershell
cd "d:\Compiler Design\BanglaLang\backend"
```

1. **Install dependencies** *(Required only once on a new machine)*:
   ```powershell
   npm install
   ```

2. **Start the Express server**:
   ```powershell
   node server.js
   ```
   *(or `npm start`)*

When successfully launched, you will see:
```text
=========================================
🚀 BanglaLang Backend running on port 5000
📌 Compiler Binary: D:\Compiler Design\BanglaLang\core\banglalang.exe
=========================================
```

---

### Step 3: Open the Web Playground

Open your browser and visit:
👉 **`http://localhost:5000`**

- Select any pre-built example code from the **Code Templates** on the left.
- Click **"কোড রান করো (Ctrl+Enter)"** to compile and view terminal output!

---

## 🛑 How to Stop / Deactivate the Server

### Method A: Terminal Keyboard Shortcut (Recommended)
In the terminal window running `node server.js`, press:
* **`Ctrl + C`**
* Type **`Y`** and press **Enter** if prompted (`Terminate batch job (Y/N)?`).

### Method B: Stop via Command (If backgrounded or unresponsive)
Run this in a PowerShell window to force-stop port 5000:
```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
```

---

## 🛠️ Troubleshooting & Common Issues

### Issue 1: Compiler Binary Missing (`banglalang.exe` not found)
* **Symptom:** Terminal output in Web UI displays:
  `BanglaLang compiler binary paoa jayni... Kripoya core folder-e giye make command run korun.`
* **Root Cause:** `banglalang.exe` has not been compiled or was deleted.
* **Fix:**
  1. Open terminal in `core/` directory:
     ```powershell
     cd "d:\Compiler Design\BanglaLang\core"
     make
     ```
  2. Ensure `banglalang.exe` is created in `core/`.

---

### Issue 2: 'node' Command is Not Recognized in PowerShell
* **Symptom:** `node : The term 'node' is not recognized as the name of a cmdlet...`
* **Root Cause:** Node.js path is missing from your system Environment Variables (`PATH`).
* **Fix:** Use the full executable path in PowerShell:
  ```powershell
  & "C:\Program Files\nodejs\node.exe" server.js
  ```
  *(Or specify your installed Node.js binary path)*

---

### Issue 3: Port 5000 Already in Use (`EADDRINUSE`)
* **Symptom:** Server crashes on startup with `Error: listen EADDRINUSE: address already in use :::5000`.
* **Root Cause:** A previous server process is still running on port 5000.
* **Fix:** Kill the existing process using PowerShell:
  ```powershell
  Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force
  ```
  Then restart `node server.js`.

---

### Issue 4: Code Execution Timeout (5s Limit)
* **Symptom:** `Execution Timed Out (5s limit exceeded). Infinite loop sombhoboto!`
* **Root Cause:** The written BanglaLang code has an infinite loop (e.g. `jotokhon (1 > 0)` without updating variable).
* **Fix:** Check loop conditions in your BanglaLang code to ensure loop terminates properly.

---

## ⚡ Quick Cheat-Sheet of Commands

| Action | PowerShell Command |
| :--- | :--- |
| **Build Compiler** | `cd core; make` |
| **Run Backend & IDE** | `cd backend; node server.js` |
| **Open Playground** | Browser -> `http://localhost:5000` |
| **Stop Server** | `Ctrl + C` (in server terminal) |
| **Kill Port 5000 Process** | `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force` |

---
*Created for BanglaLang Project — Happy Coding!* 🇧🇩
