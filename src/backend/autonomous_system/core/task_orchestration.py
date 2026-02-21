"""
Task Orchestration System - Module 4.2

Workflow management, task dependency resolution,
load balancing, resource allocation, and fault tolerance.
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime, timedelta
import threading
from collections import defaultdict, deque


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class DependencyType(Enum):
    """Types of task dependencies"""
    SEQUENTIAL = "sequential"  # Strict ordering
    PARALLEL = "parallel"  # Can run simultaneously
    CONDITIONAL = "conditional"  # Depends on result
    RESOURCE = "resource"  # Shared resource


@dataclass
class Task:
    """Represents a unit of work"""
    task_id: str
    task_type: str
    priority: TaskPriority
    content: Dict[str, Any]
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    timeout: float = 300.0
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    estimated_duration: float = 0.0


@dataclass
class TaskWorkflow:
    """Represents a workflow of tasks"""
    workflow_id: str
    name: str
    tasks: Dict[str, Task] = field(default_factory=dict)
    task_order: List[str] = field(default_factory=list)
    status: str = "created"
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    total_duration: float = 0.0


@dataclass
class LoadBalancingMetrics:
    """Metrics for load balancing decisions"""
    agent_id: str
    current_load: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    average_task_duration: float
    availability: float


class TaskDependencyResolver:
    """Resolves task dependencies and determines execution order"""

    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.execution_order: List[str] = []

    def add_dependency(self, task_id: str, depends_on: str):
        """Add dependency: task_id depends on depends_on"""
        self.dependency_graph[task_id].add(depends_on)

    def resolve_order(self, all_tasks: Dict[str, Task]) -> List[str]:
        """Resolve task execution order using topological sort"""
        in_degree = defaultdict(int)
        tasks_set = set(all_tasks.keys())

        # Calculate in-degree
        for task_id in tasks_set:
            if task_id not in in_degree:
                in_degree[task_id] = 0

            for dep in self.dependency_graph.get(task_id, set()):
                if dep in tasks_set:
                    in_degree[task_id] += 1

        # Topological sort
        queue = deque([t for t in tasks_set if in_degree[t] == 0])
        sorted_tasks = []

        while queue:
            task_id = queue.popleft()
            sorted_tasks.append(task_id)

            # Find tasks that depend on this one
            for other_task in tasks_set:
                if task_id in self.dependency_graph.get(other_task, set()):
                    in_degree[other_task] -= 1
                    if in_degree[other_task] == 0:
                        queue.append(other_task)

        self.execution_order = sorted_tasks
        return sorted_tasks

    def get_executable_tasks(self, all_tasks: Dict[str, Task],
                            completed_tasks: Set[str]) -> List[str]:
        """Get tasks that are ready to execute"""
        executable = []
        for task_id, task in all_tasks.items():
            if task.status == TaskStatus.PENDING:
                # Check if all dependencies are completed
                deps_met = all(
                    dep in completed_tasks
                    for dep in self.dependency_graph.get(task_id, set())
                )
                if deps_met:
                    executable.append(task_id)
        return executable


class LoadBalancer:
    """Distributes tasks across agents"""

    def __init__(self):
        self.agent_metrics: Dict[str, LoadBalancingMetrics] = {}
        self.task_assignments: Dict[str, str] = {}
        self.agent_workload: Dict[str, List[str]] = defaultdict(list)

    def register_agent(self, agent_id: str):
        """Register agent for load balancing"""
        self.agent_metrics[agent_id] = LoadBalancingMetrics(
            agent_id=agent_id,
            current_load=0.0,
            active_tasks=0,
            completed_tasks=0,
            failed_tasks=0,
            average_task_duration=0.0,
            availability=1.0
        )

    def update_agent_load(self, agent_id: str, active_tasks: int,
                         load_value: float):
        """Update agent load metrics"""
        if agent_id in self.agent_metrics:
            metrics = self.agent_metrics[agent_id]
            metrics.active_tasks = active_tasks
            metrics.current_load = load_value

    def select_agent(self, task: Task) -> Optional[str]:
        """Select best agent for task using load balancing"""
        available_agents = [
            a for a in self.agent_metrics
            if self.agent_metrics[a].availability > 0.5
        ]

        if not available_agents:
            return None

        # Select agent with lowest load
        selected = min(
            available_agents,
            key=lambda a: self.agent_metrics[a].current_load
        )

        return selected

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign task to agent"""
        if agent_id not in self.agent_metrics:
            return False

        self.task_assignments[task_id] = agent_id
        self.agent_workload[agent_id].append(task_id)
        return True

    def get_balancing_metrics(self) -> Dict[str, Any]:
        """Get load balancing metrics"""
        metrics_dict = {}
        total_load = 0.0

        for agent_id, metrics in self.agent_metrics.items():
            metrics_dict[agent_id] = {
                "current_load": metrics.current_load,
                "active_tasks": metrics.active_tasks,
                "completed_tasks": metrics.completed_tasks,
                "failed_tasks": metrics.failed_tasks,
                "availability": metrics.availability
            }
            total_load += metrics.current_load

        avg_load = (total_load / len(self.agent_metrics)
                   if self.agent_metrics else 0.0)

        return {
            "by_agent": metrics_dict,
            "average_load": avg_load,
            "total_load": total_load
        }


