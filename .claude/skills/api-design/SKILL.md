# API Design Skill

## Overview
Best practices and patterns for designing robust, scalable, and developer-friendly REST APIs.

## Capabilities
- RESTful API design patterns
- HTTP methods and status codes
- API versioning strategies
- Authentication and authorization
- Error handling
- API documentation (OpenAPI/Swagger)

---

## RESTful Design Principles

### Resource-Oriented URLs

```
✅ Good RESTful Design:
GET    /api/users              - List all users
GET    /api/users/123          - Get user with ID 123
POST   /api/users              - Create new user
PUT    /api/users/123          - Update user 123
PATCH  /api/users/123          - Partially update user 123
DELETE /api/users/123          - Delete user 123

GET    /api/users/123/orders   - Get orders for user 123
POST   /api/users/123/orders   - Create order for user 123

❌ Bad: Verb-based URLs:
GET    /api/getUser?id=123
POST   /api/createUser
POST   /api/deleteUser/123
```

### HTTP Methods

| Method | Purpose | Idempotent | Safe | Request Body | Response Body |
|--------|---------|------------|------|--------------|---------------|
| GET | Retrieve resource | Yes | Yes | No | Yes |
| POST | Create resource | No | No | Yes | Yes |
| PUT | Replace resource | Yes | No | Yes | Yes |
| PATCH | Update resource | No | No | Yes | Yes |
| DELETE | Delete resource | Yes | No | No | Optional |

---

## HTTP Status Codes

### Success Responses (2xx)
- **200 OK**: Request succeeded (GET, PUT, PATCH)
- **201 Created**: Resource created (POST)
- **204 No Content**: Success with no body (DELETE)

### Client Errors (4xx)
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource doesn't exist
- **409 Conflict**: Conflict with current state (e.g., duplicate)
- **422 Unprocessable Entity**: Validation failed
- **429 Too Many Requests**: Rate limit exceeded

### Server Errors (5xx)
- **500 Internal Server Error**: Generic server error
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Service temporarily down
- **504 Gateway Timeout**: Upstream service timeout

### Examples

```typescript
// 200 OK - Successful GET
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.status(200).json(user);
});

// 201 Created - Successful POST
app.post('/api/users', async (req, res) => {
  const user = await User.create(req.body);
  res.status(201).json(user);
});

// 204 No Content - Successful DELETE
app.delete('/api/users/:id', async (req, res) => {
  await User.delete(req.params.id);
  res.status(204).send();
});

// 404 Not Found
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) {
    return res.status(404).json({
      error: 'User not found',
      message: `User with ID ${req.params.id} does not exist`
    });
  }
  res.status(200).json(user);
});
```

---

## Request/Response Format

### Request Body (JSON)

```json
POST /api/users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

### Response Format

**Success Response**:
```json
{
  "id": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "createdAt": "2025-11-13T10:00:00Z",
  "updatedAt": "2025-11-13T10:00:00Z"
}
```

**Error Response**:
```json
{
  "error": "ValidationError",
  "message": "Invalid input data",
  "details": [
    {
      "field": "email",
      "message": "Email must be valid"
    },
    {
      "field": "age",
      "message": "Age must be a positive number"
    }
  ],
  "timestamp": "2025-11-13T10:00:00Z",
  "path": "/api/users"
}
```

---

## Pagination

### Cursor-Based Pagination (Recommended)

```
GET /api/users?limit=20&cursor=eyJpZCI6MTIzfQ==

Response:
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTQzfQ==",
    "hasMore": true
  }
}
```

```typescript
app.get('/api/users', async (req, res) => {
  const { limit = 20, cursor } = req.query;

  const result = await User.findPaginated({
    limit: parseInt(limit),
    cursor: cursor ? decodeCursor(cursor) : null
  });

  res.json({
    data: result.items,
    pagination: {
      nextCursor: result.nextCursor ? encodeCursor(result.nextCursor) : null,
      hasMore: result.hasMore
    }
  });
});
```

### Offset-Based Pagination (Simple)

```
GET /api/users?page=2&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

---

## Filtering and Sorting

### Query Parameters

```
GET /api/users?role=admin&status=active&sort=-createdAt&fields=id,name,email

Parameters:
- role=admin           : Filter by role
- status=active        : Filter by status
- sort=-createdAt      : Sort by createdAt descending (- prefix)
- fields=id,name,email : Only return specified fields
```

### Implementation

```typescript
app.get('/api/users', async (req, res) => {
  const {
    role,
    status,
    sort = '-createdAt',
    fields = 'id,name,email,role,status',
    limit = 20,
    page = 1
  } = req.query;

  const filters = {};
  if (role) filters.role = role;
  if (status) filters.status = status;

  const sortField = sort.startsWith('-') ? sort.slice(1) : sort;
  const sortOrder = sort.startsWith('-') ? 'DESC' : 'ASC';

  const users = await User.find({
    where: filters,
    select: fields.split(','),
    order: { [sortField]: sortOrder },
    skip: (page - 1) * limit,
    take: limit
  });

  res.json({ data: users });
});
```

