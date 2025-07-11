import json
import logging
import requests
from typing import Optional
from config import Config
from models import GitHubIssue, TriageResult, Priority, Component

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClaudeTriageEngine:
    def __init__(self):
        self.api_key = Config.CLAUDE_API_KEY
        self.api_url = Config.CLAUDE_API_URL
        self.model = Config.CLAUDE_MODEL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "anthropic-version": "2023-06-01"
        }
    
    def _build_triage_prompt(self, issue: GitHubIssue) -> str:
        """Build the prompt for AI triage analysis"""
        
        team_info = {
            "frontend": Config.FRONTEND_TEAM,
            "backend": Config.BACKEND_TEAM,
            "infra": Config.INFRA_TEAM,
            "all_members": Config.TEAM_MEMBERS
        }
        
        prompt = f"""
You are an expert software engineering triage assistant. Analyze the following GitHub issue and provide a structured triage recommendation.

ISSUE DETAILS:
Title: {issue.title}
Body: {issue.body or "No description provided"}
Current Labels: {', '.join(issue.labels) if issue.labels else "None"}
Current Assignee: {issue.assignee or "Unassigned"}

TEAM INFORMATION:
Frontend Team: {', '.join(team_info['frontend']) if team_info['frontend'] else "Not configured"}
Backend Team: {', '.join(team_info['backend']) if team_info['backend'] else "Not configured"}
Infrastructure Team: {', '.join(team_info['infra']) if team_info['infra'] else "Not configured"}
All Team Members: {', '.join(team_info['all_members']) if team_info['all_members'] else "Not configured"}

TRIAGE CRITERIA:
Priority Levels:
- P0 (Critical): Production down, security vulnerabilities, data loss
- P1 (High): Major features broken, significant user impact
- P2 (Medium): Minor feature issues, moderate user impact
- P3 (Low): Enhancements, documentation, nice-to-have features

Component Categories:
- frontend: UI/UX issues, client-side bugs, styling problems
- backend: API issues, server-side logic, database problems
- infra: DevOps, deployment, infrastructure, CI/CD
- docs: Documentation issues
- testing: Test-related issues
- unknown: Cannot determine from available information

RESPONSE FORMAT:
Provide your analysis as a valid JSON object with the following structure:
{{
    "priority": "P0|P1|P2|P3",
    "component": "frontend|backend|infra|docs|testing|unknown",
    "suggested_labels": ["label1", "label2"],
    "suggested_assignee": "username or null",
    "confidence_score": 0.0-1.0,
    "reasoning": "Brief explanation of your analysis"
}}

IMPORTANT GUIDELINES:
1. Be conservative with P0/P1 assignments - only for truly critical issues
2. Suggest assignee only if you can clearly match the issue to a team member's expertise
3. Include relevant labels like "bug", "enhancement", "security", "performance", etc.
4. Confidence score should reflect how certain you are about the classification
5. Keep reasoning concise but informative

Analyze the issue and respond with only the JSON object:
"""
        return prompt
    
    def analyze_issue(self, issue: GitHubIssue) -> Optional[TriageResult]:
        """Analyze an issue using Claude and return triage recommendations"""
        try:
            prompt = self._build_triage_prompt(issue)
            
            # Prepare the request payload for Claude API
            payload = {
                "model": self.model,
                "max_tokens": 500,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Claude API request failed with status {response.status_code}: {response.text}")
                return None
            
            response_data = response.json()
            
            # Extract the content from Claude's response
            if "content" in response_data and len(response_data["content"]) > 0:
                response_text = response_data["content"][0]["text"].strip()
            else:
                logger.error(f"Unexpected response format from Claude API: {response_data}")
                return None
            
            # Clean up the response to ensure it's valid JSON
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse the JSON response
            triage_data = json.loads(response_text)
            
            # Validate and create TriageResult
            result = TriageResult(
                priority=Priority(triage_data["priority"]),
                component=Component(triage_data["component"]),
                suggested_labels=triage_data.get("suggested_labels", []),
                suggested_assignee=triage_data.get("suggested_assignee"),
                confidence_score=float(triage_data.get("confidence_score", 0.5)),
                reasoning=triage_data.get("reasoning", "No reasoning provided")
            )
            
            logger.info(f"Successfully analyzed issue #{issue.number} - Priority: {result.priority}, Component: {result.component}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response for issue #{issue.number}: {e}")
            logger.error(f"Raw response: {response_text}")
            return None
            
        except requests.RequestException as e:
            logger.error(f"Network error when calling Claude API for issue #{issue.number}: {e}")
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing issue #{issue.number}: {e}")
            return None
    
    def _validate_assignee(self, assignee: str) -> bool:
        """Validate if the suggested assignee is in the team"""
        if not assignee:
            return False
        
        all_team_members = (
            Config.TEAM_MEMBERS + 
            Config.FRONTEND_TEAM + 
            Config.BACKEND_TEAM + 
            Config.INFRA_TEAM
        )
        
        return assignee in all_team_members
    
    def get_team_member_for_component(self, component: Component) -> Optional[str]:
        """Get a suitable team member for a given component"""
        team_mapping = {
            Component.FRONTEND: Config.FRONTEND_TEAM,
            Component.BACKEND: Config.BACKEND_TEAM,
            Component.INFRA: Config.INFRA_TEAM,
        }
        
        team = team_mapping.get(component, Config.TEAM_MEMBERS)
        return team[0] if team else None
