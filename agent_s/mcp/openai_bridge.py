#!/usr/bin/env python3
"""
OpenAI-Compatible API Bridge for MCP Server
Makes mcpart MCP tools available as OpenAI function calling
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import threading
import queue
import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-openai-bridge")

app = FastAPI(
    title="MCP OpenAI Bridge",
    description="OpenAI-compatible API for MCP tools",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable redoc
    openapi_url=None  # We'll serve our custom OpenAPI spec
)

# CORS
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
        except Exception as e:
            logger.error(f"Error reading MCP response: {e}")
            break


def send_mcp_request(method: str, params: Dict = None) -> Dict:
    """Send synchronous request to MCP"""
    global request_id, mcp_process
    
    if not mcp_process or mcp_process.poll() is not None:
        raise Exception("MCP server not running")
    
    request_id += 1
    current_id = request_id
    
    request = {
        "jsonrpc": "2.0",
        "id": current_id,
        "method": method,
        "params": params or {}
    }
    
    mcp_process.stdin.write(json.dumps(request) + '\n')
    mcp_process.stdin.flush()
    
    # Wait for response
    timeout = 10
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            response = response_queue.get(timeout=0.1)
            if response.get("id") == current_id:
                return response
            else:
                response_queue.put(response)
        except queue.Empty:
            continue
    
    raise Exception("MCP request timeout")


def _find_tool(name: str) -> Optional[Dict[str, Any]]:
    for t in tools_cache:
        if t.get("name") == name:
            return t
    return None


@app.on_event("startup")
async def startup_event():
    """Start MCP server and cache tools"""
    global mcp_process, tools_cache
    
    # Resolve mcpart build path relative to this file
    base_dir = Path(__file__).parent
    candidate = base_dir / "mcpart" / "build" / "index.js"
    # Fallback to top-level mcpart if present
    alt_candidate = Path("/home/stacy/AlphaOmega/mcpart/build/index.js")
    mcp_path = str(candidate if candidate.exists() else alt_candidate)
    
    if not os.path.exists(mcp_path):
        logger.error(f"MCP server not found at {mcp_path}")
        return
    
    try:
        logger.info("Starting MCP server...")
        mcp_process = subprocess.Popen(
            ['node', mcp_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Start response reader
        reader_thread = threading.Thread(target=read_mcp_responses, daemon=True)
        reader_thread.start()
        
        time.sleep(1)
        
        # Initialize
        init_response = send_mcp_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "openai-bridge", "version": "1.0.0"}
        })
        
        logger.info(f"MCP initialized: {init_response.get('result', {}).get('serverInfo')}")
        
        # Cache tools
        tools_response = send_mcp_request("tools/list", {})
        if "result" in tools_response and "tools" in tools_response["result"]:
            tools_cache.clear()
            tools_cache.extend(tools_response["result"]["tools"])
            logger.info(f"✓ Loaded {len(tools_cache)} MCP tools")
        
    except Exception as e:
        logger.error(f"Failed to start MCP: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup"""
    global mcp_process
    if mcp_process:
        mcp_process.terminate()
        mcp_process.wait()


# OpenAI-compatible models

class Message(BaseModel):
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatCompletionRequest(BaseModel):
    model: str = "mcp-assistant"
    messages: List[Message]
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = "auto"
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


