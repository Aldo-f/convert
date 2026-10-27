#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

const args = process.argv.slice(2);

// Determine Python command - use convert venv if available, else system python
const convertRoot = process.env.CONVERT_ROOT || path.join(__dirname, '..', '..');
const venvPython = path.join(convertRoot, '..', '..', 'opencode', 'convert-venv', 'bin', 'python');
const fs = require('fs');
const pythonCmd = fs.existsSync(venvPython) ? venvPython : (process.env.CONVERT_PYTHON || 'python');

const env = {
  ...process.env,
  PYTHONPATH: `${convertRoot}/src:${process.env.PYTHONPATH || ''}`,
};

const pythonArgs = ['-m', 'convert.cli', ...args];

const child = spawn(pythonCmd, pythonArgs, {
  stdio: 'inherit',
  env: env,
});

child.on('error', (err) => {
  console.error(`Error starting convert: ${err.message}`);
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code ?? 1);
});

process.on('SIGINT', () => child.kill('SIGINT'));
process.on('SIGTERM', () => child.kill('SIGTERM'));