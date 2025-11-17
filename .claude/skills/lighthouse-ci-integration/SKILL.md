# Lighthouse CI Integration

Comprehensive patterns for integrating Lighthouse into CI/CD pipelines to enforce performance and SEO standards.

## Lighthouse CI Configuration

```javascript
// lighthouserc.js - Complete Configuration
module.exports = {
  ci: {
    collect: {
      // URLs to test
      url: [
        'http://localhost:3000',
        'http://localhost:3000/about',
        'http://localhost:3000/products',
      ],
      // Number of runs per URL (recommend 3-5 for stability)
      numberOfRuns: 3,
      // Collect settings
      settings: {
        preset: 'desktop', // or 'mobile'
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
        },
      },
    },
    assert: {
      // Performance budgets
      assertions: {
        // Core Web Vitals
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'interaction-to-next-paint': ['error', { maxNumericValue: 200 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'first-contentful-paint': ['warn', { maxNumericValue: 1800 }],
        'speed-index': ['warn', { maxNumericValue: 3400 }],
        'total-blocking-time': ['warn', { maxNumericValue: 200 }],

        // Category scores (0-1 scale)
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.95 }],

        // Resource budgets
        'resource-summary:script:size': ['error', { maxNumericValue: 300000 }],
        'resource-summary:stylesheet:size': ['warn', { maxNumericValue: 100000 }],
        'resource-summary:image:size': ['warn', { maxNumericValue: 500000 }],
        'resource-summary:font:size': ['warn', { maxNumericValue: 150000 }],
        'resource-summary:total:size': ['error', { maxNumericValue: 1000000 }],

        // SEO audits
        'meta-description': 'error',
        'document-title': 'error',
        'viewport': 'error',
        'canonical': 'warn',
        'robots-txt': 'warn',
        'hreflang': 'warn',
        'structured-data': 'warn',

        // Accessibility
        'aria-allowed-attr': 'error',
        'aria-required-attr': 'error',
        'button-name': 'error',
        'image-alt': 'error',
        'label': 'error',
        'link-name': 'error',

        // Performance best practices
        'uses-http2': 'warn',
        'uses-long-cache-ttl': 'warn',
        'uses-optimized-images': 'warn',
        'uses-text-compression': 'error',
        'uses-responsive-images': 'warn',
        'modern-image-formats': 'warn',
        'offscreen-images': 'warn',
        'render-blocking-resources': 'warn',
        'unminified-css': 'error',
        'unminified-javascript': 'error',
        'unused-css-rules': 'warn',
        'unused-javascript': 'warn',
      },
    },
    upload: {
      // Upload to Lighthouse CI server
      target: 'temporary-public-storage',
      // Or use LHCI server
      // serverBaseUrl: 'https://your-lhci-server.com',
      // token: process.env.LHCI_TOKEN,
    },
    server: {
      // LHCI server configuration (optional)
      port: 9001,
      storage: {
        storageMethod: 'sql',
        sqlDialect: 'sqlite',
        sqlDatabasePath: './lhci.db',
      },
    },
  },
};
```

## GitHub Actions Workflow

```yaml
# .github/workflows/lighthouse-ci.yml
name: Lighthouse CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build
        env:
          NODE_ENV: production

      - name: Start application server
        run: npm run start &
        env:
          PORT: 3000

      - name: Wait for server
        run: npx wait-on http://localhost:3000 --timeout 60000

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.13.x
          lhci autorun
        env:
          LHCI_GITHUB_APP_TOKEN: ${{ secrets.LHCI_GITHUB_APP_TOKEN }}

      - name: Upload Lighthouse results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: lighthouse-results
          path: .lighthouseci

      - name: Comment PR with results
        uses: treosh/lighthouse-ci-action@v10
        if: github.event_name == 'pull_request'
        with:
          urls: |
            http://localhost:3000
            http://localhost:3000/about
          uploadArtifacts: true
          temporaryPublicStorage: true
```

## GitLab CI Configuration

```yaml
# .gitlab-ci.yml
lighthouse:
  stage: test
  image: node:18
  services:
    - name: docker:dind
  script:
    # Install dependencies
    - npm ci

    # Build application
    - npm run build

    # Start application in background
    - npm start &
    - npx wait-on http://localhost:3000

    # Install and run Lighthouse CI
    - npm install -g @lhci/cli@0.13.x
    - lhci autorun --upload.target=temporary-public-storage

  artifacts:
    when: always
    paths:
      - .lighthouseci
    reports:
      junit: .lighthouseci/lighthouse-*.xml

  only:
    - merge_requests
    - main
```

