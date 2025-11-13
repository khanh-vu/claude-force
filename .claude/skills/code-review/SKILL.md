# Code Review Skill

## Overview
Comprehensive code review checklists, patterns, and best practices for conducting thorough, constructive code reviews across multiple languages and frameworks.

## Capabilities
- Security vulnerability detection
- Performance issue identification
- Code quality assessment
- Best practices enforcement
- Architecture review
- Test coverage analysis

---

## Code Review Checklist

### 1. Functionality ✅

**Core Requirements**:
- [ ] Code implements the specified requirements
- [ ] Edge cases are handled
- [ ] Error handling is comprehensive
- [ ] Business logic is correct
- [ ] No hardcoded values (use configuration)

**Testing**:
- [ ] Unit tests are present and comprehensive
- [ ] Integration tests cover critical paths
- [ ] Test names are descriptive
- [ ] Mocks are appropriate
- [ ] Coverage meets project standards (typically 80%+)

---

### 2. Security 🔒

**OWASP Top 10**:
- [ ] No SQL injection vulnerabilities
- [ ] No XSS (Cross-Site Scripting) vulnerabilities
- [ ] No CSRF (Cross-Site Request Forgery) vulnerabilities
- [ ] No insecure deserialization
- [ ] Authentication is properly implemented
- [ ] Authorization checks are in place
- [ ] Sensitive data is not logged
- [ ] Secrets are not hardcoded

**Input Validation**:
```typescript
// ❌ Bad: No validation
function updateUser(data) {
  return db.users.update(data);
}

// ✅ Good: Validate input
function updateUser(data: UpdateUserDTO) {
  validateEmail(data.email);
  validateAge(data.age);
  sanitizeInput(data.bio);
  return db.users.update(data);
}
```

**SQL Injection Prevention**:
```python
# ❌ Bad: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Good: Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

**Authentication**:
```typescript
// ✅ Check authentication on protected routes
if (!req.user || !req.user.isAuthenticated) {
  return res.status(401).json({ error: 'Unauthorized' });
}

// ✅ Check authorization
if (req.user.id !== resource.ownerId) {
  return res.status(403).json({ error: 'Forbidden' });
}
```

---

### 3. Performance ⚡

**Common Issues to Check**:
- [ ] No N+1 query problems
- [ ] Database queries are optimized
- [ ] Appropriate indexes are used
- [ ] Caching is utilized where beneficial
- [ ] No memory leaks (event listeners cleaned up)
- [ ] Async operations don't block unnecessarily
- [ ] Large datasets are paginated

**N+1 Query Example**:
```typescript
// ❌ Bad: N+1 queries
const users = await User.findAll();
for (const user of users) {
  user.orders = await Order.findByUserId(user.id); // N queries!
}

// ✅ Good: Single query with join
const users = await User.findAll({
  include: [Order]
});
```

**Algorithm Complexity**:
```typescript
// ❌ Bad: O(n²)
function hasDuplicate(arr) {
  for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
      if (arr[i] === arr[j]) return true;
    }
  }
  return false;
}

// ✅ Good: O(n)
function hasDuplicate(arr) {
  return new Set(arr).size !== arr.length;
}
```

---

### 4. Code Quality 📝

**Readability**:
- [ ] Variable names are descriptive
- [ ] Function names describe what they do
- [ ] Magic numbers are replaced with named constants
- [ ] Complex logic has explanatory comments
- [ ] Code follows project style guide

**SOLID Principles**:
- [ ] Single Responsibility: Each class/function has one job
- [ ] Open/Closed: Open for extension, closed for modification
- [ ] Liskov Substitution: Subtypes are substitutable
- [ ] Interface Segregation: Small, focused interfaces
- [ ] Dependency Inversion: Depend on abstractions

**DRY (Don't Repeat Yourself)**:
```typescript
// ❌ Bad: Repetition
function validateUser(user) {
  if (!user.email || !user.email.includes('@')) {
    throw new Error('Invalid email');
  }
  if (!user.name || user.name.length < 2) {
    throw new Error('Invalid name');
  }
  if (!user.age || user.age < 0 || user.age > 150) {
    throw new Error('Invalid age');
  }
}

// ✅ Good: Reusable validators
const validators = {
  email: (email) => email && email.includes('@'),
  name: (name) => name && name.length >= 2,
  age: (age) => age >= 0 && age <= 150
};

function validateField(value, validator, fieldName) {
  if (!validator(value)) {
    throw new Error(`Invalid ${fieldName}`);
  }
}
```

**Meaningful Names**:
```typescript
// ❌ Bad
const d = new Date();
const x = u.filter(i => i.a);

