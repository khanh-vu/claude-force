# Scenario: Fix Email Validation Bug

## Difficulty: Simple
**Category**: Bug Fix
**Expected Duration**: 8 minutes
**Expected Agents**: 2-3

---

## Task Description

Fix a bug where email validation incorrectly rejects valid email addresses with plus signs (e.g., `user+tag@example.com`).

**Bug Report**:
> Users are unable to register with email addresses containing '+' signs. The validation regex rejects these as invalid, but they are legitimate email addresses per RFC 5322.
>
> **Steps to Reproduce**:
> 1. Attempt to register with email: `john+test@example.com`
> 2. See error: "Invalid email address"
>
> **Expected**: Registration succeeds
> **Actual**: Registration fails with validation error

---

## Requirements

### Functional Requirements
1. Accept email addresses with '+' character
2. Maintain validation for truly invalid emails
3. Support all RFC 5322 compliant email formats

### Non-Functional Requirements
1. No breaking changes to existing valid emails
2. Add regression tests to prevent future issues
3. Update validation error messages if needed

---

## Expected Agent Selection

### Workflow: Bug Fix
1. **bug-investigator**
   - Analyze root cause
   - Reproduce the issue
   - Propose fix with explanation

2. **code-reviewer**
   - Review proposed fix
   - Check for edge cases
   - Validate no breaking changes

3. **qc-automation-expert** (optional but recommended)
   - Create regression tests
   - Verify fix works
   - Test edge cases

---

## Success Criteria

### Must Have ✅
- [x] Emails with '+' sign are accepted
- [x] Previously valid emails still work
- [x] Invalid emails still rejected
- [x] Root cause identified

### Quality Checks ✅
- [x] Regression tests added
- [x] Edge cases covered
- [x] No performance degradation
- [x] Code review passed

### Documentation ⭐
- [ ] Bug fix documented
- [ ] Test cases documented
- [ ] Validation rules clarified

---

## Input Context

### Buggy Code
```javascript
// utils/validators.js
function validateEmail(email) {
  // Bug: This regex doesn't support '+' in email addresses
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email);
}

module.exports = { validateEmail };
```

### Usage
```javascript
// routes/users.js
const { validateEmail } = require('../utils/validators');

app.post('/api/users', (req, res) => {
  const { email, password } = req.body;

  if (!validateEmail(email)) {
    return res.status(400).json({
      error: 'ValidationError',
      message: 'Invalid email address'
    });
  }

  // ... create user
});
```

### Test Cases (Missing)
No existing tests for email validation.

---

## Expected Output

### Fixed Code
```javascript
// utils/validators.js
function validateEmail(email) {
  // Fixed: Support '+' and other valid RFC 5322 characters
  const emailRegex = /^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

  // Additional validation
  if (!email || email.length > 254) {
    return false;
  }

  return emailRegex.test(email);
}

module.exports = { validateEmail };
```

### Regression Tests
```javascript
// tests/validators.test.js
const { validateEmail } = require('../utils/validators');

describe('Email Validation', () => {
  describe('Valid Emails', () => {
    it('should accept standard email', () => {
      expect(validateEmail('user@example.com')).toBe(true);
    });

    it('should accept email with plus sign', () => {
      expect(validateEmail('user+tag@example.com')).toBe(true);
    });

    it('should accept email with dots', () => {
      expect(validateEmail('first.last@example.com')).toBe(true);
    });

    it('should accept email with numbers', () => {
      expect(validateEmail('user123@example.com')).toBe(true);
    });

    it('should accept email with hyphens', () => {
      expect(validateEmail('user-name@ex-ample.com')).toBe(true);
    });
  });

  describe('Invalid Emails', () => {
    it('should reject email without @', () => {
      expect(validateEmail('userexample.com')).toBe(false);
    });

    it('should reject email without domain', () => {
      expect(validateEmail('user@')).toBe(false);
    });

    it('should reject email without TLD', () => {
      expect(validateEmail('user@example')).toBe(false);
    });

    it('should reject empty email', () => {
      expect(validateEmail('')).toBe(false);
    });

    it('should reject email with spaces', () => {
      expect(validateEmail('user @example.com')).toBe(false);
    });

    it('should reject email exceeding max length', () => {
      const longEmail = 'a'.repeat(250) + '@example.com';
      expect(validateEmail(longEmail)).toBe(false);
    });
  });
});
```

