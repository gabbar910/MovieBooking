#!/usr/bin/env python3
"""
AI-Powered Bug Triage System
Automatically triages GitHub issues using OpenAI analysis
"""

import argparse
import sys
import logging
from config import Config
from triage_orchestrator import TriageOrchestrator

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Bug Triage System for GitHub Issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --dry-run                    # Run in dry-run mode (default)
  python main.py --execute                    # Execute actions on GitHub
  python main.py --limit 10                   # Process only 10 issues
  python main.py --execute --limit 5          # Execute actions on 5 issues
  python main.py --verbose                    # Enable verbose logging
        """
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute actions on GitHub (default is dry-run mode)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no actual changes to GitHub)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit the number of issues to process'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--config-check',
        action='store_true',
        help='Check configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Configuration check
        if args.config_check:
            logger.info("Checking configuration...")
            Config.validate()
            logger.info("✅ Configuration is valid")
            
            # Display configuration summary
            print("\nConfiguration Summary:")
            print(f"GitHub Repo: {Config.GITHUB_REPO}")
            print(f"OpenAI Model: {Config.OPENAI_MODEL}")
            print(f"Max Issues Per Run: {Config.MAX_ISSUES_PER_RUN}")
            print(f"Auto Label Enabled: {Config.AUTO_LABEL_ENABLED}")
            print(f"Auto Assign Enabled: {Config.AUTO_ASSIGN_ENABLED}")
            print(f"Team Members: {len(Config.TEAM_MEMBERS)}")
            print(f"Frontend Team: {len(Config.FRONTEND_TEAM)}")
            print(f"Backend Team: {len(Config.BACKEND_TEAM)}")
            print(f"Infra Team: {len(Config.INFRA_TEAM)}")
            return 0
        
        # Validate configuration
        Config.validate()
        
        # Determine dry-run mode
        if args.execute and args.dry_run:
            logger.error("Cannot specify both --execute and --dry-run")
            return 1
        
        # Override dry-run mode if --execute is specified
        if args.execute:
            Config.DRY_RUN_MODE = False
            logger.info("Running in EXECUTE mode - changes will be made to GitHub")
        else:
            Config.DRY_RUN_MODE = True
            logger.info("Running in DRY-RUN mode - no changes will be made to GitHub")
        
        # Create orchestrator and run triage
        orchestrator = TriageOrchestrator()
        
        logger.info("Starting AI-powered bug triage...")
        session = orchestrator.run_triage_session(limit=args.limit)
        
        # Display results
        summary = orchestrator.get_session_summary(session)
        print(summary)
        
        # Return appropriate exit code
        if session.errors:
            logger.warning(f"Triage completed with {len(session.errors)} errors")
            return 1
        else:
            logger.info("Triage completed successfully")
            return 0
            
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("Please check your .env file and ensure all required variables are set")
        return 1
        
    except KeyboardInterrupt:
        logger.info("Triage interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
