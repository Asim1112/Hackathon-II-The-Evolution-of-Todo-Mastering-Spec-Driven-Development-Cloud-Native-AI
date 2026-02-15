# Authentication API Contract

## Purpose
Defines the authentication endpoints and JWT operations that require the `python-jose` dependency to function correctly.

## Endpoints

### POST /api/v1/auth/signup
**Description**: Create a new user account
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
**Response**: 200 OK with user data and JWT token
```json
{
  "user": {
    "id": "string",
    "email": "user@example.com"
  },
  "token": "jwt_token_string"
}
```

### POST /api/v1/auth/signin
**Description**: Authenticate user and return JWT token
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
**Response**: 200 OK with user data and JWT token
```json
{
  "user": {
    "id": "string",
    "email": "user@example.com"
  },
  "token": "jwt_token_string"
}
```

## JWT Operations

### Token Creation
- **Function**: `create_access_token(data: dict, expires_delta: Optional[timedelta])`
- **Requirements**: `python-jose` with cryptography support
- **Output**: JWT string with expiration claim

### Token Verification
- **Function**: `verify_token(token: str)`
- **Requirements**: `python-jose` with cryptography support
- **Output**: Token payload dict or None if invalid

### Token Validation
- **Function**: `validate_token_signature(token: str)`
- **Requirements**: `python-jose` with cryptography support
- **Output**: Boolean indicating signature validity

## Security Requirements
- All protected endpoints must validate JWT tokens
- User isolation: users can only access their own data
- Proper error handling for invalid/missing tokens