### Bug Fix Documentation
```markdown
## Bug Fix: Email Validation Regex

**Issue**: Email validation rejected valid addresses with '+' character

**Root Cause**:
- Regex pattern `/^[a-zA-Z0-9._-]+@...$/` excluded '+' from allowed characters
- RFC 5322 permits '+' in local part of email addresses

**Fix**:
- Updated regex to `/^[a-zA-Z0-9._+-]+@...$/`
- Added length validation (max 254 characters per RFC 5321)
- Maintained all other validation rules

**Testing**:
- Added 11 regression test cases
- Verified no breaking changes to existing functionality
- Tested edge cases (empty, spaces, length limits)

**Impact**:
- Users can now register with '+' in email addresses
- No breaking changes for existing users
- Improved RFC compliance
```

---

## Metrics to Track

### Performance
- Bug investigation time: ~3 minutes (expected)
- Fix implementation time: ~2 minutes (expected)
- Test creation time: ~3 minutes (expected)
- Total completion time: ~8 minutes (expected)

### Quality
- Root cause identified: Yes/No
- Regression tests added: Yes/No
- Edge cases covered: Count
- Breaking changes: 0 (expected)

### Coverage
- Test cases added: 11 (expected)
- Code coverage: 100% for validators.js (expected)
- Edge cases tested: 6+ (expected)

---

## Validation Script

```javascript
// test_bug_fix.js
const { validateEmail } = require('../utils/validators');

function testBugFix() {
  const testCases = [
    // Original bug: Should now pass
    { email: 'user+tag@example.com', expected: true, description: 'Email with plus sign' },
    { email: 'john+test@example.com', expected: true, description: 'Original bug report case' },

    // Ensure no regression: Should still pass
    { email: 'user@example.com', expected: true, description: 'Standard email' },
    { email: 'first.last@example.com', expected: true, description: 'Email with dots' },

    // Should still reject invalid: Should still fail
    { email: 'invalid', expected: false, description: 'Invalid format' },
    { email: 'user@', expected: false, description: 'Missing domain' },
  ];

  let passed = 0;
  let failed = 0;

  console.log('Testing Bug Fix...\n');

  testCases.forEach(({ email, expected, description }) => {
    const result = validateEmail(email);
    const status = result === expected ? '✅' : '❌';

    if (result === expected) {
      passed++;
    } else {
      failed++;
    }

    console.log(`${status} ${description}`);
    console.log(`   Input: "${email}"`);
    console.log(`   Expected: ${expected}, Got: ${result}\n`);
  });

  console.log(`\nResults: ${passed} passed, ${failed} failed`);
  return failed === 0;
}

testBugFix();
```

---

## Learning Outcomes

### What This Demonstrates
1. **Bug investigation workflow**: Systematic root cause analysis
2. **Multi-agent coordination**: bug-investigator → code-reviewer → qc-automation-expert
3. **Regression prevention**: Comprehensive test coverage
4. **Quality gates**: Code review catches edge cases

### Skills Highlighted
- Bug-investigator's debugging expertise
- Code-reviewer's edge case analysis
- QC-automation-expert's test generation patterns
- Regression test strategies from test-generation skill

### Common Pitfalls Avoided
- ❌ Fixing bug without understanding root cause
- ❌ No regression tests → bug returns later
- ❌ Breaking existing functionality
- ❌ Not testing edge cases

---

## Variants for Testing

### Variant 1: With Performance Issue
Bug causes slow validation on long inputs
- **Complexity**: +investigation time
- **Agents**: +performance analysis

### Variant 2: With Security Impact
Bug allows SQL injection via validation bypass
- **Complexity**: +1 agent (security-specialist)
- **Duration**: +5 minutes

### Variant 3: With Multiple Files
Bug spans validator, controller, and model
- **Complexity**: More files to analyze/fix
- **Duration**: +10 minutes

---

**Status**: Ready for Execution
**Version**: 1.0.0
**Created**: 2025-11-13
