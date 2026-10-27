# convert — Blog Automation Plan

## Task: Blog Automation

## Goal
Create a script that generates blog post drafts from release notes and examples.

## Scope (IN)
- Script that reads release notes from GitHub
- Script that generates blog post draft from release notes
- Script that includes code examples from README
- Output: Markdown blog post draft

## Scope (OUT)
- Publishing to external platforms
- Social media automation
- Email newsletter automation
- SEO optimization

## TDD Approach
1. Write tests for blog post generation
2. Implement blog post generator
3. Verify output is correct

## Acceptance Criteria
- Script generates blog post draft from release notes
- Script includes code examples
- Script output is valid Markdown
- Script is testable

## Validation Steps
1. Run script with sample release notes
2. Verify output is valid Markdown
3. Verify output includes code examples

## Dependencies
- Python 3.12+
- GitHub API (for release notes)
- Existing README (for examples)

## Dependencies NOT included
- Publishing to external platforms
- Social media automation
- Email newsletter automation
- SEO optimization

## Implementation Notes
- Use Python script with argparse
- Read release notes from GitHub API
- Generate blog post draft with sections
- Include code examples from README
- Output to stdout or file

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert
python scripts/blog-generate.py --release v1.0.0 --output blog-post.md
cat blog-post.md
```

## Notes
- This is a separate script, not part of `convert`
- Can be run manually or scheduled
- Output is a draft that can be edited before publishing