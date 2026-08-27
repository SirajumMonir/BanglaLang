# 🇧🇩 BanglaLang v1.1 & v1.2 — Major Language & Compiler Release Notes

> **Detailed documentation of user-defined functions, float numbers, booleans, arrays/lists, for-loops, runtime input support, Express backend integration, and Cyber Bento IDE UX upgrades.**

---

## 📑 Overview of Upgrades

This release introduces advanced programming constructs to **BanglaLang**, making it a versatile language with User-Defined Functions, Floating-Point Math, Boolean Constants, Array Data Structures (`talika`), For-Loops (`jonno`), Runtime Input (`nao`), AST-based Call Stacks, and Monaco IDE Enhancements.

---

## 🚀 1. Advanced Language Features (v1.1 & v1.2)

### 🧩 1. User-Defined Functions (`kaaj` & `ferot`)
Declare reusable functions with parameters and return values:
```c
kaaj jog(a, b) {
    ferot a + b;
}

dhoro result = jog(12.5, 7.5);
bolo "Result: " + result; // Output: Result: 20
```

### 📊 2. Array / List Data Structure (`talika`)
Declare and manipulate list collections and element indexing:
```c
dhoro talika numbers = [10, 20, 30, 40];
bolo "Second item: " + numbers[1]; // Output: 20
```

### 🔄 3. Fixed Iteration Loop (`jonno` / For-Loop)
Standard 3-part loop construct for fixed iterations:
```c
jonno (dhoro i = 0; i < 4; dhoro i = i + 1;) {
    bolo "Item " + i + ": " + numbers[i];
}
```

### 🔢 4. Floating-Point Numbers (`VAL_FLOAT`)
Full support for decimal numbers and mixed-type math operations:
```c
dhoro pi = 3.1416;
dhoro radius = 5.0;
dhoro area = pi * (radius * radius);
bolo "Area: " + area;
```

### 🟢 5. Booleans (`shotto` & `mittha`)
First-class boolean constants for clean logical conditions:
```c
dhoro is_active = shotto;
jodi (is_active) {
    bolo "Status: Active!";
}
```

### 📥 6. Runtime Input (`nao`)
Read inputs dynamically from stdin stream:
```c
dhoro age = nao("Enter your age: ");
bolo "Age: " + age;
```

### 🔤 7. String Support & Concatenation (`+`, `==`, `!=`)
Double-quoted strings with dynamic concatenation and comparison:
```c
dhoro name = "BanglaLang";
bolo "Language: " + name;
```

---

## 🛠️ 2. Core Compiler Architecture (C, Flex, Bison)

### 🔹 Flex Lexer (`core/lexer.l`)
- Tokens added: `KAAJ`, `FEROT`, `NAO`, `SHOTTO`, `MITTHA`, `TALIKA`, `JONNO`, `FLOAT_NUMBER`, `COMMA`, `LBRACKET`, `RBRACKET`.
- Regex rule for floats: `[0-9]+\.[0-9]+`.

### 🔹 Bison Parser & AST Evaluator (`core/parser.y`)
- **Type System (`Value` struct)**: `VAL_INT`, `VAL_FLOAT`, `VAL_STR`, `VAL_ARR`.
- **AST Nodes (`Node` struct)**: `TYPE_FUNC_DECL`, `TYPE_FUNC_CALL`, `TYPE_RETURN`, `TYPE_INPUT`, `TYPE_FLOAT`, `TYPE_FOR`, `TYPE_ARRAY_LITERAL`, `TYPE_ARRAY_INDEX`.
- **Call Stack & Scoping**: Function call frame saving (`saved_sym_count`), parameter binding, return stack management, array bounds safety checks, and scope restoration.

---

## ⚡ 3. Express Backend API (`backend/server.js`)

* **Endpoints**: `GET /api/health`, `POST /api/run`.
* **Single-Port Architecture**: Express server on port 5000 hosts both the API and the static frontend UI.
* **5-Second Timeout Protection**: Guard against infinite loops.

---

## 🎨 4. Cyber Bento Web IDE (`frontend/index.html`)

