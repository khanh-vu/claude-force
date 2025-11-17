# Performance Optimization Patterns

Comprehensive patterns and techniques for optimizing Core Web Vitals (LCP, INP, CLS) and overall web performance.

## Core Web Vitals Optimizer

```python
from typing import Dict, List
import json

class CoreWebVitalsOptimizer:
    """Analyze and optimize Core Web Vitals"""

    def __init__(self):
        self.thresholds = {
            "lcp": {"good": 2.5, "needs_improvement": 4.0},
            "inp": {"good": 200, "needs_improvement": 500},
            "cls": {"good": 0.1, "needs_improvement": 0.25},
        }

    def analyze_lcp(self, lcp_value: float) -> Dict:
        """
        Analyze LCP (Largest Contentful Paint) and provide recommendations

        Good: < 2.5s | Needs Improvement: 2.5-4.0s | Poor: > 4.0s
        """
        recommendations = []

        if lcp_value > self.thresholds["lcp"]["good"]:
            recommendations.extend([
                {
                    "priority": "high",
                    "issue": "Slow LCP",
                    "recommendations": [
                        "Optimize largest image (use WebP/AVIF format)",
                        "Implement CDN for faster asset delivery",
                        "Preload critical resources with <link rel='preload'>",
                        "Remove render-blocking resources",
                        "Use server-side rendering (SSR) for above-fold content",
                        "Optimize server response time (TTFB < 600ms)",
                        "Implement lazy loading for below-fold images"
                    ]
                }
            ])

        status = self._get_status(lcp_value, "lcp")

        return {
            "metric": "LCP",
            "value": lcp_value,
            "unit": "seconds",
            "status": status,
            "recommendations": recommendations
        }

    def analyze_inp(self, inp_value: float) -> Dict:
        """
        Analyze INP (Interaction to Next Paint) and provide recommendations

        Good: < 200ms | Needs Improvement: 200-500ms | Poor: > 500ms
        """
        recommendations = []

        if inp_value > self.thresholds["inp"]["good"]:
            recommendations.extend([
                {
                    "priority": "high",
                    "issue": "Slow INP",
                    "recommendations": [
                        "Reduce JavaScript execution time",
                        "Implement code splitting to reduce bundle size",
                        "Defer non-critical JavaScript",
                        "Use web workers for heavy computations",
                        "Optimize event handlers and listeners",
                        "Debounce/throttle expensive operations",
                        "Break up long tasks (< 50ms chunks)",
                        "Optimize third-party scripts"
                    ]
                }
            ])

        status = self._get_status(inp_value, "inp")

        return {
            "metric": "INP",
            "value": inp_value,
            "unit": "milliseconds",
            "status": status,
            "recommendations": recommendations
        }

    def analyze_cls(self, cls_value: float) -> Dict:
        """
        Analyze CLS (Cumulative Layout Shift) and provide recommendations

        Good: < 0.1 | Needs Improvement: 0.1-0.25 | Poor: > 0.25
        """
        recommendations = []

        if cls_value > self.thresholds["cls"]["good"]:
            recommendations.extend([
                {
                    "priority": "high",
                    "issue": "High CLS",
                    "recommendations": [
                        "Set explicit width and height on images and videos",
                        "Reserve space for ads and embeds",
                        "Avoid inserting content above existing content",
                        "Use CSS aspect-ratio for responsive media",
                        "Preload fonts to prevent FOIT/FOUT",
                        "Use font-display: swap for web fonts",
                        "Avoid animations that trigger layout shifts"
                    ]
                }
            ])

        status = self._get_status(cls_value, "cls")

        return {
            "metric": "CLS",
            "value": cls_value,
            "unit": "score",
            "status": status,
            "recommendations": recommendations
        }

    def _get_status(self, value: float, metric: str) -> str:
        """Determine if metric passes/fails"""
        threshold = self.thresholds[metric]

        if value <= threshold["good"]:
            return "good"
        elif value <= threshold["needs_improvement"]:
            return "needs_improvement"
        else:
            return "poor"

    def generate_optimization_plan(self, vitals: Dict) -> Dict:
        """Generate complete optimization plan"""
        plan = {
            "lcp": self.analyze_lcp(vitals.get("lcp", 0)),
            "inp": self.analyze_inp(vitals.get("inp", 0)),
            "cls": self.analyze_cls(vitals.get("cls", 0))
        }

        # Overall status
        statuses = [plan["lcp"]["status"], plan["inp"]["status"], plan["cls"]["status"]]
        if all(s == "good" for s in statuses):
            plan["overall_status"] = "passing"
        elif any(s == "poor" for s in statuses):
            plan["overall_status"] = "failing"
        else:
            plan["overall_status"] = "needs_improvement"

        return plan
```

