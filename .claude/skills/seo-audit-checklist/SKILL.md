# SEO Audit Checklist

Comprehensive patterns and automation for conducting technical SEO audits and identifying optimization opportunities.

## Automated SEO Audit Script

```python
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
from typing import Dict, List, Set

class SEOAuditor:
    """Automated SEO audit checker"""

    def __init__(self, url: str):
        self.url = url
        self.domain = urlparse(url).netloc
        self.issues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        self.recommendations = []

    def audit(self) -> Dict:
        """Run complete SEO audit"""
        try:
            response = requests.get(self.url, timeout=10)
            self.soup = BeautifulSoup(response.text, 'html.parser')

            # Run all checks
            self.check_title_tag()
            self.check_meta_description()
            self.check_heading_hierarchy()
            self.check_images()
            self.check_canonical()
            self.check_robots_meta()
            self.check_structured_data()
            self.check_open_graph()
            self.check_mobile_viewport()
            self.check_https()

            return {
                "url": self.url,
                "issues": self.issues,
                "recommendations": self.recommendations,
                "score": self._calculate_score()
            }
        except Exception as e:
            return {"error": str(e)}

    def check_title_tag(self):
        """Validate title tag"""
        title = self.soup.find('title')

        if not title:
            self.issues["critical"].append({
                "type": "missing_title",
                "message": "Missing <title> tag",
                "fix": "Add <title> tag with 50-60 characters"
            })
        elif title:
            title_text = title.string.strip() if title.string else ""
            length = len(title_text)

            if length < 30:
                self.issues["high"].append({
                    "type": "title_too_short",
                    "message": f"Title too short ({length} chars)",
                    "current": title_text,
                    "fix": "Expand title to 50-60 characters"
                })
            elif length > 60:
                self.issues["medium"].append({
                    "type": "title_too_long",
                    "message": f"Title too long ({length} chars)",
                    "current": title_text,
                    "fix": "Reduce title to 50-60 characters"
                })

    def check_meta_description(self):
        """Validate meta description"""
        meta_desc = self.soup.find('meta', attrs={'name': 'description'})

        if not meta_desc or not meta_desc.get('content'):
            self.issues["high"].append({
                "type": "missing_meta_description",
                "message": "Missing meta description",
                "fix": "Add meta description (150-160 characters)"
            })
        else:
            content = meta_desc.get('content', '').strip()
            length = len(content)

            if length < 120:
                self.issues["medium"].append({
                    "type": "meta_desc_too_short",
                    "message": f"Meta description too short ({length} chars)",
                    "fix": "Expand to 150-160 characters"
                })
            elif length > 160:
                self.issues["medium"].append({
                    "type": "meta_desc_too_long",
                    "message": f"Meta description too long ({length} chars)",
                    "fix": "Reduce to 150-160 characters"
                })

    def check_heading_hierarchy(self):
        """Check H1-H6 hierarchy"""
        h1_tags = self.soup.find_all('h1')

        if len(h1_tags) == 0:
            self.issues["high"].append({
                "type": "missing_h1",
                "message": "No H1 tag found",
                "fix": "Add exactly one H1 tag per page"
            })
        elif len(h1_tags) > 1:
            self.issues["medium"].append({
                "type": "multiple_h1",
                "message": f"Multiple H1 tags found ({len(h1_tags)})",
                "fix": "Use only one H1 per page"
            })

        # Check for heading gaps
        heading_levels = []
        for i in range(1, 7):
            if self.soup.find(f'h{i}'):
                heading_levels.append(i)

        for i in range(len(heading_levels) - 1):
            if heading_levels[i+1] - heading_levels[i] > 1:
                self.issues["low"].append({
                    "type": "heading_hierarchy_gap",
                    "message": f"Heading hierarchy skips from H{heading_levels[i]} to H{heading_levels[i+1]}",
                    "fix": "Use sequential heading levels"
                })

    def check_images(self):
        """Check image optimization"""
        images = self.soup.find_all('img')

        for img in images:
            # Check alt text
            if not img.get('alt'):
                self.issues["high"].append({
                    "type": "missing_alt_text",
                    "message": f"Image missing alt text: {img.get('src', 'unknown')}",
                    "fix": "Add descriptive alt text to all images"
                })

            # Check for explicit dimensions
            if not img.get('width') or not img.get('height'):
                self.issues["medium"].append({
                    "type": "missing_image_dimensions",
                    "message": f"Image missing width/height: {img.get('src', 'unknown')}",
                    "fix": "Add explicit width and height to prevent CLS"
                })

            # Check for lazy loading
            if not img.get('loading'):
                self.issues["low"].append({
                    "type": "missing_lazy_loading",
                    "message": f"Image missing lazy loading: {img.get('src', 'unknown')}",
                    "fix": "Add loading='lazy' for below-fold images"
                })

    def check_canonical(self):
        """Check canonical URL"""
        canonical = self.soup.find('link', rel='canonical')

        if not canonical:
            self.issues["medium"].append({
                "type": "missing_canonical",
                "message": "Missing canonical link tag",
                "fix": "Add <link rel='canonical' href='...'>"
            })
        elif canonical:
            href = canonical.get('href', '')
            if not href.startswith('http'):
                self.issues["high"].append({
                    "type": "invalid_canonical",
                    "message": "Canonical URL is not absolute",
                    "current": href,
                    "fix": "Use absolute URL for canonical tag"
                })

    def check_robots_meta(self):
        """Check robots meta tag"""
        robots = self.soup.find('meta', attrs={'name': 'robots'})

        if robots:
            content = robots.get('content', '').lower()
            if 'noindex' in content:
                self.issues["critical"].append({
                    "type": "noindex_found",
                    "message": "Page has noindex directive",
                    "fix": "Remove noindex if page should be indexed"
                })
            if 'nofollow' in content:
                self.issues["high"].append({
                    "type": "nofollow_found",
                    "message": "Page has nofollow directive",
                    "fix": "Remove nofollow if links should be followed"
                })

    def check_structured_data(self):
        """Check for structured data"""
        json_ld = self.soup.find_all('script', type='application/ld+json')

        if not json_ld:
            self.issues["medium"].append({
                "type": "missing_structured_data",
                "message": "No structured data found",
                "fix": "Add Schema.org JSON-LD structured data"
            })
        else:
            for script in json_ld:
                try:
                    data = json.loads(script.string)
                    if '@context' not in data:
                        self.issues["high"].append({
                            "type": "invalid_structured_data",
                            "message": "Structured data missing @context",
                            "fix": "Add @context: 'https://schema.org'"
                        })
                except json.JSONDecodeError:
                    self.issues["high"].append({
                        "type": "invalid_json_ld",
                        "message": "Invalid JSON-LD syntax",
                        "fix": "Fix JSON-LD syntax errors"
                    })

    def check_open_graph(self):
        """Check Open Graph tags"""
        required_og = ['og:title', 'og:description', 'og:image', 'og:url']
        missing = []

        for prop in required_og:
            if not self.soup.find('meta', property=prop):
                missing.append(prop)

        if missing:
            self.issues["medium"].append({
                "type": "missing_open_graph",
                "message": f"Missing Open Graph tags: {', '.join(missing)}",
                "fix": "Add all required Open Graph meta tags"
            })

    def check_mobile_viewport(self):
        """Check mobile viewport meta tag"""
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})

        if not viewport:
            self.issues["critical"].append({
                "type": "missing_viewport",
                "message": "Missing viewport meta tag",
                "fix": "Add <meta name='viewport' content='width=device-width, initial-scale=1'>"
            })

    def check_https(self):
        """Check if site uses HTTPS"""
        if not self.url.startswith('https://'):
            self.issues["critical"].append({
                "type": "not_https",
                "message": "Site not using HTTPS",
                "fix": "Implement SSL certificate and redirect HTTP to HTTPS"
            })

    def _calculate_score(self) -> int:
        """Calculate SEO score (0-100)"""
        weights = {"critical": -20, "high": -10, "medium": -5, "low": -2}
        deductions = sum(
            weights[severity] * len(issues)
            for severity, issues in self.issues.items()
        )
        return max(0, 100 + deductions)


# Usage example
def run_seo_audit(url: str) -> Dict:
    """Run comprehensive SEO audit on URL"""
    auditor = SEOAuditor(url)
    results = auditor.audit()

    # Print summary
    print(f"SEO Score: {results['score']}/100")
    print(f"\nCritical Issues: {len(results['issues']['critical'])}")
    print(f"High Priority: {len(results['issues']['high'])}")
    print(f"Medium Priority: {len(results['issues']['medium'])}")
    print(f"Low Priority: {len(results['issues']['low'])}")

    return results
```

