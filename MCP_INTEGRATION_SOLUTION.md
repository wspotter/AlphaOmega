# MCP Integration - The ACTUAL Solution

## Problem Summary

You've been trying to register 76 MCP tools by inserting them directly into OpenWebUI's database, but they don't appear in the UI showing "Tools 0".

**Root Cause**: OpenWebUI requires tools to be registered through its proper integration layer, not direct database insertion.

## The Correct Solution

OpenWebUI v0.6.33 has **NATIVE MCP SUPPORT**. Here's how to properly integrate your mcpo proxy:

### Step 1: Access OpenWebUI Admin Settings

1. Open your browser and go to: **http://localhost:8080**
2. Log in as admin (admin@localhost)
3. Click your profile icon (top right)
4. Select **⚙️ Admin Settings**

### Step 2: Configure MCP Server

1. In Admin Settings, look for one of these sections:
   - **External Tools**
   - **Connections** → **MCP Servers**
   - **Tools** → **External Servers**

2. Click **+ Add Server** or **+ Add MCP Server**

3. Fill in the configuration:
   ```
   Name: mcpart
   Type: MCP (Streamable HTTP)
   Server URL: http://localhost:8002
   Authentication: None (since it's localhost)
   ```

4. Click **Save**

5. If prompted, restart OpenWebUI:
   ```bash
   # Kill the current process
   kill 2849740
   
   # Restart OpenWebUI
   cd /home/stacy/AlphaOmega
   source venv/bin/activate
   open-webui serve --port 8080
   ```

### Step 3: Verify Tools Appear

After restarting, check:

1. Go to **Workspace → Tools** at http://localhost:8080/workspace/tools
2. You should now see all 76 MCP tools automatically discovered
3. They'll be prefixed with "mcpart_" or similar

## Alternative: If Admin Settings Doesn't Have MCP Configuration

If your OpenWebUI v0.6.33 doesn't show an "External Tools" or "MCP Servers" option in Admin Settings, you have two options:

### Option A: Use OpenAPI Tool Servers Instead

Since mcpo already exposes an OpenAPI spec at http://localhost:8002, configure it as an OpenAPI server:

1. Admin Settings → **External Tools**
2. Add Server:
   ```
   Type: OpenAPI
   URL: http://localhost:8002
   ```

### Option B: Create an MCP Bridge Tool

Create a single OpenWebUI tool that acts as a proxy to all MCP tools:

1. Go to **Workspace → Tools**
2. Click **+ Create New Tool**
3. Paste this code:

```python
"""
MCP Bridge - Access all mcpart tools through one OpenWebUI tool
"""

import requests
import json
from typing import Optional, Callable, Awaitable
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        MCP_SERVER_URL: str = Field(
            default="http://localhost:8002",
            description="URL of the MCP server (mcpo proxy)"
        )

    def __init__(self):
        self.valves = self.Valves()

    async def list_mcp_tools(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None
    ) -> str:
        """
        List all available MCP tools from the mcpart server.
        
        :return: JSON list of available tools
        """
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": "Fetching MCP tools...", "done": False}
            })
        
        try:
            response = requests.get(f"{self.valves.MCP_SERVER_URL}/tools")
            tools = response.json()
            
            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"Found {len(tools)} tools", "done": True}
                })
            
            return json.dumps(tools, indent=2)
        except Exception as e:
            return f"Error listing tools: {str(e)}"

    async def call_mcp_tool(
        self,
        tool_name: str,
        parameters: Optional[str] = "{}",
        __event_emitter__: Callable[[dict], Awaitable[None]] = None
    ) -> str:
        """
        Call any MCP tool by name.
        
        :param tool_name: Name of the MCP tool (e.g., 'list_tasks', 'add_task')
        :param parameters: JSON string of parameters for the tool
        :return: Tool execution result
        """
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Calling {tool_name}...", "done": False}
            })
        
        try:
            params = json.loads(parameters) if isinstance(parameters, str) else parameters
            
            response = requests.post(
                f"{self.valves.MCP_SERVER_URL}/tools/{tool_name}",
                json=params,
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            
            if __event_emitter__:
                await __event_emitter__({
                    "type": "status",
                    "data": {"description": f"Tool {tool_name} completed", "done": True}
                })
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error calling {tool_name}: {str(e)}"
```

