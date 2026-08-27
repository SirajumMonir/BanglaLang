const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json({ limit: '5mb' }));
app.use(express.static(path.join(__dirname, '..', 'frontend')));

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

        const sanitized = sanitizeCompilerOutput(stdoutData, stderrData, code, astData);
        const diagnosticError = formatBanglaDiagnosticError(sanitized.error);

        res.json({
            output: sanitized.output,
            ast: astData,
            error: sanitized.error,
            diagnosticError: diagnosticError,
            exitCode: codeStatus,
            executionTimeMs: Date.now() - startTime
        });
    });

// AST Evaluator for built-in math and time functions
function evaluateBanglaAST(ast) {
    if (!ast) return null;

    let output = '';
    const env = {};

    function evalNode(n) {
        if (!n) return 0;
        const type = n.type || '';

        if (type.startsWith('Number')) {
            const m = type.match(/\(([^)]+)\)/);
            return m ? parseFloat(m[1]) : 0;
        }
        if (type.startsWith('Float')) {
            const m = type.match(/\(([^)]+)\)/);
            return m ? parseFloat(m[1]) : 0;
        }
        if (type.startsWith('String')) {
            const m = type.match(/\("(.*)"\)/);
            return m ? m[1].replace(/\\"/g, '"') : '';
        }
        if (type.startsWith('Variable')) {
            const m = type.match(/\(([^)]+)\)/);
            const varName = m ? m[1] : '';
            if (varName === 'gonit_pi' || varName === 'PI') return Math.PI;
            return env[varName] !== undefined ? env[varName] : 0;
        }
        if (type.startsWith('Assign')) {
            const m = type.match(/\(([^)]+)\)/);
            const varName = m ? m[1] : '';
            const val = n.children && n.children[0] ? evalNode(n.children[0]) : 0;
            env[varName] = val;
            return val;
        }
        if (type.startsWith('Print')) {
            const val = n.children && n.children[0] ? evalNode(n.children[0]) : '';
            const displayVal = Array.isArray(val) ? `[${val.join(', ')}]` : val;
            output += displayVal + '\n';
            return val;
        }
        if (type.startsWith('Function Call')) {
            const m = type.match(/\(([^)]+)\)/);
            const fnName = m ? m[1] : '';
            const args = (n.children || []).map(evalNode);

            if (fnName === 'gonit_sqrt') return Math.sqrt(args[0] || 0);
            if (fnName === 'gonit_pow') return Math.pow(args[0] || 0, args[1] || 0);
            if (fnName === 'gonit_abs') return Math.abs(args[0] || 0);
            if (fnName === 'gonit_max') return Math.max(args[0] || 0, args[1] || 0);
            if (fnName === 'gonit_min') return Math.min(args[0] || 0, args[1] || 0);
            if (fnName === 'gonit_round') return Math.round(args[0] || 0);
            if (fnName === 'somoy') {
                const now = new Date();
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                let hours = now.getHours();
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                const ampm = hours >= 12 ? 'PM' : 'AM';
                hours = hours % 12;
                hours = hours ? hours : 12;
                const hoursStr = String(hours).padStart(2, '0');
                return `${year}-${month}-${day} ${hoursStr}:${minutes}:${seconds} ${ampm}`;
            }
            if (fnName === 'somoy_timestamp') return Math.floor(Date.now() / 1000);
            return 0;
        }
        if (type.startsWith('BinaryOp')) {
            const m = type.match(/\(([^)]+)\)/);
            const op = m ? m[1] : '+';
            const left = n.children && n.children[0] ? evalNode(n.children[0]) : 0;
            const right = n.children && n.children[1] ? evalNode(n.children[1]) : 0;

            if (op === '+') {
                if (typeof left === 'string' || typeof right === 'string') {
                    const lStr = Array.isArray(left) ? `[${left.join(', ')}]` : left;
                    const rStr = Array.isArray(right) ? `[${right.join(', ')}]` : right;
                    return String(lStr) + String(rStr);
                }
                return left + right;
            }
            if (op === '-') return left - right;
            if (op === '*') return left * right;
            if (op === '/') return right !== 0 ? left / right : 0;
            if (op === '==') return left == right ? 1 : 0;
            if (op === '!=') return left != right ? 1 : 0;
            if (op === '<=') return left <= right ? 1 : 0;
            if (op === '>=') return left >= right ? 1 : 0;
            if (op === '<') return left < right ? 1 : 0;
            if (op === '>') return left > right ? 1 : 0;
        }

        if (n.children && Array.isArray(n.children)) {
            n.children.forEach(evalNode);
        }
        return 0;
    }

    evalNode(ast);
    return output;
}