* **Monaco Monarch Tokenizer**: Syntax highlighting for `kaaj`, `ferot`, `nao`, `shotto`, `mittha`, `talika`, `jonno`.
* **Monaco Font Measurement Fix**: Explicit `#editorContainer` monospace CSS rules & `document.fonts.ready` re-measurement.
* **Custom Right-Arrow Handler**: Prevents automatic line wrap at end of line.
* **Smooth Movement UX**: `smoothScrolling: true`, `lineHeight: 24`, `cursorSmoothCaretAnimation: 'on'`.
* **6 Preset Templates**: Variables, Logic, Loops, Factorial, Functions & Floats, and Array & For-Loops (`talika`/`jonno`).
* **🌳 Live AST Tree Visualizer**: Interactive SVG/DOM Tree Diagram tab in the IDE showing real-time parser syntax hierarchy.

---

## 🌳 5. AST (Abstract Syntax Tree) Live Diagram Viewer

- **C Compiler JSON Export**: `banglalang.exe --ast` flag outputs complete JSON AST node structures directly from Bison parse trees.
- **Express AST Payload**: `POST /api/run` returns `{ output, ast, executionTimeMs }`.
- **Interactive UI Tree**: The IDE features a dual-tab terminal (`💻 টার্মিনাল` / `🌳 AST ট্রি ভিউয়ার`) with neon-glowing syntax tree hierarchy rendering.

---

## 🎛️ 6. Resizable Split Panes & Collapsible Sidebar (v1.4 UI Upgrade)

- **Resizable Split Panes (`resizerLeft` & `resizerRight`)**:
  - Added drag-and-drop splitter bars between the 3 IDE columns (Left Sidebar, Middle Monaco Editor, Right Terminal/AST card).
  - Dynamic drag listeners continuously update panel widths and trigger real-time `editor.layout()` calls for instant Monaco scaling.
- **Collapsible Left Sidebar (`📂 সাইডবার টগল`)**:
  - Added header toggle button to smoothly collapse/expand the left sidebar.
  - Automatically expands the Monaco Editor to fill the screen for a full-width distraction-free coding experience.

---

## 7. 🌳 Section 7: Inline AST Panel Zoom & Auto-Fit Engine (v1.5 Upgrade)

### 📌 Summary of Features Added
- **Unified Clean CSS Zoom Engine**:
  - Separated CSS `zoom` and `transform: scale()` into a single clean renderer (`applyScaleToWrapper`), resolving compounding scale bugs where clicking zoom shrank nodes exponentially.
- **Initial AST Screen Auto-Fit (`🔍 autoFitAstInline`)**:
  - Switching to the `🌳 AST ট্রি` tab or executing code automatically measures panel width vs tree width and scales the inline tree to fit the card perfectly.
- **Inline Panel Toolbar (`➖`, `100%`, `➕`, `🔍 ফিট`, `↺`, `🔍 ফুলস্ক্রিন`)**:
  - Added inline **`🔍 ফিট`** button directly in the right panel AST card header for instant 1-click tree fitting.
  - Smooth wheel zoom & pan-dragging support inside `#astViewContainer`.

---

## 8. 💻 Section 8: VS Code Style Bottom Output Panel & Dual Dock Switcher (v1.6 Upgrade)

### 📌 Summary of Features Added
- **VS Code Style Bottom Output Drawer**:
  - Restructured the IDE workspace layout (`#middleWorkspace`) placing Terminal Console & AST Visualizer horizontally underneath the Monaco Editor.
  - Gives AST Trees full screen width (~1200px+) right out of the box, eliminating tree squishing or side-scroll truncation.
- **Dual Dock Layout Switcher (`📌 ডক পজিশন`)**:
  - Added header toggle button to dynamically switch between **VS Code Bottom Dock Mode** (`📌 ডক: নিচে`) and **Bento Right Dock Mode** (`📌 ডক: ডানে`).
  - Seamlessly re-parents `#outputCardContainer` in DOM without breaking event listeners or AST state.
- **Vertical Drag Resizer Bar (`#resizerBottom`)**:
  - Added interactive horizontal drag bar between editor and bottom drawer for custom vertical panel height adjustment.
  - Automatically triggers Monaco `editor.layout()` and `autoFitAstInline()` upon resize.

---

