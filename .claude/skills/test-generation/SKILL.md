# Test Generation Skill

## Overview
Comprehensive patterns and best practices for generating high-quality automated tests across different testing frameworks and paradigms.

## Capabilities
- Unit test generation (Jest, Vitest, pytest, JUnit)
- Integration test patterns
- E2E test creation (Playwright, Cypress)
- Test data generation
- Mock and stub creation
- Test coverage strategies

---

## Testing Frameworks

### JavaScript/TypeScript

#### Jest/Vitest Patterns

**Basic Unit Test Structure**:
```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { functionToTest } from './module';

describe('ModuleName', () => {
  describe('functionToTest', () => {
    it('should return expected result for valid input', () => {
      // Arrange
      const input = 'test';
      const expected = 'TEST';

      // Act
      const result = functionToTest(input);

      // Assert
      expect(result).toBe(expected);
    });

    it('should throw error for invalid input', () => {
      expect(() => functionToTest(null)).toThrow('Invalid input');
    });
  });
});
```

**Testing Async Functions**:
```typescript
it('should fetch user data successfully', async () => {
  const userId = '123';
  const userData = await fetchUser(userId);

  expect(userData).toHaveProperty('id', userId);
  expect(userData).toHaveProperty('name');
});
```

**Testing React Components**:
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('should call onClick handler when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
});
```

#### Playwright E2E Tests

```typescript
import { test, expect } from '@playwright/test';

test.describe('User Authentication', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'user@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Welcome');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'wrong@example.com');
    await page.fill('input[name="password"]', 'wrong');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error')).toBeVisible();
    await expect(page.locator('.error')).toContainText('Invalid credentials');
  });
});
```

### Python

#### pytest Patterns

**Basic Test Structure**:
```python
import pytest
from mymodule import function_to_test

class TestFunctionToTest:
    def test_returns_expected_result(self):
        # Arrange
        input_data = "test"
        expected = "TEST"

        # Act
        result = function_to_test(input_data)

        # Assert
        assert result == expected

    def test_raises_error_for_invalid_input(self):
        with pytest.raises(ValueError, match="Invalid input"):
            function_to_test(None)
```

**Fixtures**:
```python
import pytest

@pytest.fixture
def sample_user():
    return {
        'id': '123',
        'name': 'John Doe',
        'email': 'john@example.com'
    }

@pytest.fixture
def database_connection():
    conn = create_connection()
    yield conn
    conn.close()

def test_user_creation(sample_user, database_connection):
    user_id = create_user(database_connection, sample_user)
    assert user_id is not None
