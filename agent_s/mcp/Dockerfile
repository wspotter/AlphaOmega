# MCP Server Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY agent_s/mcp/requirements.txt* ./
RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx

# Copy MCP server code
# Note: This assumes mcpart repo will be cloned/added as submodule
COPY agent_s/mcp/ /app/

# Create artifact directory
RUN mkdir -p /artifacts

# Expose port
EXPOSE 8002

# Run MCP server
# This is a placeholder - actual mcpart server command depends on its implementation
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8002"]
