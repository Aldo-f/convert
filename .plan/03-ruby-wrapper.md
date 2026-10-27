# convert — Ruby CLI Wrapper Plan

## Task: Ruby CLI Wrapper

## Goal
Provide a thin Ruby wrapper that calls the Python `convert` binary, making the tool accessible from Ruby ecosystems.

## Scope (IN)
- Ruby gem (`convert-cli-ruby`) installable via RubyGems
- Wrapper that spawns the Python `convert` binary
- Same CLI interface as Python version
- Cross-platform support (Windows, macOS, Linux)

## Scope (OUT)
- Reimplementation of conversion logic in Ruby
- Any new conversion features
- Bundled Python runtime (assume Python is installed)
- Ruby-specific features beyond CLI compatibility

## TDD Approach
1. Write tests for the wrapper using Ruby test framework (Minitest or RSpec)
2. Implement minimal wrapper that passes tests
3. Add tests for edge cases (invalid Python path, missing files, etc.)

## Acceptance Criteria
- `gem install convert-cli-ruby` installs the wrapper
- `convert-cli-ruby file.txt file.md` produces the same output as the Python CLI
- All existing convert tests still pass
- Wrapper works on Windows, macOS, and Linux

## Validation Steps
1. Run `rspec` or `rake test` in the wrapper directory
2. Verify wrapper with manual tests
3. Verify Python CLI still works

## Dependencies
- Ruby 2.7+
- RubyGems
- Python 3.12+ (assumed installed)

## Dependencies NOT included
- Bundled Python runtime
- Any new conversion features
- Ruby-specific features

## Implementation Notes
- Wrapper should detect Python installation and use it
- Wrapper should pass all CLI arguments through to Python
- Wrapper should handle errors gracefully

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert-cli-ruby
bundle exec rspec
convert-cli-ruby file.txt file.md
```

## Notes
- Start with minimal implementation: just text conversions
- Add video/audio support later if needed
- Use environment variables for Python path configuration