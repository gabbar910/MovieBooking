#!/usr/bin/env python3
"""
Test script to validate the bug triage system setup
"""

import sys
import os
from typing import List, Tuple

def test_imports() -> Tuple[bool, List[str]]:
    """Test if all required modules can be imported"""
    errors = []
    
    try:
        import requests
        print("✅ requests module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import requests: {e}")
    
    try:
        import openai
        print("✅ openai module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import openai: {e}")
    
    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import python-dotenv: {e}")
    
    try:
        from pydantic import BaseModel
        print("✅ pydantic module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import pydantic: {e}")
    
    return len(errors) == 0, errors

def test_local_imports() -> Tuple[bool, List[str]]:
    """Test if local modules can be imported"""
    errors = []
    
    try:
        from config import Config
        print("✅ config module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import config: {e}")
    
    try:
        from models import GitHubIssue, TriageResult, Priority, Component
        print("✅ models module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import models: {e}")
    
    try:
        from github_adapter import GitHubAdapter
        print("✅ github_adapter module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import github_adapter: {e}")
    
    try:
        from openai_triage_engine import OpenAITriageEngine
        print("✅ openai_triage_engine module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import openai_triage_engine: {e}")
    
    try:
        from triage_orchestrator import TriageOrchestrator
        print("✅ triage_orchestrator module imported successfully")
    except ImportError as e:
        errors.append(f"❌ Failed to import triage_orchestrator: {e}")
    
    return len(errors) == 0, errors

def test_env_file() -> Tuple[bool, List[str]]:
    """Test if .env file exists and has required variables"""
    errors = []
    
    if not os.path.exists('.env'):
        errors.append("❌ .env file not found. Please copy .env.example to .env and configure it.")
        return False, errors
    
    print("✅ .env file found")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'GITHUB_TOKEN',
        'GITHUB_REPO', 
        'OPENAI_API_KEY'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var} not set in .env file")
        elif value.startswith('your_'):
            errors.append(f"❌ {var} still has placeholder value in .env file")
        else:
            print(f"✅ {var} is configured")
    
    return len(errors) == 0, errors

def test_config_validation() -> Tuple[bool, List[str]]:
    """Test configuration validation"""
    errors = []
    
    try:
        from config import Config
        Config.validate()
        print("✅ Configuration validation passed")
        return True, []
    except ValueError as e:
        errors.append(f"❌ Configuration validation failed: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"❌ Unexpected error during configuration validation: {e}")
        return False, errors

def test_model_creation() -> Tuple[bool, List[str]]:
    """Test if models can be created"""
    errors = []
    
    try:
        from models import GitHubIssue, TriageResult, Priority, Component
        
        # Test GitHubIssue creation
        issue = GitHubIssue(
            number=1,
            title="Test issue",
            body="Test body",
            state="open",
            labels=["bug"],
            assignee=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            html_url="https://github.com/test/test/issues/1"
        )
        print("✅ GitHubIssue model creation successful")
        
        # Test TriageResult creation
        result = TriageResult(
            priority=Priority.P2,
            component=Component.FRONTEND,
            suggested_labels=["bug", "frontend"],
            suggested_assignee="test-user",
            confidence_score=0.8,
            reasoning="Test reasoning"
        )
        print("✅ TriageResult model creation successful")
        
        return True, []
        
    except Exception as e:
        errors.append(f"❌ Model creation failed: {e}")
        return False, errors

def main():
    """Run all tests"""
    print("🔍 Testing Bug Triage System Setup")
    print("=" * 40)
    
    all_passed = True
    all_errors = []
    
    # Test imports
    print("\n📦 Testing Package Imports...")
    passed, errors = test_imports()
    all_passed &= passed
    all_errors.extend(errors)
    
    # Test local imports
    print("\n🏠 Testing Local Module Imports...")
    passed, errors = test_local_imports()
    all_passed &= passed
    all_errors.extend(errors)
    
    # Test .env file
    print("\n⚙️ Testing Environment Configuration...")
    passed, errors = test_env_file()
    all_passed &= passed
    all_errors.extend(errors)
    
    # Test config validation (only if .env is properly configured)
    if passed:
        print("\n✅ Testing Configuration Validation...")
        passed, errors = test_config_validation()
        all_passed &= passed
        all_errors.extend(errors)
    
    # Test model creation
    print("\n🏗️ Testing Model Creation...")
    passed, errors = test_model_creation()
    all_passed &= passed
    all_errors.extend(errors)
    
    # Summary
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py --config-check")
        print("2. Run: python main.py --dry-run --limit 5")
        print("3. If satisfied, run: python main.py --execute --limit 5")
        return 0
    else:
        print("❌ Some tests failed. Please fix the following issues:")
        for error in all_errors:
            print(f"   {error}")
        print("\nRefer to README.md for setup instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