# --------- Simple intent detection for default mode (no native tool calling) ---------
def _extract_intent_and_args(user_text: str) -> Optional[Dict[str, Any]]:
    """Very small heuristic intent parser that maps natural asks to MCP tools.

    Returns a dict like {"tool": str, "args": dict, "explain": str} or None.
    """
    if not user_text:
        return None

    text = user_text.lower().strip()

    # Tasks
    if any(k in text for k in ["task", "tasks", "todo", "to-do"]):
        # complete task by id
        import re

        m = re.search(r"(complete|finish|done)\s+(task\s+)?#?(\d+)", text)
        if m:
            task_id = int(m.group(3))
            return {"tool": "complete_task", "args": {"id": task_id}, "explain": f"Completing task #{task_id}"}

        # add task
        m = re.search(r"(add|create|new)\s+(task\s+)?(.+)", text)
        if m and len(m.groups()) >= 3:
            title = m.group(3).strip().rstrip('.')
            # crude date detection
            due = None
            m_due = re.search(r"by\s+([\w\-/: ]+)$", title)
            if m_due:
                due = m_due.group(1).strip()
                title = re.sub(r"\s*by\s+[\w\-/: ]+$", "", title).strip()
            args = {"title": title}
            if due:
                args["due"] = due
            return {"tool": "add_task", "args": args, "explain": f"Adding task '{title}'"}

        # list tasks default
        return {"tool": "list_tasks", "args": {}, "explain": "Listing tasks"}

    # Notes
    if "note" in text or "notes" in text:
        import re
        m = re.search(r"(find|search|show).*(note|notes)\s+(about|on|for)\s+(.+)", text)
        if m:
            q = m.group(4).strip()
            return {"tool": "search_notes", "args": {"query": q}, "explain": f"Searching notes for '{q}'"}
        return {"tool": "list_notes", "args": {}, "explain": "Listing notes"}

    # Inventory
    if any(k in text for k in ["inventory", "stock", "in stock", "sku", "quantity"]):
        import re
        m = re.search(r"(check|qty|quantity|stock).*(?:for|of)?\s+([\w\- ]+)$", text)
        if m:
            item = m.group(2).strip()
            return {"tool": "check_inventory", "args": {"item": item}, "explain": f"Checking inventory for '{item}'"}
        return {"tool": "list_inventory", "args": {}, "explain": "Listing inventory"}

    # Expenses
    if any(k in text for k in ["expense", "expenses", "spend", "spent", "purchases"]):
        return {"tool": "list_expenses", "args": {}, "explain": "Listing expenses"}

    # Customers
    if any(k in text for k in ["customer", "customers", "client", "clients"]):
        return {"tool": "list_customers", "args": {}, "explain": "Listing customers"}

    # Fallback: if they said "tool" or "tools" show a few
    if "tool" in text or "tools" in text:
        return {"tool": "__list_tools__", "args": {}, "explain": "Showing available tools"}

    return None


def _format_result_for_chat(tool: str, result: Any) -> str:
    """Render a compact, readable string response for the chat UI."""
    try:
        if tool == "list_tasks":
            tasks = result or []
            if not tasks:
                return "You have no tasks today."
            lines = ["Here are your tasks:"]
            for t in tasks:
                status = "✅" if t.get("completed") else "⬜"
                due = f" (due {t['due']})" if t.get("due") else ""
                lines.append(f"- {status} #{t.get('id')}: {t.get('title')}{due}")
            return "\n".join(lines)
        if tool == "add_task":
            return f"Added task: {result.get('title')} (id: {result.get('id')})"
        if tool == "complete_task":
            return f"Marked task #{result.get('id')} as complete."
        if tool in ("search_notes", "list_notes"):
            notes = result or []
            if not notes:
                return "No notes found."
            lines = ["Notes:"] + [f"- {n.get('title')}: {n.get('snippet', '')}" for n in notes[:10]]
            return "\n".join(lines)
        if tool in ("check_inventory", "list_inventory"):
            items = result if isinstance(result, list) else [result]
            clean = []
            for it in items:
                if not isinstance(it, dict):
                    continue
                name = it.get("item") or it.get("name") or it.get("sku")
                qty = it.get("quantity") or it.get("qty")
                clean.append(f"- {name}: {qty}")
            return "Inventory:\n" + ("\n".join(clean) if clean else "No items")
        if tool == "list_expenses":
            exps = result or []
            if not exps:
                return "No expenses recorded."
            total = 0.0
            lines = ["Recent expenses:"]
            for e in exps[:10]:
                amt = float(e.get("amount", 0))
                total += amt
                lines.append(f"- {e.get('date')}: ${amt:.2f} – {e.get('category')} – {e.get('memo','')}")
            lines.append(f"Total (top {min(10, len(exps))}): ${total:.2f}")
            return "\n".join(lines)
    except Exception:
        # fallback to JSON
        pass
    return json.dumps(result, ensure_ascii=False)