## Image Optimization Patterns

```typescript
// Next.js Image Optimization Component
import Image from 'next/image';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
  className?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className
}: OptimizedImageProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      quality={85}
      priority={priority}
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRg..."
      loading={priority ? 'eager' : 'lazy'}
      className={className}
    />
  );
}

// Next.js Image Configuration
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60 * 60 * 24 * 365, // 1 year
    domains: ['cdn.example.com', 'images.example.com'],
  },
};
```

```html
<!-- Responsive Images with srcset -->
<picture>
  <source
    type="image/avif"
    srcset="
      /images/hero-400.avif 400w,
      /images/hero-800.avif 800w,
      /images/hero-1200.avif 1200w
    "
    sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  />
  <source
    type="image/webp"
    srcset="
      /images/hero-400.webp 400w,
      /images/hero-800.webp 800w,
      /images/hero-1200.webp 1200w
    "
    sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  />
  <img
    src="/images/hero-800.jpg"
    alt="Hero image"
    width="1200"
    height="675"
    loading="lazy"
    decoding="async"
  />
</picture>
```

## Code Splitting Patterns

```typescript
// React Route-based Code Splitting
import { lazy, Suspense } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';

// Lazy load route components
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Products = lazy(() => import('./pages/Products'));
const Contact = lazy(() => import('./pages/Contact'));

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/products" element={<Products />} />
          <Route path="/contact" element={<Contact />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

// Component-level Code Splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<div>Loading chart...</div>}>
        <HeavyChart data={data} />
      </Suspense>
    </div>
  );
}
```

```javascript
// Webpack Code Splitting with Magic Comments
// Dynamic import with prefetch
import(/* webpackPrefetch: true */ './analytics');

// Dynamic import with preload
import(/* webpackPreload: true */ './critical-module');

// Named chunks
import(/* webpackChunkName: "admin" */ './admin/Dashboard');

// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
      },
    },
  },
};
```

## Critical CSS Extraction

```javascript
// Critical CSS with Critters (Next.js)
// next.config.js
module.exports = {
  experimental: {
    optimizeCss: true,
  },
};

// Manual Critical CSS Inline
// pages/_document.tsx
import Document, { Html, Head, Main, NextScript } from 'next/document';

class MyDocument extends Document {
  render() {
    return (
      <Html>
        <Head>
          {/* Inline critical CSS */}
          <style
            dangerouslySetInnerHTML={{
              __html: `
                body { margin: 0; font-family: system-ui; }
                .hero { min-height: 100vh; }
                .header { position: fixed; top: 0; }
              `,
            }}
          />
          {/* Preload non-critical CSS */}
          <link
            rel="preload"
            href="/styles/main.css"
            as="style"
            onLoad="this.onload=null;this.rel='stylesheet'"
          />
          <noscript>
            <link rel="stylesheet" href="/styles/main.css" />
          </noscript>
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default MyDocument;
```

## Resource Hints

```html
<!-- DNS Prefetch (early DNS resolution) -->
<link rel="dns-prefetch" href="https://fonts.googleapis.com" />
<link rel="dns-prefetch" href="https://cdn.example.com" />

<!-- Preconnect (DNS + TCP + TLS) -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />

<!-- Prefetch (load resource for next navigation) -->
<link rel="prefetch" href="/next-page.html" />
<link rel="prefetch" href="/assets/icon.svg" />

<!-- Preload (high-priority fetch for current navigation) -->
<link rel="preload" href="/critical.css" as="style" />
<link rel="preload" href="/hero.webp" as="image" />
<link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/app.js" as="script" />

<!-- Modulepreload (preload ES modules) -->
<link rel="modulepreload" href="/module.js" />
```

## Font Loading Optimization

