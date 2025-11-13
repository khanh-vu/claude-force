# Scenario: User Authentication Feature

## Difficulty: Medium
**Category**: Full-Stack Feature
**Expected Duration**: 20 minutes
**Expected Agents**: 4-5

---

## Task Description

Implement a complete JWT-based user authentication system with login, registration, and protected routes.

**User Story**:
> As a product owner, I need user authentication so that users can securely register, login, and access protected resources.

---

## Requirements

### Functional Requirements
1. User registration with email and password
2. User login with JWT token generation
3. Password hashing (bcrypt)
4. Token refresh mechanism
5. Protected API routes requiring authentication
6. Logout functionality (token invalidation)

### Non-Functional Requirements
1. Passwords must be hashed with bcrypt (min 10 rounds)
2. JWT tokens expire after 1 hour
3. Refresh tokens expire after 7 days
4. Follow OWASP authentication best practices
5. Implement rate limiting on auth endpoints
6. SQL injection prevention via parameterized queries

---

## Expected Agent Selection

### Workflow: Full-Stack Feature (Simplified)

1. **backend-architect**
   - Design authentication architecture
   - Define API endpoints and contracts
   - Plan token management strategy
   - **Hands off**: Architecture document, API contracts

2. **database-architect**
   - Design users table schema
   - Create migration files
   - Plan indexes for performance
   - **Hands off**: Schema design, migration scripts

3. **security-specialist**
   - Review authentication design for vulnerabilities
   - Validate password hashing implementation
   - Check for OWASP Top 10 issues
   - **Hands off**: Security review report, recommendations

4. **python-expert** (or backend implementation agent)
   - Implement authentication endpoints
   - Integrate password hashing
   - Implement JWT token generation/validation
   - **Hands off**: Working implementation

5. **code-reviewer**
   - Final code quality review
   - Check for security issues
   - Validate error handling
   - **Hands off**: Review report, approval/changes needed

---

## Success Criteria

### Must Have ✅
- [x] Users can register with email/password
- [x] Users can login and receive JWT token
- [x] Protected routes require valid JWT
- [x] Passwords are hashed with bcrypt
- [x] JWT tokens expire correctly
- [x] SQL injection prevented

### Security Checks ✅
- [x] No plaintext passwords stored
- [x] No SQL injection vulnerabilities
- [x] No hardcoded secrets
- [x] Proper error messages (no info leakage)
- [x] Rate limiting on auth endpoints
- [x] CORS configured correctly

### Quality Checks ✅
- [x] Code follows project conventions
- [x] Error handling comprehensive
- [x] Input validation on all endpoints
- [x] Database constraints enforced

---

## Input Context

### Existing Codebase Structure
```
project/
├── server.js           # Express server
├── config/
│   └── database.js     # Database connection
├── routes/
│   └── users.js        # Existing user routes
├── models/
│   └── User.js         # User model (basic)
└── package.json
```

### Existing User Model (Basic)
```javascript
// models/User.js
class User {
  static async findByEmail(email) {
    const result = await db.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );
    return result.rows[0];
  }

  static async create({ name, email }) {
    const result = await db.query(
      'INSERT INTO users (name, email) VALUES ($1, $2) RETURNING *',
      [name, email]
    );
    return result.rows[0];
  }
}
```

---

## Expected Output

### 1. Database Schema (database-architect)

```sql
-- migrations/001_create_users_table.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- migrations/002_create_refresh_tokens_table.sql
CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(500) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
```

### 2. Authentication Middleware

```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'No token provided'
    });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({
        error: 'Forbidden',
        message: 'Invalid or expired token'
      });
    }
    req.user = user;
    next();
  });
}

module.exports = { authenticateToken };
```

### 3. Authentication Routes

