import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Claude Configuration
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    CLAUDE_API_URL = os.getenv("CLAUDE_API_URL", "https://api.clients.geai.globant.com/v1/messages")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    
    # AI Engine Selection
    AI_ENGINE = os.getenv("AI_ENGINE", "claude")  # "openai" or "claude"
    
    # Triage Configuration
    MAX_ISSUES_PER_RUN = int(os.getenv("MAX_ISSUES_PER_RUN", "50"))
    DRY_RUN_MODE = os.getenv("DRY_RUN_MODE", "true").lower() == "true"
    AUTO_ASSIGN_ENABLED = os.getenv("AUTO_ASSIGN_ENABLED", "true").lower() == "true"
    AUTO_LABEL_ENABLED = os.getenv("AUTO_LABEL_ENABLED", "true").lower() == "true"
    
    # Team Configuration
    TEAM_MEMBERS = os.getenv("TEAM_MEMBERS", "").split(",") if os.getenv("TEAM_MEMBERS") else []
    FRONTEND_TEAM = os.getenv("FRONTEND_TEAM", "").split(",") if os.getenv("FRONTEND_TEAM") else []
    BACKEND_TEAM = os.getenv("BACKEND_TEAM", "").split(",") if os.getenv("BACKEND_TEAM") else []
    INFRA_TEAM = os.getenv("INFRA_TEAM", "").split(",") if os.getenv("INFRA_TEAM") else []
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = ["GITHUB_TOKEN", "GITHUB_REPO"]
        
        # Check AI engine specific requirements
        if cls.AI_ENGINE == "openai":
            required_vars.append("OPENAI_API_KEY")
        elif cls.AI_ENGINE == "claude":
            required_vars.append("CLAUDE_API_KEY")
        else:
            raise ValueError(f"Invalid AI_ENGINE value: {cls.AI_ENGINE}. Must be 'openai' or 'claude'")
        
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
