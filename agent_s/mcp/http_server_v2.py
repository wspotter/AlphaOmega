#!/usr/bin/env python3
"""
MCP HTTP Bridge v2 - Simplified with tool caching
Converts HTTP requests to stdio MCP protocol
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import threading
import queue
import os
from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-http-bridge")

app = FastAPI(
    title="MCP HTTP Bridge",
    description="HTTP wrapper for stdio-based MCP servers",
    version="2.0.0"
)

# CORS for OpenWebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
mcp_process = None
request_id = 0
response_queue = queue.Queue()
tools_cache = []


def read_mcp_responses():
    """Background thread to read MCP responses"""
    global mcp_process
    while mcp_process and mcp_process.poll() is None:
        try:
            line = mcp_process.stdout.readline()
            if line:
                response = json.loads(line.strip())
                response_queue.put(response)
                logger.debug(f"Received MCP response: {response.get('id')}")
        except Exception as e:
            logger.error(f"Error reading MCP response: {e}")
            break


async def send_mcp_request(method: str, params: Dict = None) -> Dict:
    """Send request to MCP and wait for response"""
    global request_id, mcp_process
    
    if not mcp_process or mcp_process.poll() is not None:
        raise HTTPException(status_code=503, detail="MCP server not running")
    
    request_id += 1
    current_id = request_id
    
    request = {
        "jsonrpc": "2.0",
        "id": current_id,
        "method": method,
        "params": params or {}
    }
    
    try:
        mcp_process.stdin.write(json.dumps(request) + '\n')
        mcp_process.stdin.flush()
        
        # Wait for response with matching ID
        timeout = 10
        import time
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                response = response_queue.get(timeout=0.1)
                if response.get("id") == current_id:
                    return response
                else:
                    # Put it back if it's not ours
                    response_queue.put(response)
            except queue.Empty:
                continue
        
        raise HTTPException(status_code=504, detail="MCP request timeout")
        
    except Exception as e:
        logger.error(f"Error sending MCP request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Start MCP server and cache tools"""
    global mcp_process, tools_cache
    
    mcp_path = "/home/stacy/AlphaOmega/agent_s/mcp/mcpart/build/index.js"
    
    if not os.path.exists(mcp_path):
        logger.error(f"MCP server not found at {mcp_path}")
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
        
        # Start response reader thread
        reader_thread = threading.Thread(target=read_mcp_responses, daemon=True)
        reader_thread.start()
        
        logger.info("MCP server started, initializing...")
        
        # Initialize
        init_response = await send_mcp_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "openwebui-bridge",
                "version": "2.0.0"
            }
        })
        
        logger.info(f"MCP initialized: {init_response.get('result', {}).get('serverInfo')}")
        
        # Cache tools list
        tools_response = await send_mcp_request("tools/list", {})
        if "result" in tools_response and "tools" in tools_response["result"]:
            tools_cache.clear()
            tools_cache.extend(tools_response["result"]["tools"])
            logger.info(f"Cached {len(tools_cache)} tools")
        
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup"""
    global mcp_process
    if mcp_process:
        mcp_process.terminate()
        mcp_process.wait()
        logger.info("MCP server stopped")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MCP HTTP Bridge v2",
        "status": "running",
        "tools": len(tools_cache),
        "mcp_status": "active" if mcp_process and mcp_process.poll() is None else "inactive"
    }


@app.get("/health")
async def health():
    """Health check"""
    mcp_running = mcp_process and mcp_process.poll() is None
    
    return {
        "status": "healthy" if mcp_running else "unhealthy",
        "mcp_running": mcp_running,
        "tools_loaded": len(tools_cache)
    }


@app.get("/tools")
async def list_tools():
    """List all cached tools"""
    return {
        "tools": tools_cache
    }


@app.post("/tools/{tool_name}")
async def execute_tool(tool_name: str, params: Dict[str, Any] = None):
    """Execute a tool"""
    logger.info(f"Executing tool: {tool_name}")
    
    try:
        response = await send_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": params or {}
        })
        
        if "error" in response:
            return {
                "success": False,
                "error": str(response["error"])
            }
        
        return {
            "success": True,
            "result": response.get("result", {})
        }
        
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/openapi.json")
async def openapi_spec():
    """Generate OpenAPI spec from cached tools"""
    global tools_cache
    
    paths = {
        "/health": {
            "get": {
                "summary": "Health check",
                "operationId": "health_check",
                "responses": {"200": {"description": "OK"}}
            }
        },
        "/tools": {
            "get": {
                "summary": "List all tools",
                "operationId": "list_tools",
                "responses": {"200": {"description": "List of tools"}}
            }
        }
    }
    
    # Add each tool as a separate endpoint
    for tool in tools_cache:
        tool_name = tool.get("name", "unknown")
        paths[f"/tools/{tool_name}"] = {
            "post": {
                "summary": tool.get("description", f"Execute {tool_name}"),
                "description": tool.get("description", ""),
                "operationId": tool_name,
                "requestBody": {
                    "required": True,
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
                                        "result": {},
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
        "openapi": "3.1.0",
        "info": {
            "title": "MCP Art Supply Assistant",
            "version": "2.0.0",
            "description": f"Business management tools via MCP ({len(tools_cache)} tools available)"
        },
        "servers": [
            {"url": "http://localhost:8002", "description": "Local MCP bridge"}
        ],
        "paths": paths
    }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🔌 MCP HTTP Bridge v2 - Starting")
    print("=" * 70)
    print("MCP Server: mcpart")
    print("HTTP Endpoint: http://localhost:8002")
    print("OpenAPI Spec: http://localhost:8002/openapi.json")
    print("Health Check: http://localhost:8002/health")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
