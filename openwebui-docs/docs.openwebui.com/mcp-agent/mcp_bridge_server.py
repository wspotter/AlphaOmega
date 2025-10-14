"""
MCP-to-OpenAPI Bridge Server
This server acts as a bridge between OpenWebUI (which speaks OpenAPI)
and an MCP server (which uses the Model Context Protocol).

Architecture:
- Exposes simple, stateless OpenAPI endpoints to OpenWebUI
- Manages complex, stateful MCP communication on the backend
- Translates between REST/HTTP and MCP protocol
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uvicorn
from mock_mcp_client import MockCUAClient

# Initialize FastAPI app with metadata for OpenAPI schema
app = FastAPI(
    title="MCP Bridge Server",
    description="Bridge server that exposes MCP (Model Context Protocol) functionality via OpenAPI endpoints",
    version="1.0.0",
)

# Initialize the MCP client (maintains state across requests)
mcp_client = MockCUAClient()

# Connect on module load
connection_result = mcp_client.connect()
print(f"MCP Bridge Server initialized: {connection_result}")


# Request/Response Models
class CommandRequest(BaseModel):
    """Request model for executing MCP commands"""
    command: str = Field(
        ...,
        description="The command to execute on the MCP server",
        example="list files on the desktop"
    )


class CommandResponse(BaseModel):
    """Response model for command execution results"""
    status: str = Field(description="Execution status (success or error)")
    command: str = Field(description="The command that was executed")
    result: Dict[str, Any] = Field(description="Command execution result")
    observation: Optional[str] = Field(
        None,
        description="Human-readable observation from the MCP server"
    )


class StateResponse(BaseModel):
    """Response model for MCP server state"""
    connected: bool = Field(description="Whether the MCP client is connected")
    session_id: Optional[str] = Field(description="Current session ID")
    current_directory: str = Field(description="Current working directory")
    command_count: int = Field(description="Number of commands executed in this session")


# API Endpoints
@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with server information"""
    return {
        "message": "MCP Bridge Server",
        "description": "OpenAPI-to-MCP Bridge for OpenWebUI",
        "status": "running",
        "mcp_connected": str(mcp_client.connected),
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


@app.post(
    "/execute_cua_command",
    response_model=CommandResponse,
    summary="Execute a command on the CUA MCP server",
    description="Executes a command on the Computer Use Agent (CUA) MCP server and returns the result. "
                "This endpoint bridges OpenWebUI's stateless OpenAPI calls to the stateful MCP protocol."
)
async def execute_cua_command(request: CommandRequest) -> CommandResponse:
    """
    Execute a command on the MCP server
    
    This endpoint demonstrates the bridge pattern:
    1. Receives a stateless HTTP request from OpenWebUI
    2. Translates it to a stateful MCP command
    3. Executes the command on the MCP server
    4. Returns the result as a standard HTTP response
    
    Args:
        request: CommandRequest containing the command to execute
        
    Returns:
        CommandResponse with execution results
        
    Raises:
        HTTPException: If the MCP client is not connected or command fails
    """
    if not mcp_client.connected:
        raise HTTPException(
            status_code=503,
            detail="MCP client is not connected. Server may be starting up."
        )
    
    # Execute command on MCP server
    result = mcp_client.execute_command(request.command)
    
    # Check for errors
    if result.get("status") == "error":
        raise HTTPException(
            status_code=400,
            detail={
                "error": result.get("error", "Unknown error"),
                "command": request.command
            }
        )
    
    # Return successful result
    return CommandResponse(
        status=result.get("status", "success"),
        command=request.command,
        result=result,
        observation=result.get("observation")
    )


@app.post(
    "/list_desktop_files",
    response_model=CommandResponse,
    summary="List files on the desktop",
    description="Convenience endpoint to list files on the desktop. "
                "This is a specialized wrapper around the execute_cua_command endpoint."
)
async def list_desktop_files() -> CommandResponse:
    """
    List files on the desktop
    
    This is a convenience endpoint that demonstrates how you can create
    specialized, user-friendly endpoints that wrap the generic MCP bridge.
    
    Returns:
        CommandResponse with list of desktop files
    """
    command = "list files /home/user/Desktop"
    request = CommandRequest(command=command)
    return await execute_cua_command(request)


@app.post(
    "/read_desktop_file/{filename}",
    response_model=CommandResponse,
    summary="Read a file from the desktop",
    description="Read the contents of a specific file from the desktop directory."
)
async def read_desktop_file(filename: str) -> CommandResponse:
    """
    Read a file from the desktop
    
    Args:
        filename: Name of the file to read
        
    Returns:
        CommandResponse with file contents
    """
    command = f"read file {filename}"
    request = CommandRequest(command=command)
    return await execute_cua_command(request)


@app.get(
    "/mcp_state",
    response_model=StateResponse,
    summary="Get current MCP server state",
    description="Retrieves the current state of the MCP server connection, "
                "including session information and command history."
)
async def get_mcp_state() -> StateResponse:
    """
    Get current MCP server state
    
    This endpoint allows OpenWebUI to check the state of the MCP connection,
    demonstrating how the bridge maintains stateful information.
    
    Returns:
        StateResponse with current state information
    """
    observation = mcp_client.get_observation()
    
    return StateResponse(
        connected=mcp_client.connected,
        session_id=mcp_client.session_id,
        current_directory=observation.get("current_directory", "unknown"),
        command_count=observation.get("command_count", 0)
    )


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mcp_connected": mcp_client.connected,
        "session_id": mcp_client.session_id
    }


@app.get(
    "/available_commands",
    summary="Get list of available MCP commands",
    description="Returns a list of commands that can be executed on the MCP server."
)
async def get_available_commands() -> Dict[str, Any]:
    """
    Get list of available commands
    
    Returns:
        Dictionary with available commands and their descriptions
    """
    help_result = mcp_client.execute_command("help")
    
    return {
        "status": "success",
        "commands": help_result.get("available_commands", []),
        "description": "These commands can be used with the /execute_cua_command endpoint"
    }


if __name__ == "__main__":
    # Run the bridge server
    print("Starting MCP Bridge Server...")
    print("This server bridges OpenWebUI (OpenAPI) to MCP protocol")
    print("OpenAPI documentation will be available at: http://localhost:8001/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )

