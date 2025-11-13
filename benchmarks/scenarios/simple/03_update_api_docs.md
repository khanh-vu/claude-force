# Scenario: Update API Documentation

## Difficulty: Simple
**Category**: Documentation
**Expected Duration**: 6 minutes
**Expected Agents**: 1-2

---

## Task Description

Update API documentation to include the newly added `/health` endpoint with OpenAPI/Swagger specification.

**User Story**:
> As an API consumer, I need documentation for the `/health` endpoint so I can integrate health checks into my monitoring system.

---

## Requirements

### Functional Requirements
1. Add `/health` endpoint to OpenAPI spec
2. Include request/response examples
3. Document all response fields
4. Maintain existing documentation style

### Non-Functional Requirements
1. Follow OpenAPI 3.0 specification
2. Include clear descriptions
3. Provide example responses
4. Keep documentation DRY (reusable components)

---

## Expected Agent Selection

### Primary Agent
**api-documenter**
- Rationale: Specialized in OpenAPI/Swagger documentation
- Expected contract: Update API spec with new endpoint
- Skills used: OpenAPI patterns, API documentation best practices

### Optional Agent
**document-writer-expert**
- Rationale: If user guide or markdown docs also need updates
- Expected contract: Update markdown documentation
- Skills used: Technical writing, markdown formatting

---

## Success Criteria

### Must Have ✅
- [x] Endpoint documented in OpenAPI spec
- [x] All response fields documented
- [x] Example responses included
- [x] Spec validates against OpenAPI 3.0

### Quality Checks ✅
- [x] Clear descriptions
- [x] Follows existing style
- [x] No broken references
- [x] Schema definitions reusable

### Optional ⭐
- [ ] Response examples for error cases
- [ ] cURL examples
- [ ] Client SDK examples

---

## Input Context

### Existing OpenAPI Spec
```yaml
# openapi.yaml
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: API for managing users

servers:
  - url: http://localhost:3000
    description: Development server

paths:
  /api/users:
    get:
      summary: List all users
      tags:
        - Users
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

    post:
      summary: Create a new user
      tags:
        - Users
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

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
          example: user_123
        name:
          type: string
          example: John Doe
        email:
          type: string
          format: email
          example: john@example.com
        createdAt:
          type: string
          format: date-time
          example: '2025-11-13T10:00:00Z'

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
```

### Health Endpoint Implementation
```javascript
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});
```

---

## Expected Output

### Updated OpenAPI Spec
```yaml
openapi: 3.0.0
info:
  title: User Management API
  version: 1.0.0
  description: API for managing users

servers:
  - url: http://localhost:3000
    description: Development server

paths:
  /health:
    get:
      summary: Health check endpoint
      description: Returns the current health status of the API server
      tags:
        - System
      responses:
        '200':
          description: Server is healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
              examples:
                healthy:
                  value:
                    status: ok
                    timestamp: '2025-11-13T10:30:45.123Z'
                    uptime: 3600.5

  /api/users:
    get:
      summary: List all users
      tags:
        - Users
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

    post:
      summary: Create a new user
      tags:
        - Users
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

components:
  schemas:
    HealthResponse:
      type: object
      description: Health check response
      properties:
        status:
          type: string
          description: Current health status
          enum: [ok, error]
          example: ok
        timestamp:
          type: string
          format: date-time
          description: Current server timestamp in ISO 8601 format
          example: '2025-11-13T10:30:45.123Z'
        uptime:
          type: number
          description: Server uptime in seconds
          example: 3600.5

    User:
      type: object
      properties:
        id:
          type: string
          example: user_123
        name:
          type: string
          example: John Doe
        email:
          type: string
          format: email
          example: john@example.com
        createdAt:
          type: string
          format: date-time
          example: '2025-11-13T10:00:00Z'

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
```

### Updated README (if applicable)
```markdown
## API Endpoints

### Health Check

Check if the API server is running and healthy.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "timestamp": "2025-11-13T10:30:45.123Z",
  "uptime": 3600.5
}
```

