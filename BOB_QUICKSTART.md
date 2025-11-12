# Quick Start: Using Bob in Terminal

## Setup (One-time)

1. **Set API Key** (if using SCADS.AI or OpenAI):
   ```powershell
   # Windows PowerShell
   $env:SCADSAI_API_KEY = "your-api-key-here"
   
   # To make it permanent, add to your PowerShell profile
   [System.Environment]::SetEnvironmentVariable('SCADSAI_API_KEY', 'your-api-key-here', 'User')
   ```
   
   Or for local Ollama (no API key needed):
   - Download from https://ollama.ai/
   - Install and it will start automatically
   - Pull a model: `ollama pull llama3.2`

2. **Configure embeddoor**:
   ```bash
   cp config.example.ini config.ini
   ```
   
   For SCADS.AI (default):
   ```ini
   [llm]
   llm_api_url = https://llm.scads.ai/v1
   # API key read from SCADSAI_API_KEY environment variable
   llm_model = llama3.2
   ```
   
   For local Ollama:
   ```ini
   [llm]
   llm_api_url = http://localhost:11434/v1/chat/completions
   llm_model = llama3.2
   ```

3. **Install requirements** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

## Using Bob

1. **Start embeddoor**:
   ```bash
   embeddoor
   ```

2. **Open IPython Terminal view** in the app

3. **Type "bob" commands**:
   ```
   bob show first 5 rows
   ```

4. **Review the suggested code** that appears in the input field

5. **Press Enter** to execute, or edit first

## Example Session

```
In [1]: bob show me the column names
💡 Bob suggests: data.columns.tolist()

In [2]: data.columns.tolist()
['id', 'name', 'age', 'category', 'price']

In [3]: bob filter data where age is greater than 30
💡 Bob suggests: data[data['age'] > 30]

In [4]: data[data['age'] > 30]
     id    name  age category  price
5   106   Alice   35   Premium   99.99
8   109   Bob     42   Standard  49.99
...

In [5]: bob show summary statistics
💡 Bob suggests: data.describe()

In [6]: data.describe()
              age        price
count   100.000000   100.000000
mean     35.500000    74.250000
std      12.234567    25.678901
...
```

## Tips

- ✅ Be specific: "show first 10 rows sorted by price descending"
- ✅ Use column names: "filter data where category equals Premium"
- ✅ Common operations: "calculate mean of age", "count unique values"
- ✅ Always review: Check the suggested code before running

## Troubleshooting

**Bob doesn't respond?**
- Check API key: `echo $env:SCADSAI_API_KEY` (should show your key)
- Or if using Ollama: Make sure it's running with `ollama serve`
- Check if model is available: `ollama list` (for Ollama)
- Verify config.ini has correct llm_api_url setting

**Wrong suggestions?**
- Try being more specific in your request
- Check that variables exist (type `data` to see if DataFrame is loaded)
- Edit the suggestion before running

That's it! Start asking Bob to help with your data analysis. 🤖
