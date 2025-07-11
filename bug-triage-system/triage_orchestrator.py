import uuid
import logging
from datetime import datetime
from typing import List, Optional
from config import Config
from models import GitHubIssue, TriageResult, TriageAction, TriageSession, Priority
from github_adapter import GitHubAdapter
from openai_triage_engine import OpenAITriageEngine
from claude_triage_engine import ClaudeTriageEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TriageOrchestrator:
    def __init__(self):
        self.github_adapter = GitHubAdapter()
        
        # Initialize AI engine based on configuration
        if Config.AI_ENGINE == "claude":
            self.ai_engine = ClaudeTriageEngine()
            logger.info("Using Claude AI engine")
        elif Config.AI_ENGINE == "openai":
            self.ai_engine = OpenAITriageEngine()
            logger.info("Using OpenAI engine")
        else:
            raise ValueError(f"Unsupported AI engine: {Config.AI_ENGINE}")
        
        self.dry_run = Config.DRY_RUN_MODE
    
    def run_triage_session(self, limit: Optional[int] = None) -> TriageSession:
        """Run a complete triage session"""
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        logger.info(f"Starting triage session {session_id} (dry_run={self.dry_run})")
        
        session = TriageSession(
            session_id=session_id,
            timestamp=timestamp,
            issues_processed=0,
            actions_taken=[],
            errors=[],
            dry_run=self.dry_run
        )
        
        try:
            # Validate configuration
            Config.validate()
            
            # Fetch open issues
            issues = self.github_adapter.get_open_issues(limit)
            if not issues:
                logger.warning("No open issues found")
                return session
            
            # Process each issue
            for issue in issues:
                try:
                    self._process_issue(issue, session)
                    session.issues_processed += 1
                    
                except Exception as e:
                    error_msg = f"Error processing issue #{issue.number}: {e}"
                    logger.error(error_msg)
                    session.errors.append(error_msg)
            
            # Execute actions
            self._execute_actions(session)
            
            logger.info(f"Triage session {session_id} completed. Processed {session.issues_processed} issues, {len(session.actions_taken)} actions planned")
            
        except Exception as e:
            error_msg = f"Critical error in triage session: {e}"
            logger.error(error_msg)
            session.errors.append(error_msg)
        
        return session
    
    def _process_issue(self, issue: GitHubIssue, session: TriageSession):
        """Process a single issue and generate triage actions"""
        logger.info(f"Processing issue #{issue.number}: {issue.title}")
        
        # Skip if already triaged (has priority label)
        priority_labels = [label for label in issue.labels if label.startswith('P')]
        if priority_labels:
            logger.info(f"Issue #{issue.number} already has priority label: {priority_labels}")
            return
        
        # Analyze with AI
        triage_result = self.ai_engine.analyze_issue(issue)
        if not triage_result:
            logger.warning(f"Failed to analyze issue #{issue.number}")
            return
        
        # Generate actions based on triage result
        actions = self._generate_actions(issue, triage_result)
        session.actions_taken.extend(actions)
        
        # Log triage result
        logger.info(f"Issue #{issue.number} triaged: {triage_result.priority.value}, {triage_result.component.value}, confidence: {triage_result.confidence_score:.2f}")
    
    def _generate_actions(self, issue: GitHubIssue, triage_result: TriageResult) -> List[TriageAction]:
        """Generate actions based on triage result"""
        actions = []
        
        # Prepare labels to add
        new_labels = []
        
        # Add priority label
        new_labels.append(triage_result.priority.value)
        
        # Add component label
        if triage_result.component.value != "unknown":
            new_labels.append(triage_result.component.value)
        
        # Add suggested labels
        for label in triage_result.suggested_labels:
            if label not in issue.labels and label not in new_labels:
                new_labels.append(label)
        
        # Create label action
        if new_labels and Config.AUTO_LABEL_ENABLED:
            actions.append(TriageAction(
                issue_number=issue.number,
                action_type="label",
                action_data={"labels": new_labels},
                dry_run=self.dry_run
            ))
        
        # Create assignment action
        if (Config.AUTO_ASSIGN_ENABLED and 
            triage_result.suggested_assignee and 
            not issue.assignee):
            
            actions.append(TriageAction(
                issue_number=issue.number,
                action_type="assign",
                action_data={"assignee": triage_result.suggested_assignee},
                dry_run=self.dry_run
            ))
        
        # Create triage comment
        comment = self._generate_triage_comment(triage_result)
        actions.append(TriageAction(
            issue_number=issue.number,
            action_type="comment",
            action_data={"comment": comment},
            dry_run=self.dry_run
        ))
        
        return actions
    
    def _generate_triage_comment(self, triage_result: TriageResult) -> str:
        """Generate a triage comment explaining the AI analysis"""
        comment = f"""🤖 **Automated Triage Analysis**

**Priority:** {triage_result.priority.value}
**Component:** {triage_result.component.value}
**Confidence:** {triage_result.confidence_score:.1%}

**Analysis:** {triage_result.reasoning}

---
*This issue has been automatically triaged using AI. Please review and adjust if necessary.*
"""
        return comment
    
    def _execute_actions(self, session: TriageSession):
        """Execute all planned actions"""
        logger.info(f"Executing {len(session.actions_taken)} actions")
        
        for action in session.actions_taken:
            try:
                success = self.github_adapter.execute_action(action)
                action.executed = success
                
                if success:
                    action.execution_result = "Success"
                else:
                    action.execution_result = "Failed"
                    session.errors.append(f"Failed to execute {action.action_type} action for issue #{action.issue_number}")
                    
            except Exception as e:
                error_msg = f"Error executing action for issue #{action.issue_number}: {e}"
                logger.error(error_msg)
                action.executed = False
                action.execution_result = str(e)
                session.errors.append(error_msg)
    
    def get_session_summary(self, session: TriageSession) -> str:
        """Generate a summary of the triage session"""
        successful_actions = sum(1 for action in session.actions_taken if action.executed)
        failed_actions = len(session.actions_taken) - successful_actions
        
        summary = f"""
Triage Session Summary
=====================
Session ID: {session.session_id}
Timestamp: {session.timestamp}
Dry Run Mode: {session.dry_run}

Issues Processed: {session.issues_processed}
Actions Planned: {len(session.actions_taken)}
Actions Successful: {successful_actions}
Actions Failed: {failed_actions}
Errors: {len(session.errors)}

Action Breakdown:
"""
        
        action_types = {}
        for action in session.actions_taken:
            action_types[action.action_type] = action_types.get(action.action_type, 0) + 1
        
        for action_type, count in action_types.items():
            summary += f"- {action_type}: {count}\n"
        
        if session.errors:
            summary += f"\nErrors:\n"
            for error in session.errors[:5]:  # Show first 5 errors
                summary += f"- {error}\n"
            
            if len(session.errors) > 5:
                summary += f"... and {len(session.errors) - 5} more errors\n"
        
        return summary
