# convert — Error Messages Plan

## Task: Error Messages

## Goal
Make `convert` error messages actionable — tell users exactly what to fix.

## Scope (IN)
- Actionable error messages for common failures
- Example: "Install python-docx for txt→docx conversions"
- Example: "File not found: /path/to/file"
- Example: "Unsupported format: .xyz"
- Standard error format: `[error] <message>`

## Scope (OUT)
- Custom error recovery beyond actionable messages
- Error reporting to external services
- User feedback surveys

## TDD Approach
1. Write tests for error message format
2. Implement error handling with actionable messages
3. Verify existing error messages are replaced

## Acceptance Criteria
- All error messages are actionable (tell user what to do)
- Error messages use standard format: `[error] <message>`
- Tests verify error message format

## Validation Steps
1. Run tests for error messages
2. Test manually with various error conditions
3. Verify all error messages are actionable

## Dependencies
- Existing CLI error handling
- Click framework

## Dependencies NOT included
- Error reporting to external services
- User feedback surveys

## Implementation Notes
- Use Click's `click.UsageError` for standard errors
- Add actionable messages to all error paths
- Keep error messages short and clear

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert
python -m pytest tests/test_errors.py -q
# Test manually with various error conditions
```

## Notes
- Start with text format errors
- Add video/audio errors later if needed