@app.get("/")
async def root():
    return {
        "service": "MCP OpenAI Bridge",
        "tools_loaded": len(tools_cache),
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "tools": len(tools_cache),
        "pid": os.getpid(),
        "endpoints": ["/dashboard", "/openapi.json", "/tools", "/v1/chat/completions"]
    }


@app.get("/docs")
async def docs_redirect():
    return RedirectResponse(url="/dashboard")


@app.get("/v1/models")
@app.get("/models")
async def list_models():
    """List available models (OpenAI format)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "mcp-assistant",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "alphaomega",
                "permission": [],
                "root": "mcp-assistant",
                "parent": None
            }
        ]
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
        # Simple HTML dashboard for tools browsing & testing
        items = []
        for t in tools_cache:
                name = t.get("name", "")
                desc = t.get("description", "")
                schema = t.get("inputSchema", {"type": "object"})
                items.append(
                        f"""
                <details style='margin:8px 0; padding:8px; border:1px solid #ddd; border-radius:6px;'>
                    <summary><b>{name}</b> – {desc}</summary>
                    <div style='margin-top:8px;'>
                        <p><code>POST /tools/{name}/execute</code></p>
                        <p style='font-size:12px;color:#666;'>Schema: <pre style='background:#f7f7f7;padding:8px;border-radius:4px;overflow:auto;'>{json.dumps(schema, indent=2)}</pre></p>
                        <form method='post' action='/tools/{name}/execute' onsubmit='return submitForm(event, this)'>
                            <textarea name='__json' rows='4' style='width:100%;font-family:monospace;' placeholder='{{{{}}}}'></textarea>
                            <div style='margin-top:6px;'>
                                <button type='submit'>Run</button>
                                <button type='button' onclick='fillSample(this, {json.dumps(schema)})' style='margin-left:8px;'>Fill sample</button>
                            </div>
                        </form>
                        <div class='result' style='white-space:pre-wrap;font-family:monospace;margin-top:6px;'></div>
                    </div>
                </details>
                        """
                )
        html = f"""
        <!doctype html>
        <html><head><meta charset='utf-8'><title>MCP Bridge Dashboard</title>
        <style>body{{{{font-family:system-ui, sans-serif;max-width:960px;margin:24px auto;padding:0 16px}}}}</style>
        <script>
            async function submitForm(evt, form){{{{
                evt.preventDefault();
                const wrap = form.parentElement;
                const resultDiv = wrap.querySelector('.result');
                resultDiv.textContent = 'Running...';
                const text = form.__json.value || '{{{{}}}}';
                const url = form.getAttribute('action');
                try {{{{
                    const res = await fetch(url, {{{{method:'POST', headers:{{{{'Content-Type':'application/json'}}}}, body:text}}}});
                    const data = await res.json();
                    resultDiv.textContent = JSON.stringify(data, null, 2);
                }}}} catch (e) {{{{
                    resultDiv.textContent = 'Error: ' + e;
                }}}}
                return false;
            }}}}
            function fillSample(btn, schema){{{{
                const form = btn.closest('form');
                const t = (schema && schema.example) ? JSON.stringify(schema.example, null, 2) : '{{{{}}}}';
                form.__json.value = t;
            }}}}
        </script>
        </head>
        <body>
            <h1>🧰 MCP OpenAI Bridge Dashboard</h1>
            <p>{len(tools_cache)} tools loaded. Use the forms below to test endpoints, or call them from OpenWebUI.</p>
            <p>Useful endpoints: <a href='/openapi.json'>openapi.json</a> • <a href='/tools'>/tools</a> • <a href='/v1/models'>/v1/models</a></p>
            {''.join(items)}
        </body></html>
        """
        return HTMLResponse(content=html)


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions with function calling"""
    
    # Check if there are tool calls to execute
    last_message = request.messages[-1] if request.messages else None
    
    if last_message and last_message.role == "assistant" and last_message.tool_calls:
        # Execute the requested tools
        tool_results = []
        
        for tool_call in last_message.tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name")
            arguments = json.loads(function.get("arguments", "{}"))
            
            logger.info(f"Executing tool: {tool_name}")
            
            try:
                response = send_mcp_request("tools/call", {
                    "name": tool_name,
                    "arguments": arguments
                })
                
                result = response.get("result", {})
                
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "content": json.dumps(result)
                })
                
            except Exception as e:
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "content": json.dumps({"error": str(e)})
                })
        
        # Return tool results
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_results
                },
                "finish_reason": "tool_calls"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
    # Default mode: proactively execute tools when intent is detected
    user_message = next((m.content for m in reversed(request.messages) if m.role == "user"), "")

    intent = _extract_intent_and_args(user_message)
    if intent:
        if intent["tool"] == "__list_tools__":
            names = ", ".join(t.get("name") for t in tools_cache[:20])
            content = f"I have access to {len(tools_cache)} tools. A few examples: {names}."
        else:
            try:
                call_name = intent["tool"]
                call_args = intent.get("args", {})
                logger.info(f"Auto-executing tool from chat: {call_name} {call_args}")
                response = send_mcp_request("tools/call", {"name": call_name, "arguments": call_args})
                result = response.get("result", {})
                content = _format_result_for_chat(call_name, result)
            except Exception as e:
                logger.exception("Auto tool execution failed")
                content = f"I tried to run {intent['tool']} but hit an error: {e}"

        tokens = len(user_message.split())
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": tokens, "completion_tokens": len(content.split()), "total_tokens": tokens + len(content.split())}
        }

    # If no intent, gently guide user and show a few tools
    example_tools = [t.get("name") for t in tools_cache[:6]]
    hint = ", ".join(example_tools)
    content = (
        "I can use built-in tools on your behalf. Try: 'What tasks do I have today?', "
        "'Search notes about invoices', or 'Check inventory for canvas'.\n"
        f"Available tools include: {hint} …"
    )
    tokens = len(user_message.split())
    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": tokens, "completion_tokens": len(content.split()), "total_tokens": tokens + len(content.split())}
    }