```

**Parametrized Tests**:
```python
@pytest.mark.parametrize("input_value,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_uppercase_conversion(input_value, expected):
    result = to_uppercase(input_value)
    assert result == expected
```

---

## Mocking Patterns

### JavaScript/TypeScript (Vitest)

**Mocking Modules**:
```typescript
import { vi } from 'vitest';
import { fetchData } from './api';

vi.mock('./api', () => ({
  fetchData: vi.fn()
}));

describe('DataProcessor', () => {
  it('should process fetched data', async () => {
    const mockData = { id: 1, value: 'test' };
    vi.mocked(fetchData).mockResolvedValue(mockData);

    const result = await processData();

    expect(fetchData).toHaveBeenCalled();
    expect(result).toEqual(mockData);
  });
});
```

**Mocking External Dependencies**:
```typescript
const mockAxios = {
  get: vi.fn(),
  post: vi.fn()
};

vi.mock('axios', () => ({
  default: mockAxios
}));
```

### Python (pytest + unittest.mock)

**Mocking Functions**:
```python
from unittest.mock import Mock, patch

def test_api_call():
    with patch('mymodule.requests.get') as mock_get:
        mock_get.return_value.json.return_value = {'data': 'test'}

        result = fetch_api_data()

        mock_get.assert_called_once()
        assert result['data'] == 'test'
```

**Mocking Classes**:
```python
from unittest.mock import MagicMock

def test_database_query():
    mock_db = MagicMock()
    mock_db.query.return_value = [{'id': 1, 'name': 'Test'}]

    service = UserService(mock_db)
    users = service.get_all_users()

    assert len(users) == 1
    mock_db.query.assert_called_once_with('SELECT * FROM users')
```

---

## Test Data Generation

### Factory Pattern

```typescript
// TypeScript Factory
export class UserFactory {
  static create(overrides = {}) {
    return {
      id: faker.string.uuid(),
      name: faker.person.fullName(),
      email: faker.internet.email(),
      createdAt: faker.date.past(),
      ...overrides
    };
  }

  static createMany(count: number, overrides = {}) {
    return Array.from({ length: count }, () => this.create(overrides));
  }
}

// Usage in tests
const user = UserFactory.create({ email: 'specific@example.com' });
const users = UserFactory.createMany(10);
```

```python
# Python Factory (using factory_boy)
import factory
from myapp.models import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Faker('uuid4')
    name = factory.Faker('name')
    email = factory.Faker('email')
    created_at = factory.Faker('date_time')

# Usage
user = UserFactory.create(email='specific@example.com')
users = UserFactory.create_batch(10)
```

---

## Test Coverage Strategies

### Coverage Goals
- **Unit Tests**: Aim for 80%+ line coverage
- **Integration Tests**: Cover all critical paths
- **E2E Tests**: Cover main user flows

### What to Test

**High Priority**:
- Business logic
- Error handling
- Edge cases
- Security-critical code
- Data transformations

**Medium Priority**:
- UI interactions
- API endpoints
- Database queries
- Integration points

**Low Priority** (may skip):
- Simple getters/setters
- Configuration files
- Third-party library wrappers (if thin)

---

## Test Organization

### File Structure

```
src/
  components/
    Button.tsx
    Button.test.tsx
  services/
    UserService.ts
    UserService.test.ts
  utils/
    formatters.ts
    formatters.test.ts
tests/
  integration/
    api/
      user-api.test.ts
  e2e/
    auth/
      login.spec.ts
  fixtures/
    users.ts
  helpers/
    test-utils.ts
```

### Naming Conventions

- Test files: `*.test.ts` or `*.spec.ts`
- Test suites: Describe the module/class being tested
- Test cases: Start with "should" and describe expected behavior
- Use `describe` blocks to group related tests

---

## Best Practices

### AAA Pattern (Arrange-Act-Assert)

```typescript
it('should calculate total price with tax', () => {
  // Arrange
  const items = [
    { price: 10, quantity: 2 },
    { price: 5, quantity: 3 }
  ];
  const taxRate = 0.1;

  // Act
  const total = calculateTotal(items, taxRate);

  // Assert
  expect(total).toBe(38.5); // (20 + 15) * 1.1
});
```

### Test Independence

```typescript
describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  afterEach(() => {
    service.cleanup();
  });

  it('test 1', () => {
    // Each test starts with fresh service instance
  });

  it('test 2', () => {
    // No state shared from test 1
  });
});
```

### Testing Error Cases

```typescript
describe('validateEmail', () => {
  it('should accept valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });

  it('should reject email without @', () => {
    expect(validateEmail('userexample.com')).toBe(false);
  });

  it('should reject empty string', () => {
    expect(validateEmail('')).toBe(false);
  });

  it('should reject null', () => {
    expect(validateEmail(null)).toBe(false);
  });
});
```

### Async Testing

```typescript
// ✅ Good: Use async/await
it('should fetch user data', async () => {
  const data = await fetchUser('123');
  expect(data).toBeDefined();
});

// ❌ Bad: Missing await
it('should fetch user data', () => {
  const data = fetchUser('123'); // Returns Promise, not data!
  expect(data).toBeDefined(); // Will fail
});
```

---

## Common Pitfalls to Avoid

1. **Testing Implementation Details**: Test behavior, not internals
2. **Brittle Tests**: Avoid tight coupling to HTML structure
3. **Slow Tests**: Mock external dependencies
4. **Unclear Assertions**: Use descriptive error messages
5. **Over-Mocking**: Don't mock everything, test real integrations when possible
6. **No Edge Cases**: Test null, empty, boundary conditions
7. **Flaky Tests**: Avoid timing issues, use proper waits

---

## Integration with CI/CD

```yaml
# GitHub Actions example
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage/coverage-final.json
```

---

## Quick Reference

### Jest/Vitest Matchers
- `toBe()` - Strict equality (===)
- `toEqual()` - Deep equality
- `toHaveProperty()` - Object has property
- `toContain()` - Array/string contains value
- `toThrow()` - Function throws error
- `toBeNull()`, `toBeUndefined()`, `toBeTruthy()`, `toBeFalsy()`

### Pytest Assertions
- `assert x == y` - Equality
- `assert x is None` - Identity
- `assert x in y` - Membership
- `assert x > y` - Comparison
- `pytest.raises(Exception)` - Exception testing
- `pytest.approx(x)` - Floating point comparison

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: QC Automation Expert
