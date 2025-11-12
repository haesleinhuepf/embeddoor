# Bob - Your Terminal AI Assistant

## Overview

Bob is an AI-powered assistant integrated into the IPython terminal view. When you start a command with `bob`, it sends your natural language request to an OpenAI-compatible LLM server, which generates a Python one-liner for you to review before execution.

## How It Works

1. **Type a command starting with "bob"**: In the terminal input, type `bob` followed by your request
   ```
   bob show the first 10 rows of data
   ```

2. **Bob generates code**: The system sends your request along with information about available variables to the LLM server

3. **Review the suggestion**: The suggested Python code appears in the input field for you to review

4. **Execute or modify**: You can either:
   - Press Enter to execute the suggested code
   - Edit the code before executing
   - Clear it and try again

## Configuration

Configure Bob's LLM server in your `config.ini` file (copy from `config.example.ini`):

```ini
[llm]
# OpenAI-compatible LLM server settings for "bob" terminal assistant
llm_api_url = http://localhost:11434/v1/chat/completions
# llm_api_key will be read from environment variable (default: SCADSAI_API_KEY)
# You can override it here if needed
# llm_api_key = your-key-here
llm_model = llama3.2
```

### Configuration Options

- **llm_api_url**: The endpoint for your OpenAI-compatible API
  - Default: `http://localhost:11434/v1/chat/completions` (Ollama default)
  - Other options: OpenAI, LM Studio, vLLM, etc.

- **llm_api_key**: API key for authentication
  - **Read from environment variable by default**: `SCADSAI_API_KEY` (or `OPENAI_API_KEY` as fallback)
  - Can be overridden in config.ini if needed
  - Falls back to `ollama` if no environment variable is set
  - Set to `none` for servers without authentication

- **llm_model**: The model to use
  - Default: `llama3.2`
  - Examples: `llama3.2`, `codellama`, `gpt-4`, `gpt-3.5-turbo`, etc.

## Example Use Cases

### Data Exploration
```
bob show me column names
bob what's the shape of data
bob display summary statistics
bob show unique values in column 'category'
```

### Data Manipulation
```
bob filter data where age > 30
bob sort by price descending
bob create a new column 'total' as sum of 'quantity' times 'price'
bob remove rows with missing values
```

### Visualization
```
bob plot histogram of age column
bob create scatter plot of price vs quantity
bob show correlation heatmap
```

### Analysis
```
bob calculate mean of numeric columns
bob group by category and sum sales
bob find top 10 most frequent values in status column
```

## Context Awareness

Bob is aware of your current terminal session and has access to:
- All variables currently defined in your session
- DataFrame shapes and column names
- Array dimensions
- Collection lengths
- Imported modules (pandas as pd, numpy as np)

This context helps Bob generate more accurate and relevant code suggestions.

## Tips

1. **Be specific**: Clear requests get better results
   - Good: "bob show first 5 rows sorted by price"
   - Less good: "bob show some data"

2. **Review before executing**: Always check the suggested code before running it

3. **Iterate**: If the suggestion isn't quite right, you can edit it or ask bob again

4. **Use familiar terms**: Bob understands common data analysis terminology

5. **Start simple**: Test with basic commands first to understand Bob's capabilities

## Troubleshooting

### Bob doesn't respond
- Check that your LLM server is running (e.g., `ollama serve` for Ollama)
- Verify the `llm_api_url` in your config.ini
- Check terminal output for error messages

### Wrong or incomplete suggestions
- Try rephrasing your request more specifically
- Check if the necessary variables exist in your session
- Verify your LLM model supports code generation

### Connection errors
- Ensure the LLM server is accessible at the configured URL
- Check firewall settings if using a remote server
- Verify API key if using authenticated services

## Setting Up Ollama (Recommended for Local Use)

1. Install Ollama: https://ollama.ai/
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Start Ollama server (usually starts automatically)
4. Use the default configuration in `config.ini`

## Using with OpenAI

Set environment variable:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

Configure in `config.ini`:
```ini
[llm]
llm_api_url = https://api.openai.com/v1/chat/completions
# API key will be read from OPENAI_API_KEY environment variable
llm_model = gpt-4
```

Or override with explicit key:
```ini
[llm]
llm_api_url = https://api.openai.com/v1/chat/completions
llm_api_key = sk-your-actual-api-key-here
llm_model = gpt-4
```

## Environment Variables

Bob reads the API key from environment variables in this order:
1. **config.ini** (if `llm_api_key` is explicitly set)
2. **SCADSAI_API_KEY** environment variable
3. **OPENAI_API_KEY** environment variable (fallback)
4. **"ollama"** (final fallback for local servers)

### Setting Environment Variables

**Windows PowerShell:**
```powershell
# Temporary (current session only)
$env:SCADSAI_API_KEY = "your-api-key-here"

# Permanent (for your user account)
[System.Environment]::SetEnvironmentVariable('SCADSAI_API_KEY', 'your-api-key-here', 'User')
```

**Linux/Mac:**
```bash
# Temporary (current session)
export SCADSAI_API_KEY="your-api-key-here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export SCADSAI_API_KEY="your-api-key-here"' >> ~/.bashrc
```

## Privacy Note

When using Bob, your prompts and variable context are sent to the configured LLM server. For sensitive data:
- Use a local LLM (like Ollama) instead of cloud services
- Be mindful of what information might be exposed in variable names and types
- Review generated code before execution
- Keep API keys secure using environment variables instead of config files
