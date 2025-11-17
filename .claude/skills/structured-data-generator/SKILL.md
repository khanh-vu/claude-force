# Structured Data Generator

Comprehensive Schema.org JSON-LD patterns for generating structured data that enhances search engine visibility and rich results.

## Base Schema Generator

```python
from typing import Dict, Optional, List
from datetime import datetime
import json

class StructuredDataGenerator:
    """Generate Schema.org JSON-LD structured data"""

    @staticmethod
    def to_json_ld(data: Dict) -> str:
        """Convert dict to JSON-LD string"""
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        return url.startswith(('http://', 'https://'))


class ArticleSchema(StructuredDataGenerator):
    """Generate Article structured data"""

    @staticmethod
    def generate(
        headline: str,
        description: str,
        image_url: str,
        author_name: str,
        date_published: str,
        date_modified: Optional[str] = None,
        publisher_name: str = "Your Site",
        publisher_logo: str = None,
        article_type: str = "Article"
    ) -> Dict:
        """
        Generate Article schema

        Args:
            headline: Article title (max 110 characters)
            description: Brief description
            image_url: Featured image URL (min 1200px wide)
            author_name: Author's name
            date_published: ISO 8601 date (YYYY-MM-DD)
            date_modified: Last modified date
            publisher_name: Publisher organization name
            publisher_logo: Publisher logo URL (600x60px recommended)
            article_type: Article, BlogPosting, or NewsArticle
        """
        schema = {
            "@context": "https://schema.org",
            "@type": article_type,
            "headline": headline[:110],  # Max 110 chars
            "description": description,
            "image": [image_url],
            "datePublished": date_published,
            "dateModified": date_modified or date_published,
            "author": {
                "@type": "Person",
                "name": author_name
            },
            "publisher": {
                "@type": "Organization",
                "name": publisher_name
            }
        }

        if publisher_logo:
            schema["publisher"]["logo"] = {
                "@type": "ImageObject",
                "url": publisher_logo
            }

        return schema


class ProductSchema(StructuredDataGenerator):
    """Generate Product structured data"""

    @staticmethod
    def generate(
        name: str,
        description: str,
        image_url: str,
        brand: str,
        sku: str,
        price: float,
        currency: str = "USD",
        availability: str = "InStock",
        condition: str = "NewCondition",
        rating_value: Optional[float] = None,
        review_count: Optional[int] = None,
        url: Optional[str] = None
    ) -> Dict:
        """
        Generate Product schema with pricing and ratings

        Args:
            name: Product name
            description: Product description
            image_url: Product image URL
            brand: Brand name
            sku: Stock keeping unit
            price: Product price
            currency: ISO 4217 currency code
            availability: InStock, OutOfStock, PreOrder, etc.
            condition: NewCondition, UsedCondition, RefurbishedCondition
            rating_value: Rating score (1.0-5.0)
            review_count: Number of reviews
            url: Product page URL
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "description": description,
            "image": image_url,
            "brand": {
                "@type": "Brand",
                "name": brand
            },
            "sku": sku,
            "offers": {
                "@type": "Offer",
                "price": price,
                "priceCurrency": currency,
                "availability": f"https://schema.org/{availability}",
                "itemCondition": f"https://schema.org/{condition}"
            }
        }

        if url:
            schema["offers"]["url"] = url

        # Add aggregate rating if provided
        if rating_value and review_count:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": rating_value,
                "reviewCount": review_count
            }

        return schema


class LocalBusinessSchema(StructuredDataGenerator):
    """Generate LocalBusiness structured data"""

    @staticmethod
    def generate(
        name: str,
        business_type: str,
        street_address: str,
        city: str,
        state: str,
        postal_code: str,
        country: str,
        phone: str,
        url: str,
        image_url: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        opening_hours: Optional[List[str]] = None,
        price_range: Optional[str] = None,
        rating_value: Optional[float] = None,
        review_count: Optional[int] = None
    ) -> Dict:
        """
        Generate LocalBusiness schema

        Args:
            name: Business name
            business_type: Restaurant, Store, MedicalClinic, etc.
            street_address: Street address
            city: City name
            state: State/province
            postal_code: ZIP/postal code
            country: Country code (e.g., US, UK)
            phone: Phone number in international format
            url: Business website URL
            image_url: Business photo URL
            latitude: GPS latitude
            longitude: GPS longitude
            opening_hours: List of opening hours (e.g., ["Mo-Fr 09:00-17:00"])
            price_range: Price range (e.g., "$", "$$", "$$$")
            rating_value: Average rating (1.0-5.0)
            review_count: Number of reviews
        """
        schema = {
            "@context": "https://schema.org",
            "@type": business_type,
            "name": name,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": street_address,
                "addressLocality": city,
                "addressRegion": state,
                "postalCode": postal_code,
                "addressCountry": country
            },
            "telephone": phone,
            "url": url
        }

        if image_url:
            schema["image"] = image_url

        # Add geo coordinates
        if latitude and longitude:
            schema["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": latitude,
                "longitude": longitude
            }

        # Add opening hours
        if opening_hours:
            schema["openingHours"] = opening_hours

        # Add price range
        if price_range:
            schema["priceRange"] = price_range

        # Add aggregate rating
        if rating_value and review_count:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": rating_value,
                "reviewCount": review_count
            }

        return schema


class FAQSchema(StructuredDataGenerator):
    """Generate FAQPage structured data"""

    @staticmethod
    def generate(questions: List[Dict[str, str]]) -> Dict:
        """
        Generate FAQ schema

        Args:
            questions: List of dicts with 'question' and 'answer' keys

        Example:
            questions = [
                {
                    "question": "What are your hours?",
                    "answer": "We're open 9am-5pm Monday-Friday."
                }
            ]
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        }

        for qa in questions:
            schema["mainEntity"].append({
                "@type": "Question",
                "name": qa["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": qa["answer"]
                }
            })

        return schema


class BreadcrumbSchema(StructuredDataGenerator):
    """Generate BreadcrumbList structured data"""

    @staticmethod
    def generate(breadcrumbs: List[Dict[str, str]]) -> Dict:
        """
        Generate Breadcrumb schema

        Args:
            breadcrumbs: List of dicts with 'name' and 'url' keys

        Example:
            breadcrumbs = [
                {"name": "Home", "url": "https://example.com"},
                {"name": "Products", "url": "https://example.com/products"},
                {"name": "Shoes", "url": "https://example.com/products/shoes"}
            ]
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": []
        }

        for position, crumb in enumerate(breadcrumbs, start=1):
            schema["itemListElement"].append({
                "@type": "ListItem",
                "position": position,
                "name": crumb["name"],
                "item": crumb["url"]
            })

        return schema


class OrganizationSchema(StructuredDataGenerator):
    """Generate Organization structured data"""

    @staticmethod
    def generate(
        name: str,
        url: str,
        logo: str,
        description: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[Dict] = None,
        social_profiles: Optional[List[str]] = None,
        founding_date: Optional[str] = None
    ) -> Dict:
        """
        Generate Organization schema

        Args:
            name: Organization name
            url: Official website URL
            logo: Logo image URL (square, min 112x112px)
            description: Brief description
            email: Contact email
            phone: Contact phone
            address: Dict with street, city, state, postal_code, country
            social_profiles: List of social media profile URLs
            founding_date: ISO 8601 date (YYYY-MM-DD)
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": name,
            "url": url,
            "logo": logo
        }

        if description:
            schema["description"] = description

        if email:
            schema["email"] = email

        if phone:
            schema["telephone"] = phone

        if address:
            schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": address.get("street", ""),
                "addressLocality": address.get("city", ""),
                "addressRegion": address.get("state", ""),
                "postalCode": address.get("postal_code", ""),
                "addressCountry": address.get("country", "")
            }

        if social_profiles:
            schema["sameAs"] = social_profiles

        if founding_date:
            schema["foundingDate"] = founding_date

        return schema


class VideoSchema(StructuredDataGenerator):
    """Generate VideoObject structured data"""

    @staticmethod
    def generate(
        name: str,
        description: str,
        thumbnail_url: str,
        upload_date: str,
        duration: str,
        content_url: Optional[str] = None,
        embed_url: Optional[str] = None,
        view_count: Optional[int] = None
    ) -> Dict:
        """
        Generate VideoObject schema

        Args:
            name: Video title
            description: Video description
            thumbnail_url: Thumbnail image URL
            upload_date: ISO 8601 date (YYYY-MM-DD)
            duration: ISO 8601 duration (e.g., "PT1M30S" for 1:30)
            content_url: Direct video file URL
            embed_url: Embeddable player URL
            view_count: Number of views
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": name,
            "description": description,
            "thumbnailUrl": thumbnail_url,
            "uploadDate": upload_date,
            "duration": duration
        }

        if content_url:
            schema["contentUrl"] = content_url

        if embed_url:
            schema["embedUrl"] = embed_url

        if view_count:
            schema["interactionStatistic"] = {
                "@type": "InteractionCounter",
                "interactionType": "https://schema.org/WatchAction",
                "userInteractionCount": view_count
            }

        return schema


class EventSchema(StructuredDataGenerator):
    """Generate Event structured data"""

    @staticmethod
    def generate(
        name: str,
        start_date: str,
        end_date: str,
        location_name: str,
        street_address: str,
        city: str,
        state: str,
        postal_code: str,
        country: str,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        url: Optional[str] = None,
        organizer_name: Optional[str] = None,
        organizer_url: Optional[str] = None,
        price: Optional[float] = None,
        currency: Optional[str] = "USD",
        availability: Optional[str] = "InStock"
    ) -> Dict:
        """
        Generate Event schema

        Args:
            name: Event name
            start_date: ISO 8601 datetime (YYYY-MM-DDTHH:MM:SS)
            end_date: ISO 8601 datetime
            location_name: Venue name
            street_address: Venue street address
            city: City name
            state: State/province
            postal_code: ZIP/postal code
            country: Country code
            description: Event description
            image_url: Event image URL
            url: Event page URL
            organizer_name: Organizer name
            organizer_url: Organizer website
            price: Ticket price
            currency: Price currency code
            availability: InStock, SoldOut, PreSale
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "Event",
            "name": name,
            "startDate": start_date,
            "endDate": end_date,
            "location": {
                "@type": "Place",
                "name": location_name,
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": street_address,
                    "addressLocality": city,
                    "addressRegion": state,
                    "postalCode": postal_code,
                    "addressCountry": country
                }
            }
        }

        if description:
            schema["description"] = description

        if image_url:
            schema["image"] = image_url

        if url:
            schema["url"] = url

        if organizer_name:
            schema["organizer"] = {
                "@type": "Organization",
                "name": organizer_name
            }
            if organizer_url:
                schema["organizer"]["url"] = organizer_url

        if price is not None:
            schema["offers"] = {
                "@type": "Offer",
                "price": price,
                "priceCurrency": currency,
                "availability": f"https://schema.org/{availability}",
                "url": url
            }

        return schema


# Usage Examples

def generate_blog_post_schema(post_data: Dict) -> str:
    """Generate schema for blog post"""
    schema = ArticleSchema.generate(
        headline=post_data["title"],
        description=post_data["excerpt"],
        image_url=post_data["featured_image"],
        author_name=post_data["author"],
        date_published=post_data["published_at"],
        date_modified=post_data.get("updated_at"),
        publisher_name="Your Blog",
        publisher_logo="https://yourblog.com/logo.png",
        article_type="BlogPosting"
    )
    return ArticleSchema.to_json_ld(schema)


def generate_ecommerce_product_schema(product: Dict) -> str:
    """Generate schema for e-commerce product"""
    schema = ProductSchema.generate(
        name=product["name"],
        description=product["description"],
        image_url=product["image"],
        brand=product["brand"],
        sku=product["sku"],
        price=product["price"],
        currency=product.get("currency", "USD"),
        availability=product.get("availability", "InStock"),
        rating_value=product.get("rating"),
        review_count=product.get("review_count"),
        url=product["url"]
    )
    return ProductSchema.to_json_ld(schema)


def generate_restaurant_schema(restaurant: Dict) -> str:
    """Generate schema for restaurant"""
    schema = LocalBusinessSchema.generate(
        name=restaurant["name"],
        business_type="Restaurant",
        street_address=restaurant["address"]["street"],
        city=restaurant["address"]["city"],
        state=restaurant["address"]["state"],
        postal_code=restaurant["address"]["zip"],
        country=restaurant["address"]["country"],
        phone=restaurant["phone"],
        url=restaurant["website"],
        image_url=restaurant.get("photo"),
        latitude=restaurant.get("latitude"),
        longitude=restaurant.get("longitude"),
        opening_hours=restaurant.get("hours"),
        price_range=restaurant.get("price_range"),
        rating_value=restaurant.get("rating"),
        review_count=restaurant.get("review_count")
    )
    return LocalBusinessSchema.to_json_ld(schema)
```

