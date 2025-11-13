# Scenario: Add Health Check Endpoint

## Difficulty: Simple
**Category**: Backend Development
**Expected Duration**: 5 minutes
**Expected Agents**: 1-2

---

## Task Description

Add a simple health check endpoint to an Express.js API that returns server status and uptime.

**User Story**:
> As a DevOps engineer, I need a `/health` endpoint so I can monitor the application's status and include it in load balancer health checks.

---

## Requirements

### Functional Requirements
1. Create GET endpoint at `/health`
2. Return JSON response with:
   - `status`: "ok" or "error"
   - `timestamp`: current ISO timestamp
   - `uptime`: process uptime in seconds
3. Return 200 status code when healthy

### Non-Functional Requirements
1. Response time < 100ms
2. No database queries (fast check)
3. Follow existing API patterns

---

## Expected Agent Selection

### Primary Agent
**backend-architect**
- Rationale: Simple API endpoint design
- Expected contract: Design endpoint structure, implement handler
- Skills used: RESTful API design, Express.js patterns

### Optional Agent (if code review requested)
**code-reviewer**
- Rationale: Validate implementation follows best practices
- Expected contract: Review endpoint implementation
- Skills used: Code quality validation, API patterns

---

## Success Criteria

### Must Have ✅
- [x] Endpoint responds at `/health`
- [x] Returns correct JSON structure
- [x] Returns 200 status code
- [x] Response includes all required fields

### Quality Checks ✅
- [x] Code follows project conventions
- [x] No security vulnerabilities
- [x] Proper error handling
- [x] Response time < 100ms

### Optional ⭐
- [ ] Unit tests for endpoint
- [ ] OpenAPI documentation
- [ ] Logging for health checks

---

## Input Context

### Existing Codebase
```javascript
// server.js
const express = require('express');
const app = express();

app.use(express.json());

// Existing endpoints
app.get('/api/users', (req, res) => {
  // ... user logic
});

app.post('/api/users', (req, res) => {
  // ... user creation logic
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

---

## Expected Output

### Implementation
```javascript
// server.js (with health endpoint added)
const express = require('express');
const app = express();

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Existing endpoints
app.get('/api/users', (req, res) => {
  // ... user logic
});

app.post('/api/users', (req, res) => {
  // ... user creation logic
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Example Response
```json
{
  "status": "ok",
  "timestamp": "2025-11-13T10:30:45.123Z",
  "uptime": 3600.5
}
```

---

## Metrics to Track

### Performance
- Agent selection time: ~0.5s (expected)
- Implementation time: ~2 minutes (expected)
- Total completion time: ~3 minutes (expected)

### Quality
- Code quality score: 95/100 (expected)
- Security vulnerabilities: 0 (expected)
- Test coverage: N/A (no tests required for simple scenario)

### Cost
- Tokens used: ~500-1000 (expected)
- API calls: 1-2 (expected)

---

## Validation Script

```javascript
// test_health_endpoint.js
const axios = require('axios');

async function validateHealthEndpoint() {
  const start = Date.now();

  try {
    const response = await axios.get('http://localhost:3000/health');
    const duration = Date.now() - start;

    // Check status code
    console.assert(response.status === 200, '✅ Status code is 200');

    // Check response structure
    const { status, timestamp, uptime } = response.data;
    console.assert(status === 'ok', '✅ Status is "ok"');
    console.assert(typeof timestamp === 'string', '✅ Timestamp is string');
    console.assert(typeof uptime === 'number', '✅ Uptime is number');

    // Check response time
    console.assert(duration < 100, `✅ Response time ${duration}ms < 100ms`);

    // Validate timestamp format (ISO 8601)
    const date = new Date(timestamp);
    console.assert(!isNaN(date.getTime()), '✅ Timestamp is valid ISO format');

    console.log('\n✅ All validation checks passed!');
    console.log(`Response time: ${duration}ms`);
    console.log(`Response:`, response.data);

    return true;
  } catch (error) {
    console.error('❌ Validation failed:', error.message);
    return false;
  }
}

validateHealthEndpoint();
```

---

## Learning Outcomes

### What This Demonstrates
1. **Simple agent selection**: Single-purpose agent for straightforward task
2. **Contract clarity**: Clear input/output expectations
3. **RESTful patterns**: Standard health check implementation
4. **Quick validation**: Fast success/failure determination

### Skills Highlighted
- Backend-architect's API design expertise
- RESTful endpoint patterns from api-design skill
- Express.js conventions

---

## Variants for Testing

### Variant 1: With Database Check
Add database connectivity check to health endpoint
- **Complexity**: +1 agent (database-architect)
- **Duration**: +3 minutes

### Variant 2: With Comprehensive Health
Include memory usage, CPU, disk space
- **Complexity**: +1 agent (backend-architect)
- **Duration**: +5 minutes

### Variant 3: With Tests
Add unit and integration tests
- **Complexity**: +1 agent (qc-automation-expert)
- **Duration**: +8 minutes

---

**Status**: Ready for Execution
**Version**: 1.0.0
**Created**: 2025-11-13
