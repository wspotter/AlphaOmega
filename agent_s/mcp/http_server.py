#!/usr/bin/env python3
"""
MCP HTTP Bridge - Converts HTTP requests to stdio MCP protocol
Allows OpenWebUI to communicate with mcpart MCP server
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import asyncio
import os
from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-http-bridge")

app = FastAPI(
    title="MCP HTTP Bridge",
    description="HTTP wrapper for stdio-based MCP servers",
    version="1.0.0"
)

# CORS for OpenWebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP process
mcp_process = None
request_id = 0


class ToolRequest(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = {}


class ToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


@app.on_event("startup")
async def start_mcp_server():
    """Start the MCP server as subprocess"""
    global mcp_process
    
    mcp_path = "/home/stacy/AlphaOmega/mcpart/build/index.js"
    
    if not os.path.exists(mcp_path):
        logger.error(f"MCP server not found at {mcp_path}")
        logger.error("Run: cd /home/stacy/AlphaOmega/mcpart && npm run build")
        return
    
    try:
        logger.info(f"Starting MCP server from {mcp_path}")
        mcp_process = subprocess.Popen(
            ['node', mcp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        logger.info("MCP server started successfully")
        
        # Initialize MCP connection
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "openwebui-bridge",
                    "version": "1.0.0"
                }
            }
        }
        
        mcp_process.stdin.write(json.dumps(init_request) + '\n')
        mcp_process.stdin.flush()
        
        # Read initialization response
        response_line = mcp_process.stdout.readline()
        logger.info(f"MCP initialized: {response_line.strip()}")
        
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_mcp_server():
    """Cleanup MCP process"""
    global mcp_process
    if mcp_process:
        mcp_process.terminate()
        mcp_process.wait()
        logger.info("MCP server stopped")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MCP HTTP Bridge",
        "status": "running",
        "mcp_status": "active" if mcp_process and mcp_process.poll() is None else "inactive"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    mcp_running = mcp_process and mcp_process.poll() is None
    
    return {
        "status": "healthy" if mcp_running else "unhealthy",
        "mcp_running": mcp_running,
        "service": "mcp-http-bridge"
    }


@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    global request_id
    request_id += 1
    
    if not mcp_process or mcp_process.poll() is not None:
        raise HTTPException(status_code=503, detail="MCP server not running")
    
    try:
        # Request tools list from MCP server
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/list",
            "params": {}
        }
        
        mcp_process.stdin.write(json.dumps(request) + '\n')
        mcp_process.stdin.flush()
        
        # Read response
        response_line = mcp_process.stdout.readline()
        response = json.loads(response_line)
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return response.get("result", {})
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, params: Dict[str, Any] = {}):
    """Execute an MCP tool"""
    global request_id
    request_id += 1
    
    if not mcp_process or mcp_process.poll() is not None:
        raise HTTPException(status_code=503, detail="MCP server not running")
    
    try:
        logger.info(f"Executing tool: {tool_name} with params: {params}")
        
        # Send MCP tool call request
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        mcp_process.stdin.write(json.dumps(request) + '\n')
        mcp_process.stdin.flush()
        
        # Read response
        response_line = mcp_process.stdout.readline()
        
        if not response_line:
            raise HTTPException(status_code=500, detail="No response from MCP server")
        
        response = json.loads(response_line)
        
        if "error" in response:
            return ToolResponse(
                success=False,
                error=str(response["error"])
            )
        
        result = response.get("result", {})
        
        return ToolResponse(
            success=True,
            result=result
        )
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}, response: {response_line}")
        raise HTTPException(status_code=500, detail="Invalid JSON response from MCP")
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/call")
async def call_tool(request: ToolRequest):
    """OpenWebUI-compatible tool call endpoint"""
    return await execute_tool(request.name, request.arguments)


@app.get("/openapi.json")
async def openapi_spec():
    """Provide OpenAPI spec for OpenWebUI"""
    # Temporarily get tools synchronously during startup
    global request_id
    request_id += 1
    
    tools = []
    
    if mcp_process and mcp_process.poll() is None:
        try:
            # Request tools list from MCP server
            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/list",
                "params": {}
            }
            
            mcp_process.stdin.write(json.dumps(request) + '\n')
            mcp_process.stdin.flush()
            
            # Read response
            response_line = mcp_process.stdout.readline()
            response = json.loads(response_line)
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
        except Exception as e:
            logger.error(f"Error getting tools for OpenAPI spec: {e}")
    
    # Generate OpenAPI spec from MCP tools
    paths = {
        "/tools": {
            "get": {
                "summary": "List all available tools",
                "operationId": "list_tools",
                "responses": {
                    "200": {
                        "description": "List of tools",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    }
    
    for tool in tools:
        tool_name = tool.get("name", "unknown")
        paths[f"/tools/{tool_name}"] = {
            "post": {
                "summary": tool.get("description", f"Execute {tool_name}"),
                "operationId": tool_name,
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": tool.get("inputSchema", {"type": "object"})
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Tool execution result",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "result": {"type": "object"},
                                        "error": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "MCP Art Supply Assistant",
            "version": "1.0.0",
            "description": f"62 business management tools via MCP ({len(tools)} tools loaded)"
        },
        "servers": [
            {"url": "http://localhost:8002"}
        ],
        "paths": paths
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🔌 MCP HTTP Bridge Starting")
    print("=" * 60)
    print("MCP Server: mcpart (62 tools)")
    print("HTTP Endpoint: http://localhost:8002")
    print("OpenAPI Spec: http://localhost:8002/openapi.json")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