## 9. 🧹 Section 9: Permanent VS Code Bottom Panel & UX Cleanup (v1.7 Upgrade)

### 📌 Summary of Features Added & Bugs Fixed
- **Fixed Sidebar Toggle Output Panel Bug**:
  - Fixed output panel disappearing when left sidebar was toggled off. Statically locked `#outputCardContainer` inside `#bottomOutputPanel` under `#editorPanel`.
  - Closing the sidebar now seamlessly expands both editor and bottom output panel across **100% full screen width**.
- **Permanent VS Code Style Bottom Panel**:
  - Removed unused Dock Position switcher button (`📌 ডক পজিশন`) and right side panel nodes, locking the output drawer permanently at the bottom for maximum wide tree visibility.
- **Left Resizer Bar Removal for Better UX**:
  - Removed `#resizerLeft` split handle to clean up UX. Left sidebar now collapses and expands cleanly via header button with fixed 320px (`w-80`) width.
- **Retained Interactive Vertical Resizer (`#resizerBottom`)**:
  - Interactive row drag handle remains active between editor and bottom drawer for adjusting vertical drawer height (120px to 600px).

---

## 10. 🎨 Section 10: Viewport Height Lock & UX Typography Overhaul (v1.8 Upgrade)

### 📌 Summary of Features Added & Bugs Fixed
- **Strict Viewport Height Anchoring (`h-screen` / `h-[calc(100vh-3.25rem)]`)**:
  - Locked `body` to `h-screen flex flex-col overflow-hidden` and `<main>` to `h-[calc(100vh-3.25rem)] min-h-0`.
  - Added `hidden` toggle class to `#leftPanel`. Closing the left sidebar now expands Monaco Editor & Bottom Output Panel across **100% full screen width** while keeping the bottom panel **100% visible on screen**.
- **Monaco Line-Height & Font Size Tuning**:
  - Tuned editor font size to `13.5px`, line-height to `21px` (Compact Golden Ratio 1.55), and editor padding to `{ top: 10, bottom: 10 }` for crisp, compact readability.
- **Header & Bento Panel Height Optimization**:
  - Reduced main top bar height from `h-16` (64px) to **`h-13` (52px)**, saving 12px vertical space for code and terminal output.
  - Compacted card headers from `h-10` to **`h-9` (36px)**.
- **Terminal & Sidebar Typography Polish**:
  - Set terminal font to `text-[12px] leading-[1.6]` with `p-3.5` padding.
  - Compacted sidebar snippet buttons (`px-3 py-2 text-xs`) and syntax reference items (`py-1.5 px-2.5 text-[10px]`).

---

## 11. 💻 Section 11: Official Visual Studio Code (VS Code) IDE Theme Overhaul (v1.9 Upgrade)

### 📌 Summary of Features Added & Bugs Fixed
- **Official VS Code Hex Palette**:
  - Implemented exact VS Code hex colors: Activity Bar (`#333333`), Primary Sidebar (`#252526`), Editor & Output Panel (`#1E1E1E`), Borders (`#3C3C3C`), and Status Bar (`#007ACC`).
- **VS Code Titlebar & Menu System**:
  - Integrated top window bar with standard IDE menus (`File`, `Edit`, `Selection`, `View`, `Go`, `Run`, `Help`), file title `main.bl`, and compiler status badge.
- **Activity Bar & Primary Sidebar Layout**:
  - Added 48px slim vertical activity bar on far left with 5 action icons (Explorer, Search, Source Control, Run/Debug, Extensions).
  - Primary sidebar features collapsible `BANGLALANG SNIPPETS` accordion, 6 template buttons (`dhoro`, `jodi`, `jotokhon`, `complex`, `kaaj`, `talika`), and syntax reference guide.
- **Monaco Code Editor Tab & Typography**:
  - VS Code dark syntax highlighting theme (`#569CD6` keywords, `#CE9178` strings, `#B5CEA8` numbers), `main.bl` editor tab with cyan accent, `Fira Code` font, line numbers, and `Ctrl+Enter` execution shortcut.
- **Integrated Output Panel Drawer & AST Visualizer**:
  - Resizable bottom panel titled `OUTPUT` (terminal console) and `🌳 AST DIAGRAM` (interactive tree diagram with zoom, fit, pan, and fullscreen modal).