---

## API Versioning

### URL Versioning (Recommended)

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

```typescript
app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);
```

### Header Versioning

```
GET /api/users
Accept: application/vnd.api+json; version=1
```

### When to Version
- Breaking changes to response format
- Removing fields
- Changing field types
- Changing behavior significantly

---

## Authentication & Authorization

### JWT Bearer Token

```
GET /api/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

```typescript
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

app.get('/api/users/me', authenticateToken, (req, res) => {
  res.json(req.user);
});
```

### API Keys

```
GET /api/data
X-API-Key: sk_live_51H...
```

```typescript
const authenticateApiKey = async (req, res, next) => {
  const apiKey = req.headers['x-api-key'];

  if (!apiKey) {
    return res.status(401).json({ error: 'API key required' });
  }

  const isValid = await validateApiKey(apiKey);
  if (!isValid) {
    return res.status(403).json({ error: 'Invalid API key' });
  }

  next();
};
```

---

## Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: {
    error: 'Too Many Requests',
    message: 'Too many requests from this IP, please try again later.'
  },
  standardHeaders: true, // Return rate limit info in headers
  legacyHeaders: false
});

app.use('/api/', limiter);
```

**Response Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699891200
```

---

## Error Handling

### Consistent Error Format

```typescript
class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public details?: any
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

// Error handler middleware
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  res.status(statusCode).json({
    error: err.name,
    message,
    details: err.details,
    timestamp: new Date().toISOString(),
    path: req.path
  });
});
```

### Usage

```typescript
app.post('/api/users', async (req, res, next) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      throw new ApiError(400, 'Email and password are required');
    }

    const existingUser = await User.findByEmail(email);
    if (existingUser) {
      throw new ApiError(409, 'User with this email already exists');
    }

    const user = await User.create(req.body);
    res.status(201).json(user);
  } catch (error) {
    next(error);
  }
});
```

---

## CORS Configuration

```typescript
import cors from 'cors';

// Development: Allow all origins
app.use(cors());

// Production: Whitelist specific origins
app.use(cors({
  origin: ['https://example.com', 'https://app.example.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  exposedHeaders: ['X-RateLimit-Limit', 'X-RateLimit-Remaining'],
  credentials: true,
  maxAge: 86400 // 24 hours
}));
```

---

## API Documentation (OpenAPI/Swagger)

### Example OpenAPI Spec

```yaml
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: API for managing users

servers:
  - url: https://api.example.com/v1
    description: Production server

paths:
  /users:
    get:
      summary: List all users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

    post:
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserInput'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
          format: email
        createdAt:
          type: string
          format: date-time

    CreateUserInput:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
        email:
          type: string
          format: email

    Error:
      type: object
      properties:
        error:
          type: string
        message:
          type: string
        details:
          type: array
          items:
            type: object

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

---

## Best Practices Summary

### URL Design
✅ Use nouns for resources, not verbs
✅ Use plural nouns (`/users`, not `/user`)
✅ Use nested routes for relationships (`/users/123/orders`)
✅ Use hyphens for multi-word resources (`/order-items`)
❌ Avoid deep nesting (max 2-3 levels)

### Response Format
✅ Use JSON as default format
✅ Include timestamps (ISO 8601 format)
✅ Use camelCase for JSON properties
✅ Provide consistent error format
✅ Include request ID for debugging

### Security
✅ Always use HTTPS in production
✅ Implement rate limiting
✅ Validate and sanitize all inputs
✅ Use proper authentication (JWT, OAuth)
✅ Implement CORS correctly
✅ Don't expose sensitive data in responses

### Performance
✅ Implement caching (ETags, Cache-Control)
✅ Support compression (gzip)
✅ Use pagination for large datasets
✅ Support field filtering
✅ Optimize database queries

### Documentation
✅ Use OpenAPI/Swagger specification
✅ Provide code examples
✅ Document error responses
✅ Keep documentation up to date
✅ Include authentication requirements

---

## Quick Reference

### Common Patterns

**Health Check**:
```typescript
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});
```

**Soft Delete**:
```typescript
app.delete('/api/users/:id', async (req, res) => {
  await User.update(req.params.id, { deletedAt: new Date() });
  res.status(204).send();
});
```

**Bulk Operations**:
```typescript
app.post('/api/users/bulk', async (req, res) => {
  const { users } = req.body;
  const created = await User.bulkCreate(users);
  res.status(201).json({ created: created.length, data: created });
});
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: Backend Architect