```javascript
// routes/auth.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const rateLimit = require('express-rate-limit');
const User = require('../models/User');
const RefreshToken = require('../models/RefreshToken');

const router = express.Router();

// Rate limiting for auth endpoints
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: { error: 'Too many login attempts, please try again later' }
});

// Register
router.post('/register', authLimiter, async (req, res) => {
  try {
    const { email, password, name } = req.body;

    // Validation
    if (!email || !password || !name) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Email, password, and name are required'
      });
    }

    if (password.length < 8) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Password must be at least 8 characters'
      });
    }

    // Check if user exists
    const existingUser = await User.findByEmail(email);
    if (existingUser) {
      return res.status(409).json({
        error: 'ConflictError',
        message: 'User with this email already exists'
      });
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 10);

    // Create user
    const user = await User.create({
      email,
      password_hash: passwordHash,
      name
    });

    res.status(201).json({
      id: user.id,
      email: user.email,
      name: user.name,
      createdAt: user.created_at
    });
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      error: 'InternalServerError',
      message: 'Failed to register user'
    });
  }
});

// Login
router.post('/login', authLimiter, async (req, res) => {
  try {
    const { email, password } = req.body;

    // Validation
    if (!email || !password) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Email and password are required'
      });
    }

    // Find user
    const user = await User.findByEmail(email);
    if (!user) {
      return res.status(401).json({
        error: 'AuthenticationError',
        message: 'Invalid credentials'
      });
    }

    // Verify password
    const validPassword = await bcrypt.compare(password, user.password_hash);
    if (!validPassword) {
      return res.status(401).json({
        error: 'AuthenticationError',
        message: 'Invalid credentials'
      });
    }

    // Generate tokens
    const accessToken = jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    const refreshToken = jwt.sign(
      { id: user.id },
      process.env.REFRESH_TOKEN_SECRET,
      { expiresIn: '7d' }
    );

    // Store refresh token
    await RefreshToken.create({
      user_id: user.id,
      token: refreshToken,
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    });

    res.json({
      accessToken,
      refreshToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      error: 'InternalServerError',
      message: 'Failed to login'
    });
  }
});

// Refresh token
router.post('/refresh', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        error: 'ValidationError',
        message: 'Refresh token is required'
      });
    }

    // Verify refresh token
    const decoded = jwt.verify(refreshToken, process.env.REFRESH_TOKEN_SECRET);

    // Check if token exists in database
    const tokenRecord = await RefreshToken.findByToken(refreshToken);
    if (!tokenRecord) {
      return res.status(403).json({
        error: 'ForbiddenError',
        message: 'Invalid refresh token'
      });
    }

    // Generate new access token
    const accessToken = jwt.sign(
      { id: decoded.id },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.json({ accessToken });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(403).json({
      error: 'ForbiddenError',
      message: 'Invalid or expired refresh token'
    });
  }
});

// Logout
router.post('/logout', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (refreshToken) {
      await RefreshToken.deleteByToken(refreshToken);
    }

    res.json({ message: 'Logged out successfully' });
  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({
      error: 'InternalServerError',
      message: 'Failed to logout'
    });
  }
});

module.exports = router;
```

### 4. Protected Route Example

```javascript
// routes/profile.js
const express = require('express');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Protected route
router.get('/me', authenticateToken, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);

    if (!user) {
      return res.status(404).json({
        error: 'NotFoundError',
        message: 'User not found'
      });
    }

    res.json({
      id: user.id,
      email: user.email,
      name: user.name,
      createdAt: user.created_at
    });
  } catch (error) {
    console.error('Profile fetch error:', error);
    res.status(500).json({
      error: 'InternalServerError',
      message: 'Failed to fetch profile'
    });
  }
});

module.exports = router;
```

### 5. Environment Variables

```bash
# .env.example
JWT_SECRET=your-secret-key-here
REFRESH_TOKEN_SECRET=your-refresh-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
```

---

## Metrics to Track

### Performance
- Architecture design time: ~5 minutes
- Database schema design: ~3 minutes
- Security review: ~4 minutes
- Implementation time: ~6 minutes
- Code review: ~2 minutes
- **Total**: ~20 minutes

### Quality
- Security vulnerabilities: 0 (expected)
- OWASP Top 10 compliance: 100%
- Test coverage: 80%+ (if tests added)
- Code quality score: 90/100+