## Schema Validator

```python
import requests
import json

def validate_structured_data(html_content: str) -> Dict:
    """Validate structured data against Schema.org"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')
    json_ld_scripts = soup.find_all('script', type='application/ld+json')

    results = []

    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)

            # Basic validation
            validation = {
                "valid": True,
                "errors": [],
                "warnings": []
            }

            # Check for @context
            if "@context" not in data:
                validation["errors"].append("Missing @context")
                validation["valid"] = False

            # Check for @type
            if "@type" not in data:
                validation["errors"].append("Missing @type")
                validation["valid"] = False

            # Type-specific validation
            schema_type = data.get("@type")

            if schema_type == "Article":
                required = ["headline", "image", "datePublished", "author"]
                for field in required:
                    if field not in data:
                        validation["errors"].append(f"Missing required field: {field}")
                        validation["valid"] = False

            elif schema_type == "Product":
                required = ["name", "image", "description"]
                for field in required:
                    if field not in data:
                        validation["errors"].append(f"Missing required field: {field}")
                        validation["valid"] = False

                # Check offers
                if "offers" not in data:
                    validation["errors"].append("Product missing offers")
                    validation["valid"] = False

            results.append({
                "type": schema_type,
                "validation": validation,
                "data": data
            })

        except json.JSONDecodeError as e:
            results.append({
                "valid": False,
                "error": f"Invalid JSON: {str(e)}"
            })

    return {"schemas": results}
```

---

**Use these patterns** when generating Schema.org structured data for enhanced search results and SEO.