class ResourceAllocator:
    """Allocates resources for task execution"""

    def __init__(self, total_cpu: float = 100.0,
                 total_memory: float = 1024.0):
        self.total_cpu = total_cpu
        self.total_memory = total_memory
        self.allocated_cpu: Dict[str, float] = {}
        self.allocated_memory: Dict[str, float] = {}

    def allocate_resources(self, task_id: str, cpu_required: float,
                          memory_required: float) -> bool:
        """Allocate resources to task"""
        available_cpu = (self.total_cpu -
                        sum(self.allocated_cpu.values()))
        available_memory = (self.total_memory -
                           sum(self.allocated_memory.values()))

        if cpu_required <= available_cpu and memory_required <= available_memory:
            self.allocated_cpu[task_id] = cpu_required
            self.allocated_memory[task_id] = memory_required
            return True

        return False

    def deallocate_resources(self, task_id: str):
        """Free resources from task"""
        if task_id in self.allocated_cpu:
            del self.allocated_cpu[task_id]
        if task_id in self.allocated_memory:
            del self.allocated_memory[task_id]

    def get_resource_utilization(self) -> Dict[str, Any]:
        """Get resource utilization metrics"""
        used_cpu = sum(self.allocated_cpu.values())
        used_memory = sum(self.allocated_memory.values())

        return {
            "cpu": {
                "used": used_cpu,
                "total": self.total_cpu,
                "utilization": used_cpu / self.total_cpu if self.total_cpu > 0 else 0.0
            },
            "memory": {
                "used": used_memory,
                "total": self.total_memory,
                "utilization": used_memory / self.total_memory if self.total_memory > 0 else 0.0
            }
        }


class FaultTolerance:
    """Handles task failures and recovery"""

    def __init__(self):
        self.failed_tasks: Dict[str, int] = defaultdict(int)
        self.task_history: List[Task] = []
        self.retry_queue: deque = deque()
        self.deadletter_queue: List[Task] = []

    def handle_task_failure(self, task: Task) -> bool:
        """Handle task failure with retry logic"""
        task.retry_count += 1

        if task.retry_count <= task.max_retries:
            task.status = TaskStatus.RETRYING
            self.retry_queue.append(task)
            self.failed_tasks[task.task_id] = task.retry_count
            return True
        else:
            # Too many retries
            task.status = TaskStatus.FAILED
            self.deadletter_queue.append(task)
            return False

    def get_retriable_tasks(self) -> List[Task]:
        """Get tasks ready for retry"""
        retriable = []
        temp_queue = deque()

        while self.retry_queue:
            task = self.retry_queue.popleft()
            if task.retry_count < task.max_retries:
                retriable.append(task)
            temp_queue.append(task)

        self.retry_queue = temp_queue
        return retriable

    def get_dead_letter_tasks(self) -> List[Task]:
        """Get tasks that failed permanently"""
        return self.deadletter_queue

    def record_task_history(self, task: Task):
        """Record completed task in history"""
        self.task_history.append(task)


