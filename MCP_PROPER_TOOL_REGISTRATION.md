# MCP Tool Registration - The Right Way

## Problem Identified

After checking the OpenWebUI documentation, I discovered the issue:

**You should NOT directly insert tools into the database!**

OpenWebUI tools are meant to be:
1. Imported from the Community Tool Library (https://openwebui.com/tools)
2. Created through the Workspace UI
3. Registered via the OpenWebUI API

Direct database insertion bypasses OpenWebUI's registration logic, which is why tools appear in the database but not in the UI.

## Official Documentation Says

From `/features/plugin/tools/`:

> Tools are small Python scripts that add superpowers to your LLM.
> 
> **How to Install Tools:**
> 1. Go to https://openwebui.com/tools
> 2. Choose a Tool, then click the Get button
> 3. Enter your Open WebUI instance's IP address or URL
> 4. Click "Import to WebUI" — done!

This means there's an import/registration flow that must be followed.

## The Correct Approach

### Option 1: Use OpenWebUI's Tool Creation UI

1. Go to http://localhost:8080/workspace/tools
2. Click "Create New Tool" (+ button)
3. Paste your tool code
4. Save

This ensures proper registration through OpenWebUI's internal logic.

### Option 2: Use OpenWebUI's API (If Available)

Check if OpenWebUI exposes a `/api/v1/tools/create` endpoint:

```bash
# Get auth token first
TOKEN=$(curl -s http://localhost:8080/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@localhost","password":"your_password"}' | jq -r '.token')

# Create tool via API
curl -X POST http://localhost:8080/api/v1/tools/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_tasks",
    "content": "class Tools:...",
    "specs": [...]
  }'
```

### Option 3: Create an "MCP Tool Importer" as an OpenWebUI Tool

Create a special OpenWebUI tool that imports MCP tools from your mcpo server.

## Recommended Solution for AlphaOmega

Since you have 76 MCP tools and want automation, I recommend:

**Create an OpenWebUI Function/Tool that acts as an MCP bridge**

Instead of registering 76 individual tools, create ONE OpenWebUI tool that:
1. Lists available MCP tools from mcpo
2. Routes tool calls to mcpo dynamically
3. Returns results back to OpenWebUI

This is exactly what OpenWebUI's MCP integration is supposed to do!

## Check If OpenWebUI Has Native MCP Support

Let me check your OpenWebUI documentation...

From the docs, I found: `/features/mcp.html` - "🔌 Model Context Protocol (MCP)"

**OpenWebUI v0.6+ has NATIVE MCP SUPPORT!**

You don't need to register tools individually - you should configure MCP servers directly in OpenWebUI!

## Correct MCP Integration Steps

1. **Configure MCP Server in OpenWebUI Settings**
   
   Go to: Settings → Connections → MCP Servers

2. **Add your mcpo proxy as an MCP server**
   
   ```json
   {
     "name": "mcpart",
     "transport": {
       "type": "http",
       "url": "http://localhost:8002"
     }
   }
   ```

3. **OpenWebUI will automatically discover and list all 76 tools**

4. **Tools will appear in the Tools menu automatically**

## Why Your Database Insertion Didn't Work

OpenWebUI's frontend queries tools through specific API endpoints that:
- Check tool registration metadata
- Validate tool schemas
- Apply permissions and filtering
- Track tool usage and state

Direct DB insertion bypasses all of this, so the UI can't see them even though they're in the database.

## Next Steps

1. **Check if OpenWebUI has MCP configuration UI**
   - Look in Settings → Connections or Settings → Tools

2. **If MCP UI exists, configure mcpo there**
   - URL: http://localhost:8002
   - Type: MCP HTTP Server

3. **If no MCP UI, check OpenWebUI version**
   ```bash
   pip show open-webui
   ```
   
   You need v0.6.33+ for native MCP support.

4. **If version is too old, upgrade OpenWebUI**
   ```bash
   pip install --upgrade open-webui
   # Restart OpenWebUI service
   ```

5. **After MCP configuration, tools should appear automatically**

## Testing the MCP Integration

Once configured:

```bash
# Check if OpenWebUI can see MCP tools
curl http://localhost:8080/api/v1/tools/ \
  -H "Authorization: Bearer $TOKEN"

# This should now show all 76 MCP tools
```

## Alternative: Manual Tool Creation (One Example)

If MCP integration doesn't work, create ONE tool as a bridge:

```python
"""
MCP Bridge Tool for OpenWebUI
Proxies calls to mcpo server
"""

class Tools:
    def __init__(self):
        self.MCP_URL = "http://localhost:8002"
    
    def call_mcp_tool(
        self,
        tool_name: str,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
        **kwargs
    ) -> str:
        """
        Call any MCP tool by name.
        
        :param tool_name: Name of the MCP tool (e.g., 'list_tasks')
        :param kwargs: Tool parameters
        :return: Tool result
        """
        import requests
        
        await __event_emitter__({
            "type": "status",
            "data": {"description": f"Calling MCP tool: {tool_name}", "done": False}
        })
        
        response = requests.post(
            f"{self.MCP_URL}/tools/{tool_name}",
            json=kwargs
        )
        
        await __event_emitter__({
            "type": "status",
            "data": {"description": f"MCP tool {tool_name} completed", "done": True}
        })
        
        return response.json()
```

Save this as ONE tool called "mcp_bridge" in OpenWebUI's UI, then you can call any MCP tool through it.

## Summary

**Don't register tools in the database directly!**

Use one of these approaches:
1. ✅ Configure mcpo as an MCP server in OpenWebUI Settings (BEST)
2. ✅ Create tools through OpenWebUI's UI
3. ✅ Create an MCP bridge tool that proxies to mcpo
4. ❌ Direct database insertion (doesn't work)

Check your OpenWebUI version and settings for MCP configuration options!