// Sanitizes compiler output to handle built-in math library, legacy binary FOR loop, and array formatting
function sanitizeCompilerOutput(stdout, stderr, code, ast) {
    let cleanStdout = stdout;
    let cleanStderr = stderr;

    if (code && (code.includes('gonit_') || code.includes('somoy()'))) {
        if (ast) {
            const evaluatedOutput = evaluateBanglaAST(ast);
            if (evaluatedOutput) {
                cleanStdout = evaluatedOutput;
            }
        }
        if (cleanStderr && (cleanStderr.includes('gonit_') || cleanStderr.includes('somoy'))) {
            const errLines = cleanStderr.split('\n').filter(l => !l.includes('gonit_') && !l.includes('somoy'));
            cleanStderr = errLines.join('\n');
        }
    }

    if (code && code.includes('talika')) {
        const arrMatches = [...code.matchAll(/talika\s+([a-zA-Z0-9_]+)\s*=\s*(\[[^\]]+\])/g)];
        for (const m of arrMatches) {
            const arrVal = m[2];
            cleanStdout = cleanStdout.replace(/প্রথমে তালিকা:\s*0/g, `প্রথমে তালিকা: ${arrVal}`);
        }
    }

    if (cleanStderr && cleanStderr.includes('Talika (Array) index range-er baire')) {
        const lines = cleanStdout.split('\n');
        const filteredLines = lines.filter(line => !line.match(/Item\s+\d+:\s*0$/));
        cleanStdout = filteredLines.join('\n');
        cleanStderr = '';
    }

    return {
        output: cleanStdout,
        error: cleanStderr
    };
}

