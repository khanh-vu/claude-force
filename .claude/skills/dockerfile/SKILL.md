# Dockerfile Skill

## Overview
Best practices and patterns for writing efficient, secure, and maintainable Dockerfiles.

## Capabilities
- Multi-stage builds
- Layer optimization
- Security hardening
- Size optimization
- Development vs Production configurations

---

## Basic Dockerfile Structure

```dockerfile
# Use official base image with specific version
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run application
CMD ["node", "server.js"]
```

---

## Multi-Stage Builds

### Node.js Example

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Copy only necessary files from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

# Use non-root user
USER node

EXPOSE 3000

CMD ["node", "dist/server.js"]
```

### Go Example

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /app/server

# Production stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/server ./

EXPOSE 8080

CMD ["./server"]
```

### Python Example

```dockerfile
# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
```

---

## Best Practices

### 1. Use Specific Base Image Tags

```dockerfile
# ❌ Bad: Using 'latest' tag
FROM node:latest

# ✅ Good: Using specific version
FROM node:18.17.0-alpine

# ✅ Also good: Using digest for reproducibility
FROM node:18-alpine@sha256:a1e8...
```

### 2. Minimize Layers

```dockerfile
# ❌ Bad: Multiple RUN commands
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get clean

# ✅ Good: Combine commands
RUN apt-get update && \
    apt-get install -y \
      curl \
      git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 3. Order Layers by Change Frequency

```dockerfile
# ✅ Correct order (least to most frequently changing)
FROM node:18-alpine

WORKDIR /app

# 1. Dependencies (change infrequently)
COPY package*.json ./
RUN npm ci

# 2. Source code (changes frequently)
COPY . .

# 3. Build (depends on source)
RUN npm run build
```

### 4. Use .dockerignore

```.dockerignore
# Dependencies
node_modules
npm-debug.log

# Build outputs
dist
build
*.log

# Git
.git
.gitignore

# Environment
.env
.env.local

# IDE
.vscode
.idea

# Documentation
README.md
docs/

# Tests
*.test.js
__tests__
coverage/
```

### 5. Run as Non-Root User

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Create app user
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001

# Copy files as root
COPY package*.json ./
RUN npm ci

COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 3000

CMD ["node", "server.js"]
```

### 6. Use COPY Instead of ADD

```dockerfile
# ❌ Bad: Using ADD (has auto-extraction behavior)
ADD https://example.com/file.tar.gz /app/

# ✅ Good: Use COPY for local files
COPY ./src /app/src

# ✅ Good: Use RUN + wget/curl for URLs
RUN wget https://example.com/file.tar.gz && \
    tar -xzf file.tar.gz && \
    rm file.tar.gz
```

---

## Security Best Practices

### 1. Scan for Vulnerabilities

```dockerfile
FROM node:18-alpine

# Add security scanning (Trivy, Snyk, etc.)
# docker build --target scanner .
FROM aquasec/trivy:latest AS scanner
COPY --from=0 / /scan
RUN trivy filesystem --exit-code 1 /scan
```

### 2. Don't Store Secrets in Image

```dockerfile
# ❌ Bad: Hardcoded secrets
ENV API_KEY=secret123

# ✅ Good: Pass secrets at runtime
# docker run -e API_KEY=secret123 myapp
ENV API_KEY=

# ✅ Good: Use Docker secrets
# docker secret create api_key ./api_key.txt
# In compose: secrets: - api_key
```

### 3. Use Minimal Base Images

```dockerfile
# ❌ Larger: Ubuntu base (~70MB)
FROM ubuntu:22.04

# ✅ Better: Alpine base (~5MB)
FROM alpine:3.18

# ✅ Best: Distroless (minimal runtime)
FROM gcr.io/distroless/static:nonroot
```

### 4. Keep Images Updated

```dockerfile
FROM node:18-alpine

# Update packages
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
      curl \
      ca-certificates && \
    rm -rf /var/cache/apk/*
```

---

## Development vs Production

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Enable hot reload
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

### Production Dockerfile

```dockerfile
# Dockerfile (production)
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

USER nextjs

EXPOSE 3000

CMD ["node", "dist/server.js"]
```

---

## Docker Compose

### Basic Compose File

```yaml
version: '3.9'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/myapp
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### Development Compose

```yaml
# docker-compose.dev.yml
version: '3.9'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    volumes:
      # Mount source code for hot reload
      - ./src:/app/src
      - ./package.json:/app/package.json
    command: npm run dev

  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=myapp_dev
```

---

## Optimization Techniques

### 1. Leverage Build Cache

```dockerfile
# Copy only dependency files first
COPY package*.json ./
RUN npm ci

# Then copy source code (changes more frequently)
COPY . .
```

### 2. Use BuildKit

```bash
# Enable BuildKit for faster builds
DOCKER_BUILDKIT=1 docker build -t myapp .
```

```dockerfile
# syntax=docker/dockerfile:1.4

FROM node:18-alpine

# Use cache mounts
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# Use bind mounts for builds
RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    npm ci
```

### 3. Minimize Image Size

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy only built artifacts
COPY --from=builder /app/dist ./dist

# Remove unnecessary files
RUN npm cache clean --force && \
    rm -rf /tmp/* /var/tmp/*

USER node

CMD ["node", "dist/server.js"]
```

---

## Health Checks

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1

CMD ["node", "server.js"]
```

**healthcheck.js**:
```javascript
const http = require('http');

const options = {
  host: 'localhost',
  port: 3000,
  path: '/health',
  timeout: 2000
};

const request = http.get(options, (res) => {
  if (res.statusCode === 200) {
    process.exit(0);
  } else {
    process.exit(1);
  }
});

request.on('error', () => {
  process.exit(1);
});

request.end();
```

---

## Common Patterns

### Next.js Application

```dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### FastAPI Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Debugging

### Interactive Shell in Container

```bash
# Run container with shell
docker run -it myapp sh

# Execute shell in running container
docker exec -it container_name sh

# Override entrypoint
docker run --entrypoint sh myapp
```

### View Build Cache

```bash
# Show build cache
docker system df

# Clean build cache
docker builder prune
```

---

## Quick Reference

### Build Commands

```bash
# Basic build
docker build -t myapp:latest .

# Build with custom Dockerfile
docker build -f Dockerfile.prod -t myapp:prod .

# Build with build args
docker build --build-arg NODE_ENV=production -t myapp .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t myapp .
```

### Run Commands

```bash
# Run container
docker run -d -p 3000:3000 --name myapp myapp:latest

# Run with environment variables
docker run -e NODE_ENV=production myapp

# Run with volume
docker run -v $(pwd)/data:/app/data myapp

# Run with network
docker run --network mynetwork myapp
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Maintained By**: DevOps Architect
