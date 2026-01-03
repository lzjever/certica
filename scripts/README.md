# Scripts

This directory contains utility scripts for the Certica project.

## generate_release_notes.py

Generates release notes from CHANGELOG.md or git commits for GitHub releases.

### Usage

```bash
# Output to stdout
python3 scripts/generate_release_notes.py 1.0.0

# Output to file
python3 scripts/generate_release_notes.py 1.0.0 release_notes.md
```

### How it works

1. First tries to extract the changelog section for the given version from `CHANGELOG.md`
2. If not found, falls back to git commits since the previous tag
3. Adds installation instructions
4. Outputs the complete release notes

### Used in CI/CD

This script is automatically used by the GitHub Actions workflow (`.github/workflows/release.yml`) when creating releases.