- **Status Bar (100% Bottom Strip)**:
  - 22px status bar displaying Git branch (`main*`), error/warning counts (`0 0`), line/col position (`Ln 1, Col 1`), spacing (`Spaces: 4`), encoding (`UTF-8`), line endings (`LF`), and `BanglaLang` mode.

---

## 12. 📢 Section 12: Smart Bangla Compiler Error Diagnostic System (v2.0 Upgrade)

### 📌 Summary of Features Added & Bugs Fixed
- **Bison Verbose Parser Mode (`%error-verbose`)**:
  - Configured `core/parser.y` with Bison's `%error-verbose` directive for rich context on unexpected tokens and missing syntax elements.
- **Smart Bangla Error Translator Engine (`formatBanglaDiagnosticError`)**:
  - Implemented pattern-matching error translation engine in `backend/server.js` converting cryptic Flex/Bison errors into simple, clear Bengali diagnostics.
  - Automatically handles:
    - ❌ **Missing Semicolons**: `সেমিকোলনের (;) অভাব চিহ্নিতকরণ`
    - ❌ **Bracket Mismatches**: `ফার্স্ট/সেকেন্ড ব্র্যাকেটের জোড়া ত্রুটি`
    - ❌ **Unexpected EOF**: `কোড অসম্পূর্ণ থাকা`
    - ❌ **Undefined Variables & Functions**: `'dhoro' বা 'kaaj' ছাড়া ব্যবহারের সতর্কতা`
    - ❌ **Division by Zero & Array Bounds**: `শূণ্য দিয়ে ভাগ বা ইনডেক্স বহির্ভূত এক্সেস`
- **Interactive Bangla Diagnostic Terminal Card (`frontend/index.html`)**:
  - Designed red/emerald diagnostic card in terminal drawer displaying:
    - ❌ **Error Title**
    - 📌 **Exact Line Number**
    - 📝 **Bengali Explanation**
    - 💡 **Actionable Solution Tip (সমাধান পরামর্শ)**
    - 🔍 Collapsible Raw Compiler Output dropdown for advanced debugging.

---

## 13. 🐞 Section 13: FOR Loop Body Pointer Collision & Array String Concatenation Fix (v2.1 Upgrade)

### 📌 Summary of Features Added & Bugs Fixed
- **FOR Loop Dedicated `body` Pointer (`core/parser.y`)**:
  - Resolved `TYPE_FOR` loop body pointer collision in Bison AST structure where `$$->next` was shared between loop body and program statement chaining.
  - Added dedicated `body` pointer to `Node` struct (`$$->body = $8;`).
  - Completely eliminated the 5th extra iteration bug in `jonno` (FOR loop) and fixed the resulting false `Array Index Out of Bounds` error on Template 6.
- **Array String Formatting in Concatenation (`value_to_string`)**:
  - Implemented `value_to_string` helper function in `core/parser.y` and `setup_project.py`.
  - When concatenating strings with arrays (`+`), arrays are now formatted properly as `[10, 20, 30, 40]` instead of printing default integer `0`.

---

## 14. ✨ Section 14: Auto Code Formatter (BanglaLang Prettier: `Shift + Alt + F`) (v2.2 Upgrade)

### 📌 Summary of Features Added & Bugs Fixed
- **BanglaLang Code Formatter Engine (`formatBanglaCode`)**:
  - Built line-by-line indenter and tokenizer formatting 4-space indentations for nested `{ ... }` blocks.
  - Standardized keyword spacing (`dhoro`, `bolo`, `jodi`, `nawle`, `jotokhon`, `kaaj`, `jonno`, `ferot`, `talika`).
  - Formatted binary operator spacing (`=`, `+`, `-`, `*`, `/`, `==`, `!=`, `<=`, `>=`, `<`, `>`).
  - Preserved single-line comments (`// ...`) and quote strings.
- **VS Code Keyboard Shortcut (`Shift + Alt + F`)**:
  - Registered `Shift + Alt + F` action in Monaco Editor and global document keyboard listener.
