# Fix CI/CD Python Version Issue

## Problem
The project uses Python 3.14 which is incompatible with some dependencies (asyncpg, pydantic-core) that require C compilation.

## Solutions

### Option 1: Use Python 3.12 in CI (Recommended)
Change the GitHub Actions workflow to use Python 3.12 instead of 3.14:

```yaml
- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: 3.12
```

### Option 2: Use Pre-compiled Wheels
Add pre-compiled wheels to requirements.txt for problematic packages:

```txt
asyncpg==0.29.0
# Use pre-compiled wheel for Windows
# https://pypi.org/project/asyncpg/#files
pydantic[email]==2.8.0
```

### Option 3: Use Virtual Environment with Older Python
Set up a virtual environment with Python 3.12 for local development.

## Recommended Action
Use Option 1 (change CI to Python 3.12) as it's the simplest and most reliable solution for CI/CD.
