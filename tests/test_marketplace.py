"""
Marketplace Tests for claude-force.

Tests the plugin marketplace system including:
- Plugin listing and filtering
- Search functionality
- Installation and uninstallation
- Dependency resolution
- Error handling
- CLI integration
"""

import unittest
import tempfile
import shutil
import json
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

from claude_force.marketplace import (
    MarketplaceManager,
    Plugin,
    PluginSource,
    PluginCategory,
    InstallationResult,
    get_marketplace_manager
)


class TestPluginDataclass(unittest.TestCase):
    """Test Plugin dataclass functionality."""

    def test_plugin_creation(self):
        """Plugin should be creatable with required fields."""
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            version="1.0.0",
            source=PluginSource.BUILTIN,
            category=PluginCategory.DEVELOPMENT
        )

        self.assertEqual(plugin.id, "test-plugin")
        self.assertEqual(plugin.name, "Test Plugin")
        self.assertEqual(plugin.version, "1.0.0")
        self.assertEqual(plugin.source, PluginSource.BUILTIN)
        self.assertEqual(plugin.category, PluginCategory.DEVELOPMENT)
        self.assertFalse(plugin.installed)

    def test_plugin_to_dict(self):
        """Plugin should convert to dict correctly."""
        plugin = Plugin(
            id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            version="1.0.0",
            source=PluginSource.WSHOBSON,
            category=PluginCategory.AI_ML,
            agents=["agent1", "agent2"],
            skills=["skill1"],
            keywords=["ai", "ml"]
        )

        data = plugin.to_dict()

        self.assertEqual(data["id"], "test-plugin")
        self.assertEqual(data["source"], "wshobson")
        self.assertEqual(data["category"], "ai-ml")
        self.assertEqual(data["agents"], ["agent1", "agent2"])
        self.assertEqual(data["skills"], ["skill1"])
        self.assertEqual(data["keywords"], ["ai", "ml"])

    def test_plugin_from_dict(self):
        """Plugin should be creatable from dict."""
        data = {
            "id": "test-plugin",
            "name": "Test Plugin",
            "description": "A test plugin",
            "version": "1.0.0",
            "source": "builtin",
            "category": "development",
            "agents": ["agent1"],
            "skills": ["skill1"],
            "workflows": ["workflow1"],
            "tools": ["tool1"],
            "dependencies": ["dep1"],
            "keywords": ["test"],
            "author": "Test Author",
            "repository": "test/repo",
            "installed": True,
            "installed_version": "1.0.0"
        }

        plugin = Plugin.from_dict(data)

        self.assertEqual(plugin.id, "test-plugin")
        self.assertEqual(plugin.source, PluginSource.BUILTIN)
        self.assertEqual(plugin.category, PluginCategory.DEVELOPMENT)
        self.assertEqual(plugin.agents, ["agent1"])
        self.assertEqual(plugin.skills, ["skill1"])
        self.assertEqual(plugin.workflows, ["workflow1"])
        self.assertEqual(plugin.tools, ["tool1"])
        self.assertEqual(plugin.dependencies, ["dep1"])
        self.assertEqual(plugin.keywords, ["test"])
        self.assertEqual(plugin.author, "Test Author")
        self.assertEqual(plugin.repository, "test/repo")
        self.assertTrue(plugin.installed)
        self.assertEqual(plugin.installed_version, "1.0.0")


