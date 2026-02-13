# Lessons Learned: Dependency Management

## Issue
The `python-jose` dependency was declared in both `pyproject.toml` and `requirements.txt` but was not installed in the Python environment, causing a `ModuleNotFoundError: No module named 'jose'` when starting the backend.

## Solution
Installed `python-jose[cryptography]` package which resolved the import issue in `src/auth/utils.py`.

## Root Cause
Dependencies were properly declared in project files but the installation step was missed or failed during environment setup.

## Prevention
- Always run dependency installation commands after cloning/updating the project
- For backend: `pip install -e .` or `pip install -r requirements.txt`
- Verify critical imports work after environment setup

## Files Updated
- backend/README.md - Added dependency installation instructions
- backend/src/auth/utils.py - Fixed timestamp conversion in JWT creation/verification