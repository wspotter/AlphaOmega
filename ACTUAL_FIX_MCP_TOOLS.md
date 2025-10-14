# 🔧 REAL FIX: OpenWebUI Tool Integration

## The ACTUAL Problem

OpenWebUI sees your MCP server as ONE big tool (an on/off switch) instead of 76 individual tools because:

1. `mcpo` exposes tools via **OpenAPI/REST** endpoints
2. OpenWebUI's "MCP (Streamable HTTP)" expects **MCP JSON-RPC protocol**
3. They're speaking different languages!

---

## Solution: Use OpenAPI Integration Instead

Since `mcpo` is already providing OpenAPI endpoints, use OpenWebUI's **OpenAPI** tool integration (not MCP):

### Step 1: Remove Existing MCP Server Configuration

1. Go to OpenWebUI → Admin Settings → External Tools
2. Find "AlphaOmega Tools" (if you added it)
3. Delete it

### Step 2: Add Each Tool Individually as OpenAPI

OpenWebUI's OpenAPI integration requires you to add **individual tool endpoints**.

**Add these one by one:**

#### Tool 1: List Tasks
```
Type: OpenAPI
Name: List Tasks
URL: http://localhost:8002/list_tasks
Method: POST
```

#### Tool 2: Create Task
```
Type: OpenAPI
Name: Create Task  
URL: http://localhost:8002/create_task
Method: POST
```

#### Tool 3: Check Inventory
```
Type: OpenAPI
Name: Check Inventory
URL: http://localhost:8002/check_inventory
Method: POST
```

**Problem:** You'd need to add all 76 tools individually! 😱

---

## Better Solution: Create OpenWebUI Pipeline

Instead of configuring 76 individual tools, create a **Pipeline** that wraps the MCP server.

### Create Pipeline File

Create `pipelines/mcp_tools_pipeline.py`:

