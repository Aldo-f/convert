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
1. Write tests for the wrapper using Node.js test framework (Jest or Mocha)
2. Implement minimal wrapper that passes tests
3. Add tests for edge cases (invalid Python path, missing files, etc.)

## Acceptance Criteria
- `npm install -g convert-cli-node` installs the wrapper
- `convert-cli-node file.txt file.md` produces the same output as the Python CLI
- All existing convert tests still pass
- Wrapper works on Windows, macOS, and Linux

## Validation Steps
1. Run `npm test` in the wrapper directory
2. Verify wrapper with manual tests
3. Verify Python CLI still works

## Dependencies
- Node.js 14+
- npm
- Python 3.12+ (assumed installed)

## Dependencies NOT included
- Bundled Python runtime
- Any new conversion features
- Node.js-specific features

## Implementation Notes
- Wrapper should detect Python installation and use it
- Wrapper should pass all CLI arguments through to Python
- Wrapper should handle errors gracefully

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert-cli-node
npm test
convert-cli-node file.txt file.md
```

## Notes
- Start with minimal implementation: just text conversions
- Add video/audio support later if needed
- Use environment variables for Python path configuration