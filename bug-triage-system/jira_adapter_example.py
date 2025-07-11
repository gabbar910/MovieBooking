"""
Example Jira Adapter for future integration
This is a template/example for extending the system to support Jira
"""

import requests
import logging
from typing import List, Optional
from models import TriageAction
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraIssue:
    """Jira issue model (example)"""
    def __init__(self, key: str, summary: str, description: str, issue_type: str, 
                 status: str, assignee: Optional[str] = None, labels: List[str] = None):
        self.key = key
        self.summary = summary
        self.description = description
        self.issue_type = issue_type
        self.status = status
        self.assignee = assignee
        self.labels = labels or []

class JiraAdapter:
    """
    Example Jira adapter for future integration
    This demonstrates how the system could be extended to support Jira
    """
    
    def __init__(self):
        # These would be added to Config class
        self.jira_url = "https://your-domain.atlassian.net"
        self.username = "your-email@domain.com"
        self.api_token = "your-jira-api-token"
        self.project_key = "PROJECT"
        
        self.auth = (self.username, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_open_issues(self, limit: int = 50) -> List[JiraIssue]:
        """Fetch open issues from Jira"""
        try:
            # JQL (Jira Query Language) to get open issues
            jql = f"project = {self.project_key} AND status != Done ORDER BY created DESC"
            
            url = f"{self.jira_url}/rest/api/3/search"
            params = {
                "jql": jql,
                "maxResults": limit,
                "fields": "summary,description,issuetype,status,assignee,labels"
            }
            
            response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
            response.raise_for_status()
            
            data = response.json()
            issues = []
            
            for issue_data in data.get("issues", []):
                fields = issue_data["fields"]
                
                issue = JiraIssue(
                    key=issue_data["key"],
                    summary=fields.get("summary", ""),
                    description=fields.get("description", {}).get("content", [{}])[0].get("content", [{}])[0].get("text", "") if fields.get("description") else "",
                    issue_type=fields.get("issuetype", {}).get("name", ""),
                    status=fields.get("status", {}).get("name", ""),
                    assignee=fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                    labels=fields.get("labels", [])
                )
                issues.append(issue)
            
            logger.info(f"Fetched {len(issues)} open issues from Jira project {self.project_key}")
            return issues
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Jira issues: {e}")
            return []
    
    def add_labels(self, issue_key: str, labels: List[str], dry_run: bool = True) -> bool:
        """Add labels to a Jira issue"""
        if dry_run:
            logger.info(f"[DRY RUN] Would add labels {labels} to Jira issue {issue_key}")
            return True
        
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{issue_key}"
            
            # Get current labels first
            response = requests.get(url, headers=self.headers, auth=self.auth, params={"fields": "labels"})
            response.raise_for_status()
            current_labels = [label for label in response.json()["fields"]["labels"]]
            
            # Add new labels
            all_labels = current_labels + labels
            
            data = {
                "fields": {
                    "labels": all_labels
                }
            }
            
            response = requests.put(url, headers=self.headers, auth=self.auth, json=data)
            response.raise_for_status()
            
            logger.info(f"Added labels {labels} to Jira issue {issue_key}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding labels to Jira issue {issue_key}: {e}")
            return False
    
    def assign_issue(self, issue_key: str, assignee: str, dry_run: bool = True) -> bool:
        """Assign a Jira issue to a user"""
        if dry_run:
            logger.info(f"[DRY RUN] Would assign Jira issue {issue_key} to {assignee}")
            return True
        
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/assignee"
            data = {"accountId": assignee}  # In Jira, you need accountId, not username
            
            response = requests.put(url, headers=self.headers, auth=self.auth, json=data)
            response.raise_for_status()
            
            logger.info(f"Assigned Jira issue {issue_key} to {assignee}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error assigning Jira issue {issue_key} to {assignee}: {e}")
            return False
    
    def add_comment(self, issue_key: str, comment: str, dry_run: bool = True) -> bool:
        """Add a comment to a Jira issue"""
        if dry_run:
            logger.info(f"[DRY RUN] Would add comment to Jira issue {issue_key}: {comment[:100]}...")
            return True
        
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment"
            
            # Jira uses Atlassian Document Format (ADF) for comments
            data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }
            
            response = requests.post(url, headers=self.headers, auth=self.auth, json=data)
            response.raise_for_status()
            
            logger.info(f"Added comment to Jira issue {issue_key}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding comment to Jira issue {issue_key}: {e}")
            return False
    
    def execute_action(self, action: TriageAction) -> bool:
        """Execute a triage action on Jira"""
        try:
            # Note: action.issue_number would need to be adapted for Jira keys
            issue_key = f"{self.project_key}-{action.issue_number}"
            
            if action.action_type == "label":
                return self.add_labels(
                    issue_key,
                    action.action_data["labels"],
                    action.dry_run
                )
            elif action.action_type == "assign":
                return self.assign_issue(
                    issue_key,
                    action.action_data["assignee"],
                    action.dry_run
                )
            elif action.action_type == "comment":
                return self.add_comment(
                    issue_key,
                    action.action_data["comment"],
                    action.dry_run
                )
            else:
                logger.error(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing Jira action {action.action_type} for issue {action.issue_number}: {e}")
            return False

# Example usage and integration notes:
"""
To integrate Jira support into the main system:

1. Add Jira configuration to config.py:
   - JIRA_URL
   - JIRA_USERNAME  
   - JIRA_API_TOKEN
   - JIRA_PROJECT_KEY

2. Modify models.py to add JiraIssue model

3. Update triage_orchestrator.py to support multiple adapters:
   - Add jira_adapter alongside github_adapter
   - Modify run_triage_session to handle both GitHub and Jira issues
   - Update action execution to route to appropriate adapter

4. Extend main.py to add Jira-specific command line options:
   - --source github|jira|both
   - --jira-project PROJECT_KEY

5. Update OpenAI prompts to handle Jira-specific fields and workflows

Example command after integration:
python main.py --source both --execute --limit 10
"""

if __name__ == "__main__":
    # Example test (won't work without proper Jira credentials)
    print("This is an example Jira adapter for future integration.")
    print("See the comments at the bottom for integration instructions.")
