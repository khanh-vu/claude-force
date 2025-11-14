"""
Semantic Agent Selection

Uses embeddings and cosine similarity to intelligently match tasks to agents.
Provides confidence scores and multi-agent recommendations.
"""

import json
import hashlib
import hmac
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class AgentMatch:
    """Result of agent matching"""
    agent_name: str
    confidence: float
    reasoning: str
    domains: List[str]
    priority: int


class SemanticAgentSelector:
    """
    Semantic agent selection using embeddings and cosine similarity.

    This selector uses sentence embeddings to match tasks with agents based on
    semantic similarity rather than keyword matching, resulting in better accuracy.
    """

    def __init__(self, config_path: str = ".claude/claude.json",
                 model_name: str = "all-MiniLM-L6-v2",
                 use_cache: bool = True):
        """
        Initialize semantic selector

        Args:
            config_path: Path to claude.json configuration
            model_name: Sentence transformer model to use (default: all-MiniLM-L6-v2)
                       This is a lightweight, fast model good for production.
                       Alternatives: all-mpnet-base-v2 (more accurate, slower)
            use_cache: Whether to use cached embeddings (default: True)
        """
        self.config_path = Path(config_path)
        self.model_name = model_name
        self.use_cache = use_cache
        self.config = self._load_config()
        self.model = None
        self.agent_embeddings = {}
        self._lazy_init = False
        self._cache_dir = self.config_path.parent / ".cache"
        self._embeddings_cache_file = self._cache_dir / "agent_embeddings.json"
        self._cache_key = self._get_cache_key()

    def _load_config(self) -> dict:
        """Load agent configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path) as f:
            return json.load(f)

    def _ensure_initialized(self):
        """Lazy initialization of sentence transformer model"""
        if self._lazy_init:
            return

        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self._lazy_init = True
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

    def _load_agent_description(self, agent_name: str) -> str:
        """Load agent description from agent file"""
        agent_info = self.config.get("agents", {}).get(agent_name, {})
        agent_file = agent_info.get("file", f"agents/{agent_name}.md")

        agent_path = self.config_path.parent / agent_file
        if not agent_path.exists():
            # Fallback to domains if no file
            domains = agent_info.get("domains", [])
            return f"Agent specialized in: {', '.join(domains)}"

        try:
            with open(agent_path) as f:
                content = f.read()
                # Extract key sections for embedding
                lines = content.split('\n')
                description_parts = []

                # Look for purpose, responsibilities, capabilities
                for i, line in enumerate(lines):
                    if any(keyword in line.lower() for keyword in
                          ['purpose', 'responsibility', 'capability', 'expertise', 'specialization']):
                        # Get next few lines
                        description_parts.extend(lines[i:min(i+10, len(lines))])

                if description_parts:
                    return '\n'.join(description_parts)

                # Fallback: use first 1000 chars
                return content[:1000]
        except Exception as e:
            # Fallback to basic info
            domains = agent_info.get("domains", [])
            return f"Agent specialized in: {', '.join(domains)}. Error loading details: {e}"

    def _get_config_hash(self) -> str:
        """Generate hash of config for cache invalidation."""
        config_str = json.dumps(self.config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    def _get_cache_key(self) -> str:
        """Generate HMAC key for cache integrity verification."""
        # Use config path and model name as key material
        key_material = f"{self.config_path}:{self.model_name}".encode()
        return hashlib.sha256(key_material).hexdigest()

    def _load_from_cache(self) -> bool:
        """
        Load embeddings from cache if valid.

        Returns:
            True if cache loaded successfully, False otherwise
        """
        if not self._embeddings_cache_file.exists():
            return False

        try:
            with open(self._embeddings_cache_file, 'r') as f:
                cache_data = json.load(f)

            # Verify HMAC signature
            stored_hmac = cache_data.get('hmac', '')
            cache_content = json.dumps({
                'config_hash': cache_data.get('config_hash'),
                'model_name': cache_data.get('model_name'),
                'embeddings': cache_data.get('embeddings')
            }, sort_keys=True)

            expected_hmac = hmac.new(
                self._cache_key.encode(),
                cache_content.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(stored_hmac, expected_hmac):
                # Cache integrity check failed
                return False

            # Validate cache
            if cache_data.get('config_hash') != self._get_config_hash():
                return False

            if cache_data.get('model_name') != self.model_name:
                return False

            # Load embeddings (convert lists back to numpy arrays)
            embeddings_data = cache_data.get('embeddings', {})
            self.agent_embeddings = {
                agent: np.array(embedding)
                for agent, embedding in embeddings_data.items()
            }
            return True

        except Exception:
            # If cache load fails, regenerate
            return False

    def _save_to_cache(self):
        """Save embeddings to cache with HMAC signature."""
        try:
            # Create cache directory if not exists
            self._cache_dir.mkdir(parents=True, exist_ok=True)

            # Convert numpy arrays to lists for JSON serialization
            embeddings_serializable = {
                agent: embedding.tolist()
                for agent, embedding in self.agent_embeddings.items()
            }

            cache_content = {
                'config_hash': self._get_config_hash(),
                'model_name': self.model_name,
                'embeddings': embeddings_serializable
            }

            # Generate HMAC signature for integrity
            cache_content_str = json.dumps(cache_content, sort_keys=True)
            signature = hmac.new(
                self._cache_key.encode(),
                cache_content_str.encode(),
                hashlib.sha256
            ).hexdigest()

            # Add signature to cache data
            cache_data = {**cache_content, 'hmac': signature}

            with open(self._embeddings_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception:
            # Cache save failure should not break functionality
            pass

    def _compute_agent_embeddings(self):
        """Pre-compute embeddings for all agents with caching support."""
        # Try to load from cache first
        if self.use_cache and self._load_from_cache():
            return

        self._ensure_initialized()

        agents = self.config.get("agents", {})
        descriptions = []
        agent_names = []

        for agent_name in agents.keys():
            description = self._load_agent_description(agent_name)
            descriptions.append(description)
            agent_names.append(agent_name)

        # Compute embeddings in batch for efficiency
        embeddings = self.model.encode(descriptions, convert_to_numpy=True)

        # Store embeddings
        for agent_name, embedding in zip(agent_names, embeddings):
            self.agent_embeddings[agent_name] = embedding

        # Save to cache
        if self.use_cache:
            self._save_to_cache()

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def select_agents(self, task: str, top_k: int = 3,
                     min_confidence: float = 0.3) -> List[AgentMatch]:
        """
        Select best agents for a task using semantic similarity

        Args:
            task: Task description
            top_k: Number of top agents to return
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            List of AgentMatch objects sorted by confidence
        """
        self._ensure_initialized()

        # Compute agent embeddings if not already done
        if not self.agent_embeddings:
            self._compute_agent_embeddings()

        # Compute task embedding
        task_embedding = self.model.encode(task, convert_to_numpy=True)

        # Compute similarities
        similarities = []
        agents_config = self.config.get("agents", {})

        for agent_name, agent_embedding in self.agent_embeddings.items():
            similarity = self._cosine_similarity(task_embedding, agent_embedding)

            # Get agent metadata
            agent_info = agents_config.get(agent_name, {})
            domains = agent_info.get("domains", [])
            priority = agent_info.get("priority", 3)

            # Generate reasoning
            reasoning = self._generate_reasoning(task, agent_name, similarity, domains)

            similarities.append(AgentMatch(
                agent_name=agent_name,
                confidence=similarity,
                reasoning=reasoning,
                domains=domains,
                priority=priority
            ))

        # Sort by confidence (with slight priority boost)
        similarities.sort(key=lambda x: (x.confidence + (0.05 * (4 - x.priority))), reverse=True)

        # Filter by minimum confidence and return top_k
        filtered = [m for m in similarities if m.confidence >= min_confidence]
        return filtered[:top_k]

    def _generate_reasoning(self, task: str, agent_name: str,
                           confidence: float, domains: List[str]) -> str:
        """Generate human-readable reasoning for agent selection"""
        task_lower = task.lower()

        # Check domain matches
        domain_matches = [d for d in domains if d.lower() in task_lower]

        if confidence > 0.7:
            level = "High"
        elif confidence > 0.5:
            level = "Medium"
        else:
            level = "Low"

        reasoning_parts = [f"{level} confidence match"]

        if domain_matches:
            reasoning_parts.append(f"domains: {', '.join(domain_matches)}")

        if confidence > 0.7:
            reasoning_parts.append("strong semantic similarity")
        elif confidence > 0.5:
            reasoning_parts.append("good semantic similarity")
        else:
            reasoning_parts.append("weak semantic similarity")

        return " - ".join(reasoning_parts)

    def explain_selection(self, task: str, agent_name: str) -> Dict:
        """
        Explain why a specific agent was or wasn't selected

        Args:
            task: Task description
            agent_name: Agent to explain

        Returns:
            Dictionary with explanation details
        """
        matches = self.select_agents(task, top_k=len(self.config.get("agents", {})))

        # Find the agent
        agent_match = None
        rank = None
        for i, match in enumerate(matches, 1):
            if match.agent_name == agent_name:
                agent_match = match
                rank = i
                break

        if not agent_match:
            return {
                "agent": agent_name,
                "selected": False,
                "reason": "Agent not found or confidence too low"
            }

        return {
            "agent": agent_name,
            "selected": rank <= 3,
            "rank": rank,
            "confidence": round(agent_match.confidence, 3),
            "reasoning": agent_match.reasoning,
            "domains": agent_match.domains,
            "all_candidates": [
                {
                    "agent": m.agent_name,
                    "confidence": round(m.confidence, 3)
                }
                for m in matches[:5]
            ]
        }

    def benchmark_selection(self, test_cases: List[Dict]) -> Dict:
        """
        Benchmark semantic selection against test cases

        Args:
            test_cases: List of dicts with 'task' and 'expected_agents'

        Returns:
            Dictionary with benchmark results
        """
        results = []
        correct = 0
        total = 0

        for test_case in test_cases:
            task = test_case.get("task", "")
            expected = set(test_case.get("expected_agents", []))

            if not task or not expected:
                continue

            # Select agents
            matches = self.select_agents(task, top_k=3)
            selected = {m.agent_name for m in matches}

            # Check accuracy
            intersection = selected & expected
            accuracy = len(intersection) / len(expected) if expected else 0

            total += 1
            if accuracy >= 0.5:  # At least 50% of expected agents selected
                correct += 1

            results.append({
                "task": task[:100],
                "expected": list(expected),
                "selected": list(selected),
                "accuracy": accuracy,
                "top_match": matches[0].agent_name if matches else None,
                "top_confidence": round(matches[0].confidence, 3) if matches else 0
            })

        return {
            "total_tests": total,
            "correct": correct,
            "accuracy": round(correct / total, 3) if total > 0 else 0,
            "detailed_results": results
        }


def get_selector(config_path: str = ".claude/claude.json",
                 model_name: str = "all-MiniLM-L6-v2") -> SemanticAgentSelector:
    """
    Factory function to create semantic selector

    Args:
        config_path: Path to configuration
        model_name: Sentence transformer model

    Returns:
        SemanticAgentSelector instance
    """
    return SemanticAgentSelector(config_path, model_name)