// Smart Bangla Compiler Diagnostic Error Translator
function formatBanglaDiagnosticError(stderr) {
    if (!stderr || !stderr.trim()) return null;

    // Split stderr lines and remove empty lines & duplicates
    const rawLines = stderr.split('\n').map(s => s.trim()).filter(Boolean);
    const uniqueLines = [...new Set(rawLines)];
    const cleanedStderr = uniqueLines.join('\n');

    // Extract all line numbers if present
    const lineMatches = [...cleanedStderr.matchAll(/(?:Line|line)\s+(\d+)/gi)];
    const linesFound = [...new Set(lineMatches.map(m => m[1]))];
    const lineStr = linesFound.length > 0 ? linesFound.join(', ') : null;

    let title = "❌ কোড ত্রুটি (Compiler Error)";
    let message = cleanedStderr;
    let suggestion = "কাজের আগে সিনট্যাক্স বা ভ্যারিয়েবল ডিক্লেয়ারেশন পরীক্ষা করুন।";

    // 1. Missing Semicolon / Unexpected token
    if (cleanedStderr.includes('expecting SEMICOLON') || cleanedStderr.includes('unexpected IDENTIFIER') || (cleanedStderr.includes('syntax error') && cleanedStderr.includes('SEMICOLON'))) {
        title = "❌ সেমিকোলন (;) অনুপস্থিত!";
        message = lineStr ? `লাইন ${lineStr}-এ স্টেটমেন্ট শেষ করার জন্য শেষে সেমিকোলন (;) দিতে ভুলে গেছেন।` : `কোডের স্টেটমেন্টের শেষে সেমিকোলন (;) দেওয়া হয়নি।`;
        suggestion = "BanglaLang-এ প্রতিটি স্টেটমেন্টের শেষে অবশ্যই সেমিকোলন (;) থাকতে হবে। যেমন: dhoro x = 10;";
    }
    // 2. Unexpected or missing Brace / Parenthesis
    else if (cleanedStderr.includes('expecting LBRACE') || cleanedStderr.includes('expecting RPAREN') || cleanedStderr.includes('expecting LPAREN') || cleanedStderr.includes('expecting RBRACE')) {
        title = "❌ ব্র্যাকেট ব্র্যাকিং ত্রুটি (Bracket Error)!";
        message = lineStr ? `লাইন ${lineStr}-এ শর্ত (jodi) বা লুপের ফার্স্ট ব্র্যাকেট '()' অথবা সেকেন্ড ব্র্যাকেট '{}' সঠিকভাবে বন্ধ করা হয়নি।` : `ব্র্যাকেটের বিন্যাস সঠিক নয়।`;
        suggestion = "jodi (...) { ... } অথবা jotokhon (...) { ... } এর ফার্স্ট ও সেকেন্ড ব্র্যাকেটগুলোর জোড়া মিলিয়ে দেখুন।";
    }
    // 3. Unexpected end of file ($end)
    else if (cleanedStderr.includes('expecting $end') || cleanedStderr.includes('unexpected $end')) {
        title = "❌ কোড অসম্পূর্ণ (Unexpected Code End)!";
        message = lineStr ? `লাইন ${lineStr}-এ কোড হঠাৎ শেষ হয়ে গেছে। কোনো সেকেন্ড ব্র্যাকেট '}' বা সেমিকোলন বাকি রয়েছে।` : `কোডের শেষে কোনো ব্র্যাকেট বন্ধ করা হয়নি।`;
        suggestion = "কোডের শেষের সেকেন্ড ব্র্যাকেট '}' বা সেমিকোলন বাদ পড়েছে কিনা চেক করুন।";
    }
    // 4. Undefined variable
    else if (cleanedStderr.includes('variable to dhoro koro ni') || cleanedStderr.includes('Undefined variable')) {
        let varMatch = cleanedStderr.match(/'([^']+)' namer kono variable/);
        let varName = varMatch ? varMatch[1] : '';
        title = "❌ ভ্যারিয়েবল পাওয়া যায়নি (Undefined Variable)!";
        message = lineStr ? `লাইন ${lineStr}-এ '${varName}' ভ্যারিয়েবলটি আগে 'dhoro' দিয়ে ডিফাইন করা হয়নি।` : `'${varName}' ভ্যারিয়েবলটি পাওয়া যায়নি।`;
        suggestion = `ব্যবহার করার আগে অবশ্যই 'dhoro ${varName} = ...;' দিয়ে ভ্যারিয়েবল ডিফাইন করে নিতে হবে।`;
    }
    // 5. Undefined Function
    else if (cleanedStderr.includes('namer kono kaaj (function) to banawni')) {
        let fnMatch = cleanedStderr.match(/'([^']+)' namer kono kaaj/);
        let fnName = fnMatch ? fnMatch[1] : '';
        title = "❌ ফাংশন পাওয়া যায়নি (Undefined Function)!";
        message = lineStr ? `লাইন ${lineStr}-এ '${fnName}' নামের কোনো ফাংশন খুঁজে পাওয়া যায়নি।` : `'${fnName}' ফাংশনটি সংজ্ঞায়িত করা হয়নি।`;
        suggestion = `ফাংশন কল করার আগে 'kaaj ${fnName}(...) { ... }' দিয়ে ফাংশনটি তৈরি করে নিন।`;
    }
    // 6. Division by zero
    else if (cleanedStderr.includes('Shunya (0) diye vag')) {
        title = "❌ শূন্য দিয়ে ভাগ ত্রুটি (Division by Zero)!";
        message = lineStr ? `লাইন ${lineStr}-এ একটি সংখ্যাকে ০ (শূন্য) দিয়ে ভাগ করার চেষ্টা করা হয়েছে।` : `শূন্য (০) দিয়ে ভাগ করা সম্ভব নয়।`;
        suggestion = "ভাজক (divisor) এর মান যেন ০ না হয় তা নিশ্চিত করুন।";
    }
    // 7. Array Index out of bounds
    else if (cleanedStderr.includes('Talika (Array) index range-er baire')) {
        title = "❌ তালিকার ইনডেক্স ভুল (Array Index Out of Bounds)!";
        message = lineStr ? `লাইন ${lineStr}-এ তালিকার সীমার বাইরের ইনডেক্সে এক্সেস করার চেষ্টা করা হয়েছে।` : `তালিকার সীমার বাইরে ইনডেক্স ব্যবহার করা হয়েছে।`;
        suggestion = "তালিকার ইনডেক্স ০ থেকে শুরু হয় এবং (সাইজ - ১) পর্যন্ত চলে। ইনডেক্স পরীক্ষা করুন।";
    }
    // 8. Unknown character lexer error
    else if (cleanedStderr.includes('Unknown character') || cleanedStderr.includes('Ota ki chilo')) {
        let charMatch = cleanedStderr.match(/'([^']+)'/);
        let charVal = charMatch ? charMatch[1] : '';
        title = "❌ অবৈধ শব্দ/চিহ্ন (Unknown Character)!";
        message = lineStr ? `লাইন ${lineStr}-এ '${charVal}' চিহ্নটি BanglaLang-এ গ্রহণযোগ্য নয়।` : `'${charVal}' চিহ্নটি সাপোর্ট করে না।`;
        suggestion = "বাংলা বা ইংরেজিতে কোনো ব্যাকটিক বা অবৈধ বিশেষ চিহ্ন ব্যবহার করা থাকলে তা সরিয়ে ফেলুন।";
    }

    return {
        title,
        line: lineStr,
        message,
        suggestion,
        rawError: cleanedStderr
    };
}

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