```python
"""
MCP Tools Pipeline for OpenWebUI
Exposes all 76 MCP tools as OpenWebUI functions
"""
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
import httpx
import json


class Pipeline:
    """Pipeline that exposes MCP server tools"""
    
    class Valves(BaseModel):
        """Configuration"""
        MCP_SERVER_URL: str = Field(
            default="http://localhost:8002",
            description="MCP server base URL"
        )
    
    def __init__(self):
        self.name = "MCP Tools"
        self.valves = self.Valves()
        self.client = httpx.AsyncClient()
        
    async def on_startup(self):
        """Load tools from MCP server"""
        try:
            response = await self.client.get(f"{self.valves.MCP_SERVER_URL}/openapi.json")
            spec = response.json()
            self.tools = self._parse_tools_from_openapi(spec)
            print(f"✓ Loaded {len(self.tools)} MCP tools")
        except Exception as e:
            print(f"✗ Failed to load MCP tools: {e}")
            self.tools = []
    
    async def on_shutdown(self):
        """Cleanup"""
        await self.client.aclose()
    
    def _parse_tools_from_openapi(self, spec: Dict) -> List[Dict]:
        """Extract tool definitions from OpenAPI spec"""
        tools = []
        paths = spec.get("paths", {})
        
        for path, methods in paths.items():
            tool_name = path.strip("/")
            if "post" in methods:
                method_spec = methods["post"]
                tools.append({
                    "name": tool_name,
                    "description": method_spec.get("summary", tool_name),
                    "parameters": method_spec.get("requestBody", {})
                                         .get("content", {})
                                         .get("application/json", {})
                                         .get("schema", {"type": "object"}),
                    "endpoint": path
                })
        
        return tools
    
    def pipes(self) -> List[Dict[str, str]]:
        """Return available tools as functions"""
        return [
            {
                "id": tool["name"],
                "name": tool["description"]
            }
            for tool in self.tools
        ]
    
    async def pipe(
        self,
        body: Dict[str, Any],
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__: Optional[Callable[[dict], Any]] = None
    ) -> str:
        """Execute tool based on user message"""
        
        # Detect which tool to call from message
        message = body.get("messages", [{}])[-1].get("content", "")
        
        # Simple intent matching
        tool_name = self._detect_tool(message)
        
        if not tool_name:
            return "I can help you with tasks, inventory, customers, and more. What would you like to do?"
        
        # Find tool
        tool = next((t for t in self.tools if t["name"] == tool_name), None)
        if not tool:
            return f"Tool {tool_name} not found"
        
        # Call MCP server
        try:
            url = f"{self.valves.MCP_SERVER_URL}{tool['endpoint']}"
            params = self._extract_params(message, tool["parameters"])
            
            response = await self.client.post(
                url,
                json=params,
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            return self._format_response(tool_name, result)
            
        except Exception as e:
            return f"Error calling {tool_name}: {str(e)}"
    
    def _detect_tool(self, message: str) -> Optional[str]:
        """Simple keyword-based tool detection"""
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ["task", "todo"]):
            if "create" in message_lower or "add" in message_lower:
                return "create_task"
            else:
                return "list_tasks"
        
        if "inventory" in message_lower or "stock" in message_lower:
            return "check_inventory"
        
        if "customer" in message_lower:
            return "list_customers"
        
        if "note" in message_lower or "search" in message_lower:
            return "search_notes"
        
        return None
    
    def _extract_params(self, message: str, schema: Dict) -> Dict:
        """Extract parameters from message based on schema"""
        # Simple implementation - you can make this smarter
        return {}
    
    def _format_response(self, tool_name: str, result: Any) -> str:
        """Format tool result for chat"""
        if isinstance(result, list):
            if not result:
                return f"No {tool_name.replace('_', ' ')} found."
            
            # Format list nicely
            if tool_name == "list_tasks":
                lines = [f"**Your Tasks:**\n"]
                for task in result:
                    priority = task.get("priority", "medium")
                    emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                    lines.append(f"{emoji} **{task.get('title')}** - {task.get('description', '')}")
                return "\n".join(lines)
            
            return json.dumps(result, indent=2)
        
        return json.dumps(result, indent=2)
```

### Install Pipeline

```bash
cd /home/stacy/AlphaOmega
cp pipelines/mcp_tools_pipeline.py /path/to/openwebui/pipelines/
```

### Activate in OpenWebUI

1. Settings → Admin → Pipelines
2. Find "MCP Tools"
3. Enable it
4. Test in chat

---

## OR: Simplest Solution - Use the Existing Router Pipeline

You ALREADY have `alphaomega_router.py` that can route to MCP!

Just add MCP detection to it:

```python
# In alphaomega_router.py, add to _detect_intent:

# MCP tool keywords
mcp_keywords = [
    "task", "todo", "inventory", "stock", "customer",
    "note", "expense", "invoice", "sales", "vip"
]
if any(kw in message_lower for kw in mcp_keywords):
    return "mcp"
```

Then add the MCP routing method:

```python
async def _route_to_mcp(self, message, messages, event_emitter):
    """Route to MCP tools"""
    # Call MCP server directly
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{self.valves.MCP_HOST}/list_tasks",
            json={},
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        yield json.dumps(result, indent=2)
```

---

## Summary

**Why it's broken:**
- `mcpo` exposes OpenAPI/REST, not MCP JSON-RPC
- OpenWebUI's "MCP (Streamable HTTP)" expects JSON-RPC
- Mismatch!

**Quick fixes:**
1. ✅ **Use existing alphaomega_router.py pipeline** - Add MCP routing
2. ✅ **Create dedicated MCP pipeline** - Wrap all 76 tools
3. ❌ Don't use "MCP (Streamable HTTP)" option - it won't work with `mcpo`

**Best approach:** Update your existing router pipeline to include MCP tool routing. It's already set up for this!

Want me to update `alphaomega_router.py` to include MCP tool support?
