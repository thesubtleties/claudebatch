import os
import csv
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any

from mcp.server.fastmcp import FastMCP, Context

# Create our MCP server
app = FastMCP(
    "LearningResourceGenerator",
    instructions="""
    This MCP server helps create structured learning resources using Claude batch processing.
    
    Workflow:
    1. Discuss the subject you want to create learning materials for
    2. Use create_learning_resource_structure to design an outline
    3. Use generate_system_prompt_template to create a system prompt
    4. Use update_system_prompt to save it to file
    5. Use generate_template to create a request template
    6. Use update_template to save it to file
    7. Use create_variables_csv to generate the variables CSV
    8. Use run_batch_processing to start the batch job
    9. Use check_batch_results to retrieve the results
    
    Example: "I want to create learning resources about JavaScript fundamentals. Can you help me organize the topics and create the necessary files for batch processing?"
    """,
)

# Define the base directory for file operations
# In Docker, we'll use /data as the mounted volume
DATA_DIR = "/data"
# App directory is where the Python scripts are located
APP_DIR = "/app"

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)


@app.tool()
def welcome() -> str:
    """Get started with the Learning Resource Generator."""
    return """
    # Welcome to the Learning Resource Generator!
    
    This MCP server helps you create structured learning resources using Claude batch processing.
    
    ## Workflow
    
    1. **Discuss the subject** you want to create learning materials for
    2. **Create a learning structure** with main topics and subtopics using `create_learning_resource_structure`
    3. **Generate a system prompt** for your subject using `generate_system_prompt_template`
    4. **Update the system_prompt.txt file** using `update_system_prompt`
    5. **Create a template** using `generate_template`
    6. **Update the template.txt file** using `update_template`
    7. **Create a variables.csv file** using `create_variables_csv`
    8. **Run the batch processing** using `run_batch_processing`
    9. **Check the results** using `check_batch_results`
    
    Let's get started! What subject would you like to create learning resources for?
    """


