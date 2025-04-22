# ClaudeBatch

A command-line tool for efficient batch processing with Claude AI, leveraging system prompt caching for cost optimization.

## Features

- Process multiple requests in a single batch
- Cache system prompts to reduce token costs (90% savings after first use)
- Use templates with variable substitution
- Save outputs as properly formatted text files
- Fallback mechanisms for error handling

## Installation

```bash
# Clone the repository
git clone https://github.com/thesubtleties/claudebatch.git
cd claudebatch

# Install dependencies
pip install -r requirements.txt
```

## Setup

1. Create a `.env` file with your API key and settings (or rename the provided `.env.example`):

```
# Copy .env.example to .env and update with your values
ANTHROPIC_API_KEY=your_api_key_here
MODEL=claude-3-7-sonnet-20250219  # Choose your preferred model
MAX_TOKENS=4000
TEMPERATURE=0.2
```

**Note on Models:**

- For better quality, use `claude-3-7-sonnet-20250219`
- For faster, cheaper responses, use `claude-3-5-haiku-20241022`
- The `.env.example` includes both options (uncomment as needed)

2. Create a `system_prompt.txt` file with your system prompt
3. Create a `template.txt` file with your message template (use `{variablename}` for placeholders)

## Usage

```bash
# Basic usage
python batch.py --csv your_variables.csv

# With fallback for error handling - may have issues with emojis, and overall text encoding
python batch.py --csv your_variables.csv --fallback

# Retrieve results from a previous batch
python get_results.py --batch-id msgbatch_your_batch_id
```

## CSV Format

Your CSV should include columns matching the variables in your template:

```csv
title,description
"Binary Search","Binary Search\n\nStandard implementation\nRotated array search\nSearch in 2D matrix"
"Dynamic Programming","Dynamic Programming\n\n1D problems\n2D problems\nKnapsack variations"
```

## Cost Benefits

- **Batch Processing**: Up to 50% cheaper than individual requests
- **System Prompt Caching**: 90% cheaper for cached portions after first use
- Perfect for generating variations of content with the same system instructions

## Requirements

- Python 3.8+
- anthropic Python package
- python-dotenv
- requests

## License

MIT

---

**Note**: This tool is not affiliated with Anthropic. Use responsibly and in accordance with Claude's terms of service.
