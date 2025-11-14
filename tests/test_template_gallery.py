"""
Template Gallery Tests for claude-force.

Tests template browsing, searching, and discovery functionality.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

from claude_force.template_gallery import (
    TemplateGallery,
    TemplateGalleryItem,
    TemplateExample,
    TemplateMetrics,
    get_template_gallery
)


class TestTemplateExample(unittest.TestCase):
    """Test TemplateExample dataclass."""

    def test_example_creation(self):
        """TemplateExample should be creatable with required fields."""
        example = TemplateExample(
            task="Build authentication",
            description="OAuth2 authentication flow",
            expected_output=["Login component", "Auth API", "Tests"]
        )

        self.assertEqual(example.task, "Build authentication")
        self.assertEqual(example.description, "OAuth2 authentication flow")
        self.assertEqual(len(example.expected_output), 3)
        self.assertEqual(example.estimated_time, "15-30 minutes")
        self.assertEqual(example.complexity, "medium")

    def test_example_with_custom_values(self):
        """TemplateExample should handle custom estimated_time and complexity."""
        example = TemplateExample(
            task="Complex task",
            description="Description",
            expected_output=["Output"],
            estimated_time="60-90 minutes",
            complexity="complex"
        )

        self.assertEqual(example.estimated_time, "60-90 minutes")
        self.assertEqual(example.complexity, "complex")


class TestTemplateMetrics(unittest.TestCase):
    """Test TemplateMetrics dataclass."""

    def test_metrics_defaults(self):
        """TemplateMetrics should have zero defaults."""
        metrics = TemplateMetrics()

        self.assertEqual(metrics.uses_count, 0)
        self.assertEqual(metrics.success_rate, 0.0)
        self.assertEqual(metrics.avg_rating, 0.0)
        self.assertEqual(metrics.total_ratings, 0)

    def test_metrics_with_values(self):
        """TemplateMetrics should store values correctly."""
        metrics = TemplateMetrics(
            uses_count=100,
            success_rate=0.95,
            avg_rating=4.5,
            total_ratings=20
        )

        self.assertEqual(metrics.uses_count, 100)
        self.assertEqual(metrics.success_rate, 0.95)
        self.assertEqual(metrics.avg_rating, 4.5)
        self.assertEqual(metrics.total_ratings, 20)


class TestTemplateGalleryItem(unittest.TestCase):
    """Test TemplateGalleryItem dataclass."""

    def test_gallery_item_creation(self):
        """TemplateGalleryItem should be creatable with required fields."""
        item = TemplateGalleryItem(
            template_id="test-template",
            name="Test Template",
            description="A test template",
            category="test",
            difficulty="beginner",
            agents=["agent1"],
            workflows=["workflow1"],
            skills=["skill1"],
            keywords=["test"],
            tech_stack=["Python"],
            use_cases=["Testing"]
        )

        self.assertEqual(item.template_id, "test-template")
        self.assertEqual(item.name, "Test Template")
        self.assertEqual(item.difficulty, "beginner")
        self.assertEqual(len(item.agents), 1)
        self.assertEqual(len(item.examples), 0)
        self.assertIsNone(item.metrics)

    def test_gallery_item_to_dict(self):
        """TemplateGalleryItem should convert to dict correctly."""
        metrics = TemplateMetrics(uses_count=10, avg_rating=4.0)
        item = TemplateGalleryItem(
            template_id="test",
            name="Test",
            description="Test",
            category="test",
            difficulty="beginner",
            agents=[],
            workflows=[],
            skills=[],
            keywords=[],
            tech_stack=[],
            use_cases=[],
            metrics=metrics
        )

        data = item.to_dict()

        self.assertEqual(data["template_id"], "test")
        self.assertIsNotNone(data["metrics"])
        self.assertEqual(data["metrics"]["uses_count"], 10)


class TestTemplateGalleryInit(unittest.TestCase):
    """Test TemplateGallery initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery_dir = Path(self.temp_dir) / ".claude/gallery"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_gallery_creates_directory(self):
        """Gallery should create directory on init."""
        gallery = TemplateGallery(gallery_dir=self.gallery_dir)

        self.assertTrue(gallery.gallery_dir.exists())
        self.assertTrue(gallery.gallery_dir.is_dir())

    def test_gallery_creates_default_gallery(self):
        """Gallery should create default gallery.json if none exists."""
        gallery = TemplateGallery(gallery_dir=self.gallery_dir)

        self.assertTrue(gallery.gallery_file.exists())

        # Verify it's valid JSON
        with open(gallery.gallery_file) as f:
            data = json.load(f)

        self.assertIn("templates", data)
        self.assertGreater(len(data["templates"]), 0)

    def test_gallery_loads_templates(self):
        """Gallery should load templates from file."""
        gallery = TemplateGallery(gallery_dir=self.gallery_dir)

        items = gallery.items

        self.assertIsInstance(items, dict)
        self.assertGreater(len(items), 0)

        # Verify template structure
        first_item = list(items.values())[0]
        self.assertIsInstance(first_item, TemplateGalleryItem)
        self.assertIsNotNone(first_item.template_id)
        self.assertIsNotNone(first_item.name)


