# Email Validation Utility Contract

## Purpose
Defines the interface and behavior of the email validation utility function that will be available in the shared utility module.

## Function Interface

### isValidEmail(email: string): boolean
**Description**: Validates an email address string against RFC 5322 standards using a safe regex pattern
**Import Path**: `import { isValidEmail } from "@/lib/utils"`
**Parameters**:
- `email`: string - The email address to validate
**Return Type**: `boolean` - True if email format is valid, false otherwise
**Error Handling**: Returns false for invalid inputs without throwing exceptions

**Valid Examples**:
- `isValidEmail("user@example.com")` → `true`
- `isValidEmail("test.email+tag@domain.co.uk")` → `true`
- `isValidEmail("user.name@sub.domain.org")` → `true`

**Invalid Examples**:
- `isValidEmail("invalid-email")` → `false`
- `isValidEmail("@example.com")` → `false`
- `isValidEmail("user@")` → `false`
- `isValidEmail("")` → `false`
- `isValidEmail(null)` → `false` (would cause TypeError - caller should handle)

## Module Interface
- **Export Type**: Named export of validation function
- **Function Name**: `isValidEmail`
- **Input Type**: string
- **Output Type**: boolean
- **Side Effects**: None (pure function)

## Performance Requirements
- Function should execute in under 1ms for typical email addresses
- Should not cause performance degradation in form validation
- Memory usage should be minimal

## Security Requirements
- Should not expose email addresses or validation details to potential attackers
- Regex pattern should be safe from ReDoS (Regular Expression Denial of Service) attacks
- Function should not leak information about email existence