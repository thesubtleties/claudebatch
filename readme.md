# Learning Resource Generator - Quick Start Guide

This guide will help you get started with the Learning Resource Generator, an MCP server that helps you create structured learning materials using Claude batch processing.

## Prerequisites

- Python 3.8+ installed
- ClaudeBatch repository cloned and dependencies installed
- Anthropic API key set in your `.env` file

## Starting the MCP Server

Run the Learning Resource Generator script to start the MCP server:

```bash
python learning_resource_generator.py
```

This starts the MCP server using stdio transport, which allows you to connect to it from an MCP client like Claude Desktop.

## Connecting from Claude Desktop

### Option 1: Direct Connection (Local Python)

1. Open Claude Desktop
2. Navigate to Settings
3. Go to the MCP section
4. Click "Add Server" and select "stdio"
5. Enter the command: `python /path/to/your/learning_resource_generator.py`
6. Name your server (e.g., "Learning Resource Generator")
7. Click "Add"

### Option 2: Docker + WSL Connection (Windows)

For Windows users who want to run the Learning Resource Generator through Docker and WSL:

1. Ensure Docker and WSL are installed and configured on your Windows machine
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
4. Restart Claude Desktop
5. The Learning Resource Generator should now appear in your MCP servers list

## Using the Learning Resource Generator with Claude

One of the great advantages of using the MCP-based Learning Resource Generator is that Claude naturally understands how to work with it. Once you've connected the MCP server to Claude Desktop:

1. **No need for complex commands** - Simply describe what you want to create in natural language
2. **Claude understands the available tools** - Claude will recommend the appropriate tools at each step
3. **Guided workflow** - Claude will walk you through the process from start to finish

For example, instead of having to remember exact command syntax, you can simply say:

```
I'd like to create learning resources about Python for beginners. Can you help me?
```

Claude will then guide you through the process, suggesting appropriate tools and helping you structure your content in a conversational way.

## Workflow Walkthrough

### Step 1: Define Your Subject

Start by discussing the subject you want to create learning materials for with Claude. For example:

```
I'd like to create a learning resource about Python for Data Science.
```

### Step 2: Create a Learning Structure

Use the `create_learning_resource_structure` tool to define the structure of your learning resource:

```
create_learning_resource_structure(
    subject="Python for Data Science",
    main_topics=[
        "Getting Started with Python",
        "Data Manipulation with Pandas",
        "Data Visualization with Matplotlib",
        "Statistical Analysis with SciPy"
    ]
)
```

For more complex structures, you can add subtopics:

```
create_learning_resource_structure(
    subject="Python for Data Science",
    main_topics=[
        "Getting Started with Python",
        "Data Manipulation with Pandas",
        "Data Visualization with Matplotlib",
        "Statistical Analysis with SciPy"
    ],
    subtopics={
        "Getting Started with Python": [
            "Installing Python and Required Libraries",
            "Basic Python Syntax for Data Science",
            "Working with Jupyter Notebooks"
        ],
        "Data Manipulation with Pandas": [
            "Loading Data from Different Sources",
            "Data Cleaning and Preprocessing",
            "Advanced Indexing and Selection"
        ]
    }
)
```

### Step 3: Generate a System Prompt Template

Use the `generate_system_prompt_template` tool to create a system prompt that will guide Claude in generating consistent learning materials:

```
generate_system_prompt_template(subject="Python for Data Science")
```

### Step 4: Save the System Prompt

Review the generated system prompt and save it to the system_prompt.txt file:

```
update_system_prompt(content="...")
```

### Step 5: Generate a Request Template

Create a template for your requests to Claude:

```
generate_template(subject="Python for Data Science")
```

### Step 6: Save the Template

Save the template to the template.txt file:

```
update_template(content="...")
```

### Step 7: Create Variables CSV

Create a variables.csv file with your topics:

```
create_variables_csv(
    title="Python for Data Science",
    topics=[
        "Getting Started with Python",
        "Data Manipulation with Pandas",
        "Data Visualization with Matplotlib",
        "Statistical Analysis with SciPy"
    ]
)
```

### Step 8: Run Batch Processing

Start the batch processing to generate your learning resources:

```
run_batch_processing()
```

This will submit a batch request to Claude API. The output will include a batch ID.

### Step 9: Check Results

Once processing is complete, check the results using the batch ID:

```
check_batch_results(batch_id="msgbatch_your_batch_id")
```

Your generated learning resources will be saved in the `responses` directory, with one file per topic.

## Tips for Best Results

1. **Be Specific**: The more specific you are about your subject and topics, the better the generated content will be.

2. **Review Prompts**: Take time to review and refine the system prompt and template before running the batch processing.

3. **Start Small**: For your first attempt, start with a small number of topics to see how the process works.

4. **Customize System Prompts**: Feel free to edit the generated system prompts to tailor the style and format of your learning resources.

5. **Add Descriptions**: When creating your variables.csv, you can optionally add descriptions for each topic to guide Claude in generating more targeted content.

## Troubleshooting

- **Connection Issues**: Make sure your MCP server is running before trying to connect from Claude Desktop.

- **Batch Processing Errors**: Check that your API key is valid and you have sufficient quota.

- **Missing Files**: Ensure that system_prompt.txt, template.txt, and variables.csv files exist before running batch processing.

- **Formatting Issues**: If the output isn't formatted correctly, try adjusting your system prompt to provide more specific formatting instructions.

## Example: Creating a Web Development Learning Resource

Here's an example workflow for creating a web development learning resource:

```
# Step 1: Define the structure
create_learning_resource_structure(
    subject="Modern Web Development",
    main_topics=[
        "HTML5 Essentials",
        "CSS3 and Responsive Design",
        "JavaScript Fundamentals",
        "Frontend Frameworks"
    ],
    subtopics={
        "HTML5 Essentials": [
            "Semantic HTML",
            "Forms and Validation",
            "Accessibility Best Practices"
        ],
        "CSS3 and Responsive Design": [
            "Flexbox and Grid Layouts",
            "CSS Variables and Custom Properties",
            "Media Queries and Breakpoints"
        ]
    }
)

# Step 2: Generate the system prompt
generate_system_prompt_template(subject="Modern Web Development")

# Step 3: Save the system prompt
update_system_prompt(content="...")

# Step 4: Generate the template
generate_template(subject="Modern Web Development")

# Step 5: Save the template
update_template(content="...")

# Step 6: Create the variables CSV
create_variables_csv(
    title="Modern Web Development",
    topics=[
        "HTML5 Essentials",
        "CSS3 and Responsive Design",
        "JavaScript Fundamentals",
        "Frontend Frameworks"
    ]
)

# Step 7: Run batch processing
run_batch_processing()

# Step 8: Check results once the batch is complete
check_batch_results(batch_id="msgbatch_your_batch_id")
```

Happy learning resource generation!