class TestListTemplates(unittest.TestCase):
    """Test template listing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery_dir = Path(self.temp_dir) / ".claude/gallery"
        self.gallery = TemplateGallery(gallery_dir=self.gallery_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_all_templates(self):
        """Should list all templates."""
        templates = self.gallery.list_templates()

        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)

        for template in templates:
            self.assertIsInstance(template, TemplateGalleryItem)

    def test_list_by_category(self):
        """Should filter by category."""
        # Get a category from available templates
        all_templates = self.gallery.list_templates()
        if not all_templates:
            self.skipTest("No templates available")

        category = all_templates[0].category

        filtered = self.gallery.list_templates(category=category)

        self.assertGreater(len(filtered), 0)
        for template in filtered:
            self.assertEqual(template.category, category)

    def test_list_by_difficulty(self):
        """Should filter by difficulty."""
        # Get a difficulty from available templates
        all_templates = self.gallery.list_templates()
        if not all_templates:
            self.skipTest("No templates available")

        difficulty = all_templates[0].difficulty

        filtered = self.gallery.list_templates(difficulty=difficulty)

        self.assertGreater(len(filtered), 0)
        for template in filtered:
            self.assertEqual(template.difficulty, difficulty)

    def test_list_by_min_rating(self):
        """Should filter by minimum rating."""
        filtered = self.gallery.list_templates(min_rating=4.0)

        for template in filtered:
            if template.metrics:
                self.assertGreaterEqual(template.metrics.avg_rating, 4.0)

    def test_list_sorted_by_popularity(self):
        """Templates should be sorted by popularity."""
        templates = self.gallery.list_templates()

        if len(templates) < 2:
            self.skipTest("Need at least 2 templates")

        # Verify sorting (descending by uses_count)
        for i in range(len(templates) - 1):
            uses_current = templates[i].metrics.uses_count if templates[i].metrics else 0
            uses_next = templates[i + 1].metrics.uses_count if templates[i + 1].metrics else 0
            self.assertGreaterEqual(uses_current, uses_next)


class TestGetTemplate(unittest.TestCase):
    """Test get_template functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery_dir = Path(self.temp_dir) / ".claude/gallery"
        self.gallery = TemplateGallery(gallery_dir=self.gallery_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_existing_template(self):
        """Should return template for valid ID."""
        # Get a template ID from available templates
        all_templates = self.gallery.list_templates()
        if not all_templates:
            self.skipTest("No templates available")

        template_id = all_templates[0].template_id

        template = self.gallery.get_template(template_id)

        self.assertIsNotNone(template)
        self.assertIsInstance(template, TemplateGalleryItem)
        self.assertEqual(template.template_id, template_id)

    def test_get_nonexistent_template(self):
        """Should return None for nonexistent template."""
        template = self.gallery.get_template("nonexistent-template-xyz")

        self.assertIsNone(template)


class TestSearchTemplates(unittest.TestCase):
    """Test template search functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery_dir = Path(self.temp_dir) / ".claude/gallery"
        self.gallery = TemplateGallery(gallery_dir=self.gallery_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_by_keyword(self):
        """Should search by keyword."""
        # Default gallery has templates with keywords
        results = self.gallery.search("api")

        self.assertIsInstance(results, list)
        # Should find at least one template
        self.assertGreater(len(results), 0)

    def test_search_by_name(self):
        """Should search by template name."""
        all_templates = self.gallery.list_templates()
        if not all_templates:
            self.skipTest("No templates available")

        # Search for part of a template name
        name_word = all_templates[0].name.split()[0].lower()
        results = self.gallery.search(name_word)

        self.assertGreater(len(results), 0)

    def test_search_case_insensitive(self):
        """Search should be case insensitive."""
        lower_results = self.gallery.search("api")
        upper_results = self.gallery.search("API")
        mixed_results = self.gallery.search("Api")

        # Should return same number of results
        self.assertEqual(len(lower_results), len(upper_results))
        self.assertEqual(len(lower_results), len(mixed_results))

    def test_search_no_results(self):
        """Search with no matches should return empty list."""
        results = self.gallery.search("nonexistent-xyz-123")

        self.assertEqual(len(results), 0)

    def test_search_in_use_cases(self):
        """Should search in use cases."""
        # Default gallery has use cases
        all_templates = self.gallery.list_templates()
        if not all_templates:
            self.skipTest("No templates available")

        # Find a template with use cases
        template_with_use_cases = None
        for t in all_templates:
            if t.use_cases:
                template_with_use_cases = t
                break

        if not template_with_use_cases:
            self.skipTest("No template with use cases")

        # Search for use case
        use_case_word = template_with_use_cases.use_cases[0].split()[0].lower()
        results = self.gallery.search(use_case_word)

        self.assertGreater(len(results), 0)
        self.assertIn(template_with_use_cases, results)


class TestPopularTemplates(unittest.TestCase):
    """Test popular templates functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery_dir = Path(self.temp_dir) / ".claude/gallery"
        self.gallery = TemplateGallery(gallery_dir=self.gallery_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_popular_templates(self):
        """Should return most popular templates."""
        popular = self.gallery.get_popular_templates(top_k=3)

        self.assertIsInstance(popular, list)
        self.assertLessEqual(len(popular), 3)

        # Should be sorted by uses_count
        for i in range(len(popular) - 1):
            uses_current = popular[i].metrics.uses_count if popular[i].metrics else 0
            uses_next = popular[i + 1].metrics.uses_count if popular[i + 1].metrics else 0
            self.assertGreaterEqual(uses_current, uses_next)

    def test_get_popular_templates_default_limit(self):
        """Should default to top 5."""
        popular = self.gallery.get_popular_templates()

        self.assertLessEqual(len(popular), 5)


class TestTopRatedTemplates(unittest.TestCase):
    """Test top-rated templates functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery_dir = Path(self.temp_dir) / ".claude/gallery"
        self.gallery = TemplateGallery(gallery_dir=self.gallery_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_top_rated_templates(self):
        """Should return highest rated templates."""
        top_rated = self.gallery.get_top_rated_templates(top_k=3)

        self.assertIsInstance(top_rated, list)
        self.assertLessEqual(len(top_rated), 3)

        # All should have metrics and ratings
        for template in top_rated:
            self.assertIsNotNone(template.metrics)
            self.assertGreaterEqual(template.metrics.total_ratings, 5)

        # Should be sorted by rating
        for i in range(len(top_rated) - 1):
            rating_current = top_rated[i].metrics.avg_rating if top_rated[i].metrics else 0
            rating_next = top_rated[i + 1].metrics.avg_rating if top_rated[i + 1].metrics else 0
            self.assertGreaterEqual(rating_current, rating_next)

    def test_top_rated_requires_min_ratings(self):
        """Top rated should require minimum number of ratings."""
        top_rated = self.gallery.get_top_rated_templates()

        # All should have at least 5 ratings
        for template in top_rated:
            if template.metrics:
                self.assertGreaterEqual(template.metrics.total_ratings, 5)


class TestDefaultGallery(unittest.TestCase):
    """Test default gallery content."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.gallery_dir = Path(self.temp_dir) / ".claude/gallery"
        self.gallery = TemplateGallery(gallery_dir=self.gallery_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_gallery_has_templates(self):
        """Default gallery should have templates."""
        templates = self.gallery.list_templates()

        self.assertGreater(len(templates), 0)

    def test_all_templates_have_required_fields(self):
        """All templates should have required fields."""
        for template in self.gallery.items.values():
            self.assertIsNotNone(template.template_id)
            self.assertIsNotNone(template.name)
            self.assertIsNotNone(template.description)
            self.assertIsNotNone(template.category)
            self.assertIsNotNone(template.difficulty)

    def test_all_templates_have_components(self):
        """All templates should have at least one of: agents, workflows, skills."""
        for template in self.gallery.items.values():
            has_components = (
                len(template.agents) > 0 or
                len(template.workflows) > 0 or
                len(template.skills) > 0
            )
            self.assertTrue(
                has_components,
                f"Template '{template.template_id}' has no components"
            )

    def test_templates_have_examples(self):
        """Templates should have examples."""
        templates_with_examples = [
            t for t in self.gallery.items.values()
            if len(t.examples) > 0
        ]

        # At least some templates should have examples
        self.assertGreater(len(templates_with_examples), 0)

    def test_templates_have_metrics(self):
        """Templates should have usage metrics."""
        templates_with_metrics = [
            t for t in self.gallery.items.values()
            if t.metrics is not None
        ]

        # At least some templates should have metrics
        self.assertGreater(len(templates_with_metrics), 0)


class TestGetTemplateGallery(unittest.TestCase):
    """Test get_template_gallery singleton function."""

    def test_get_template_gallery_creates_instance(self):
        """get_template_gallery should create instance."""
        gallery = get_template_gallery()

        self.assertIsInstance(gallery, TemplateGallery)

    def test_get_template_gallery_with_custom_dir(self):
        """get_template_gallery should accept custom directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            custom_dir = Path(temp_dir) / ".claude/gallery"
            gallery = get_template_gallery(gallery_dir=custom_dir)

            self.assertEqual(gallery.gallery_dir, custom_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
