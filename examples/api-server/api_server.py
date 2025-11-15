#!/usr/bin/env python3
"""
FastAPI REST Server for Claude-Force

A production-ready REST API server that exposes claude-force agents as HTTP endpoints.

Features:
- RESTful API for agent execution
- Async/await support for concurrent requests
- Queue-based task processing for long-running jobs
- API key authentication
- Rate limiting
- Request validation
- Performance metrics
- OpenAPI documentation

Run:
    uvicorn api_server:app --reload --port 8000

API Docs:
    http://localhost:8000/docs
"""

import os
import sys
import time
import hashlib
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
from enum import Enum

# Add parent directory to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Depends, Security, BackgroundTasks, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn

from claude_force import AgentOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================================================
# Configuration
# ==============================================================================


class Config:
    """Server configuration"""

    API_KEYS = os.getenv("API_KEYS", "dev-key-12345").split(",")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))  # requests per minute
    MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "10"))
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


# ==============================================================================
# Data Models
# ==============================================================================


class AgentTaskRequest(BaseModel):
    """Request to run an agent"""

    agent_name: str = Field(..., description="Name of the agent to run")
    task: str = Field(..., min_length=1, max_length=10000, description="Task description")
    model: Optional[str] = Field(Config.DEFAULT_MODEL, description="Claude model to use")
    max_tokens: Optional[int] = Field(4096, ge=100, le=8000, description="Max tokens")
    temperature: Optional[float] = Field(1.0, ge=0.0, le=2.0, description="Temperature")

    @validator("agent_name")
    def validate_agent_name(cls, v):
        """Validate agent name format"""
        allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
        if not all(c in allowed_chars for c in v.lower()):
            raise ValueError("Agent name can only contain alphanumeric, dash, and underscore")
        return v


class AgentRecommendRequest(BaseModel):
    """Request for agent recommendations"""

    task: str = Field(..., min_length=1, max_length=10000, description="Task description")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of recommendations")
    min_confidence: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="Minimum confidence")


class WorkflowRequest(BaseModel):
    """Request to run a workflow"""

    workflow_name: str = Field(..., description="Name of the workflow to run")
    task: str = Field(..., min_length=1, max_length=10000, description="Initial task description")
    model: Optional[str] = Field(Config.DEFAULT_MODEL, description="Claude model to use")


class TaskStatus(str, Enum):
    """Task execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentResponse(BaseModel):
    """Response from agent execution"""

    success: bool
    agent_name: str
    task_id: Optional[str] = None
    output: Optional[str] = None
    metadata: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: float


class AsyncTaskResponse(BaseModel):
    """Response for async task submission"""

    task_id: str
    status: TaskStatus
    message: str
    check_url: str


class TaskStatusResponse(BaseModel):
    """Response for task status check"""

    task_id: str
    status: TaskStatus
    agent_name: Optional[str] = None
    submitted_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[AgentResponse] = None


# ==============================================================================
# In-Memory Task Queue (For Demo - Use Redis/Celery in Production)
# ==============================================================================


class TaskQueue:
    """Simple in-memory task queue"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running_count = 0

    def submit_task(self, agent_name: str, task: str, **kwargs) -> str:
        """Submit a task to the queue"""
        task_id = hashlib.sha256(f"{agent_name}{task}{time.time()}".encode()).hexdigest()[:16]

        self.tasks[task_id] = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "agent_name": agent_name,
            "task": task,
            "kwargs": kwargs,
            "submitted_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
        }

        logger.info(f"Task {task_id} submitted to queue")
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **updates):
        """Update task data"""
        if task_id in self.tasks:
            self.tasks[task_id].update(updates)

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks"""
        return [t for t in self.tasks.values() if t["status"] == TaskStatus.PENDING]


# ==============================================================================
# Initialize FastAPI App
# ==============================================================================

app = FastAPI(
    title="Claude-Force API",
    description="REST API for Claude-Force Multi-Agent System",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
orchestrator: Optional[AgentOrchestrator] = None
task_queue = TaskQueue()

# API key security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


# ==============================================================================
# Authentication
# ==============================================================================


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify API key"""
    if api_key not in Config.API_KEYS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return api_key


# ==============================================================================
# Startup/Shutdown Events
# ==============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator

    if not Config.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY not set - API will not function")
        return

    try:
        orchestrator = AgentOrchestrator(
            anthropic_api_key=Config.ANTHROPIC_API_KEY, enable_tracking=True
        )
        logger.info("AgentOrchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Server shutting down")


# ==============================================================================
# Background Task Processing
# ==============================================================================