class TaskOrchestrator:
    """Central orchestrator for task management"""

    def __init__(self):
        self.workflows: Dict[str, TaskWorkflow] = {}
        self.tasks: Dict[str, Task] = {}
        self.dependency_resolver = TaskDependencyResolver()
        self.load_balancer = LoadBalancer()
        self.resource_allocator = ResourceAllocator()
        self.fault_tolerance = FaultTolerance()
        self.completed_tasks: Set[str] = set()
        self.lock = threading.RLock()

    def create_workflow(self, workflow_id: str, name: str) -> TaskWorkflow:
        """Create a new workflow"""
        workflow = TaskWorkflow(
            workflow_id=workflow_id,
            name=name
        )
        self.workflows[workflow_id] = workflow
        return workflow

    def add_task_to_workflow(self, workflow_id: str, task: Task):
        """Add task to workflow"""
        with self.lock:
            if workflow_id not in self.workflows:
                return False

            workflow = self.workflows[workflow_id]
            workflow.tasks[task.task_id] = task
            workflow.task_order.append(task.task_id)
            self.tasks[task.task_id] = task
            return True

    def add_task_dependency(self, task_id: str, depends_on: str):
        """Add dependency between tasks"""
        self.dependency_resolver.add_dependency(task_id, depends_on)

    def get_next_executable_tasks(self, workflow_id: str) -> List[Task]:
        """Get next batch of executable tasks"""
        with self.lock:
            if workflow_id not in self.workflows:
                return []

            workflow = self.workflows[workflow_id]
            executable_ids = self.dependency_resolver.get_executable_tasks(
                workflow.tasks,
                self.completed_tasks
            )

            return [workflow.tasks[tid] for tid in executable_ids]

    def assign_task(self, task: Task) -> Optional[str]:
        """Assign task to agent with load balancing"""
        with self.lock:
            agent_id = self.load_balancer.select_agent(task)
            if agent_id:
                task.assigned_agent = agent_id
                task.status = TaskStatus.QUEUED
                self.load_balancer.assign_task(task.task_id, agent_id)
                return agent_id
            return None

    def mark_task_completed(self, task_id: str, result: Dict[str, Any]):
        """Mark task as completed"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                task.result = result
                self.completed_tasks.add(task_id)
                self.fault_tolerance.record_task_history(task)
                self.resource_allocator.deallocate_resources(task_id)

    def mark_task_failed(self, task_id: str, error: str):
        """Mark task as failed and attempt retry"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.error = error
                self.fault_tolerance.handle_task_failure(task)

    def get_orchestration_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow orchestration status"""
        with self.lock:
            if workflow_id not in self.workflows:
                return {}

            workflow = self.workflows[workflow_id]
            total_tasks = len(workflow.tasks)
            completed = sum(
                1 for t in workflow.tasks.values()
                if t.status == TaskStatus.COMPLETED
            )
            failed = sum(
                1 for t in workflow.tasks.values()
                if t.status == TaskStatus.FAILED
            )

            return {
                "workflow_id": workflow_id,
                "total_tasks": total_tasks,
                "completed_tasks": completed,
                "failed_tasks": failed,
                "progress": completed / total_tasks if total_tasks > 0 else 0.0,
                "status": workflow.status,
                "load_balancing": self.load_balancer.get_balancing_metrics(),
                "resource_utilization": self.resource_allocator.get_resource_utilization()
            }
