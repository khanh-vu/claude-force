"""
Quick Start - Intelligent project initialization for claude-force.

Provides template-based project setup with semantic matching and
interactive selection.
"""

import os
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False


@dataclass
class ProjectTemplate:
    """Project template definition."""
    id: str
    name: str
    description: str
    category: str
    difficulty: str
    estimated_setup_time: str
    agents: List[str]
    workflows: List[str]
    skills: List[str]
    keywords: List[str]
    tech_stack: Dict[str, List[str]]
    use_cases: List[str]
    confidence: float = 0.0  # Matching confidence


@dataclass
class ProjectConfig:
    """Generated project configuration."""
    name: str
    description: str
    template_id: str
    agents: List[str]
    workflows: List[str]
    skills: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    customizations: Dict[str, Any] = field(default_factory=dict)


class QuickStartOrchestrator:
    """
    Intelligent project initialization with template suggestion.

    Features:
    - Semantic template matching
    - Interactive template selection
    - Automatic .claude/ directory generation
    - Customized agent definitions
    - Governance setup
    """

    def __init__(
        self,
        templates_path: Optional[str] = None,
        use_semantic: bool = True
    ):
        """
        Initialize QuickStartOrchestrator.

        Args:
            templates_path: Path to templates.yaml file
            use_semantic: Use semantic matching (requires sentence-transformers)
        """
        self.templates_path = templates_path or self._get_default_templates_path()
        self.templates = self._load_templates()
        self.use_semantic = use_semantic and SEMANTIC_AVAILABLE

        if self.use_semantic:
            try:
                self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                self._precompute_embeddings()
            except Exception as e:
                print(f"Warning: Could not load semantic model: {e}")
                self.use_semantic = False

    def _get_default_templates_path(self) -> str:
        """Get default templates path."""
        current_dir = Path(__file__).parent
        return str(current_dir / "templates" / "definitions" / "templates.yaml")

    def _load_templates(self) -> List[ProjectTemplate]:
        """Load templates from YAML file."""
        try:
            with open(self.templates_path, 'r') as f:
                data = yaml.safe_load(f)

            templates = []
            for template_data in data.get('templates', []):
                template = ProjectTemplate(
                    id=template_data['id'],
                    name=template_data['name'],
                    description=template_data['description'],
                    category=template_data['category'],
                    difficulty=template_data['difficulty'],
                    estimated_setup_time=template_data['estimated_setup_time'],
                    agents=template_data['agents'],
                    workflows=template_data['workflows'],
                    skills=template_data['skills'],
                    keywords=template_data['keywords'],
                    tech_stack=template_data['tech_stack'],
                    use_cases=template_data['use_cases']
                )
                templates.append(template)

            return templates

        except Exception as e:
            raise ValueError(f"Failed to load templates: {e}")

    def _precompute_embeddings(self):
        """Precompute template embeddings for faster matching."""
        if not self.use_semantic:
            return

        self.template_embeddings = {}

        for template in self.templates:
            # Combine all template text for embedding
            text = f"{template.name} {template.description} "
            text += " ".join(template.keywords)
            text += " ".join(template.use_cases)

            embedding = self.embedder.encode([text])[0]
            self.template_embeddings[template.id] = embedding

    def match_templates(
        self,
        description: str,
        tech_stack: Optional[List[str]] = None,
        top_k: int = 3
    ) -> List[ProjectTemplate]:
        """
        Match templates to project description using semantic similarity.

        Args:
            description: Project description
            tech_stack: Optional list of technologies
            top_k: Number of templates to return

        Returns:
            List of matched templates with confidence scores
        """
        if self.use_semantic:
            return self._semantic_match(description, tech_stack, top_k)
        else:
            return self._keyword_match(description, tech_stack, top_k)

    def _semantic_match(
        self,
        description: str,
        tech_stack: Optional[List[str]],
        top_k: int
    ) -> List[ProjectTemplate]:
        """Match templates using semantic similarity."""
        # Encode description
        query_text = description
        if tech_stack:
            query_text += " " + " ".join(tech_stack)

        query_embedding = self.embedder.encode([query_text])[0]

        # Compute similarities
        similarities = {}
        for template in self.templates:
            template_embedding = self.template_embeddings[template.id]

            # Cosine similarity
            similarity = np.dot(query_embedding, template_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(template_embedding)
            )

            # Boost if tech stack matches
            if tech_stack:
                tech_boost = self._compute_tech_stack_boost(template, tech_stack)
                similarity = similarity * 0.7 + tech_boost * 0.3

            similarities[template.id] = similarity

        # Sort by similarity
        sorted_templates = sorted(
            self.templates,
            key=lambda t: similarities[t.id],
            reverse=True
        )

        # Set confidence scores
        for template in sorted_templates[:top_k]:
            template.confidence = similarities[template.id]

        return sorted_templates[:top_k]

    def _keyword_match(
        self,
        description: str,
        tech_stack: Optional[List[str]],
        top_k: int
    ) -> List[ProjectTemplate]:
        """Match templates using keyword overlap (fallback)."""
        description_lower = description.lower()
        tech_lower = [t.lower() for t in (tech_stack or [])]

        scores = {}
        for template in self.templates:
            score = 0.0

            # Keyword matches
            for keyword in template.keywords:
                if keyword.lower() in description_lower:
                    score += 1.0

            # Use case matches
            for use_case in template.use_cases:
                if any(word in description_lower for word in use_case.lower().split()):
                    score += 0.5

            # Tech stack matches
            if tech_lower:
                tech_boost = self._compute_tech_stack_boost(template, tech_stack)
                score += tech_boost * 5

            # Normalize
            max_score = len(template.keywords) + len(template.use_cases) + 5
            scores[template.id] = min(score / max_score, 1.0)

        # Sort by score
        sorted_templates = sorted(
            self.templates,
            key=lambda t: scores[t.id],
            reverse=True
        )

        # Set confidence scores
        for template in sorted_templates[:top_k]:
            template.confidence = scores[template.id]

        return sorted_templates[:top_k]

    def _compute_tech_stack_boost(
        self,
        template: ProjectTemplate,
        tech_stack: List[str]
    ) -> float:
        """Compute tech stack match boost."""
        if not tech_stack:
            return 0.0

        tech_lower = [t.lower() for t in tech_stack]
        matches = 0
        total = 0

        for stack_category, technologies in template.tech_stack.items():
            for tech in technologies:
                total += 1
                if any(t in tech.lower() for t in tech_lower):
                    matches += 1

        return matches / total if total > 0 else 0.0

    def analyze_project(
        self,
        description: str,
        tech_stack: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze project description to extract metadata.

        Args:
            description: Project description
            tech_stack: Optional tech stack

        Returns:
            Project analysis with detected features
        """
        description_lower = description.lower()

        analysis = {
            "description": description,
            "tech_stack": tech_stack or [],
            "detected_features": [],
            "complexity": "intermediate",
            "category": "general"
        }

        # Detect features
        if any(kw in description_lower for kw in ["rag", "chatbot", "llm", "gpt", "claude"]):
            analysis["detected_features"].append("llm-integration")

        if any(kw in description_lower for kw in ["ml", "model", "training", "prediction"]):
            analysis["detected_features"].append("machine-learning")

        if any(kw in description_lower for kw in ["database", "postgres", "mongodb", "sql"]):
            analysis["detected_features"].append("database")

        if any(kw in description_lower for kw in ["api", "rest", "graphql", "endpoint"]):
            analysis["detected_features"].append("api")

        if any(kw in description_lower for kw in ["frontend", "react", "vue", "ui"]):
            analysis["detected_features"].append("frontend")

        if any(kw in description_lower for kw in ["etl", "pipeline", "airflow", "data"]):
            analysis["detected_features"].append("data-pipeline")

        # Determine complexity
        feature_count = len(analysis["detected_features"])
        if feature_count >= 4:
            analysis["complexity"] = "advanced"
        elif feature_count >= 2:
            analysis["complexity"] = "intermediate"
        else:
            analysis["complexity"] = "simple"

        return analysis

    def generate_config(
        self,
        template: ProjectTemplate,
        project_name: str,
        description: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> ProjectConfig:
        """
        Generate project configuration from template.

        Args:
            template: Selected template
            project_name: Project name
            description: Project description
            customizations: Optional customizations

        Returns:
            Project configuration
        """
        config = ProjectConfig(
            name=project_name,
            description=description,
            template_id=template.id,
            agents=template.agents.copy(),
            workflows=template.workflows.copy(),
            skills=template.skills.copy(),
            customizations=customizations or {}
        )

        return config

    def initialize_project(
        self,
        config: ProjectConfig,
        output_dir: str = ".claude",
        create_examples: bool = True
    ) -> Dict[str, Any]:
        """
        Initialize .claude/ directory structure.

        Args:
            config: Project configuration
            output_dir: Output directory (default: .claude)
            create_examples: Create example task files

        Returns:
            Initialization result with created files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        created_files = []

        # 1. Create claude.json
        claude_json_path = output_path / "claude.json"
        claude_json = self._generate_claude_json(config)

        with open(claude_json_path, 'w') as f:
            json.dump(claude_json, f, indent=2)
        created_files.append(str(claude_json_path))

        # 2. Create task.md template
        task_md_path = output_path / "task.md"
        task_md = self._generate_task_template(config)

        with open(task_md_path, 'w') as f:
            f.write(task_md)
        created_files.append(str(task_md_path))

        # 3. Create README.md
        readme_path = output_path / "README.md"
        readme = self._generate_readme(config)

        with open(readme_path, 'w') as f:
            f.write(readme)
        created_files.append(str(readme_path))

        # 4. Create scorecard.md
        scorecard_path = output_path / "scorecard.md"
        scorecard = self._generate_scorecard(config)

        with open(scorecard_path, 'w') as f:
            f.write(scorecard)
        created_files.append(str(scorecard_path))

        # 5. Create directories
        for directory in ['agents', 'contracts', 'hooks', 'skills', 'tasks', 'metrics']:
            dir_path = output_path / directory
            dir_path.mkdir(exist_ok=True)

        # 6. Create example task if requested
        if create_examples:
            example_task_path = output_path / "examples" / "example-task.md"
            example_task_path.parent.mkdir(exist_ok=True)

            example_task = self._generate_example_task(config)
            with open(example_task_path, 'w') as f:
                f.write(example_task)
            created_files.append(str(example_task_path))

        return {
            "success": True,
            "config": config,
            "created_files": created_files,
            "output_dir": str(output_path)
        }

    def _generate_claude_json(self, config: ProjectConfig) -> Dict[str, Any]:
        """Generate claude.json configuration."""
        return {
            "version": "1.0.0",
            "name": config.name,
            "description": config.description,
            "template": config.template_id,
            "created_at": config.created_at,

            "agents": {
                agent: {
                    "file": f"agents/{agent}.md",
                    "contract": f"contracts/{agent}.contract"
                }
                for agent in config.agents
            },

            "workflows": {
                workflow: config.agents  # Simplified - use all agents
                for workflow in config.workflows
            },

            "governance": {
                "hooks_enabled": True,
                "pre_run_required": True,
                "post_run_validation": True
            },

            "skills_integration": {
                "enabled": True,
                "skills_path": "skills/",
                "available_skills": config.skills
            },

            "paths": {
                "task": "task.md",
                "work": "work.md",
                "scorecard": "scorecard.md",
                "context": "tasks/context_session_1.md",
                "agents": "agents/",
                "contracts": "contracts/",
                "hooks": "hooks/",
                "skills": "skills/"
            }
        }

    def _generate_task_template(self, config: ProjectConfig) -> str:
        """Generate task.md template."""
        return f"""# Task

## Project: {config.name}

{config.description}

## Objective

[Describe what you want to accomplish with this task]

## Context

[Provide relevant background information]

## Requirements

- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Details

[Any specific technical requirements or constraints]

## Questions

[Any questions or clarifications needed]

---

**Created**: {config.created_at}
**Template**: {config.template_id}
"""

    def _generate_readme(self, config: ProjectConfig) -> str:
        """Generate README.md."""
        return f"""# {config.name}

{config.description}

## Quick Start

This project was initialized using the `{config.template_id}` template.

### Available Agents

{chr(10).join(f'- **{agent}**' for agent in config.agents)}

### Available Workflows

{chr(10).join(f'- **{workflow}**' for workflow in config.workflows)}

### Available Skills

{chr(10).join(f'- **{skill}**' for skill in config.skills)}

## Usage

### Run an agent:
```bash
claude-force run agent <agent-name> --task "Your task"
```

### Run a workflow:
```bash
claude-force run workflow <workflow-name> --task "Your task"
```

### Get agent info:
```bash
claude-force info <agent-name>
```

## Next Steps

1. Edit `.claude/task.md` with your first task
2. Run appropriate agent or workflow
3. Review output in `.claude/work.md`

---

Created: {config.created_at}
Template: {config.template_id}
"""

    def _generate_scorecard(self, config: ProjectConfig) -> str:
        """Generate scorecard.md."""
        return """# Quality Scorecard

## Code Quality
- [ ] Code follows best practices
- [ ] Type hints are comprehensive
- [ ] Error handling is robust
- [ ] Code is well-documented

## Testing
- [ ] Unit tests are comprehensive
- [ ] Integration tests are included
- [ ] Edge cases are covered
- [ ] Tests are passing

## Security
- [ ] No hardcoded secrets
- [ ] Input validation is present
- [ ] Security best practices followed
- [ ] Dependencies are secure

## Documentation
- [ ] Code is documented
- [ ] API documentation exists
- [ ] Examples are provided
- [ ] README is updated

## Performance
- [ ] Code is optimized
- [ ] No obvious bottlenecks
- [ ] Resource usage is acceptable
- [ ] Scalability considered
"""

    def _generate_example_task(self, config: ProjectConfig) -> str:
        """Generate example task."""
        return f"""# Example Task for {config.name}

## Objective

[Example objective based on your project type]

## Steps

1. Step 1
2. Step 2
3. Step 3

## Expected Output

[What should be produced]

## Tips

- Use the appropriate agent for this task
- Review the agent's output carefully
- Iterate if needed

---

Template: {config.template_id}
"""


def get_quick_start_orchestrator(
    templates_path: Optional[str] = None,
    use_semantic: bool = True
) -> QuickStartOrchestrator:
    """
    Get QuickStartOrchestrator instance.

    Args:
        templates_path: Optional path to templates.yaml
        use_semantic: Use semantic matching

    Returns:
        QuickStartOrchestrator instance
    """
    return QuickStartOrchestrator(
        templates_path=templates_path,
        use_semantic=use_semantic
    )
