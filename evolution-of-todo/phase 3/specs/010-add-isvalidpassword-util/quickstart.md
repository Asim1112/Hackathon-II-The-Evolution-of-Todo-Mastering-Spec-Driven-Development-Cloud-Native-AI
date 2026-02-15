# QuickStart Guide: Add Missing isValidPassword Utility Function

**Feature**: Add Missing isValidPassword Utility Function
**Branch**: `010-add-isvalidpassword-util`
**Date**: 2026-02-05
**Guide Version**: 1.0

## Overview

This quickstart guide provides immediate implementation steps to add the missing `isValidPassword` function to the shared utility module. Follow these steps to resolve the Next.js module resolution error that's preventing the signup page from loading.

## Immediate Action Steps

### Step 1: Implement the Function (2 minutes)
Open `frontend/lib/utils.ts` and add the following function:

```typescript
export function isValidPassword(password: string): boolean {
  // At least 8 characters
  if (password.length < 8) {
    return false;
  }

  // At least one uppercase letter
  if (!/[A-Z]/.test(password)) {
    return false;
  }

  // At least one lowercase letter
  if (!/[a-z]/.test(password)) {
    return false;
  }

  // At least one number
  if (!/\d/.test(password)) {
    return false;
  }

  // At least one special character
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    return false;
  }

  return true;
}
```

### Step 2: Verify Export (1 minute)
Ensure the function is exported alongside existing utilities:
```typescript
export { cn, generateId, isValidEmail, isValidPassword };
```

### Step 3: Test Module Resolution (2 minutes)
Verify the signup page loads without module resolution errors:
```bash
npm run dev
```
Navigate to `http://localhost:3000/auth/signup` to confirm the page loads.

## Implementation Details

### Function Purpose
The `isValidPassword` function validates password strength according to security requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Usage Pattern
The function is designed to be used in authentication forms:
```typescript
if (!isValidPassword(userPassword)) {
  showError("Password must contain at least 8 characters with uppercase, lowercase, number, and special character");
}
```

## Validation Checklist

### Pre-Implementation
- [ ] Confirm `frontend/lib/utils.ts` exists
- [ ] Verify current exports in the file
- [ ] Check that `SignUpForm.tsx` imports `isValidPassword`

### Post-Implementation
- [ ] Function added to `utils.ts` with correct signature
- [ ] Function properly exported
- [ ] Signup page loads without module errors
- [ ] Password validation works in the form
- [ ] Build completes successfully

## Common Issues & Solutions

### Issue: Function exists but import still fails
**Solution**: Verify exact function name `isValidPassword` with correct capitalization

### Issue: Page still shows module resolution error
**Solution**: Restart development server and clear Next.js cache:
```bash
rm -rf .next
npm run dev
```

### Issue: Password validation too strict
**Solution**: Adjust the validation rules in the function to match your requirements

## Testing Commands

### Start Development Server
```bash
npm run dev
```

### Run Production Build
```bash
npm run build
```

### Test Page Access
Visit `http://localhost:3000/auth/signup` to verify page loads without errors.

## Success Indicators

### Immediate Success
- [ ] `frontend/lib/utils.ts` contains `isValidPassword` function
- [ ] Export statement includes `isValidPassword`
- [ ] `npm run dev` starts without errors

### Verification Success
- [ ] Signup page loads at `http://localhost:3000/auth/signup`
- [ ] No "Export isValidPassword doesn't exist" errors
- [ ] Password validation works in the form

## Rollback Plan

If implementation causes issues:

1. Remove the `isValidPassword` function from `utils.ts`
2. Remove it from the export statement
3. Comment out validation in `SignUpForm.tsx` temporarily
4. Restart the development server

## Next Steps

1. Run unit tests to verify validation logic
2. Perform full authentication flow test
3. Deploy to staging environment for further validation