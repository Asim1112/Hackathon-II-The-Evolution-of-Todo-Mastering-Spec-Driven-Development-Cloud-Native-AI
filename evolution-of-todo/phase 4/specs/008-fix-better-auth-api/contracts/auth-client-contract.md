# Better Auth Client Contract

## Purpose
Defines the expected interface and behavior of the Better Auth client that replaces the non-existent signIn, signUp, signOut functions.

## Client Interface

### createAuthClient(options): BetterAuthClient
**Description**: Factory function to create a Better Auth client instance
**Import Path**: `import { createAuthClient } from "better-auth/react"`
**Parameters**:
- `options`: Configuration object matching backend settings
**Return Type**: `BetterAuthClient` - Instance with authentication methods

### BetterAuthClient.signIn(credentials): Promise<AuthResult>
**Description**: Authenticates a user with provided credentials
**Parameters**:
- `credentials`: Object with email and password
**Return Type**: `Promise<AuthResult>` - Session information and user data
**Usage**: Called when user submits sign-in form

### BetterAuthClient.signUp(credentials): Promise<AuthResult>
**Description**: Registers a new user with provided credentials
**Parameters**:
- `credentials`: Object with email and password
**Return Type**: `Promise<AuthResult>` - Session information and user data
**Usage**: Called when user submits sign-up form

### BetterAuthClient.signOut(): Promise<void>
**Description**: Ends the current user session
**Parameters**: None
**Return Type**: `Promise<void>` - Resolves when session is cleared
**Usage**: Called when user selects sign-out option

## Module Interface
- **Export Type**: Named export of factory function
- **Function Name**: `createAuthClient`
- **Dependencies**: Better Auth 1.4.9 with proper backend configuration
- **Import Convention**: `import { createAuthClient } from "better-auth/react"`

## Compatibility Requirements
- Must work with Better Auth backend configured for JWT authentication
- Should maintain token-based session management
- Must handle authentication errors appropriately
- Should preserve user state across page refreshes