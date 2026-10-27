# convert — Contextual Help Plan

## Task: Contextual Help

## Goal
Make `convert` help format-specific so users can get help for specific conversion pairs.

## Scope (IN)
- `convert txt-to-docx --help` shows format-specific options
- `convert md-to-txt --help` shows format-specific options
- Default `convert --help` shows general usage and supported formats

## Scope (OUT)
- Interactive help menu
- Wizard-style help
- Help for all formats (just implement for text formats first)

## TDD Approach
1. Write tests for help output of format-specific commands
2. Implement CLI changes to support format-specific help
3. Verify existing help still works

## Acceptance Criteria
- `convert txt-to-docx --help` outputs format-specific help
- `convert md-to-txt --help` outputs format-specific help
- `convert --help` still outputs general usage

## Validation Steps
1. Run tests for contextual help
2. Run `convert --help` and verify output
3. Run `convert txt-to-docx --help` and verify output

## Dependencies
- Existing CLI structure
- Click framework

## Dependencies NOT included
- Interactive help wizard
- Help for all formats (just text first)

## Implementation Notes
- Use Click's custom commands or subcommands
- Keep it minimal: just help text for the pairs
- Use `help` parameter in the command

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert
python -m convert.cli --help
python -m convert.cli txt-to-docx --help
```

## Notes
- Start with text format pairs only
- Add video/audio help later if needed