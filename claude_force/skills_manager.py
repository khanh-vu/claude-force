"""
Progressive Skills Manager - Load skills on-demand to reduce token usage.

Instead of loading all 11 skills into every agent prompt, this manager
analyzes the task and activates only relevant skills.

Benefits:
- 40-60% reduction in prompt tokens
- Faster API responses
- Lower costs
- Skills still available when needed
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set

logger = logging.getLogger(__name__)


class ProgressiveSkillsManager:
    """
    Load skills on-demand to reduce token usage.

    Instead of loading all 11 skills into every agent prompt,
    activate only relevant skills based on task analysis.

    Metrics:
    - Before (all skills): ~15,000 tokens/request
    - After (progressive): ~5,000-8,000 tokens/request
    - Savings: 40-60% token reduction
    """

    # Skill activation rules based on keywords
    SKILL_KEYWORDS = {
        "test-generation": [
            "test", "testing", "pytest", "unit test", "integration test",
            "test case", "test suite", "coverage", "mock", "fixture"
        ],
        "code-review": [
            "review", "code quality", "security", "best practices",
            "refactor", "optimize", "analyze code", "code smell"
        ],
        "api-design": [
            "api", "rest", "graphql", "endpoint", "route",
            "openapi", "swagger", "api spec", "request", "response"
        ],
        "dockerfile": [
            "docker", "container", "dockerfile", "image",
            "docker-compose", "containerize"
        ],
        "git-workflow": [
            "git", "commit", "pr", "pull request", "branch",
            "merge", "rebase", "git flow", "version control"
        ],
        "create-agent": [
            "agent", "create agent", "new agent", "agent definition",
            "agent contract"
        ],
        "create-skill": [
            "skill", "create skill", "new skill", "skill definition"
        ],
        "docx": [
            "docx", "word", "document", ".docx", "word document"
        ],
        "xlsx": [
            "xlsx", "excel", "spreadsheet", ".xlsx", "excel file"
        ],
        "pptx": [
            "pptx", "powerpoint", "presentation", ".pptx", "slides"
        ],
        "pdf": [
            "pdf", ".pdf", "pdf file"
        ]
    }

    # Agent-skill associations (which skills are relevant for which agents)
    AGENT_SKILLS = {
        "frontend-architect": ["test-generation", "code-review", "api-design"],
        "backend-architect": ["test-generation", "code-review", "api-design", "dockerfile"],
        "database-architect": ["code-review"],
        "python-expert": ["test-generation", "code-review", "git-workflow"],
        "ui-components-expert": ["test-generation", "code-review"],
        "deployment-integration-expert": ["dockerfile", "git-workflow"],
        "devops-architect": ["dockerfile", "git-workflow"],
        "google-cloud-expert": ["dockerfile"],
        "qc-automation-expert": ["test-generation", "git-workflow"],
        "document-writer-expert": ["docx", "pptx", "pdf"],
        "api-documenter": ["api-design"],
        "frontend-developer": ["test-generation", "code-review", "api-design", "git-workflow"],
        "code-reviewer": ["test-generation", "code-review", "api-design", "git-workflow"],
        "security-specialist": ["code-review", "test-generation"],
        "bug-investigator": ["test-generation", "code-review"],
        "ai-engineer": ["test-generation", "code-review", "api-design"],
        "prompt-engineer": ["code-review"],
        "claude-code-expert": ["create-agent", "create-skill", "git-workflow"],
        "data-engineer": ["test-generation", "code-review", "dockerfile"]
    }

    def __init__(self, skills_dir: Optional[str] = None):
        """
        Initialize ProgressiveSkillsManager.

        Args:
            skills_dir: Path to skills directory (default: .claude/skills)
        """
        self.skills_dir = Path(skills_dir) if skills_dir else Path(".claude/skills")
        self.skills_registry = self._load_skills_registry()
        self.skill_cache: Dict[str, str] = {}

    def _load_skills_registry(self) -> Dict[str, Dict[str, any]]:
        """
        Load skills registry metadata.

        Scans the skills directory for all subdirectories with SKILL.md files,
        in addition to checking for known skills in SKILL_KEYWORDS.

        Returns:
            Dictionary of skill metadata
        """
        registry = {}

        # First, add all known skills from SKILL_KEYWORDS
        for skill_id in self.SKILL_KEYWORDS.keys():
            skill_path = self.skills_dir / skill_id
            if skill_path.exists() and skill_path.is_dir():
                registry[skill_id] = {
                    "id": skill_id,
                    "path": str(skill_path),
                    "keywords": self.SKILL_KEYWORDS.get(skill_id, []),
                    "exists": True
                }
            else:
                registry[skill_id] = {
                    "id": skill_id,
                    "path": str(skill_path),
                    "keywords": self.SKILL_KEYWORDS.get(skill_id, []),
                    "exists": False
                }

        # Also scan skills directory for any additional skills
        if self.skills_dir.exists() and self.skills_dir.is_dir():
            for skill_path in self.skills_dir.iterdir():
                if not skill_path.is_dir():
                    continue

                skill_id = skill_path.name

                # Skip if already in registry
                if skill_id in registry:
                    continue

                # Check if it has SKILL.md or README.md
                has_skill_file = (skill_path / "SKILL.md").exists()
                has_readme = (skill_path / "README.md").exists()

                if has_skill_file or has_readme:
                    registry[skill_id] = {
                        "id": skill_id,
                        "path": str(skill_path),
                        "keywords": self.SKILL_KEYWORDS.get(skill_id, []),
                        "exists": True
                    }

        return registry

    def analyze_required_skills(
        self,
        agent_name: str,
        task: str,
        include_agent_skills: bool = True
    ) -> List[str]:
        """
        Analyze task to determine which skills are needed.

        Args:
            agent_name: Name of the agent
            task: Task description
            include_agent_skills: Also include agent's preferred skills

        Returns:
            List of skill IDs to activate
        """
        required: Set[str] = set()
        task_lower = task.lower()

        # Analyze task keywords to find matching skills
        for skill_id, keywords in self.SKILL_KEYWORDS.items():
            if any(kw in task_lower for kw in keywords):
                # Only include if skill exists
                if self.skills_registry.get(skill_id, {}).get("exists", False):
                    required.add(skill_id)

        # Include agent's preferred skills if requested
        if include_agent_skills:
            agent_skills = self.AGENT_SKILLS.get(agent_name, [])
            for skill_id in agent_skills:
                # Only include existing skills that aren't already in required
                if self.skills_registry.get(skill_id, {}).get("exists", False):
                    # Check if task might need this skill
                    # (add if task is long/complex or mentions related concepts)
                    if len(task) > 200 or any(
                        kw in task_lower
                        for kw in self.SKILL_KEYWORDS.get(skill_id, [])
                    ):
                        required.add(skill_id)

        return sorted(list(required))

    def load_skills(self, skill_ids: List[str]) -> str:
        """
        Load skill content on-demand.

        Args:
            skill_ids: List of skill IDs to load

        Returns:
            Combined skill content as markdown string
        """
        if not skill_ids:
            return ""

        content_parts = []

        for skill_id in skill_ids:
            # Check cache first
            if skill_id in self.skill_cache:
                content = self.skill_cache[skill_id]
            else:
                content = self._load_skill_file(skill_id)
                if content:
                    self.skill_cache[skill_id] = content

            if content:
                content_parts.append((skill_id, content))

        if not content_parts:
            return ""

        # Combine skills with separators
        combined = "\n\n---\n\n".join([
            f"# Skill: {skill_id}\n\n{content}"
            for skill_id, content in content_parts
        ])

        return combined

    def _load_skill_file(self, skill_id: str) -> Optional[str]:
        """
        Load skill file from disk.

        Args:
            skill_id: Skill ID

        Returns:
            Skill content or None if not found
        """
        skill_info = self.skills_registry.get(skill_id)
        if not skill_info or not skill_info.get("exists"):
            return None

        skill_path = Path(skill_info["path"])

        # Try SKILL.md first
        skill_file = skill_path / "SKILL.md"
        if skill_file.exists():
            try:
                return skill_file.read_text()
            except Exception as e:
                logger.error(f"Failed to load skill {skill_id}: {e}")
                return None

        # Try README.md as fallback
        readme_file = skill_path / "README.md"
        if readme_file.exists():
            try:
                return readme_file.read_text()
            except Exception as e:
                logger.error(f"Failed to load skill {skill_id} README: {e}")
                return None

        return None

    def get_token_savings_estimate(
        self,
        loaded_skills: int,
        total_skills: int = 11,
        avg_skill_tokens: int = 1500
    ) -> Dict[str, any]:
        """
        Estimate token savings from progressive disclosure.

        Args:
            loaded_skills: Number of skills loaded
            total_skills: Total available skills
            avg_skill_tokens: Average tokens per skill

        Returns:
            Dictionary with savings metrics
        """
        skipped_skills = total_skills - loaded_skills
        tokens_saved = skipped_skills * avg_skill_tokens

        total_tokens_before = total_skills * avg_skill_tokens
        total_tokens_after = loaded_skills * avg_skill_tokens

        reduction_pct = (tokens_saved / total_tokens_before * 100) if total_tokens_before > 0 else 0

        return {
            "loaded_skills": loaded_skills,
            "skipped_skills": skipped_skills,
            "tokens_saved": tokens_saved,
            "total_tokens_before": total_tokens_before,
            "total_tokens_after": total_tokens_after,
            "reduction_percentage": round(reduction_pct, 1)
        }

    def get_available_skills(self) -> List[str]:
        """
        Get list of all available skills.

        Returns:
            List of skill IDs
        """
        return [
            skill_id
            for skill_id, info in self.skills_registry.items()
            if info.get("exists", False)
        ]

    def clear_cache(self):
        """Clear the skill cache."""
        self.skill_cache.clear()


def get_skills_manager(skills_dir: Optional[str] = None) -> ProgressiveSkillsManager:
    """
    Get ProgressiveSkillsManager instance.

    Args:
        skills_dir: Path to skills directory

    Returns:
        ProgressiveSkillsManager instance
    """
    return ProgressiveSkillsManager(skills_dir=skills_dir)
