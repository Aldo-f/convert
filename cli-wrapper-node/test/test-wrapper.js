const assert = require('assert');
const { spawn } = require('child_process');
const path = require('path');

const cliPath = path.join(__dirname, '..', 'cli.js');
const convertRoot = path.join(__dirname, '..', '..');

function runConvertCli(args, input) {
  return new Promise((resolve) => {
    const env = {
      ...process.env,
      CONVERT_ROOT: convertRoot,
      PYTHONPATH: `${convertRoot}/src:${process.env.PYTHONPATH || ''}`,
    };
    const child = spawn('node', [cliPath, ...args], { env });
    let stdout = '';
    let stderr = '';
    if (input) child.stdin.write(input);
    child.stdin.end();
    child.stdout.on('data', (data) => { stdout += data; });
    child.stderr.on('data', (data) => { stderr += data; });
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

async function runTests() {
  // Test 1: help works
  const r1 = await runConvertCli(['--help']);
  assert.strictEqual(r1.code, 0, `--help should exit 0, got ${r1.code}`);
  assert.ok(r1.stdout.includes('Usage'), '--help should show usage');
  console.log('PASS: help works');

  // Test 2: unknown converter fails gracefully
  const r2 = await runConvertCli(['convert', 'nonexistent.xyz', 'out.md']);
  assert.notStrictEqual(r2.code, 0, 'invalid conversion should exit non-zero');
  console.log('PASS: unknown converter fails gracefully');

  // Test 3: txt to md works
  const fs = require('fs');
  const srcDir = path.join(convertRoot, '.tmp_test');
  const srcFile = path.join(srcDir, 'in.txt');
  const outFile = path.join(srcDir, 'out.md');
  fs.mkdirSync(srcDir, { recursive: true });
  fs.writeFileSync(srcFile, 'hello world');

  const r3 = await runConvertCli(['convert', srcFile, outFile]);
  assert.strictEqual(r3.code, 0, `txt-to-md should exit 0, got ${r3.code}: ${r3.stderr}`);
  const result = fs.readFileSync(outFile, 'utf-8').trim();
  assert.strictEqual(result, 'hello world', `output should be 'hello world', got '${result}'`);
  console.log('PASS: txt-to-md works');

  fs.rmSync(srcDir, { recursive: true, force: true });

  console.log('\nAll wrapper tests passed.');
}

runTests().catch((err) => {
  console.error('Test failed:', err.message);
  process.exit(1);
});