**Fields**:
- `status` (string): Health status - "ok" if healthy, "error" if issues detected
- `timestamp` (string): Current server time in ISO 8601 format
- `uptime` (number): Server uptime in seconds

**Example**:
```bash
curl http://localhost:3000/health
```

**Use Cases**:
- Load balancer health checks
- Monitoring system integration
- Service discovery
- Deployment validation
```

---

## Metrics to Track

### Performance
- Documentation time: ~4 minutes (expected)
- Validation time: ~1 minute (expected)
- Total completion time: ~6 minutes (expected)

### Quality
- OpenAPI spec valid: Yes/No
- All fields documented: Yes/No
- Examples provided: Yes/No
- Style consistency: 95%+ (expected)

### Completeness
- Request documented: Yes (GET only)
- Response documented: Yes
- Error cases documented: Optional
- Examples provided: Yes

---

## Validation Script

```bash
#!/bin/bash
# validate_openapi.sh

echo "Validating OpenAPI specification..."

# Install validator if not present
npm install -g @apidevtools/swagger-cli

# Validate spec
swagger-cli validate openapi.yaml

if [ $? -eq 0 ]; then
  echo "✅ OpenAPI spec is valid"
else
  echo "❌ OpenAPI spec validation failed"
  exit 1
fi

# Check for required fields
echo -e "\nChecking for required documentation..."

required_fields=(
  "/health"
  "HealthResponse"
  "status"
  "timestamp"
  "uptime"
)

all_present=true

for field in "${required_fields[@]}"; do
  if grep -q "$field" openapi.yaml; then
    echo "✅ Found: $field"
  else
    echo "❌ Missing: $field"
    all_present=false
  fi
done

if [ "$all_present" = true ]; then
  echo -e "\n✅ All required fields documented"
else
  echo -e "\n❌ Some required fields missing"
  exit 1
fi

# Generate HTML docs
echo -e "\nGenerating HTML documentation..."
npx redoc-cli bundle openapi.yaml -o docs/api-docs.html
echo "✅ Documentation generated at docs/api-docs.html"
```

---

## Learning Outcomes

### What This Demonstrates
1. **API documentation workflow**: OpenAPI spec updates
2. **Schema reusability**: Component definitions
3. **Documentation completeness**: All fields described
4. **Style consistency**: Following established patterns

### Skills Highlighted
- API-documenter's OpenAPI expertise
- API design patterns from api-design skill
- Component-based schema definitions
- Documentation best practices

### Documentation Best Practices
- ✅ Use OpenAPI 3.0 standard
- ✅ Define reusable components
- ✅ Include examples for all responses
- ✅ Add clear descriptions
- ✅ Document all fields with types
- ✅ Use tags for organization
- ✅ Validate spec with tools

---

## Variants for Testing

### Variant 1: Full API Documentation
Document entire API from scratch
- **Complexity**: +3-4 agents
- **Duration**: +30 minutes
- **Agents**: api-documenter, document-writer-expert, backend-architect

### Variant 2: With Client SDK
Generate and document client SDK
- **Complexity**: +2 agents
- **Duration**: +20 minutes
- **Tools**: OpenAPI Generator

### Variant 3: With Postman Collection
Create Postman collection from OpenAPI spec
- **Complexity**: +1 agent
- **Duration**: +10 minutes
- **Output**: Postman collection JSON

---

## Quality Checklist

### OpenAPI Spec Quality
- [ ] Valid OpenAPI 3.0 syntax
- [ ] All paths documented
- [ ] All parameters documented
- [ ] All responses documented
- [ ] Schemas use $ref for reusability
- [ ] Examples provided
- [ ] Tags for organization
- [ ] Security schemes defined (if applicable)

### Documentation Quality
- [ ] Clear, concise descriptions
- [ ] Consistent terminology
- [ ] Proper grammar and spelling
- [ ] Code examples formatted correctly
- [ ] Links work correctly
- [ ] Version information accurate

---

**Status**: Ready for Execution
**Version**: 1.0.0
**Created**: 2025-11-13