## CircleCI Configuration

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  lighthouse:
    docker:
      - image: cimg/node:18.0
    steps:
      - checkout

      - restore_cache:
          keys:
            - v1-deps-{{ checksum "package-lock.json" }}

      - run:
          name: Install dependencies
          command: npm ci

      - save_cache:
          key: v1-deps-{{ checksum "package-lock.json" }}
          paths:
            - node_modules

      - run:
          name: Build application
          command: npm run build

      - run:
          name: Start application
          command: npm start
          background: true

      - run:
          name: Wait for application
          command: npx wait-on http://localhost:3000 --timeout 60000

      - run:
          name: Run Lighthouse CI
          command: |
            npm install -g @lhci/cli@0.13.x
            lhci autorun

      - store_artifacts:
          path: .lighthouseci

workflows:
  version: 2
  test:
    jobs:
      - lighthouse:
          filters:
            branches:
              only:
                - main
                - /pull\/.*/
```

## Custom Lighthouse Runner Script

```javascript
// scripts/run-lighthouse.js
const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');
const fs = require('fs');
const path = require('path');

async function runLighthouse(url, outputPath) {
  // Launch Chrome
  const chrome = await chromeLauncher.launch({
    chromeFlags: ['--headless', '--disable-gpu', '--no-sandbox'],
  });

  const options = {
    logLevel: 'info',
    output: ['html', 'json'],
    port: chrome.port,
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
  };

  // Run Lighthouse
  const runnerResult = await lighthouse(url, options);

  // Extract results
  const reportHtml = runnerResult.report[0];
  const reportJson = runnerResult.report[1];
  const lhr = runnerResult.lhr;

  // Save reports
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const htmlPath = path.join(outputPath, `lighthouse-${timestamp}.html`);
  const jsonPath = path.join(outputPath, `lighthouse-${timestamp}.json`);

  fs.writeFileSync(htmlPath, reportHtml);
  fs.writeFileSync(jsonPath, reportJson);

  // Check thresholds
  const scores = {
    performance: lhr.categories.performance.score * 100,
    accessibility: lhr.categories.accessibility.score * 100,
    bestPractices: lhr.categories['best-practices'].score * 100,
    seo: lhr.categories.seo.score * 100,
  };

  // Core Web Vitals
  const vitals = {
    lcp: lhr.audits['largest-contentful-paint'].numericValue,
    inp: lhr.audits['interaction-to-next-paint']?.numericValue || 0,
    cls: lhr.audits['cumulative-layout-shift'].numericValue,
  };

  console.log('\n=== Lighthouse Scores ===');
  console.log(`Performance: ${scores.performance}`);
  console.log(`Accessibility: ${scores.accessibility}`);
  console.log(`Best Practices: ${scores.bestPractices}`);
  console.log(`SEO: ${scores.seo}`);

  console.log('\n=== Core Web Vitals ===');
  console.log(`LCP: ${vitals.lcp}ms`);
  console.log(`INP: ${vitals.inp}ms`);
  console.log(`CLS: ${vitals.cls}`);

  // Fail CI if thresholds not met
  const failed = [];
  if (scores.performance < 90) failed.push('Performance');
  if (scores.accessibility < 90) failed.push('Accessibility');
  if (scores.seo < 95) failed.push('SEO');
  if (vitals.lcp > 2500) failed.push('LCP');
  if (vitals.inp > 200) failed.push('INP');
  if (vitals.cls > 0.1) failed.push('CLS');

  await chrome.kill();

  if (failed.length > 0) {
    console.error(`\n❌ Failed thresholds: ${failed.join(', ')}`);
    console.error(`\nReports saved to:\n  HTML: ${htmlPath}\n  JSON: ${jsonPath}`);
    process.exit(1);
  }

  console.log('\n✅ All thresholds passed!');
  console.log(`\nReports saved to:\n  HTML: ${htmlPath}\n  JSON: ${jsonPath}`);

  return { scores, vitals, reports: { html: htmlPath, json: jsonPath } };
}

// CLI usage
const url = process.argv[2] || 'http://localhost:3000';
const outputPath = process.argv[3] || './lighthouse-reports';

if (!fs.existsSync(outputPath)) {
  fs.mkdirSync(outputPath, { recursive: true });
}

runLighthouse(url, outputPath).catch((error) => {
  console.error('Lighthouse failed:', error);
  process.exit(1);
});
```

```json
// package.json scripts
{
  "scripts": {
    "lighthouse": "node scripts/run-lighthouse.js",
    "lighthouse:ci": "lhci autorun",
    "lighthouse:local": "lighthouse http://localhost:3000 --view"
  },
  "devDependencies": {
    "@lhci/cli": "^0.13.0",
    "lighthouse": "^11.0.0",
    "chrome-launcher": "^1.1.0"
  }
}
```

## Lighthouse CI Server Setup

```dockerfile
# Dockerfile for LHCI Server
FROM node:18-alpine