### Agent Coordination
- Successful handoffs: 4-5
- Rework required: 0-1
- Architecture changes: 0-1

---

## Validation Script

```javascript
// test_authentication.js
const axios = require('axios');

async function testAuthentication() {
  const baseURL = 'http://localhost:3000';
  let accessToken;
  let refreshToken;
  const testEmail = `test${Date.now()}@example.com`;

  console.log('Testing Authentication System...\n');

  // Test 1: Register
  try {
    console.log('1. Testing registration...');
    const registerRes = await axios.post(`${baseURL}/auth/register`, {
      email: testEmail,
      password: 'TestPassword123!',
      name: 'Test User'
    });
    console.log('✅ Registration successful');
    console.log(`   User ID: ${registerRes.data.id}`);
  } catch (error) {
    console.log('❌ Registration failed:', error.response?.data);
    return;
  }

  // Test 2: Login
  try {
    console.log('\n2. Testing login...');
    const loginRes = await axios.post(`${baseURL}/auth/login`, {
      email: testEmail,
      password: 'TestPassword123!'
    });
    accessToken = loginRes.data.accessToken;
    refreshToken = loginRes.data.refreshToken;
    console.log('✅ Login successful');
    console.log(`   Access token received: ${accessToken.substring(0, 20)}...`);
  } catch (error) {
    console.log('❌ Login failed:', error.response?.data);
    return;
  }

  // Test 3: Access protected route
  try {
    console.log('\n3. Testing protected route access...');
    const profileRes = await axios.get(`${baseURL}/profile/me`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    console.log('✅ Protected route accessed successfully');
    console.log(`   User: ${profileRes.data.name} (${profileRes.data.email})`);
  } catch (error) {
    console.log('❌ Protected route access failed:', error.response?.data);
    return;
  }

  // Test 4: Refresh token
  try {
    console.log('\n4. Testing token refresh...');
    const refreshRes = await axios.post(`${baseURL}/auth/refresh`, {
      refreshToken
    });
    console.log('✅ Token refresh successful');
    console.log(`   New access token: ${refreshRes.data.accessToken.substring(0, 20)}...`);
  } catch (error) {
    console.log('❌ Token refresh failed:', error.response?.data);
    return;
  }

  // Test 5: Invalid credentials
  try {
    console.log('\n5. Testing invalid credentials...');
    await axios.post(`${baseURL}/auth/login`, {
      email: testEmail,
      password: 'WrongPassword'
    });
    console.log('❌ Should have rejected invalid credentials');
  } catch (error) {
    if (error.response?.status === 401) {
      console.log('✅ Invalid credentials rejected correctly');
    } else {
      console.log('❌ Unexpected error:', error.response?.data);
    }
  }

  // Test 6: Logout
  try {
    console.log('\n6. Testing logout...');
    await axios.post(`${baseURL}/auth/logout`, { refreshToken });
    console.log('✅ Logout successful');
  } catch (error) {
    console.log('❌ Logout failed:', error.response?.data);
  }

  console.log('\n✅ All authentication tests completed!');
}

testAuthentication();
```

---

## Learning Outcomes

### What This Demonstrates
1. **Multi-agent coordination**: 4-5 agents working sequentially
2. **Security-first design**: OWASP compliance, security review
3. **Architectural planning**: Design before implementation
4. **Quality gates**: Code review catches issues
5. **Complete feature**: From architecture to working code

### Skills Highlighted
- Backend-architect's system design
- Database-architect's schema optimization
- Security-specialist's vulnerability detection
- API design patterns from api-design skill
- JWT authentication patterns
- OWASP Top 10 awareness

### Agent Handoffs
- **backend-architect → database-architect**: API contracts → Schema design
- **database-architect → security-specialist**: Schema → Security review
- **security-specialist → python-expert**: Security requirements → Implementation
- **python-expert → code-reviewer**: Implementation → Final review

---

**Status**: Ready for Execution
**Version**: 1.0.0
**Created**: 2025-11-13