@app.get("/v1/tools")
@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": tools_cache,
        "count": len(tools_cache)
    }


@app.get("/tools/{tool_name}")
async def get_tool(tool_name: str):
    t = _find_tool(tool_name)
    if not t:
        raise HTTPException(status_code=404, detail="Tool not found")
    # Add a sample curl for convenience
    sample = {
        "curl": f"curl -s -X POST http://localhost:8002/tools/{tool_name}/execute -H 'Content-Type: application/json' -d '{{}}' | jq ."
    }
    out = dict(t)
    out["sample"] = sample
    return JSONResponse(out)


@app.get("/openapi.json")
async def openapi_spec():
    """Generate OpenAPI spec for OpenWebUI Tool Server integration"""
    
    # Build paths for each tool
    paths = {}
    
    for tool in tools_cache:
        tool_name = tool.get("name", "")
        tool_description = tool.get("description", "")
        input_schema = tool.get("inputSchema", {"type": "object", "properties": {}})
        
        # Create path for this tool
        path = f"/tools/{tool_name}/execute"
        paths[path] = {
            "post": {
                "summary": tool_description,
                "description": tool_description,
                "operationId": f"{tool_name}_execute",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": input_schema
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "tool": {"type": "string"},
                                        "result": {"type": "object"}
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
            "title": "MCP Art Supply Store Tools",
            "description": f"Access to {len(tools_cache)} business management tools via MCP",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "http://localhost:8002",
                "description": "Local MCP Bridge"
            }
        ],
        "paths": paths,
        "components": {
            "schemas": {},
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer"
                }
            }
        }
    }


@app.post("/v1/tools/{tool_name}/execute")
@app.post("/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, params: dict = {}):
    """Execute a specific tool"""
    try:
        logger.info(f"Direct tool execution: {tool_name} with {params}")
        
        response = send_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": params
        })
        
        result = response.get("result", {})
        
        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return {
            "success": False,
            "tool": tool_name,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("🤖 MCP OpenAI Bridge")
    print("=" * 70)
    print("OpenAI API: http://localhost:8002/v1")
    print("Models: http://localhost:8002/v1/models")
    print("Chat: http://localhost:8002/v1/chat/completions")
    print("=" * 70)
    print()
    print("Add to OpenWebUI:")
    print("  Settings → Connections → Add Connection")
    print("  URL: http://localhost:8002/v1")
    print("  Type: OpenAI")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