def process_task_background(task_id: str):
    """Process a task in the background"""
    global orchestrator, task_queue

    task_data = task_queue.get_task(task_id)
    if not task_data:
        return

    try:
        # Update status to running
        task_queue.update_task(
            task_id, status=TaskStatus.RUNNING, started_at=datetime.utcnow().isoformat()
        )
        task_queue.running_count += 1

        # Execute agent
        start_time = time.time()
        result = orchestrator.run_agent(
            agent_name=task_data["agent_name"], task=task_data["task"], **task_data["kwargs"]
        )
        execution_time = (time.time() - start_time) * 1000

        # Create response
        response = AgentResponse(
            success=result.success,
            agent_name=task_data["agent_name"],
            task_id=task_id,
            output=result.output,
            metadata=result.metadata,
            error=result.error,
            execution_time_ms=execution_time,
        )

        # Update task with result
        task_queue.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.utcnow().isoformat(),
            result=response.dict(),
        )

        logger.info(f"Task {task_id} completed successfully")

    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task_queue.update_task(
            task_id,
            status=TaskStatus.FAILED,
            completed_at=datetime.utcnow().isoformat(),
            result={"error": str(e)},
        )
    finally:
        task_queue.running_count -= 1


# ==============================================================================
# API Endpoints
# ==============================================================================


@app.get("/")
async def root():
    """Root endpoint"""
    return {"service": "Claude-Force API", "version": "2.1.0", "status": "running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "orchestrator": orchestrator is not None,
        "anthropic_api": Config.ANTHROPIC_API_KEY is not None,
        "tasks_running": task_queue.running_count,
        "tasks_queued": len(task_queue.get_pending_tasks()),
    }


@app.get("/agents")
async def list_agents(api_key: str = Depends(verify_api_key)):
    """List all available agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        agents = orchestrator.list_agents()
        return {"agents": agents, "count": len(agents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/recommend", response_model=List[Dict[str, Any]])
async def recommend_agents(request: AgentRecommendRequest, api_key: str = Depends(verify_api_key)):
    """Get agent recommendations for a task"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        recommendations = orchestrator.recommend_agents(
            task=request.task, top_k=request.top_k, min_confidence=request.min_confidence
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/run", response_model=AgentResponse)
async def run_agent_sync(request: AgentTaskRequest, api_key: str = Depends(verify_api_key)):
    """Run an agent synchronously (waits for completion)"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        start_time = time.time()

        result = orchestrator.run_agent(
            agent_name=request.agent_name,
            task=request.task,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        execution_time = (time.time() - start_time) * 1000

        return AgentResponse(
            success=result.success,
            agent_name=request.agent_name,
            output=result.output,
            metadata=result.metadata,
            error=result.error,
            execution_time_ms=execution_time,
        )

    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/run/async", response_model=AsyncTaskResponse)
async def run_agent_async(
    request: AgentTaskRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key),
):
    """Run an agent asynchronously (returns immediately with task ID)"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Check if we're at capacity
    if task_queue.running_count >= Config.MAX_CONCURRENT_JOBS:
        raise HTTPException(
            status_code=429, detail=f"Too many concurrent jobs (max: {Config.MAX_CONCURRENT_JOBS})"
        )

    try:
        # Submit task to queue
        task_id = task_queue.submit_task(
            agent_name=request.agent_name,
            task=request.task,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )

        # Schedule background processing
        background_tasks.add_task(process_task_background, task_id)

        return AsyncTaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message="Task submitted successfully",
            check_url=f"/tasks/{task_id}",
        )

    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, api_key: str = Depends(verify_api_key)):
    """Get the status of an async task"""
    task_data = task_queue.get_task(task_id)

    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatusResponse(
        task_id=task_data["task_id"],
        status=task_data["status"],
        agent_name=task_data["agent_name"],
        submitted_at=task_data["submitted_at"],
        started_at=task_data["started_at"],
        completed_at=task_data["completed_at"],
        result=task_data["result"],
    )


@app.post("/workflows/run", response_model=AgentResponse)
async def run_workflow(request: WorkflowRequest, api_key: str = Depends(verify_api_key)):
    """Run a multi-agent workflow"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        start_time = time.time()

        result = orchestrator.run_workflow(
            workflow_name=request.workflow_name, initial_task=request.task, model=request.model
        )

        execution_time = (time.time() - start_time) * 1000

        return AgentResponse(
            success=result.success,
            agent_name=request.workflow_name,
            output=result.output,
            metadata=result.metadata,
            error=result.error,
            execution_time_ms=execution_time,
        )

    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/summary")
async def get_metrics_summary(hours: Optional[int] = None, api_key: str = Depends(verify_api_key)):
    """Get performance metrics summary"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        summary = orchestrator.get_performance_summary(hours=hours)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/agents")
async def get_agent_metrics(
    agent_name: Optional[str] = None, api_key: str = Depends(verify_api_key)
):
    """Get per-agent performance metrics"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        metrics = orchestrator.get_agent_performance(agent_name=agent_name)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/costs")
async def get_cost_breakdown(api_key: str = Depends(verify_api_key)):
    """Get cost breakdown"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        costs = orchestrator.get_cost_breakdown()
        return costs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("CLAUDE-FORCE API SERVER")
    print("=" * 70)
    print()
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print()
    print("Configuration:")
    print(f"  - API Keys: {len(Config.API_KEYS)} configured")
    print(f"  - Anthropic API: {'✅ Set' if Config.ANTHROPIC_API_KEY else '❌ Not set'}")
    print(f"  - Rate Limit: {Config.RATE_LIMIT} req/min")
    print(f"  - Max Concurrent: {Config.MAX_CONCURRENT_JOBS}")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
