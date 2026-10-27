# convert — GitHub README Plan

## Task: GitHub README

## Goal
Create a comprehensive, user-friendly README that makes it easy to discover, install, and use `convert`.

## Scope (IN)
- Project description and purpose
- Installation instructions (pip, optional npm/gem)
- Quick start examples (one-liners)
- Supported conversions table
- CLI reference (flags, subcommands)
- Development setup (tests, lint, formatting)
- Links to issue tracker, contributing guide, license

## Scope (OUT)
- Blog posts or marketing copy beyond README
- Community features (Discord, Slack, etc.)
- Migration guides (wait for feature parity)
- Beta/GA gating

## TDD Approach
1. Write the README as documentation-first
2. Verify all examples work with the actual CLI
3. Test installation steps manually

## Acceptance Criteria
- README renders correctly on GitHub
- All installation commands work
- All CLI examples work
- Supported conversions table is accurate

## Validation Steps
1. Render README locally (markdown preview)
2. Test all installation commands
3. Test all CLI examples from README
3. Verify links work

## Dependencies
- Existing CLI functionality
- GitHub repository

## Dependencies NOT included
- Community features
- Migration guides
- Blog posts

## Implementation Notes
- Keep it scannable: headings, tables, code blocks
- Show real examples with expected output
- Include "Why convert?" section
- Link to issue templates for feedback

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert
cat README.md  # verify content
# Test install commands manually
# Test CLI examples from README
```

## Notes
- Update README when features change
- Keep examples current with CLI output
- Use shields.io badges for CI, coverage, version