#!/usr/bin/env python3
"""
Test script for Claude integration with the bug triage system.
This script tests the Claude API connection and basic functionality.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from claude_triage_engine import ClaudeTriageEngine
from models import GitHubIssue

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_claude_configuration():
    """Test Claude configuration and environment variables"""
    logger.info("Testing Claude configuration...")
    
    required_vars = {
        'CLAUDE_API_KEY': Config.CLAUDE_API_KEY,
        'CLAUDE_API_URL': Config.CLAUDE_API_URL,
        'CLAUDE_MODEL': Config.CLAUDE_MODEL,
        'AI_ENGINE': Config.AI_ENGINE
    }
    
    missing_vars = []
    for var_name, var_value in required_vars.items():
        if not var_value:
            missing_vars.append(var_name)
        else:
            logger.info(f"✓ {var_name}: {var_value}")
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    if Config.AI_ENGINE != "claude":
        logger.warning(f"⚠️  AI_ENGINE is set to '{Config.AI_ENGINE}', expected 'claude'")
        return False
    
    logger.info("✓ Claude configuration looks good!")
    return True

def test_claude_engine_initialization():
    """Test Claude engine initialization"""
    logger.info("Testing Claude engine initialization...")
    
    try:
        engine = ClaudeTriageEngine()
        logger.info("✓ Claude engine initialized successfully")
        return engine
    except Exception as e:
        logger.error(f"❌ Failed to initialize Claude engine: {e}")
        return None

def test_claude_api_call():
    """Test a sample API call to Claude"""
    logger.info("Testing Claude API call with sample issue...")
    
    engine = test_claude_engine_initialization()
    if not engine:
        return False
    
    # Create a sample issue for testing
    sample_issue = GitHubIssue(
        number=123,
        title="Sample Bug: Application crashes on startup",
        body="The application crashes immediately when launched. Error message shows 'NullPointerException in main thread'. This affects all users on Windows 10.",
        labels=["bug"],
        assignee=None,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
    
    try:
        result = engine.analyze_issue(sample_issue)
        
        if result:
            logger.info("✓ Claude API call successful!")
            logger.info(f"  Priority: {result.priority.value}")
            logger.info(f"  Component: {result.component.value}")
            logger.info(f"  Confidence: {result.confidence_score:.2f}")
            logger.info(f"  Reasoning: {result.reasoning}")
            logger.info(f"  Suggested Labels: {result.suggested_labels}")
            logger.info(f"  Suggested Assignee: {result.suggested_assignee}")
            return True
        else:
            logger.error("❌ Claude API call returned no result")
            return False
            
    except Exception as e:
        logger.error(f"❌ Claude API call failed: {e}")
        return False

def test_config_validation():
    """Test configuration validation"""
    logger.info("Testing configuration validation...")
    
    try:
        Config.validate()
        logger.info("✓ Configuration validation passed")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration validation failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting Claude integration tests...")
    logger.info("=" * 50)
    
    tests = [
        ("Configuration", test_claude_configuration),
        ("Engine Initialization", test_claude_engine_initialization),
        ("Config Validation", test_config_validation),
        ("API Call", test_claude_api_call),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running test: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Claude integration is working correctly.")
        return 0
    else:
        logger.error(f"💥 {total - passed} test(s) failed. Please check your configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
