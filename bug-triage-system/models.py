from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Priority(str, Enum):
    P0 = "P0"  # Critical - Production down
    P1 = "P1"  # High - Major feature broken
    P2 = "P2"  # Medium - Minor feature issues
    P3 = "P3"  # Low - Enhancement/Nice to have

class Component(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    INFRA = "infra"
    DOCS = "docs"
    TESTING = "testing"
    UNKNOWN = "unknown"

class GitHubIssue(BaseModel):
    number: int
    title: str
    body: Optional[str]
    state: str
    labels: List[str]
    assignee: Optional[str]
    created_at: str
    updated_at: str
    html_url: str

class TriageResult(BaseModel):
    priority: Priority
    component: Component
    suggested_labels: List[str]
    suggested_assignee: Optional[str]
    confidence_score: float
    reasoning: str

class TriageAction(BaseModel):
    issue_number: int
    action_type: str  # "label", "assign", "comment"
    action_data: dict
    dry_run: bool = True
    executed: bool = False
    execution_result: Optional[str] = None

class TriageSession(BaseModel):
    session_id: str
    timestamp: str
    issues_processed: int
    actions_taken: List[TriageAction]
    errors: List[str]
    dry_run: bool