# RESOURCES: Allow reading files from the data directory
@app.resource("file://{path}")
def read_file(path: str) -> str:
    """Read a file from the data directory.

    Args:
        path: The path to the file, relative to the data directory
    """
    # Ensure the path doesn't try to escape the data directory
    safe_path = os.path.normpath(os.path.join(DATA_DIR, path))
    if not safe_path.startswith(DATA_DIR):
        raise ValueError(
            f"Access denied: Cannot access paths outside {DATA_DIR}"
        )

    try:
        with open(safe_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File {path} not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@app.resource("directory://{path}")
def list_directory(path: str = "") -> str:
    """List files in the data directory.

    Args:
        path: The directory path to list, relative to the data directory
    """
    # Ensure the path doesn't try to escape the data directory
    safe_path = os.path.normpath(os.path.join(DATA_DIR, path))
    if not safe_path.startswith(DATA_DIR):
        raise ValueError(
            f"Access denied: Cannot access paths outside {DATA_DIR}"
        )

    try:
        if not os.path.isdir(safe_path):
            return f"Error: {path} is not a directory"

        files = os.listdir(safe_path)
        result = []

        for file in files:
            full_path = os.path.join(safe_path, file)
            file_type = "Directory" if os.path.isdir(full_path) else "File"
            size = (
                os.path.getsize(full_path)
                if os.path.isfile(full_path)
                else "-"
            )
            result.append(f"{file} ({file_type}, {size} bytes)")

        return f"Contents of {path or 'root directory'}:\n" + "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# TOOLS: Update system prompt, template, and variables
@app.tool()
def update_system_prompt(content: str) -> str:
    """Update the system_prompt.txt file with new content.

    Args:
        content: The new system prompt content
    """
    file_path = os.path.join(DATA_DIR, "system_prompt.txt")

    try:
        with open(file_path, "w") as f:
            f.write(content)

        return f"Successfully updated system_prompt.txt ({len(content)} characters)"
    except Exception as e:
        return f"Error updating system prompt: {str(e)}"


@app.tool()
def update_template(content: str) -> str:
    """Update the template.txt file with new content.

    Args:
        content: The new template content
    """
    file_path = os.path.join(DATA_DIR, "template.txt")

    try:
        with open(file_path, "w") as f:
            f.write(content)

        return f"Successfully updated template.txt ({len(content)} characters)"
    except Exception as e:
        return f"Error updating template: {str(e)}"


@app.tool()
def create_variables_csv(
    title: str, topics: List[str], descriptions: List[str] = None
) -> str:
    """Create a variables.csv file with a title and list of topics.

    Args:
        title: The main title for the learning resource
        topics: List of topics to include
        descriptions: Optional list of descriptions for each topic
    """
    file_path = os.path.join(DATA_DIR, "variables.csv")

    try:
        # If descriptions is not provided, use empty strings
        if descriptions is None:
            descriptions = [""] * len(topics)

        # Ensure descriptions and topics have the same length
        if len(descriptions) != len(topics):
            return f"Error: Number of topics ({len(topics)}) must match number of descriptions ({len(descriptions)})"

        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(["title", "description"])

            # Write main title and full description
            full_description = f"{title}\n\n" + "\n".join(topics)
            writer.writerow([title, full_description])

            # Optionally write individual topics
            for i, topic in enumerate(topics):
                if descriptions[i]:
                    writer.writerow([topic, descriptions[i]])

        return (
            f"Successfully created variables.csv with {len(topics) + 1} rows"
        )
    except Exception as e:
        return f"Error creating variables CSV: {str(e)}"


@app.tool()
def run_batch_processing() -> str:
    """Run the batch.py script to start Claude batch processing.

    This will execute the batch.py script with the necessary arguments.
    """
    try:
        # Get environment variables
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("MODEL", "claude-3-opus-20240229")
        max_tokens = os.getenv("MAX_TOKENS", "4000")
        temperature = os.getenv("TEMPERATURE", "0.2")

        # Construct the command
        cmd = [
            "python",
            os.path.join(APP_DIR, "batch.py"),
            "--csv",
            os.path.join(DATA_DIR, "variables.csv"),
            "--system",
            os.path.join(DATA_DIR, "system_prompt.txt"),
            "--template",
            os.path.join(DATA_DIR, "template.txt"),
            "--output-dir",
            os.path.join(DATA_DIR, "responses"),
        ]

        # Add optional arguments if environment variables are set
        if model:
            cmd.extend(["--model", model])
        if max_tokens:
            cmd.extend(["--max-tokens", max_tokens])
        if temperature:
            cmd.extend(["--temperature", temperature])

        # Execute the command
        env = os.environ.copy()
        if api_key:
            env["ANTHROPIC_API_KEY"] = api_key

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Get the output (with a timeout to prevent hanging)
        stdout, stderr = process.communicate(timeout=30)

        if process.returncode != 0:
            return f"Error running batch processing: {stderr}"

        # Extract batch ID from output if possible
        batch_id = None
        for line in stdout.split("\n"):
            if "Batch submitted with ID:" in line:
                batch_id = line.split("Batch submitted with ID:")[1].strip()
                break

        if batch_id:
            return f"Batch processing started successfully. Batch ID: {batch_id}\n\nNote: Processing may take several minutes. You can check the status later with get_results.py."
        else:
            return f"Batch processing started, but couldn't extract batch ID. Check the batch.py output for details."
    except subprocess.TimeoutExpired:
        return "Batch processing started, but the command is still running. This is normal as batch processing continues in the background."
    except Exception as e:
        return f"Error running batch processing: {str(e)}"


@app.tool()
def check_batch_results(batch_id: str) -> str:
    """Check the results of a batch processing job.

    Args:
        batch_id: The ID of the batch to check
    """
    try:
        # Get environment variables
        api_key = os.getenv("ANTHROPIC_API_KEY")

        # Construct the command
        cmd = [
            "python",
            os.path.join(APP_DIR, "get_results.py"),
            "--batch-id",
            batch_id,
            "--output-dir",
            os.path.join(DATA_DIR, "responses"),
        ]

        # Execute the command
        env = os.environ.copy()
        if api_key:
            env["ANTHROPIC_API_KEY"] = api_key

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Get the output (with a timeout to prevent hanging)
        stdout, stderr = process.communicate(timeout=30)

        if process.returncode != 0:
            return f"Error checking batch results: {stderr}"

        return f"Batch results check completed:\n\n{stdout}"
    except subprocess.TimeoutExpired:
        return "The check is still running. This might take a while for large batches."
    except Exception as e:
        return f"Error checking batch results: {str(e)}"


# Rest of your tools remain the same...


@app.tool()
def create_learning_resource_structure(
    subject: str,
    main_topics: List[str],
    subtopics: Dict[str, List[str]] = None,
) -> str:
    """Create a structured learning resource with main topics and subtopics.

    Args:
        subject: The main subject of the learning resource
        main_topics: List of main topics to cover
        subtopics: Dictionary mapping main topics to lists of subtopics
    """
    try:
        # Format the structure
        structure = f"# Learning Resource: {subject}\n\n"
        structure += "## Table of Contents\n\n"

        # Add main topics and subtopics
        for i, topic in enumerate(main_topics):
            structure += f"{i+1}. {topic}\n"

            # Add subtopics if available
            if subtopics and topic in subtopics:
                for j, subtopic in enumerate(subtopics[topic]):
                    structure += f"   {i+1}.{j+1}. {subtopic}\n"

            structure += "\n"

        # Create a list of topics for variables.csv
        topics_list = []
        for topic in main_topics:
            topics_list.append(topic)
            if subtopics and topic in subtopics:
                for subtopic in subtopics[topic]:
                    topics_list.append(f"{topic} - {subtopic}")

        return structure
    except Exception as e:
        return f"Error creating learning resource structure: {str(e)}"


@app.tool()
def generate_system_prompt_template(
    subject: str, format_style: str = "markdown"
) -> str:
    """Generate a system prompt template for learning resources.

    Args:
        subject: The subject area for the learning resource
        format_style: The desired format style (markdown, xml, etc.)
    """
    if format_style.lower() == "xml":
        system_prompt = f"""<?xml version="1.0" encoding="UTF-8"?>
<system_prompt>
    <identity>
        <role>{subject} Learning Resource Generator</role>
        <purpose>Create consistent, well-formatted, and informative {subject} learning materials</purpose>
    </identity>

    <core_behavior>
        <formatting_rules>
            <rule>Use emoji icons for section headers</rule>
            <rule>Format code examples in appropriate language blocks</rule>
            <rule>Include a clear header with the topic name</rule>
            <rule>Maintain consistent section ordering</rule>
            <rule>Use clear, concise descriptions</rule>
            <rule>Include practical examples where applicable</rule>
        </formatting_rules>

        <template_structure>
            <section name="title">(related emoji) `{{topic}}` Learning Guide (related emoji)</section>
            
            <section name="introduction" required="true">
                <header>## Introduction 📝</header>
                <content>
                    <description>Clear, concise explanation of the topic</description>
                    <key_concepts>Core concepts and importance</key_concepts>
                </content>
            </section>

            <section name="core_concepts" required="true">
                <header>## Core Concepts 🧠</header>
                <content>
                    <fundamentals>Key ideas and principles</fundamentals>
                    <explanations>Clear, accessible explanations</explanations>
                </content>
            </section>

            <section name="examples" required="true">
                <header>## Examples and Usage 🔍</header>
                <content>
                    <practical_examples>Real-world applications</practical_examples>
                    <code_samples>Implementation examples where relevant</code_samples>
                </content>
            </section>

            <flexible_sections>
                <section name="implementation">## Implementation Details 💻</section>
                <section name="common_patterns">## Common Patterns and Techniques 🚀</section>
                <section name="best_practices">## Best Practices 🔄</section>
                <section name="applications">## Real-world Applications 🌐</section>
                <section name="visualization">## Visualization 📊</section>
                <section name="custom">Allow topic-specific sections as needed</section>
            </flexible_sections>

            <section name="advantages_disadvantages" required="true">
                <header>## Advantages and Disadvantages ⚖️</header>
                <content>
                    <pros>Key strengths and benefits</pros>
                    <cons>Limitations and drawbacks</cons>
                </content>
            </section>

            <section name="further_learning" required="true">
                <header>## Further Learning 📚</header>
                <content>
                    <links>
                        <resources>Books, articles, and tutorials</resources>
                        <practice>Exercises and projects</practice>
                        <communities>Forums and communities</communities>
                    </links>
                </content>
            </section>
        </template_structure>
    </core_behavior>

    <adaptation_rules>
        <rule>Adjust sections based on topic complexity</rule>
        <rule>Add specific sections when necessary for particular topics</rule>
        <rule>Include relevant emoji that match the topic's purpose</rule>
        <rule>Expand sections that need more detail for particular topics</rule>
        <rule>Include diagrams or visualizations when helpful</rule>
    </adaptation_rules>

    <output_guidelines>
        <format>Markdown with code blocks</format>
        <style>Clear, concise, and educational</style>
        <examples>Include practical implementation examples</examples>
        <completeness>Cover essential concepts without overwhelming</completeness>
        <code_examples>Provide clean, well-commented code examples when relevant</code_examples>
    </output_guidelines>

    <response_pattern>
        When asked to create a learning resource:
        1. Start with the standard template
        2. Customize sections based on the specific topic
        3. Include practical examples and applications
        4. Provide implementation details where relevant
        5. Add topic-specific sections if needed
        6. Include advantages and disadvantages
        7. Include further learning section with relevant resources
        8. End with a horizontal rule (---)
    </response_pattern>
</system_prompt>
"""
    else:  # Default to markdown
        system_prompt = f"""# {subject} Learning Resource Generator

## Role and Purpose
- Create consistent, well-formatted, and informative {subject} learning materials
- Generate beginner-friendly content that's accessible to all learners
- Provide practical examples and clear explanations

## Formatting Guidelines
- Use emoji icons for section headers
- Format code examples in appropriate language blocks
- Include a clear header with the topic name
- Maintain consistent section ordering
- Use clear, concise descriptions
- Include practical examples where applicable

## Standard Template Structure

### 📌 Title
(related emoji) `{{topic}}` Learning Guide (related emoji)

### 📝 Introduction
- Clear, concise explanation of the topic
- Why it's important and how it fits into the broader subject
- Who would benefit from learning this topic
- Prerequisites or related concepts

### 🧠 Core Concepts
- Key ideas and principles
- Fundamental components
- Clear, accessible explanations
- Visual representations where helpful

### 🔍 Examples and Usage
- Real-world applications
- Implementation examples
- Step-by-step walkthroughs
- Code samples where relevant

### 💻 Implementation Details (when applicable)
- Technical specifications
- Implementation considerations
- Common approaches

### 🚀 Common Patterns and Techniques
- Standard usage patterns
- Effective techniques
- Tips and tricks

### 🔄 Best Practices
- Industry standards
- Optimization techniques
- Common pitfalls to avoid

### 🌐 Real-world Applications
- Industry use cases
- Practical scenarios
- Case studies

### ⚖️ Advantages and Disadvantages
- Key strengths and benefits
- Limitations and drawbacks
- When to use and when to avoid

### 📚 Further Learning
- Books, articles, and tutorials
- Exercises and projects
- Forums and communities
- Related topics to explore

## Response Format
When asked to create a learning resource:
1. Start with the standard template
2. Customize sections based on the specific topic
3. Include practical examples and applications
4. Provide implementation details where relevant
5. Add topic-specific sections if needed
6. Include advantages and disadvantages
7. Include further learning section with relevant resources
8. End with a horizontal rule (---)

## Tone and Style
- Educational and informative
- Beginner-friendly but not oversimplified
- Engaging but focused on clarity
- Neutral and inclusive language
- Appropriate for classroom or self-study use
"""

    return system_prompt


@app.tool()
def generate_template(subject: str) -> str:
    """Generate a template for the learning resource request.

    Args:
        subject: The subject area for the learning resource
    """
    template = f"""I need a beginner's guide to {{title}}. Could you make that for my {subject} learning materials? This will be shared with classmates, so the tone should be educational and not directed to me individually but something anyone could use.

{{description}}
"""

    return template


if __name__ == "__main__":
    # Run the server with stdio transport
    app.run(transport="stdio")