## Robots.txt Validator

```python
import requests
from urllib.parse import urljoin

def validate_robots_txt(domain: str) -> Dict:
    """Validate robots.txt file"""
    robots_url = urljoin(f"https://{domain}", '/robots.txt')
    issues = []
    recommendations = []

    try:
        response = requests.get(robots_url, timeout=5)

        if response.status_code == 404:
            issues.append({
                "severity": "medium",
                "message": "No robots.txt file found",
                "fix": "Create robots.txt file"
            })
            return {"exists": False, "issues": issues}

        content = response.text
        lines = content.split('\n')

        # Check for sitemap
        if 'sitemap:' not in content.lower():
            recommendations.append({
                "type": "add_sitemap",
                "message": "robots.txt missing Sitemap directive",
                "fix": "Add 'Sitemap: https://yourdomain.com/sitemap.xml'"
            })

        # Check for disallow all
        if 'disallow: /' in content.lower():
            for i, line in enumerate(lines):
                if 'user-agent: *' in line.lower():
                    if i + 1 < len(lines) and 'disallow: /' in lines[i + 1].lower():
                        issues.append({
                            "severity": "critical",
                            "message": "robots.txt blocks all crawlers",
                            "fix": "Remove 'Disallow: /' unless intentional"
                        })

        return {
            "exists": True,
            "content": content,
            "issues": issues,
            "recommendations": recommendations
        }

    except Exception as e:
        return {"error": str(e)}
```

## Sitemap Validator

