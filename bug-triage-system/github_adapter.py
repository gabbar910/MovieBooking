import requests
import json
from typing import List, Optional
from config import Config
from models import GitHubIssue, TriageAction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubAdapter:
    def __init__(self):
        self.token = Config.GITHUB_TOKEN
        self.repo = Config.GITHUB_REPO
        self.api_url = Config.GITHUB_API_URL
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
    
    def get_open_issues(self, limit: int = None) -> List[GitHubIssue]:
        """Fetch open issues from GitHub repository"""
        try:
            url = f"{self.api_url}/repos/{self.repo}/issues"
            params = {
                "state": "open",
                "per_page": limit or Config.MAX_ISSUES_PER_RUN,
                "sort": "created",
                "direction": "desc"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            issues_data = response.json()
            issues = []
            
            for issue_data in issues_data:
                # Skip pull requests (they appear as issues in GitHub API)
                if "pull_request" in issue_data:
                    continue
                
                issue = GitHubIssue(
                    number=issue_data["number"],
                    title=issue_data["title"],
                    body=issue_data.get("body", ""),
                    state=issue_data["state"],
                    labels=[label["name"] for label in issue_data.get("labels", [])],
                    assignee=issue_data["assignee"]["login"] if issue_data.get("assignee") else None,
                    created_at=issue_data["created_at"],
                    updated_at=issue_data["updated_at"],
                    html_url=issue_data["html_url"]
                )
                issues.append(issue)
            
            logger.info(f"Fetched {len(issues)} open issues from {self.repo}")
            return issues
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching issues: {e}")
            return []
    
    def add_labels(self, issue_number: int, labels: List[str], dry_run: bool = True) -> bool:
        """Add labels to an issue"""
        if dry_run:
            logger.info(f"[DRY RUN] Would add labels {labels} to issue #{issue_number}")
            return True
        
        try:
            url = f"{self.api_url}/repos/{self.repo}/issues/{issue_number}/labels"
            data = {"labels": labels}
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Added labels {labels} to issue #{issue_number}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding labels to issue #{issue_number}: {e}")
            return False
    
    def assign_issue(self, issue_number: int, assignee: str, dry_run: bool = True) -> bool:
        """Assign an issue to a user"""
        if dry_run:
            logger.info(f"[DRY RUN] Would assign issue #{issue_number} to {assignee}")
            return True
        
        try:
            url = f"{self.api_url}/repos/{self.repo}/issues/{issue_number}"
            data = {"assignees": [assignee]}
            
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Assigned issue #{issue_number} to {assignee}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error assigning issue #{issue_number} to {assignee}: {e}")
            return False
    
    def add_comment(self, issue_number: int, comment: str, dry_run: bool = True) -> bool:
        """Add a comment to an issue"""
        if dry_run:
            logger.info(f"[DRY RUN] Would add comment to issue #{issue_number}: {comment[:100]}...")
            return True
        
        try:
            url = f"{self.api_url}/repos/{self.repo}/issues/{issue_number}/comments"
            data = {"body": comment}
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Added comment to issue #{issue_number}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding comment to issue #{issue_number}: {e}")
            return False
    
    def execute_action(self, action: TriageAction) -> bool:
        """Execute a triage action"""
        try:
            if action.action_type == "label":
                return self.add_labels(
                    action.issue_number,
                    action.action_data["labels"],
                    action.dry_run
                )
            elif action.action_type == "assign":
                return self.assign_issue(
                    action.issue_number,
                    action.action_data["assignee"],
                    action.dry_run
                )
            elif action.action_type == "comment":
                return self.add_comment(
                    action.issue_number,
                    action.action_data["comment"],
                    action.dry_run
                )
            else:
                logger.error(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing action {action.action_type} for issue #{action.issue_number}: {e}")
            return False
