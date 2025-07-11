# Claude Integration Guide

This document explains how to configure and use the Claude AI engine with the Globant API instead of OpenAI for the bug triage system.

## Overview

The bug triage system now supports two AI engines:

- **OpenAI GPT** (original implementation)
- **Claude Sonnet** (new implementation using Globant API)

## Configuration

### Environment Variables

Add the following variables to your `.env` file:

```bash
# AI Engine Selection
AI_ENGINE=claude  # Set to "claude" or "openai"

# Claude Configuration (Globant API)
CLAUDE_API_KEY=your_claude_api_key
CLAUDE_API_URL=https://api.clients.geai.globant.com/v1/messages
CLAUDE_MODEL=claude-3-sonnet-20240229
```

### Switching Between AI Engines

To switch between AI engines, simply change the `AI_ENGINE` environment variable:

- For Claude: `AI_ENGINE=claude`
- For OpenAI: `AI_ENGINE=openai`

## Claude API Configuration

### API Endpoint

The system is configured to use the Globant Claude API endpoint:

```
https://api.clients.geai.globant.com/v1/messages
```

### Supported Models

The default model is `claude-3-sonnet-20240229`, but you can configure other Claude models by setting the `CLAUDE_MODEL` environment variable.

### Authentication

The Claude engine uses Bearer token authentication. Set your API key in the `CLAUDE_API_KEY` environment variable.

## API Request Format

The Claude engine sends requests in the following format:

```json
{
  "model": "claude-3-sonnet-20240229",
  "max_tokens": 500,
  "temperature": 0.3,
  "messages": [
    {
      "role": "user",
      "content": "Your triage prompt here..."
    }
  ]
}
```

## Response Handling

The Claude engine expects responses in the following format:

```json
{
  "content": [
    {
      "text": "JSON response with triage analysis"
    }
  ]
}
```

## Error Handling

The Claude engine includes comprehensive error handling for:

- Network connectivity issues
- API authentication failures
- Invalid response formats
- JSON parsing errors
- Rate limiting

## Differences from OpenAI Implementation

### Request Format

- Claude uses the `/v1/messages` endpoint
- Different request payload structure
- Uses `anthropic-version` header

### Response Format

- Claude returns content in a different structure
- Response parsing is adapted for Claude's format

### Error Handling

- Additional handling for Claude-specific error codes
- Network timeout handling for the Globant API

## Testing the Integration

1. Set up your environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your Claude API key and other settings
   ```

2. Ensure `AI_ENGINE=claude` in your `.env` file

3. Run the test setup:

   ```bash
   python test_setup.py
   ```

4. Run a triage session:
   ```bash
   python main.py
   ```

## Troubleshooting

### Common Issues

1. **Authentication Error**
   - Verify your `CLAUDE_API_KEY` is correct
   - Check if the API key has proper permissions

2. **Network Timeout**
   - The system uses a 30-second timeout for API calls
   - Check your network connectivity to the Globant API

3. **Invalid Response Format**
   - The Claude engine expects JSON responses
   - Check the logs for raw response content if parsing fails

4. **Model Not Found**
   - Verify the `CLAUDE_MODEL` is supported by the Globant API
   - Check the model name spelling

### Debug Logging

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- Claude API calls have a 30-second timeout
- The system processes issues sequentially to avoid rate limiting
- Consider adjusting `MAX_ISSUES_PER_RUN` based on API limits

## Security Notes

- Store API keys securely in environment variables
- Never commit API keys to version control
- Use different API keys for development and production environments
- The Globant API endpoint uses HTTPS for secure communication

## Migration from OpenAI

To migrate from OpenAI to Claude:

1. Obtain a Claude API key from Globant
2. Update your `.env` file with Claude configuration
3. Set `AI_ENGINE=claude`
4. Test with a small batch of issues first
5. Monitor the results and adjust configuration as needed

The triage logic and output format remain the same, so existing workflows and integrations should continue to work without modification.