4. Click **Save**
5. Enable this tool for your models

Now you can use it like:
- "List all MCP tools"
- "Call the list_tasks tool"
- "Use add_task to create a new task with title 'Test' and priority 'high'"

## Why Database Insertion Didn't Work

OpenWebUI's tool system:
- Requires specific registration metadata and validation
- Tracks tool state, permissions, and usage analytics
- Applies user-specific filtering and access control
- Integrates with the model function-calling system

Direct database insertion bypasses all of this, so:
- ✅ Tools exist in database
- ❌ UI query logic filters them out
- ❌ No registration metadata
- ❌ No integration with function-calling system

## Verification Steps

After proper MCP integration:

```bash
# 1. Check if OpenWebUI can see tools through its API
curl -s http://localhost:8080/api/v1/tools/ | jq '.[] | .id' | head -10

# 2. Check MCP server is responding
curl -s http://localhost:8002/tools | jq '.[] | .name' | head -10

# 3. Test a tool call through OpenWebUI
# (Do this through the UI by asking: "What tasks do I have?")
```

## Expected Behavior After Fix

1. **Workspace → Tools** shows 76+ tools
2. Tools are prefixed with your MCP server name (e.g., "mcpart_list_tasks")
3. You can enable them per-model or globally
4. LLM can call them during conversations

## Troubleshooting

### Tools Still Not Appearing?

1. **Check OpenWebUI logs:**
   ```bash
   # OpenWebUI logs are usually in the terminal where you started it
   # Look for MCP-related errors
   ```

2. **Verify mcpo is accessible:**
   ```bash
   curl -v http://localhost:8002/tools
   # Should return 200 OK with JSON list
   ```

3. **Check OpenWebUI version supports MCP:**
   ```bash
   cd /home/stacy/AlphaOmega
   source venv/bin/activate
   pip show open-webui | grep Version
   # Should be v0.6.31 or higher
   ```

4. **Try restarting OpenWebUI:**
   ```bash
   kill $(pgrep -f "open-webui serve --port 8080")
   cd /home/stacy/AlphaOmega
   source venv/bin/activate
   open-webui serve --port 8080 > logs/openwebui.log 2>&1 &
   ```

### MCP Configuration Not Showing in Admin Settings?

If Admin Settings doesn't have External Tools section:

1. **Update OpenWebUI to latest:**
   ```bash
   cd /home/stacy/AlphaOmega
   source venv/bin/activate
   pip install --upgrade open-webui
   ```

2. **Check if feature is enabled:**
   Some features may be gated by environment variables. Check OpenWebUI docs for:
   - `ENABLE_MCP_SERVERS=true`
   - `ENABLE_EXTERNAL_TOOLS=true`

3. **Use the MCP Bridge tool** (Option B above) as a workaround

## Next Steps

1. ✅ Go to http://localhost:8080 Admin Settings
2. ✅ Look for "External Tools" or "MCP Servers" section
3. ✅ Add mcpo server (http://localhost:8002)
4. ✅ Restart OpenWebUI
5. ✅ Verify tools appear in Workspace → Tools
6. ✅ Test by asking "What tasks do I have?"

## Clean Up Old Database Entries (Optional)

If you want to remove the manually inserted tools:

```bash
cd /home/stacy/AlphaOmega
sqlite3 openwebui_data/webui.db

-- List tools to verify
SELECT id, name FROM tool WHERE id LIKE 'mcp_%' LIMIT 5;

-- Delete manually inserted tools (only if new integration works)
DELETE FROM tool WHERE id LIKE 'mcp_tool_%';

-- Verify deletion
SELECT COUNT(*) FROM tool WHERE id LIKE 'mcp_%';

.quit
```

Only do this AFTER confirming the proper MCP integration is working!

## Summary

**STOP** inserting tools into the database manually!

**START** using OpenWebUI's native MCP integration:
1. Admin Settings → External Tools → Add MCP Server
2. URL: http://localhost:8002
3. Save and restart
4. Tools appear automatically ✨

If that doesn't work, use the **MCP Bridge tool** as a single-tool proxy to all MCP functionality.