# Install Lighthouse CI server
RUN npm install -g @lhci/server@0.13.x

# Create app directory
WORKDIR /usr/src/lhci

# Expose port
EXPOSE 9001

# Start server
CMD ["lhci", "server", "--port=9001", "--storage.storageMethod=sql", "--storage.sqlDialect=postgres", "--storage.sqlConnectionUrl=${DATABASE_URL}"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  lhci-server:
    build: .
    ports:
      - '9001:9001'
    environment:
      - DATABASE_URL=postgresql://lhci:password@postgres:5432/lhci
    depends_on:
      - postgres

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=lhci
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=lhci
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

## Performance Budget Enforcer

```javascript
// scripts/check-performance-budget.js
const fs = require('fs');
const path = require('path');

const BUDGETS = {
  performance: 90,
  accessibility: 90,
  bestPractices: 90,
  seo: 95,
  lcp: 2500,
  inp: 200,
  cls: 0.1,
  scriptSize: 300000, // 300KB
  stylesheetSize: 100000, // 100KB
  imageSize: 500000, // 500KB
  totalSize: 1000000, // 1MB
};

function checkBudget(lighthouseJsonPath) {
  const report = JSON.parse(fs.readFileSync(lighthouseJsonPath, 'utf8'));

  const results = {
    passed: [],
    failed: [],
  };

  // Check category scores
  const categories = report.categories;
  Object.entries(categories).forEach(([key, category]) => {
    const score = category.score * 100;
    const budget = BUDGETS[key] || 0;
    const metric = {
      name: category.title,
      value: score,
      budget: budget,
      unit: '%',
    };

    if (score >= budget) {
      results.passed.push(metric);
    } else {
      results.failed.push(metric);
    }
  });

  // Check Core Web Vitals
  const audits = report.audits;

  const lcp = audits['largest-contentful-paint'].numericValue;
  if (lcp <= BUDGETS.lcp) {
    results.passed.push({ name: 'LCP', value: lcp, budget: BUDGETS.lcp, unit: 'ms' });
  } else {
    results.failed.push({ name: 'LCP', value: lcp, budget: BUDGETS.lcp, unit: 'ms' });
  }

  const inp = audits['interaction-to-next-paint']?.numericValue || 0;
  if (inp <= BUDGETS.inp) {
    results.passed.push({ name: 'INP', value: inp, budget: BUDGETS.inp, unit: 'ms' });
  } else {
    results.failed.push({ name: 'INP', value: inp, budget: BUDGETS.inp, unit: 'ms' });
  }

  const cls = audits['cumulative-layout-shift'].numericValue;
  if (cls <= BUDGETS.cls) {
    results.passed.push({ name: 'CLS', value: cls, budget: BUDGETS.cls, unit: 'score' });
  } else {
    results.failed.push({ name: 'CLS', value: cls, budget: BUDGETS.cls, unit: 'score' });
  }

  // Print results
  console.log('\n=== Performance Budget Check ===\n');

  if (results.passed.length > 0) {
    console.log('✅ Passed:');
    results.passed.forEach((metric) => {
      console.log(`  ${metric.name}: ${metric.value.toFixed(2)}${metric.unit} (budget: ${metric.budget}${metric.unit})`);
    });
  }

  if (results.failed.length > 0) {
    console.log('\n❌ Failed:');
    results.failed.forEach((metric) => {
      console.log(`  ${metric.name}: ${metric.value.toFixed(2)}${metric.unit} (budget: ${metric.budget}${metric.unit})`);
    });

    console.log('\n💡 Recommendations:');
    results.failed.forEach((metric) => {
      if (metric.name === 'Performance') {
        console.log('  - Optimize JavaScript and CSS bundle sizes');
        console.log('  - Implement code splitting and lazy loading');
        console.log('  - Optimize images (use WebP/AVIF)');
      } else if (metric.name === 'LCP') {
        console.log('  - Optimize largest image (use CDN, modern formats)');
        console.log('  - Preload critical resources');
        console.log('  - Reduce server response time');
      } else if (metric.name === 'INP') {
        console.log('  - Reduce JavaScript execution time');
        console.log('  - Defer non-critical scripts');
        console.log('  - Use web workers for heavy tasks');
      } else if (metric.name === 'CLS') {
        console.log('  - Set explicit dimensions on images');
        console.log('  - Reserve space for ads and embeds');
        console.log('  - Preload fonts');
      }
    });

    process.exit(1);
  }

  console.log('\n✅ All performance budgets passed!\n');
}

// CLI usage
const lighthouseJsonPath = process.argv[2] || './.lighthouseci/lhr.json';
checkBudget(lighthouseJsonPath);
```

---

**Use these patterns** to integrate Lighthouse into CI/CD pipelines and enforce performance standards automatically.
