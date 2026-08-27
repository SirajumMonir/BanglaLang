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