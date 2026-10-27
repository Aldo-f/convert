# convert — Node CLI Wrapper Plan

## Task: Node CLI Wrapper

## Goal
Provide a thin Node.js wrapper that calls the Python `convert` binary, making the tool accessible from JavaScript ecosystems.

## Scope (IN)
- Node.js package (`convert-cli-node`) installable via npm
- Wrapper that spawns the Python `convert` binary
- Same CLI interface as Python version
- Cross-platform support (Windows, macOS, Linux)

## Scope (OUT)
- Reimplementation of conversion logic in Node.js
- Any new conversion features
- Bundled Python runtime (assume Python is installed)
- Node.js-specific features beyond CLI compatibility

## TDD Approach
1. Create `convert-cli-node` directory with `package.json`
2. Write tests using Jest (or Mocha) that verify CLI output matches Python
3. Implement wrapper that spawns Python CLI and returns output
4. Verify with manual tests

## Acceptance Criteria
- `npm install -g convert-cli-node` installs the wrapper
- `convert-cli-node file.txt file.md` produces the same output as the Python CLI
- All existing convert tests still pass
- Wrapper works on Windows, macOS, and Linux

## Implementation Steps
1. Create `src/cli.js` with `#!/usr/bin/env node`
2. Parse command-line arguments (use `commander` or similar)
3. Spawn Python CLI with `child_process.spawn`
4. Forward stdout/stderr to Node process
5. Handle exit codes and errors

## Dependencies
- Node.js 14+
- npm
- Python 3.12+ (assumed installed)

## Dependencies NOT included
- Bundled Python runtime
- Any new conversion features
- Node.js-specific features beyond CLI compatibility

## Implementation Steps
1. Create `package.json` with proper scripts
2. Implement CLI parsing with `commander` or `yargs`
3. Spawn Python CLI: `python -m convert.cli $@`
4. Pipe stdout/stderr from Python to Node
5. Handle exit codes and errors

## Implementation Notes
- Use child_process.spawn to run `python -m convert.cli $@`
- Forward stdout/stderr directly to Node process
- Return exit code from Python CLI
- Handle Ctrl+C gracefully

## Validation
- Test with `convert txt-to-md in.txt out.md`
- Verify output matches Python CLI exactly
- Check exit codes match
- Verify cross-platform compatibility