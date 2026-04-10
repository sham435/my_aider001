from __future__ import annotations
import uuid
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    BLOCKED = "blocked"

class TaskNode(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str
    agent: str
    prompt: str
    depends_on: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    output_files: List[str] = Field(default_factory=list)
    artifacts: dict = Field(default_factory=dict)

class DAG(BaseModel):
    goal: str
    nodes: dict[str, TaskNode] = Field(default_factory=dict)

    def add_node(self, node: TaskNode) -> None:
        self.nodes[node.id] = node

    def next_runnable(self) -> Optional[TaskNode]:
        for node in self.nodes.values():
            if node.status != TaskStatus.PENDING:
                continue
            if all(self.nodes[dep].status == TaskStatus.DONE for dep in node.depends_on):
                return node
        return None

    def mark_done(self, node_id: str, files: List[str]) -> None:
        if node_id in self.nodes:
            self.nodes[node_id].status = TaskStatus.DONE
            self.nodes[node_id].output_files = files

    def all_done(self) -> bool:
        return all(n.status == TaskStatus.DONE for n in self.nodes.values())