// ✅ Good
const currentDate = new Date();
const activeUsers = users.filter(user => user.isActive);
```

---

### 5. Error Handling 🚨

**Proper Error Handling**:
```typescript
// ❌ Bad: Silent failures
function parseData(json) {
  try {
    return JSON.parse(json);
  } catch (e) {
    return null; // Error is hidden
  }
}

// ✅ Good: Log and propagate
function parseData(json) {
  try {
    return JSON.parse(json);
  } catch (error) {
    logger.error('Failed to parse JSON', { error, json });
    throw new ParseError('Invalid JSON format', { cause: error });
  }
}
```

**Async Error Handling**:
```typescript
// ❌ Bad: Unhandled promise rejection
async function fetchData() {
  const response = await fetch(url);
  return response.json();
}

// ✅ Good: Proper error handling
async function fetchData() {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new HttpError(response.status, response.statusText);
    }
    return await response.json();
  } catch (error) {
    logger.error('Failed to fetch data', { error, url });
    throw error;
  }
}
```

---

### 6. Type Safety 🔧

**TypeScript Best Practices**:
```typescript
// ❌ Bad: Using any
function processData(data: any) {
  return data.value.toUpperCase();
}

// ✅ Good: Proper types
interface DataInput {
  value: string;
}

function processData(data: DataInput): string {
  return data.value.toUpperCase();
}
```

**Null Safety**:
```typescript
// ❌ Bad: No null check
function getUsername(user) {
  return user.profile.name.toUpperCase();
}

// ✅ Good: Optional chaining
function getUsername(user) {
  return user?.profile?.name?.toUpperCase() ?? 'Anonymous';
}
```

---

### 7. Architecture & Design 🏗️

**Separation of Concerns**:
```typescript
// ❌ Bad: Mixed concerns
class UserController {
  async createUser(req, res) {
    const { email, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await db.query(
      'INSERT INTO users (email, password) VALUES ($1, $2)',
      [email, hashedPassword]
    );
    await sendEmail(email, 'Welcome!');
    res.json(user);
  }
}

// ✅ Good: Separated layers
class UserController {
  async createUser(req, res) {
    const userData = req.body;
    const user = await this.userService.createUser(userData);
    res.json(user);
  }
}

class UserService {
  async createUser(userData) {
    const hashedPassword = await this.hashPassword(userData.password);
    const user = await this.userRepository.create({
      ...userData,
      password: hashedPassword
    });
    await this.emailService.sendWelcomeEmail(user.email);
    return user;
  }
}
```

**Dependency Injection**:
```typescript
// ❌ Bad: Hard dependencies
class OrderService {
  private db = new Database();
  private emailer = new EmailService();

  async processOrder(order) {
    await this.db.save(order);
    await this.emailer.send(order.email, 'Order confirmed');
  }
}

// ✅ Good: Injected dependencies
class OrderService {
  constructor(
    private db: IDatabase,
    private emailer: IEmailService
  ) {}

