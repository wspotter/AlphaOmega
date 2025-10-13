# MCP Server Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY mcpart/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY mcpart/ ./

# Build the application
RUN npm run build

# Create artifact directory
RUN mkdir -p /artifacts

# Expose port
EXPOSE 8002

# Set environment variables
ENV MCP_PORT=8002

# Run MCP server
CMD ["npm", "start"]
