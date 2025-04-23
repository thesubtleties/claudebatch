# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "mcp[cli]"

# Copy all your existing files
COPY batch.py /app/
COPY get_results.py /app/
COPY learning_resource_generator.py /app/

# Create directory for data that will be mounted
RUN mkdir -p /data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the MCP server
CMD ["python", "learning_resource_generator.py"]