```css
/* Font Display Strategy */
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom-font.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* Prevent FOIT, use system font until custom loads */
}

/* Subset Fonts (load only needed characters) */
@font-face {
  font-family: 'CustomFont';
  src: url('/fonts/custom-font-latin.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC;
}
```

```html
<!-- Preload Fonts -->
<link
  rel="preload"
  href="/fonts/custom-font.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>

<!-- Google Fonts Optimization -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
  rel="stylesheet"
/>
```

## Lazy Loading Patterns

```typescript
// Intersection Observer Lazy Loading
class LazyLoader {
  private observer: IntersectionObserver;

  constructor() {
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            this.loadElement(entry.target as HTMLElement);
            this.observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px', // Start loading 50px before element enters viewport
        threshold: 0.01,
      }
    );
  }

  observe(elements: NodeListOf<Element>) {
    elements.forEach((el) => this.observer.observe(el));
  }

  private loadElement(element: HTMLElement) {
    if (element.tagName === 'IMG') {
      const img = element as HTMLImageElement;
      const dataSrc = img.dataset.src;
      if (dataSrc) {
        img.src = dataSrc;
        img.removeAttribute('data-src');
      }
    } else if (element.tagName === 'IFRAME') {
      const iframe = element as HTMLIFrameElement;
      const dataSrc = iframe.dataset.src;
      if (dataSrc) {
        iframe.src = dataSrc;
        iframe.removeAttribute('data-src');
      }
    }
  }
}

// Initialize lazy loading
const lazyLoader = new LazyLoader();
const lazyElements = document.querySelectorAll('[data-src]');
lazyLoader.observe(lazyElements);
```

```html
<!-- Native Lazy Loading (simpler but less control) -->
<img src="image.jpg" alt="Description" loading="lazy" width="800" height="600" />

<iframe src="video.html" loading="lazy" width="560" height="315"></iframe>
```

## Service Worker Caching

```javascript
// service-worker.js - Stale-While-Revalidate Strategy
const CACHE_NAME = 'v1';
const CACHE_ASSETS = [
  '/',
  '/styles/main.css',
  '/scripts/app.js',
  '/images/logo.svg',
];

// Install event - cache critical assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CACHE_ASSETS);
    })
  );
});

// Fetch event - serve from cache, update in background
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        // Return cached version and fetch update in background
        const fetchPromise = fetch(event.request).then((networkResponse) => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        });

        return cachedResponse || fetchPromise;
      });
    })
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
});
```

## Performance Budget

```json
{
  "budgets": [
    {
      "resourceSizes": [
        {
          "resourceType": "script",
          "budget": 300
        },
        {
          "resourceType": "stylesheet",
          "budget": 100
        },
        {
          "resourceType": "image",
          "budget": 500
        },
        {
          "resourceType": "font",
          "budget": 150
        },
        {
          "resourceType": "total",
          "budget": 1000
        }
      ]
    },
    {
      "timings": [
        {
          "metric": "lcp",
          "budget": 2500
        },
        {
          "metric": "inp",
          "budget": 200
        },
        {
          "metric": "cls",
          "budget": 0.1
        }
      ]
    }
  ]
}
```

## Web Vitals Monitoring

```typescript
// Real User Monitoring (RUM) for Core Web Vitals
import { onLCP, onINP, onCLS, onFCP, onTTFB } from 'web-vitals';

function sendToAnalytics(metric: any) {
  const body = JSON.stringify(metric);

  // Use `navigator.sendBeacon()` if available, falling back to `fetch()`
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/analytics', body);
  } else {
    fetch('/analytics', { body, method: 'POST', keepalive: true });
  }
}

// Monitor Core Web Vitals
onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
onFCP(sendToAnalytics);
onTTFB(sendToAnalytics);

// Custom metric thresholds
function reportWebVitals() {
  onLCP((metric) => {
    if (metric.value > 2500) {
      console.warn('LCP is slow:', metric.value);
    }
    sendToAnalytics(metric);
  });

  onINP((metric) => {
    if (metric.value > 200) {
      console.warn('INP is slow:', metric.value);
    }
    sendToAnalytics(metric);
  });

  onCLS((metric) => {
    if (metric.value > 0.1) {
      console.warn('CLS is high:', metric.value);
    }
    sendToAnalytics(metric);
  });
}

reportWebVitals();
```

---

**Use these patterns** to optimize Core Web Vitals and achieve excellent web performance scores.