  async processOrder(order) {
    await this.db.save(order);
    await this.emailer.send(order.email, 'Order confirmed');
  }
}
```

---

### 8. Testing 🧪

**Test Quality Checks**:
- [ ] Tests are independent (no shared state)
- [ ] Tests are deterministic (no random data)
- [ ] Tests have clear arrange-act-assert structure
- [ ] Test names describe what is being tested
- [ ] Edge cases are tested
- [ ] Error cases are tested
- [ ] Mocks are used appropriately

```typescript
// ✅ Good test structure
describe('calculateDiscount', () => {
  it('should apply 10% discount for orders over $100', () => {
    // Arrange
    const order = { total: 150 };

    // Act
    const discount = calculateDiscount(order);

    // Assert
    expect(discount).toBe(15);
  });

  it('should return 0 for orders under $100', () => {
    const order = { total: 50 };
    const discount = calculateDiscount(order);
    expect(discount).toBe(0);
  });

  it('should throw error for negative totals', () => {
    const order = { total: -10 };
    expect(() => calculateDiscount(order)).toThrow('Invalid total');
  });
});
```

---

### 9. Documentation 📚

**Code Documentation**:
- [ ] Complex logic has explanatory comments
- [ ] Public APIs have JSDoc/docstring comments
- [ ] README is updated if needed
- [ ] Breaking changes are documented
- [ ] Migration guide is provided if needed

```typescript
/**
 * Calculates the total price including tax and discounts.
 *
 * @param items - Array of cart items with price and quantity
 * @param taxRate - Tax rate as decimal (e.g., 0.1 for 10%)
 * @param discountCode - Optional discount code to apply
 * @returns The final price after tax and discounts
 * @throws {InvalidDiscountError} If discount code is invalid
 *
 * @example
 * const total = calculateTotal(
 *   [{ price: 10, quantity: 2 }],
 *   0.1,
 *   'SAVE10'
 * );
 */
function calculateTotal(
  items: CartItem[],
  taxRate: number,
  discountCode?: string
): number {
  // Implementation
}
```

---

### 10. Git & Version Control 📋

**Commit Quality**:
- [ ] Commits are atomic (one logical change)
- [ ] Commit messages are descriptive
- [ ] No debug code or commented-out code
- [ ] No unnecessary files (node_modules, .env, etc.)
- [ ] Branch name follows convention

**Good Commit Messages**:
```
feat: add user authentication with JWT
fix: resolve race condition in order processing
refactor: extract validation logic into separate module
test: add integration tests for payment flow
docs: update API documentation for v2 endpoints
```

---

## Language-Specific Checks

### JavaScript/TypeScript
- [ ] `===` used instead of `==`
- [ ] `const` and `let` used instead of `var`
- [ ] Promises are properly handled
- [ ] Optional chaining is used for null safety
- [ ] Types are properly defined (TypeScript)

### Python
- [ ] PEP 8 style guide followed
- [ ] Type hints are used
- [ ] Context managers used for resources
- [ ] List comprehensions used appropriately
- [ ] Virtual environment documented

### Go
- [ ] Errors are explicitly handled
- [ ] defer used for cleanup
- [ ] Goroutines don't leak
- [ ] Channels are properly closed
- [ ] Code is formatted with `gofmt`

---

## Code Smells to Watch For

### Common Code Smells
1. **Long Functions**: Functions > 50 lines
2. **Long Parameter Lists**: More than 3-4 parameters
3. **Duplicated Code**: Same logic in multiple places
4. **Dead Code**: Unused functions/variables
5. **God Classes**: Classes doing too much
6. **Magic Numbers**: Unexplained numeric constants
7. **Nested Conditionals**: Deep if/else chains
8. **Primitive Obsession**: Using primitives instead of objects

### Refactoring Suggestions
```typescript
// Code smell: Long parameter list
function createUser(name, email, age, address, phone, role, department) {
  // ...
}

// Better: Use object parameter
interface CreateUserParams {
  name: string;
  email: string;
  age: number;
  address: string;
  phone: string;
  role: string;
  department: string;
}

function createUser(params: CreateUserParams) {
  // ...
}
```

---

## Review Comment Templates

### Requesting Changes
```
❌ **Issue**: SQL injection vulnerability
**Line**: 45
**Severity**: Critical

The query concatenates user input directly into SQL.

**Current**:
`const query = "SELECT * FROM users WHERE name = '" + username + "'";`

**Suggested**:
`const query = "SELECT * FROM users WHERE name = $1";`
`await db.query(query, [username]);`

**Why**: Prevents SQL injection attacks (OWASP Top 10).
```

### Suggestions
```
💡 **Suggestion**: Extract to separate function
**Line**: 120

This validation logic is complex and reused in multiple places. Consider extracting it into a `validateUserInput()` function for better maintainability.
```

### Praise
```
✅ **Great work**: Comprehensive error handling
**Line**: 78-95

Excellent error handling with descriptive messages and proper logging. This will make debugging much easier.
```

---

## Checklist Summary

Use this for quick review:

```markdown
## Quick Review Checklist

### Must Check
- [ ] Tests pass
- [ ] No security vulnerabilities
- [ ] No performance issues (N+1 queries, etc.)
- [ ] Proper error handling
- [ ] No hardcoded secrets
- [ ] Code is readable

### Should Check
- [ ] Tests cover edge cases
- [ ] Documentation is updated
- [ ] Follows style guide
- [ ] No code smells
- [ ] Dependencies are necessary

### Nice to Have
- [ ] Performance is optimal
- [ ] Code could be simplified
- [ ] Better naming suggestions
```

---

## Tools & Automation

### Linters & Formatters
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting
- **Pylint**: Python linting
- **Black**: Python formatting
- **golangci-lint**: Go linting

### Security Scanners
- **Snyk**: Dependency vulnerability scanning
- **SonarQube**: Code quality and security
- **npm audit**: Node.js security audit
- **Bandit**: Python security scanner

### Code Coverage
- **Istanbul/nyc**: JavaScript coverage
- **Coverage.py**: Python coverage
- **Codecov**: Coverage reporting platform

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: Code Reviewer Agent
