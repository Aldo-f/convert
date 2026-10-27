# convert — PyPI Publish Plan

## Task: PyPI Publish

## Goal
Make the `convert` CLI available via PyPI as `convert-cli` for easy installation on all platforms.

## Scope (IN)
- Package metadata (`setup.py` or `pyproject.toml`) suitable for PyPI
- Scripts entry point `convert = convert.cli:cli` (for `convert` command)
- PyPI project page with README, documentation, and project description
- Upload to PyPI via `twine`

## Scope (OUT)
- Any new features beyond existing CLI
- New dependencies
- Cross-platform building (wheels for macOS, Linux, Windows)
- Tightly integrated with PyPI ecosystem

## TDD Approach
1. Write tests for the packaging
2. Implement PyPI packaging
3. Verify installation and functionality

## Acceptance Criteria
- `pip install convert-cli` installs the package
- `convert` command works after installation
- All existing tests pass
- Package metadata is valid

## Validation Steps
1. Run `python -m pytest` in the convert directory
2. Build the package: `python -m build`
3. Install locally: `pip install .`
4. Test: `convert --help`
5. Upload to PyPI (if tests pass)

## Dependencies
- Python 3.12+
- `build` and `twine`
- `setup.py` or `pyproject.toml`

## Dependencies NOT included
- Any new features beyond existing CLI
- New dependencies
- Cross-platform building tools

## Implementation Notes
- Use `pyproject.toml` if the project uses it
- Keep README simple and focused on installation and usage
- Include tests in the package distribution
- Add changelog to version notes

## Validation
Run:
```bash
cd /mnt/HDD1/dev/scripts/convert
python -m pytest tests/ -q
python -m build
twine check dist/*
```

## Notes
- Use GitHub Actions to automate deployment
- Only publish from main branch
- Keep version numbers semantic (major.minor.patch)