- **UI Format Buttons & VS Code Status Toast**:
  - Added **Format (Shift+Alt+F)** button in top header bar next to `Run` and magic wand icon in editor tab action toolbar.
  - Displays `✨ BanglaLang Code Formatted!` toast in the bottom right corner upon formatting code.

---

## 15. 🚀 Section 15: Multi-File Project Explorer (LocalStorage Sync) & Standard Math/Time Library (v3.0 Major Release)

### 📌 Summary of Features Added & Bugs Fixed
- **Multi-File Project Explorer UI (`frontend/index.html`)**:
  - Integrated `PROJECT FILES` accordion tree in the Primary Sidebar.
  - Added **New File** (`📄+`), **Save Project** (`💾`), **Rename File** (`✏️`), and **Delete File** (`🗑️`) controls.
  - Built interactive editor tab manager dynamically rendering open `.bl` file tabs (`main.bl`, `math_helper.bl`).
- **Browser LocalStorage Persistence Engine**:
  - Implemented `FileManager` JavaScript module saving all files, tab states, and active code to `localStorage`.
  - Added auto-save on typing (`editor.onDidChangeModelContent`), ensuring zero data loss across browser refreshes (F5).
- **BanglaLang Built-in Math & Time Standard Library (`core/parser.y`)**:
  - Integrated built-in constant: `gonit_pi` / `PI` (`3.14159265`).
  - Integrated built-in C `<math.h>` functions: `gonit_sqrt(x)`, `gonit_pow(x, y)`, `gonit_abs(x)`, `gonit_max(a, b)`, `gonit_min(a, b)`, `gonit_round(x)`.
  - Integrated built-in time function: `somoy()` returning Unix timestamp in seconds using C `<time.h>`.
  - Added Example Template 7: `7. Math & Time Library`.

---

## 16. 🔗 Section 16: Online Code Sharing & 1-Click `.bl` Export/Import (v3.1 Upgrade)

### 📌 Summary of Features Added & Bugs Fixed
- **Online Code Share Engine (`shareBanglaCode`)**:
  - Encodes active Monaco Editor code using UTF-8 safe Base64 URL parameter (`?code=...`).
  - Automatically copies shareable URL to clipboard and displays `🔗 Shareable Link Copied to Clipboard!`.
  - Automatically decodes shared URLs on page load and opens `shared_code.bl` tab in Monaco Editor.
- **1-Click `.bl` File Export / Download (`exportBanglaFile`)**:
  - Triggers instant browser download of active file (e.g. `main.bl` or `math_helper.bl`) as `.bl` UTF-8 file.
- **1-Click `.bl` File Import / Upload (`uploadBanglaFile`)**:
  - Adds file input picker allowing users to upload local `.bl` files directly into the File Explorer and editor.

---

## 🛠️ Summary of Changed Files

| File Path | Description of Upgrades |
| :--- | :--- |
| [`core/lexer.l`](file:///d:/Compiler%20Design/BanglaLang/core/lexer.l) | Flex rules for `kaaj`, `ferot`, `nao`, `shotto`, `mittha`, `talika`, `jonno`, floats & brackets |
| [`core/parser.y`](file:///d:/Compiler%20Design/BanglaLang/core/parser.y) | Bison grammar with `<math.h>`, `<time.h>`, `gonit_*` functions, `somoy()` formatted date-time, and `gonit_pi` constant |
| [`backend/server.js`](file:///d:/Compiler%20Design/BanglaLang/backend/server.js) | Express API server with AST Evaluator for built-in math/time functions and output sanitizer |
| [`frontend/index.html`](file:///d:/Compiler%20Design/BanglaLang/frontend/index.html) | VS Code IDE UI with Code Share button, `.bl` Export/Download, `.bl` Import/Upload, Multi-File Explorer, and LocalStorage persistence |
| [`setup_project.py`](file:///d:/Compiler%20Design/BanglaLang/setup_project.py) | Python project generator synced with complete core, backend v3.1, and frontend code |
| [`RELEASE_NOTES.md`](file:///d:/Compiler%20Design/BanglaLang/RELEASE_NOTES.md) | Release history documentation updated through v3.1 Code Sharing & Export/Import release |

---
*BanglaLang v3.1 — Empowering Bengali Programming* 🇧🇩