```python
import xml.etree.ElementTree as ET
import requests

def validate_sitemap(sitemap_url: str) -> Dict:
    """Validate XML sitemap"""
    issues = []
    stats = {"urls": 0, "errors": 0}

    try:
        response = requests.get(sitemap_url, timeout=10)

        if response.status_code != 200:
            return {
                "error": f"Sitemap returned status {response.status_code}",
                "exists": False
            }

        # Parse XML
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = root.findall('.//ns:url', namespace)
        stats["urls"] = len(urls)

        for url_elem in urls:
            loc = url_elem.find('ns:loc', namespace)

            if loc is None:
                issues.append({
                    "severity": "high",
                    "message": "URL missing <loc> element"
                })
                stats["errors"] += 1
                continue

            # Check if URL is accessible
            url = loc.text

            # Validate lastmod format if present
            lastmod = url_elem.find('ns:lastmod', namespace)
            if lastmod is not None:
                try:
                    from datetime import datetime
                    datetime.fromisoformat(lastmod.text.replace('Z', '+00:00'))
                except ValueError:
                    issues.append({
                        "severity": "low",
                        "message": f"Invalid lastmod format for {url}",
                        "fix": "Use ISO 8601 format (YYYY-MM-DD)"
                    })

        # Check sitemap size
        if stats["urls"] > 50000:
            issues.append({
                "severity": "high",
                "message": f"Sitemap has {stats['urls']} URLs (max 50,000)",
                "fix": "Split into multiple sitemaps and use sitemap index"
            })

        return {
            "valid": True,
            "stats": stats,
            "issues": issues
        }

    except ET.ParseError as e:
        return {"error": f"Invalid XML: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
```

## Core Web Vitals Checker

```python
import requests
import json

def check_core_web_vitals(url: str, api_key: str) -> Dict:
    """Check Core Web Vitals using PageSpeed Insights API"""

    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "key": api_key,
        "category": ["performance", "seo"],
        "strategy": "mobile"
    }

    try:
        response = requests.get(api_url, params=params)
        data = response.json()

        # Extract Core Web Vitals
        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})

        vitals = {
            "lcp": audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000,
            "inp": audits.get("interaction-to-next-paint", {}).get("numericValue", 0),
            "cls": audits.get("cumulative-layout-shift", {}).get("numericValue", 0),
            "fcp": audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000,
            "ttfb": audits.get("server-response-time", {}).get("numericValue", 0),
        }

        # Determine pass/fail
        thresholds = {
            "lcp": {"good": 2.5, "needs_improvement": 4.0},
            "inp": {"good": 200, "needs_improvement": 500},
            "cls": {"good": 0.1, "needs_improvement": 0.25},
        }

        results = {}
        for metric, value in vitals.items():
            if metric in thresholds:
                t = thresholds[metric]
                if value <= t["good"]:
                    status = "good"
                elif value <= t["needs_improvement"]:
                    status = "needs_improvement"
                else:
                    status = "poor"

                results[metric] = {
                    "value": value,
                    "status": status
                }

        return {
            "url": url,
            "vitals": results,
            "performance_score": lighthouse.get("categories", {}).get("performance", {}).get("score", 0) * 100,
            "seo_score": lighthouse.get("categories", {}).get("seo", {}).get("score", 0) * 100
        }

    except Exception as e:
        return {"error": str(e)}
```

## Complete Audit Report Generator

```python
def generate_audit_report(url: str, api_key: str = None) -> str:
    """Generate comprehensive SEO audit report"""

    report = f"""
# SEO Audit Report
**URL**: {url}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. Technical SEO Audit
"""

    # Run basic SEO audit
    seo_results = run_seo_audit(url)
    report += f"\n**SEO Score**: {seo_results['score']}/100\n\n"

    # Critical issues
    if seo_results['issues']['critical']:
        report += "### Critical Issues\n"
        for issue in seo_results['issues']['critical']:
            report += f"- **{issue['message']}**\n"
            report += f"  - Fix: {issue['fix']}\n"

    # High priority
    if seo_results['issues']['high']:
        report += "\n### High Priority Issues\n"
        for issue in seo_results['issues']['high']:
            report += f"- {issue['message']}\n"
            report += f"  - Fix: {issue['fix']}\n"

    # Check robots.txt
    domain = urlparse(url).netloc
    robots_results = validate_robots_txt(domain)
    report += "\n## 2. Robots.txt Validation\n"
    if robots_results.get('exists'):
        report += "✅ robots.txt exists\n"
    else:
        report += "❌ robots.txt not found\n"

    # Check Core Web Vitals if API key provided
    if api_key:
        report += "\n## 3. Core Web Vitals\n"
        vitals = check_core_web_vitals(url, api_key)
        if 'vitals' in vitals:
            for metric, data in vitals['vitals'].items():
                status_emoji = "✅" if data['status'] == 'good' else "⚠️" if data['status'] == 'needs_improvement' else "❌"
                report += f"{status_emoji} **{metric.upper()}**: {data['value']:.2f} ({data['status']})\n"

    report += "\n---\n**End of Report**\n"

    return report
```

---

**Use these patterns** when conducting SEO audits and generating optimization recommendations.
