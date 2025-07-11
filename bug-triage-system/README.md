# AI-Powered Bug Triage System

An intelligent automation system that uses AI models (OpenAI GPT or Claude Sonnet) to automatically triage GitHub issues by analyzing content, assigning priorities, categorizing components, and suggesting appropriate team members for assignment.

## Features

- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-4 or Claude Sonnet to analyze issue content and context
- 🔄 **Multiple AI Engines**: Support for both OpenAI and Claude (via Globant API)
- 🏷️ **Automatic Labeling**: Adds priority (P0-P3) and component labels
- 👥 **Smart Assignment**: Suggests appropriate team members based on issue type
- 💬 **Triage Comments**: Adds explanatory comments with AI reasoning
- 🔒 **Safety First**: Dry-run mode by default with manual approval for critical issues
- 📊 **Detailed Reporting**: Comprehensive session summaries and error tracking
- ⚡ **Rate Limited**: Respects API limits with configurable batch processing

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub API    │◄──►│ Triage           │◄──►│   OpenAI API    │
│   (Issues)      │    │ Orchestrator     │    │   (Analysis)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Action Executor  │
                       │ (Labels/Assign)  │
                       └──────────────────┘
```

## Installation

1. **Clone or download the system**

   ```bash
   cd bug-triage-system
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```env
# GitHub Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO=owner/repo-name
GITHUB_API_URL=https://api.github.com

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# Triage Configuration
MAX_ISSUES_PER_RUN=50
DRY_RUN_MODE=true
AUTO_ASSIGN_ENABLED=true
AUTO_LABEL_ENABLED=true

# Team Configuration (comma-separated)
TEAM_MEMBERS=user1,user2,user3
FRONTEND_TEAM=frontend-dev1,frontend-dev2
BACKEND_TEAM=backend-dev1,backend-dev2
INFRA_TEAM=devops1,devops2
```

### Getting API Credentials

#### GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with these permissions:
   - `repo` (Full control of private repositories)
   - `public_repo` (Access public repositories)
3. Copy the token to your `.env` file

#### OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key to your `.env` file

### Claude Integration (Alternative to OpenAI)

The system now supports Claude Sonnet via the Globant API as an alternative to OpenAI. To use Claude:

1. **Set AI Engine**: Add `AI_ENGINE=claude` to your `.env` file
2. **Configure Claude API**: Add the following to your `.env`:

   ```env
   # Claude Configuration (Globant API)
   CLAUDE_API_KEY=your_claude_api_key
   CLAUDE_API_URL=https://api.clients.geai.globant.com/v1/messages
   CLAUDE_MODEL=claude-3-sonnet-20240229
   ```

3. **Test Integration**: Run the Claude-specific test:
   ```bash
   python test_claude_integration.py
   ```

For detailed Claude setup instructions, see [CLAUDE_INTEGRATION.md](CLAUDE_INTEGRATION.md).

## Usage

### Basic Commands

```bash
# Check configuration
python main.py --config-check

# Run in dry-run mode (default - no changes made)
python main.py

# Execute actions on GitHub
python main.py --execute

# Process limited number of issues
python main.py --limit 10

# Verbose logging
python main.py --verbose

# Execute with limit and verbose logging
python main.py --execute --limit 5 --verbose
```

### Triage Process

1. **Fetch Issues**: Retrieves open GitHub issues
2. **AI Analysis**: Each issue is analyzed by OpenAI for:
   - Priority level (P0-P3)
   - Component category (frontend/backend/infra/docs/testing)
   - Suggested labels
   - Recommended assignee
3. **Action Generation**: Creates actions for:
   - Adding priority and component labels
   - Assigning to appropriate team members
   - Adding triage explanation comments
4. **Execution**: Applies changes to GitHub (if not in dry-run mode)

### Priority Levels

- **P0 (Critical)**: Production down, security vulnerabilities, data loss
- **P1 (High)**: Major features broken, significant user impact
- **P2 (Medium)**: Minor feature issues, moderate user impact
- **P3 (Low)**: Enhancements, documentation, nice-to-have features

### Component Categories

- **frontend**: UI/UX issues, client-side bugs, styling problems
- **backend**: API issues, server-side logic, database problems
- **infra**: DevOps, deployment, infrastructure, CI/CD
- **docs**: Documentation issues
- **testing**: Test-related issues
- **unknown**: Cannot determine from available information

## Safety Features

### Dry-Run Mode

- **Default behavior**: No changes are made to GitHub
- **Safe testing**: See what actions would be taken
- **Use `--execute` flag**: To actually apply changes

### Rate Limiting

- **Configurable limits**: `MAX_ISSUES_PER_RUN` setting
- **API respect**: Follows GitHub and OpenAI rate limits
- **Batch processing**: Processes issues in manageable chunks

### Error Handling

- **Graceful failures**: Continues processing if individual issues fail
- **Detailed logging**: Comprehensive error reporting
- **Session tracking**: Full audit trail of all actions

## Example Output

```
2024-01-15 10:30:15 - main - INFO - Starting AI-powered bug triage...
2024-01-15 10:30:16 - github_adapter - INFO - Fetched 5 open issues from owner/repo
2024-01-15 10:30:17 - triage_orchestrator - INFO - Processing issue #123: Login button not working
2024-01-15 10:30:20 - openai_triage_engine - INFO - Successfully analyzed issue #123 - Priority: P1, Component: frontend
2024-01-15 10:30:20 - github_adapter - INFO - [DRY RUN] Would add labels ['P1', 'frontend', 'bug'] to issue #123

Triage Session Summary
=====================
Session ID: 550e8400-e29b-41d4-a716-446655440000
Timestamp: 2024-01-15T10:30:15.123456
Dry Run Mode: True

Issues Processed: 5
Actions Planned: 15
Actions Successful: 15
Actions Failed: 0
Errors: 0

Action Breakdown:
- label: 5
- assign: 3
- comment: 5
```

## Scheduling

For automated triage, you can schedule the system using:

### Cron (Linux/Mac)

```bash
# Run every hour during business hours
0 9-17 * * 1-5 cd /path/to/bug-triage-system && python main.py --execute --limit 20
```

### Windows Task Scheduler

Create a scheduled task that runs:

```cmd
python C:\path\to\bug-triage-system\main.py --execute --limit 20
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify GitHub token has correct permissions
   - Check if token has expired
   - Ensure repository name format is `owner/repo`

2. **OpenAI API Errors**
   - Verify API key is valid
   - Check if you have sufficient credits
   - Ensure model name is correct (e.g., `gpt-4`)

3. **No Issues Found**
   - Check if repository has open issues
   - Verify repository name is correct
   - Ensure token has access to the repository

4. **Rate Limiting**
   - Reduce `MAX_ISSUES_PER_RUN`
   - Add delays between runs
   - Check API usage limits

### Debug Mode

Run with verbose logging to see detailed information:

```bash
python main.py --verbose --config-check
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Considerations

- **API Keys**: Never commit API keys to version control
- **Permissions**: Use minimal required GitHub token permissions
- **Dry-Run**: Always test with dry-run mode first
- **Review**: Manually review AI suggestions for critical issues

## Future Enhancements

- [ ] Jira integration
- [ ] Slack notifications
- [ ] Custom triage rules
- [ ] Machine learning model training
- [ ] Web dashboard
- [ ] Webhook support
- [ ] Multi-repository support
