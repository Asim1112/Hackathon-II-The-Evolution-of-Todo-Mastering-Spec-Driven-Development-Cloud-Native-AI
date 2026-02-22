# Quickstart: Backend Setup with python-jose Dependency

## Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- uv package manager (recommended) or pip
- Access to Neon PostgreSQL database (preconfigured)

## Installation Steps

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend/

# Install dependencies including python-jose
uv sync
# OR if you don't have uv:
pip install -e .
```

### 2. Verify python-jose Installation
```bash
# Test the import that was failing
python -c "from jose import JWTError, jwt; print('python-jose import successful')"
```

### 3. Start Backend Server
```bash
# Start the FastAPI server
uvicorn src.api.main:app --reload --port 8000
```

The server should start without the ModuleNotFoundError and be available at http://localhost:8000

## Environment Configuration

Your environment is already configured:
- **Backend .env** contains the Neon database URL and JWT secret
- **Frontend .env** points to the backend API at http://localhost:8000

## Troubleshooting

If you still encounter issues:

1. **Verify installation**:
   ```bash
   pip list | grep jose
   # Should show python-jose version
   ```

2. **Clean reinstall**:
   ```bash
   pip uninstall python-jose
   pip install python-jose[cryptography]
   ```

3. **Check import**:
   ```bash
   python -c "from jose import JWTError, jwt; print('Import successful')"
   ```

## Next Steps

1. Start the frontend in a new terminal:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

2. Access the application at http://localhost:3000