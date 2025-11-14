"""
Agent Memory System for Claude-Force

Provides session persistence and cross-session learning capabilities:
- Stores agent interactions and results
- Tracks successful strategies
- Retrieves relevant past context for similar tasks
- Learns from past executions

Usage:
    memory = AgentMemory(db_path="sessions.db")

    # Store session
    session_id = memory.store_session(
        agent_name="code-reviewer",
        task="Review authentication code",
        output="Found 3 security issues...",
        success=True,
        metadata={"model": "claude-3-5-sonnet-20241022"}
    )

    # Retrieve similar sessions
    similar = memory.find_similar_sessions(
        task="Review login code",
        agent_name="code-reviewer",
        limit=5
    )

    # Get context for agent
    context = memory.get_context_for_task(
        task="Review API authentication",
        agent_name="code-reviewer"
    )
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class SessionMemory:
    """A stored agent session."""

    session_id: str
    agent_name: str
    task: str
    task_hash: str
    output: str
    success: bool
    execution_time_ms: float
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: str
    metadata: Dict[str, Any]
    similarity_score: float = 0.0


class AgentMemory:
    """
    Agent memory system with session persistence and learning.

    Stores agent executions in SQLite database and provides:
    - Session history tracking
    - Similar task retrieval
    - Context injection for agents
    - Strategy learning from past successes
    """

    def __init__(self, db_path: str = ".claude/sessions.db"):
        """
        Initialize agent memory system.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    task TEXT NOT NULL,
                    task_hash TEXT NOT NULL,
                    output TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    execution_time_ms REAL NOT NULL,
                    model TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    UNIQUE(agent_name, task_hash, timestamp)
                )
            """
            )

            # Create indices for fast retrieval
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_name
                ON sessions(agent_name)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_task_hash
                ON sessions(task_hash)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON sessions(timestamp DESC)
            """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_success
                ON sessions(success)
            """
            )

            # Create strategies table for tracking successful approaches
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS strategies (
                    strategy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    task_category TEXT NOT NULL,
                    strategy_description TEXT NOT NULL,
                    success_count INTEGER NOT NULL DEFAULT 1,
                    failure_count INTEGER NOT NULL DEFAULT 0,
                    avg_execution_time_ms REAL NOT NULL,
                    last_used TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    UNIQUE(agent_name, task_category, strategy_description)
                )
            """
            )

            conn.commit()

    def _task_hash(self, task: str) -> str:
        """
        Generate hash for task deduplication.

        Args:
            task: Task description

        Returns:
            SHA256 hash of normalized task
        """
        # Normalize task (lowercase, strip whitespace)
        normalized = task.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def store_session(
        self,
        agent_name: str,
        task: str,
        output: str,
        success: bool,
        execution_time_ms: float = 0.0,
        model: str = "claude-3-5-sonnet-20241022",
        input_tokens: int = 0,
        output_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store an agent session in memory.

        Args:
            agent_name: Name of the agent
            task: Task description
            output: Agent output
            success: Whether execution was successful
            execution_time_ms: Execution time in milliseconds
            model: Model used
            input_tokens: Input token count
            output_tokens: Output token count
            metadata: Additional metadata

        Returns:
            Session ID
        """
        session_id = f"{agent_name}_{self._task_hash(task)}_{datetime.now().isoformat()}"
        timestamp = datetime.now().isoformat()
        task_hash = self._task_hash(task)

        metadata = metadata or {}
        metadata_json = json.dumps(metadata)

        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO sessions (
                        session_id, agent_name, task, task_hash, output,
                        success, execution_time_ms, model, input_tokens,
                        output_tokens, timestamp, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        agent_name,
                        task,
                        task_hash,
                        output,
                        1 if success else 0,
                        execution_time_ms,
                        model,
                        input_tokens,
                        output_tokens,
                        timestamp,
                        metadata_json,
                    ),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Duplicate session (same agent, task hash, and timestamp)
                # Update session_id to be unique
                session_id = f"{session_id}_dup_{hash(output)}"

        return session_id

    def find_similar_sessions(
        self,
        task: str,
        agent_name: Optional[str] = None,
        success_only: bool = True,
        limit: int = 5,
        days: Optional[int] = None,
    ) -> List[SessionMemory]:
        """
        Find sessions similar to the given task.

        Args:
            task: Task to find similar sessions for
            agent_name: Filter by agent name (None for all agents)
            success_only: Only return successful sessions
            limit: Maximum number of sessions to return
            days: Only return sessions from last N days (None for all)

        Returns:
            List of similar SessionMemory objects
        """
        task_hash = self._task_hash(task)

        query = """
            SELECT session_id, agent_name, task, task_hash, output,
                   success, execution_time_ms, model, input_tokens,
                   output_tokens, timestamp, metadata
            FROM sessions
            WHERE 1=1
        """
        params = []

        # Filter by agent name
        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        # Filter by success
        if success_only:
            query += " AND success = 1"

        # Filter by time window
        if days is not None:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            query += " AND timestamp >= ?"
            params.append(cutoff)

        # Order by task similarity (exact hash first) and recency
        query += """
            ORDER BY
                CASE WHEN task_hash = ? THEN 0 ELSE 1 END,
                timestamp DESC
            LIMIT ?
        """
        params.extend([task_hash, limit])

        sessions = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)

            for row in cursor.fetchall():
                metadata = json.loads(row[11])
                session = SessionMemory(
                    session_id=row[0],
                    agent_name=row[1],
                    task=row[2],
                    task_hash=row[3],
                    output=row[4],
                    success=bool(row[5]),
                    execution_time_ms=row[6],
                    model=row[7],
                    input_tokens=row[8],
                    output_tokens=row[9],
                    timestamp=row[10],
                    metadata=metadata,
                    similarity_score=1.0 if row[3] == task_hash else 0.5,
                )
                sessions.append(session)

        return sessions

    def get_context_for_task(self, task: str, agent_name: str, max_sessions: int = 3) -> str:
        """
        Get relevant context from past sessions for a task.

        Args:
            task: Current task
            agent_name: Agent name
            max_sessions: Maximum number of past sessions to include

        Returns:
            Formatted context string to inject into agent prompt
        """
        similar_sessions = self.find_similar_sessions(
            task=task,
            agent_name=agent_name,
            success_only=True,
            limit=max_sessions,
            days=90,  # Last 90 days
        )

        if not similar_sessions:
            return ""

        context_parts = [
            "# Relevant Past Experience",
            "",
            "Here are successful approaches from similar tasks:",
            "",
        ]

        for i, session in enumerate(similar_sessions, 1):
            context_parts.extend(
                [
                    f"## Past Task {i} (Similarity: {session.similarity_score:.0%})",
                    f"**Task**: {session.task[:200]}...",
                    f"**Approach**: {session.output[:400]}...",
                    f"**Result**: ✓ Success in {session.execution_time_ms:.0f}ms",
                    "",
                ]
            )

        context_parts.extend(["Use these successful approaches to inform your current task.", ""])

        return "\n".join(context_parts)

    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """
        Retrieve a specific session by ID.

        Args:
            session_id: Session ID

        Returns:
            SessionMemory if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT session_id, agent_name, task, task_hash, output,
                       success, execution_time_ms, model, input_tokens,
                       output_tokens, timestamp, metadata
                FROM sessions
                WHERE session_id = ?
                """,
                (session_id,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            metadata = json.loads(row[11])
            return SessionMemory(
                session_id=row[0],
                agent_name=row[1],
                task=row[2],
                task_hash=row[3],
                output=row[4],
                success=bool(row[5]),
                execution_time_ms=row[6],
                model=row[7],
                input_tokens=row[8],
                output_tokens=row[9],
                timestamp=row[10],
                metadata=metadata,
            )

    def get_statistics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get memory statistics.

        Args:
            agent_name: Filter by agent (None for all)

        Returns:
            Dictionary with statistics
        """
        query = "SELECT COUNT(*), AVG(success), AVG(execution_time_ms) FROM sessions"
        params = []

        if agent_name:
            query += " WHERE agent_name = ?"
            params.append(agent_name)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            row = cursor.fetchone()

            return {
                "total_sessions": row[0] or 0,
                "success_rate": (row[1] or 0.0) * 100,
                "avg_execution_time_ms": row[2] or 0.0,
            }

    def prune_old_sessions(self, days: int = 90) -> int:
        """
        Remove sessions older than specified days.

        Args:
            days: Age threshold in days

        Returns:
            Number of sessions deleted
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE timestamp < ?", (cutoff,))
            deleted = cursor.rowcount
            conn.commit()

        return deleted

    def clear_all(self):
        """Clear all sessions (use with caution)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions")
            conn.execute("DELETE FROM strategies")
            conn.commit()


def get_memory(db_path: str = ".claude/sessions.db") -> AgentMemory:
    """
    Factory function to get agent memory instance.

    Args:
        db_path: Path to SQLite database

    Returns:
        AgentMemory instance
    """
    return AgentMemory(db_path)
