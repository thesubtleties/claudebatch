# ClaudeBatch

A versatile command-line tool for efficient batch processing with Claude AI, leveraging system prompt caching for cost optimization. Now featuring an MCP (Model Context Protocol) server for creating structured learning resources.

## Features

- Process multiple requests in a single batch
- Cache system prompts to reduce token costs (90% savings after first use)
- Use templates with variable substitution
- Save outputs as properly formatted text files
- Fallback mechanisms for error handling
- **NEW**: Learning Resource Generator via MCP integration

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

## Basic Usage

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

## Using the Learning Resource Generator (MCP Server)

ClaudeBatch now includes an MCP server that helps you create structured learning resources. This feature leverages the Model Context Protocol to provide an interactive way to generate educational content.

### Starting the MCP Server

To use the Learning Resource Generator:

1. Ensure you have set up your `.env` file with your Anthropic API key
2. Start the MCP server:

```bash
# Using stdio transport (recommended for local use)
python learning_resource_generator.py
```

3. Connect the MCP server to an MCP client like Claude Desktop

#### Docker Option (Windows with WSL)

You can also run the Learning Resource Generator using Docker and WSL on Windows:

1. Build the Docker image:

```bash
docker build -t mcp/learning-generator .
```

2. Create a `claude_desktop_config.json` file in `C:\Users\YourUser\AppData\Roaming\Claude\` with the following content:

```json
{
  "mcpServers": {
    "learningGenerator": {
      "command": "wsl",
      "args": [
        "docker",
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/path/to/your/folder/.env",
        "-v",
        "/path/to/your/folder:/data",
        "mcp/learning-generator"
      ]
    }
  }
}
```

3. Replace `/path/to/your/folder` with the actual path to your project folder containing the `.env` file
4. Restart Claude Desktop to load the configuration

### Workflow

The Learning Resource Generator provides a structured workflow:

1. Discuss the subject you want to create learning materials for
2. Create a learning structure with main topics and subtopics using `create_learning_resource_structure`
3. Generate a system prompt template using `generate_system_prompt_template`
4. Update the system_prompt.txt file using `update_system_prompt`
5. Create a template using `generate_template`
6. Update the template.txt file using `update_template`
7. Create a variables.csv file using `create_variables_csv`
8. Run the batch processing using `run_batch_processing`
9. Check the results using `check_batch_results`

### Using the Learning Resource Generator with Claude

The Learning Resource Generator is designed to work naturally with Claude AI. Once connected:

1. Simply tell Claude what subject you'd like to create learning resources for
2. Claude will understand how to use the available MCP tools and guide you through the process
3. You can communicate with Claude in plain text - no need to memorize command structures

For example, you can just say: "I'd like to create learning resources about Python for beginners" and Claude will help you structure the topics and generate the content using the available MCP tools.

Claude will walk you through each step of the process, from structuring your learning resources to running the batch processing.

### Example Commands

Within your MCP client (like Claude Desktop), you can use these tools:

```
create_learning_resource_structure(subject="Data Structures and Algorithms", main_topics=["Arrays", "Linked Lists", "Trees", "Graphs"])

generate_system_prompt_template(subject="Data Structures and Algorithms")

update_system_prompt(content="Your generated system prompt here")

generate_template(subject="Data Structures and Algorithms")

update_template(content="Your generated template here")

create_variables_csv(title="Data Structures and Algorithms", topics=["Arrays", "Linked Lists", "Trees", "Graphs"])

run_batch_processing()

check_batch_results(batch_id="msgbatch_your_batch_id")
```

### Output

The Learning Resource Generator creates structured, well-formatted learning materials saved in the `responses` directory. Each topic gets its own markdown file with consistent formatting based on your system prompt template.

## Cost Benefits

- **Batch Processing**: Up to 50% cheaper than individual requests
- **System Prompt Caching**: 90% cheaper for cached portions after first use
- Perfect for generating variations of content with the same system instructions

## Requirements

- Python 3.8+
- anthropic Python package
- python-dotenv
- requests
- mcp (for the Learning Resource Generator)

## License

MIT

---

**Note**: This tool is not affiliated with Anthropic. Use responsibly and in accordance with Claude's terms of service.
