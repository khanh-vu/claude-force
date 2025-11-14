"""
Template Gallery for claude-force.

Provides a browsable gallery of project templates with examples,
usage statistics, and detailed information to help users discover
the right template for their project.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class TemplateExample:
    """Example task and output for a template."""

    task: str
    description: str
    expected_output: List[str]
    estimated_time: str = "15-30 minutes"
    complexity: str = "medium"


@dataclass
class TemplateMetrics:
    """Usage metrics for a template."""

    uses_count: int = 0
    success_rate: float = 0.0
    avg_rating: float = 0.0
    total_ratings: int = 0


@dataclass
class TemplateGalleryItem:
    """Complete template gallery item with metadata and examples."""

    template_id: str
    name: str
    description: str
    category: str
    difficulty: str

    # Components
    agents: List[str]
    workflows: List[str]
    skills: List[str]

    # Metadata
    keywords: List[str]
    tech_stack: List[str]
    use_cases: List[str]

    # Gallery-specific
    examples: List[TemplateExample] = field(default_factory=list)
    metrics: Optional[TemplateMetrics] = None
    screenshot_path: Optional[str] = None
    readme_path: Optional[str] = None

    # Recommendations
    best_for: List[str] = field(default_factory=list)
    not_recommended_for: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "agents": self.agents,
            "workflows": self.workflows,
            "skills": self.skills,
            "keywords": self.keywords,
            "tech_stack": self.tech_stack,
            "use_cases": self.use_cases,
            "examples": [
                {
                    "task": ex.task,
                    "description": ex.description,
                    "expected_output": ex.expected_output,
                    "estimated_time": ex.estimated_time,
                    "complexity": ex.complexity,
                }
                for ex in self.examples
            ],
            "metrics": (
                {
                    "uses_count": self.metrics.uses_count if self.metrics else 0,
                    "success_rate": self.metrics.success_rate if self.metrics else 0.0,
                    "avg_rating": self.metrics.avg_rating if self.metrics else 0.0,
                    "total_ratings": self.metrics.total_ratings if self.metrics else 0,
                }
                if self.metrics
                else None
            ),
            "screenshot_path": self.screenshot_path,
            "readme_path": self.readme_path,
            "best_for": self.best_for,
            "not_recommended_for": self.not_recommended_for,
        }


class TemplateGallery:
    """
    Template gallery manager.

    Provides:
    - Template discovery with examples
    - Usage metrics and ratings
    - Search and filtering
    - Detailed template information
    """

    def __init__(self, gallery_dir: Optional[Path] = None):
        """
        Initialize template gallery.

        Args:
            gallery_dir: Path to gallery directory (default: .claude/gallery)
        """
        self.gallery_dir = gallery_dir or Path(".claude/gallery")
        self.gallery_file = self.gallery_dir / "gallery.json"

        # Ensure gallery directory exists
        self.gallery_dir.mkdir(parents=True, exist_ok=True)

        # Load gallery items
        self.items = self._load_gallery()

    def _load_gallery(self) -> Dict[str, TemplateGalleryItem]:
        """Load gallery items from file."""
        if not self.gallery_file.exists():
            # Create default gallery
            self._create_default_gallery()

        try:
            with open(self.gallery_file) as f:
                data = json.load(f)

            items = {}
            for item_data in data.get("templates", []):
                # Parse examples
                examples = []
                for ex_data in item_data.get("examples", []):
                    examples.append(
                        TemplateExample(
                            task=ex_data["task"],
                            description=ex_data["description"],
                            expected_output=ex_data["expected_output"],
                            estimated_time=ex_data.get("estimated_time", "15-30 minutes"),
                            complexity=ex_data.get("complexity", "medium"),
                        )
                    )

                # Parse metrics
                metrics = None
                if "metrics" in item_data and item_data["metrics"]:
                    metrics = TemplateMetrics(
                        uses_count=item_data["metrics"].get("uses_count", 0),
                        success_rate=item_data["metrics"].get("success_rate", 0.0),
                        avg_rating=item_data["metrics"].get("avg_rating", 0.0),
                        total_ratings=item_data["metrics"].get("total_ratings", 0),
                    )

                item = TemplateGalleryItem(
                    template_id=item_data["template_id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    category=item_data["category"],
                    difficulty=item_data["difficulty"],
                    agents=item_data["agents"],
                    workflows=item_data["workflows"],
                    skills=item_data["skills"],
                    keywords=item_data["keywords"],
                    tech_stack=item_data["tech_stack"],
                    use_cases=item_data["use_cases"],
                    examples=examples,
                    metrics=metrics,
                    screenshot_path=item_data.get("screenshot_path"),
                    readme_path=item_data.get("readme_path"),
                    best_for=item_data.get("best_for", []),
                    not_recommended_for=item_data.get("not_recommended_for", []),
                )

                items[item.template_id] = item

            return items

        except Exception as e:
            logger.error(f"Failed to load gallery: {e}")
            return {}

    def _create_default_gallery(self):
        """Create default gallery with examples."""
        default_gallery = {
            "templates": [
                {
                    "template_id": "fullstack-web",
                    "name": "Full-Stack Web Application",
                    "description": "Complete web application with frontend, backend, and database",
                    "category": "fullstack",
                    "difficulty": "intermediate",
                    "agents": ["frontend-architect", "backend-architect", "database-architect"],
                    "workflows": ["full-stack-feature"],
                    "skills": ["api-design", "test-generation"],
                    "keywords": ["web", "fullstack", "react", "api", "database"],
                    "tech_stack": ["React", "Node.js/Python", "PostgreSQL/MongoDB"],
                    "use_cases": [
                        "SaaS applications",
                        "E-commerce platforms",
                        "User dashboards",
                        "Admin panels",
                    ],
                    "best_for": [
                        "Teams building complete web applications",
                        "Projects requiring both frontend and backend",
                        "Applications with complex data models",
                    ],
                    "examples": [
                        {
                            "task": "Build user authentication with OAuth",
                            "description": "Implement complete authentication flow",
                            "expected_output": [
                                "Frontend: Login/signup components",
                                "Backend: Auth endpoints with JWT",
                                "Database: Users and sessions tables",
                                "Tests: 15+ unit and integration tests",
                            ],
                            "estimated_time": "45-60 minutes",
                            "complexity": "complex",
                        }
                    ],
                    "metrics": {
                        "uses_count": 127,
                        "success_rate": 0.89,
                        "avg_rating": 4.5,
                        "total_ratings": 42,
                    },
                },
                {
                    "template_id": "llm-app",
                    "name": "LLM-Powered Application",
                    "description": "RAG systems, chatbots, and semantic search with LLMs",
                    "category": "ai",
                    "difficulty": "intermediate",
                    "agents": ["prompt-engineer", "ai-engineer", "backend-architect"],
                    "workflows": ["llm-integration"],
                    "skills": ["api-design", "test-generation"],
                    "keywords": ["llm", "rag", "chatbot", "openai", "claude"],
                    "tech_stack": ["Python", "LangChain/LlamaIndex", "Vector DB"],
                    "use_cases": [
                        "Customer support chatbots",
                        "Document Q&A systems",
                        "Semantic search engines",
                        "AI assistants",
                    ],
                    "best_for": [
                        "Building chatbots and conversational AI",
                        "Document retrieval systems",
                        "Semantic search applications",
                    ],
                    "examples": [
                        {
                            "task": "Build customer support chatbot with RAG",
                            "description": "Chatbot with knowledge base retrieval",
                            "expected_output": [
                                "Vector database setup and ingestion",
                                "RAG pipeline with retrieval",
                                "Chatbot API endpoints",
                                "Prompt templates and evaluation",
                            ],
                            "estimated_time": "30-45 minutes",
                            "complexity": "complex",
                        }
                    ],
                    "metrics": {
                        "uses_count": 89,
                        "success_rate": 0.91,
                        "avg_rating": 4.7,
                        "total_ratings": 31,
                    },
                },
                {
                    "template_id": "api-service",
                    "name": "REST API Service",
                    "description": "Backend API with database and authentication",
                    "category": "backend",
                    "difficulty": "beginner",
                    "agents": ["backend-architect", "database-architect", "security-specialist"],
                    "workflows": ["backend-feature"],
                    "skills": ["api-design", "test-generation", "dockerfile"],
                    "keywords": ["api", "rest", "backend", "microservice"],
                    "tech_stack": ["FastAPI/Flask/Express", "PostgreSQL/MongoDB", "Docker"],
                    "use_cases": [
                        "RESTful APIs",
                        "Microservices",
                        "Backend for mobile apps",
                        "Third-party integrations",
                    ],
                    "best_for": [
                        "Backend-focused projects",
                        "Microservices architecture",
                        "Mobile app backends",
                    ],
                    "examples": [
                        {
                            "task": "Create user management API with CRUD operations",
                            "description": "Complete user API with validation",
                            "expected_output": [
                                "User model and database schema",
                                "CRUD endpoints (GET, POST, PUT, DELETE)",
                                "Input validation and error handling",
                                "API documentation (OpenAPI/Swagger)",
                                "Unit and integration tests",
                            ],
                            "estimated_time": "20-30 minutes",
                            "complexity": "simple",
                        }
                    ],
                    "metrics": {
                        "uses_count": 156,
                        "success_rate": 0.93,
                        "avg_rating": 4.6,
                        "total_ratings": 58,
                    },
                },
                {
                    "template_id": "ml-project",
                    "name": "Machine Learning Project",
                    "description": "ML model training, evaluation, and deployment",
                    "category": "ai",
                    "difficulty": "advanced",
                    "agents": ["ai-engineer", "data-engineer", "python-expert"],
                    "workflows": ["ai-ml-development"],
                    "skills": ["test-generation", "git-workflow"],
                    "keywords": ["ml", "ai", "pytorch", "tensorflow", "training"],
                    "tech_stack": ["Python", "PyTorch/TensorFlow", "MLflow", "Docker"],
                    "use_cases": [
                        "Classification models",
                        "Regression models",
                        "NLP models",
                        "Computer vision",
                    ],
                    "best_for": [
                        "Machine learning experimentation",
                        "Model training and evaluation",
                        "ML model deployment",
                    ],
                    "examples": [
                        {
                            "task": "Train sentiment analysis model on customer reviews",
                            "description": "End-to-end ML pipeline for text classification",
                            "expected_output": [
                                "Data preprocessing pipeline",
                                "Model training script with hyperparameters",
                                "Evaluation metrics and visualizations",
                                "Model export and deployment code",
                                "Inference API endpoint",
                            ],
                            "estimated_time": "60-90 minutes",
                            "complexity": "complex",
                        }
                    ],
                    "metrics": {
                        "uses_count": 73,
                        "success_rate": 0.85,
                        "avg_rating": 4.4,
                        "total_ratings": 28,
                    },
                },
            ]
        }

        with open(self.gallery_file, "w") as f:
            json.dump(default_gallery, f, indent=2)

    def list_templates(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        min_rating: Optional[float] = None,
    ) -> List[TemplateGalleryItem]:
        """
        List templates with filtering.

        Args:
            category: Filter by category
            difficulty: Filter by difficulty
            min_rating: Minimum average rating

        Returns:
            List of matching templates
        """
        templates = list(self.items.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if difficulty:
            templates = [t for t in templates if t.difficulty == difficulty]

        if min_rating is not None:
            templates = [t for t in templates if t.metrics and t.metrics.avg_rating >= min_rating]

        # Sort by popularity (uses_count)
        templates.sort(key=lambda t: t.metrics.uses_count if t.metrics else 0, reverse=True)

        return templates

    def get_template(self, template_id: str) -> Optional[TemplateGalleryItem]:
        """Get template by ID."""
        return self.items.get(template_id)

    def search(self, query: str) -> List[TemplateGalleryItem]:
        """
        Search templates by query.

        Searches in: name, description, keywords, use_cases, tech_stack

        Args:
            query: Search query

        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        results = []

        for template in self.items.values():
            # Build searchable text
            searchable = [
                template.name.lower(),
                template.description.lower(),
                *[k.lower() for k in template.keywords],
                *[u.lower() for u in template.use_cases],
                *[t.lower() for t in template.tech_stack],
            ]

            if any(query_lower in text for text in searchable):
                results.append(template)

        # Sort by relevance (exact matches first)
        results.sort(
            key=lambda t: (
                query_lower in t.name.lower(),
                query_lower in t.description.lower(),
                t.metrics.uses_count if t.metrics else 0,
            ),
            reverse=True,
        )

        return results

    def get_popular_templates(self, top_k: int = 5) -> List[TemplateGalleryItem]:
        """
        Get most popular templates.

        Args:
            top_k: Number of templates to return

        Returns:
            List of top templates by usage
        """
        templates = list(self.items.values())
        templates.sort(key=lambda t: t.metrics.uses_count if t.metrics else 0, reverse=True)
        return templates[:top_k]

    def get_top_rated_templates(self, top_k: int = 5) -> List[TemplateGalleryItem]:
        """
        Get highest rated templates.

        Args:
            top_k: Number of templates to return

        Returns:
            List of top templates by rating
        """
        templates = [t for t in self.items.values() if t.metrics and t.metrics.total_ratings >= 5]
        templates.sort(key=lambda t: t.metrics.avg_rating if t.metrics else 0, reverse=True)
        return templates[:top_k]


def get_template_gallery(gallery_dir: Optional[Path] = None) -> TemplateGallery:
    """
    Get singleton template gallery instance.

    Args:
        gallery_dir: Path to gallery directory

    Returns:
        TemplateGallery instance
    """
    return TemplateGallery(gallery_dir=gallery_dir)