class TestMarketplaceManagerInit(unittest.TestCase):
    """Test MarketplaceManager initialization."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_creates_marketplace_directory(self):
        """Manager should create marketplace directory."""
        manager = MarketplaceManager(claude_dir=self.claude_dir)

        self.assertTrue(manager.marketplace_dir.exists())
        self.assertTrue(manager.marketplace_dir.is_dir())

    def test_manager_creates_default_registry(self):
        """Manager should create default registry if none exists."""
        manager = MarketplaceManager(claude_dir=self.claude_dir)

        self.assertTrue(manager.registry_file.exists())

        # Verify registry is valid YAML
        with open(manager.registry_file) as f:
            data = yaml.safe_load(f)

        self.assertIn("categories", data)
        self.assertIsInstance(data["categories"], list)
        self.assertGreater(len(data["categories"]), 0)

    def test_manager_loads_available_plugins(self):
        """Manager should load available plugins from registry."""
        manager = MarketplaceManager(claude_dir=self.claude_dir)

        plugins = manager.available_plugins

        self.assertIsInstance(plugins, dict)
        self.assertGreater(len(plugins), 0)

        # Verify at least one plugin
        first_plugin = list(plugins.values())[0]
        self.assertIsInstance(first_plugin, Plugin)

    def test_manager_handles_empty_installed_file(self):
        """Manager should handle missing installed.json gracefully."""
        manager = MarketplaceManager(claude_dir=self.claude_dir)

        # No installed.json should exist yet
        self.assertFalse(manager.installed_file.exists())

        # Should have empty installed plugins
        self.assertEqual(len(manager.installed_plugins), 0)


class TestPluginListing(unittest.TestCase):
    """Test plugin listing functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.manager = MarketplaceManager(claude_dir=self.claude_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_list_all_plugins(self):
        """Should list all available plugins."""
        plugins = self.manager.list_available()

        self.assertIsInstance(plugins, list)
        self.assertGreater(len(plugins), 0)

        # All should be Plugin instances
        for plugin in plugins:
            self.assertIsInstance(plugin, Plugin)

    def test_list_by_category(self):
        """Should filter plugins by category."""
        # List development plugins
        dev_plugins = self.manager.list_available(category="development")

        self.assertGreater(len(dev_plugins), 0)

        # All should be development category
        for plugin in dev_plugins:
            self.assertEqual(plugin.category, PluginCategory.DEVELOPMENT)

    def test_list_by_source(self):
        """Should filter plugins by source."""
        # List wshobson plugins
        wshobson_plugins = self.manager.list_available(source="wshobson")

        self.assertGreater(len(wshobson_plugins), 0)

        # All should be wshobson source
        for plugin in wshobson_plugins:
            self.assertEqual(plugin.source, PluginSource.WSHOBSON)

    def test_list_installed_only(self):
        """Should filter to show only installed plugins."""
        # Install a plugin first
        plugin_id = list(self.manager.available_plugins.keys())[0]
        self.manager.install_plugin(plugin_id)

        # List installed only
        installed = self.manager.list_available(installed_only=True)

        self.assertEqual(len(installed), 1)
        self.assertTrue(installed[0].installed)

    def test_list_with_multiple_filters(self):
        """Should handle multiple filters simultaneously."""
        plugins = self.manager.list_available(
            category="development",
            source="builtin"
        )

        # All plugins should match both filters
        for plugin in plugins:
            self.assertEqual(plugin.category, PluginCategory.DEVELOPMENT)
            self.assertEqual(plugin.source, PluginSource.BUILTIN)


class TestPluginSearch(unittest.TestCase):
    """Test plugin search functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.manager = MarketplaceManager(claude_dir=self.claude_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_by_keyword(self):
        """Should search plugins by keyword."""
        results = self.manager.search("python")

        self.assertIsInstance(results, list)
        # Should find at least one python-related plugin
        self.assertGreater(len(results), 0)

    def test_search_by_name(self):
        """Should search plugins by name."""
        # Get first plugin name
        first_plugin = list(self.manager.available_plugins.values())[0]
        name_word = first_plugin.name.split()[0].lower()

        results = self.manager.search(name_word)

        self.assertGreater(len(results), 0)

    def test_search_by_description(self):
        """Should search plugins by description."""
        results = self.manager.search("development")

        self.assertGreater(len(results), 0)

    def test_search_case_insensitive(self):
        """Search should be case insensitive."""
        lower_results = self.manager.search("python")
        upper_results = self.manager.search("PYTHON")
        mixed_results = self.manager.search("PyThOn")

        # All should return same results
        self.assertEqual(len(lower_results), len(upper_results))
        self.assertEqual(len(lower_results), len(mixed_results))

    def test_search_no_results(self):
        """Search with no matches should return empty list."""
        results = self.manager.search("nonexistent-plugin-xyz123")

        self.assertEqual(len(results), 0)

    def test_search_in_agents(self):
        """Should search in agent names."""
        # Find a plugin with agents
        plugin_with_agents = None
        for plugin in self.manager.available_plugins.values():
            if plugin.agents:
                plugin_with_agents = plugin
                break

        if plugin_with_agents:
            agent_name = plugin_with_agents.agents[0]
            results = self.manager.search(agent_name)

            self.assertGreater(len(results), 0)
            self.assertIn(plugin_with_agents, results)

    def test_search_in_skills(self):
        """Should search in skill names."""
        # Find a plugin with skills
        plugin_with_skills = None
        for plugin in self.manager.available_plugins.values():
            if plugin.skills:
                plugin_with_skills = plugin
                break

        if plugin_with_skills:
            skill_name = plugin_with_skills.skills[0]
            results = self.manager.search(skill_name)

            self.assertGreater(len(results), 0)
            self.assertIn(plugin_with_skills, results)


class TestPluginInstallation(unittest.TestCase):
    """Test plugin installation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.manager = MarketplaceManager(claude_dir=self.claude_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_install_valid_plugin(self):
        """Should install a valid plugin successfully."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        result = self.manager.install_plugin(plugin_id)

        self.assertIsInstance(result, InstallationResult)
        self.assertTrue(result.success)
        self.assertEqual(result.plugin.id, plugin_id)
        self.assertGreater(result.agents_added + result.skills_added +
                          result.workflows_added + result.tools_added, 0)

    def test_install_updates_installed_plugins(self):
        """Installation should update installed_plugins dict."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        self.manager.install_plugin(plugin_id)

        self.assertIn(plugin_id, self.manager.installed_plugins)
        self.assertTrue(self.manager.installed_plugins[plugin_id].installed)

    def test_install_creates_installed_file(self):
        """Installation should create installed.json."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        self.manager.install_plugin(plugin_id)

        self.assertTrue(self.manager.installed_file.exists())

        # Verify file is valid JSON
        with open(self.manager.installed_file) as f:
            data = json.load(f)

        self.assertIn(plugin_id, data)

    def test_install_nonexistent_plugin(self):
        """Installing nonexistent plugin should fail gracefully."""
        result = self.manager.install_plugin("nonexistent-plugin-xyz")

        self.assertFalse(result.success)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("not found", result.errors[0])

    def test_install_already_installed(self):
        """Installing already installed plugin should warn."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        # Install once
        self.manager.install_plugin(plugin_id)

        # Install again
        result = self.manager.install_plugin(plugin_id)

        self.assertFalse(result.success)
        self.assertGreater(len(result.warnings), 0)
        self.assertIn("already installed", result.warnings[0])

    def test_install_with_force_reinstalls(self):
        """Installing with force should reinstall."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        # Install once
        self.manager.install_plugin(plugin_id)

        # Install again with force
        result = self.manager.install_plugin(plugin_id, force=True)

        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)

    def test_install_marks_plugin_as_installed(self):
        """Installation should mark plugin as installed in available_plugins."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        self.manager.install_plugin(plugin_id)

        plugin = self.manager.available_plugins[plugin_id]
        self.assertTrue(plugin.installed)
        self.assertIsNotNone(plugin.installed_version)

    def test_install_with_dependencies(self):
        """Should install dependencies before main plugin."""
        # Create a test plugin with dependencies
        test_plugin_data = {
            "id": "test-with-deps",
            "name": "Test With Dependencies",
            "description": "Test plugin with dependencies",
            "version": "1.0.0",
            "source": "builtin",
            "category": "development",
            "dependencies": [list(self.manager.available_plugins.keys())[0]]
        }

        # Add to available plugins
        test_plugin = Plugin.from_dict(test_plugin_data)
        self.manager.available_plugins["test-with-deps"] = test_plugin

        # Install plugin with dependency
        result = self.manager.install_plugin("test-with-deps")

        # Both plugin and dependency should be installed
        self.assertTrue(result.success)
        self.assertIn("test-with-deps", self.manager.installed_plugins)
        self.assertIn(test_plugin_data["dependencies"][0],
                     self.manager.installed_plugins)


class TestPluginUninstallation(unittest.TestCase):
    """Test plugin uninstallation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.manager = MarketplaceManager(claude_dir=self.claude_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_uninstall_installed_plugin(self):
        """Should uninstall an installed plugin successfully."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        # Install first
        self.manager.install_plugin(plugin_id)

        # Then uninstall
        result = self.manager.uninstall_plugin(plugin_id)

        self.assertTrue(result)
        self.assertNotIn(plugin_id, self.manager.installed_plugins)

    def test_uninstall_nonexistent_plugin(self):
        """Uninstalling nonexistent plugin should return False."""
        result = self.manager.uninstall_plugin("nonexistent-plugin-xyz")

        self.assertFalse(result)

    def test_uninstall_not_installed_plugin(self):
        """Uninstalling not-installed plugin should return False."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        result = self.manager.uninstall_plugin(plugin_id)

        self.assertFalse(result)

    def test_uninstall_updates_available_plugins(self):
        """Uninstallation should update installed status in available_plugins."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        # Install and uninstall
        self.manager.install_plugin(plugin_id)
        self.manager.uninstall_plugin(plugin_id)

        plugin = self.manager.available_plugins[plugin_id]
        self.assertFalse(plugin.installed)
        self.assertIsNone(plugin.installed_version)

    def test_uninstall_updates_installed_file(self):
        """Uninstallation should update installed.json."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        # Install and uninstall
        self.manager.install_plugin(plugin_id)
        self.manager.uninstall_plugin(plugin_id)

        # Verify file updated
        with open(self.manager.installed_file) as f:
            data = json.load(f)

        self.assertNotIn(plugin_id, data)


class TestGetPlugin(unittest.TestCase):
    """Test get_plugin functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.manager = MarketplaceManager(claude_dir=self.claude_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_existing_plugin(self):
        """Should return plugin for valid ID."""
        plugin_id = list(self.manager.available_plugins.keys())[0]

        plugin = self.manager.get_plugin(plugin_id)

        self.assertIsNotNone(plugin)
        self.assertIsInstance(plugin, Plugin)
        self.assertEqual(plugin.id, plugin_id)

    def test_get_nonexistent_plugin(self):
        """Should return None for nonexistent plugin."""
        plugin = self.manager.get_plugin("nonexistent-plugin-xyz")

        self.assertIsNone(plugin)


class TestMarketplaceManagerSingleton(unittest.TestCase):
    """Test get_marketplace_manager singleton function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_marketplace_manager_creates_instance(self):
        """get_marketplace_manager should create instance."""
        manager = get_marketplace_manager(claude_dir=self.claude_dir)

        self.assertIsInstance(manager, MarketplaceManager)

    def test_get_marketplace_manager_with_custom_dir(self):
        """get_marketplace_manager should accept custom directory."""
        manager = get_marketplace_manager(claude_dir=self.claude_dir)

        self.assertEqual(manager.claude_dir, self.claude_dir)


class TestDefaultRegistry(unittest.TestCase):
    """Test default registry content."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"
        self.manager = MarketplaceManager(claude_dir=self.claude_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_default_registry_has_plugins(self):
        """Default registry should have plugins."""
        plugins = self.manager.available_plugins

        self.assertGreater(len(plugins), 0)

    def test_default_registry_has_categories(self):
        """Default registry should have multiple categories."""
        categories = set(p.category for p in self.manager.available_plugins.values())

        self.assertGreaterEqual(len(categories), 3)
        self.assertIn(PluginCategory.DEVELOPMENT, categories)

    def test_default_registry_has_sources(self):
        """Default registry should have multiple sources."""
        sources = set(p.source for p in self.manager.available_plugins.values())

        self.assertGreaterEqual(len(sources), 2)
        self.assertIn(PluginSource.BUILTIN, sources)
        self.assertIn(PluginSource.WSHOBSON, sources)

    def test_all_plugins_have_required_fields(self):
        """All plugins should have required fields."""
        for plugin in self.manager.available_plugins.values():
            self.assertIsNotNone(plugin.id)
            self.assertIsNotNone(plugin.name)
            self.assertIsNotNone(plugin.description)
            self.assertIsNotNone(plugin.version)
            self.assertIsNotNone(plugin.source)
            self.assertIsNotNone(plugin.category)

    def test_all_plugins_have_content(self):
        """All plugins should have at least one of: agents, skills, workflows, tools."""
        for plugin in self.manager.available_plugins.values():
            has_content = (
                len(plugin.agents) > 0 or
                len(plugin.skills) > 0 or
                len(plugin.workflows) > 0 or
                len(plugin.tools) > 0
            )
            self.assertTrue(
                has_content,
                f"Plugin '{plugin.id}' has no content (no agents, skills, workflows, or tools)"
            )


class TestRegistryPersistence(unittest.TestCase):
    """Test registry persistence across instances."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.claude_dir = Path(self.temp_dir) / ".claude"

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_installed_plugins_persist(self):
        """Installed plugins should persist across instances."""
        # Create first manager and install plugin
        manager1 = MarketplaceManager(claude_dir=self.claude_dir)
        plugin_id = list(manager1.available_plugins.keys())[0]
        manager1.install_plugin(plugin_id)

        # Create second manager
        manager2 = MarketplaceManager(claude_dir=self.claude_dir)

        # Plugin should still be installed
        self.assertIn(plugin_id, manager2.installed_plugins)
        plugin = manager2.available_plugins[plugin_id]
        self.assertTrue(plugin.installed)

    def test_registry_persists(self):
        """Registry should persist across instances."""
        # Create first manager
        manager1 = MarketplaceManager(claude_dir=self.claude_dir)
        original_count = len(manager1.available_plugins)

        # Create second manager
        manager2 = MarketplaceManager(claude_dir=self.claude_dir)

        # Should have same plugins
        self.assertEqual(len(manager2.available_plugins), original_count)


if __name__ == "__main__":
    unittest.main()
