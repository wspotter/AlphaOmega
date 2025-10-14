# OpenAPI Integration for MCP Tools

## The Alternative Approach

Since MCP native integration didn't work, let's use OpenAPI instead. The mcpo proxy already exposes a complete OpenAPI 3.1.0 specification!

## Step-by-Step Configuration

### 1. Verify OpenAPI Spec is Available

```bash
curl http://localhost:8002/openapi.json | jq '.'
```

You should see:
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "art-supply-store-assistant",
    "description": "art-supply-store-assistant MCP Server",
    "version": "1.0.0"
  },
  "paths": {
    "/check_inventory": { ... },
    "/add_task": { ... },
    ...
  }
}
```

✅ **Confirmed**: mcpo provides full OpenAPI spec with all 76 tools!

### 2. Configure in OpenWebUI Admin Settings

Navigate to: **Settings → Admin Settings → External Tools**

#### Option A: Add as OpenAPI Server

1. Click **"+ Add Server"** or equivalent
2. Select Type: **OpenAPI** (not MCP)
3. Configure:
   - **Name**: `MCP Tools`
   - **URL**: `http://localhost:8002/openapi.json`
   - **Auth**: None (or Bearer token if configured)
   - **Visibility**: Public

4. Click **Save**

#### Option B: Import OpenAPI Spec File

If OpenWebUI has an "Import OpenAPI Spec" option:

1. Download the spec:
   ```bash
   curl http://localhost:8002/openapi.json > /tmp/mcpo-openapi.json
   ```

2. In OpenWebUI Admin Settings → External Tools:
   - Click "Import" or "Upload OpenAPI Spec"
   - Select `/tmp/mcpo-openapi.json`
   - Configure visibility and permissions

### 3. Verify Tools Appear

After configuration:

1. Go to **Workspace → Tools**
2. You should see all 76 tools listed
3. Each tool will have:
   - Name (e.g., `check_inventory`, `add_task`)
   - Description from OpenAPI spec
   - Parameters auto-generated from schema

### 4. Enable Tools for Models

1. In **Workspace → Tools**, click each tool you want to use
2. Toggle "Enable" for specific models or globally
3. Save changes

### 5. Test Tool Calling

In a chat:
```
You: "What tasks do I have?"
```

OpenWebUI should:
1. Recognize the tool call opportunity
2. Call `GET /list_tasks` or `POST /list_tasks`
3. Display results

## Architecture with OpenAPI

```
┌─────────────────────────────────────────────────────────┐
│ OpenWebUI (Port 8080)                                   │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Admin Settings → External Tools                     │ │
│ │   └─> OpenAPI Server: http://localhost:8002         │ │
│ └─────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (OpenAPI 3.1.0)
                         ▼
┌─────────────────────────────────────────────────────────┐
│ mcpo (MCP Proxy) - Port 8002                            │
│ - Exposes OpenAPI spec at /openapi.json                 │
│ - Translates HTTP → MCP stdio                           │
│ - Provides REST endpoints for all tools                 │
└────────────────────────┬────────────────────────────────┘
                         │ stdio
                         ▼
┌─────────────────────────────────────────────────────────┐
│ mcpart (MCP Server) - Port 3000                         │
│ - 76 business tools (tasks, notes, inventory, sales...) │
│ - Node.js MCP implementation                            │
└─────────────────────────────────────────────────────────┘
```

## Why OpenAPI Instead of MCP?

### Advantages:
1. ✅ **More mature support** - OpenAPI has been around longer
2. ✅ **Better tooling** - OpenAPI specs are well-understood by OpenWebUI
3. ✅ **Auto-discovery** - Tools and schemas are automatically parsed
4. ✅ **Standard format** - No experimental protocols

### What You Get:
- All 76 MCP tools exposed as REST endpoints
- Automatic parameter validation from JSON schemas
- Tool descriptions from OpenAPI spec
- No database hacking needed!

## Troubleshooting

### OpenAPI spec not loading?

```bash
# Test the spec is valid
curl http://localhost:8002/openapi.json | jq '.openapi'
# Should return: "3.1.0"

# Check if mcpo is running
curl http://localhost:8002/health
```

### Tools not appearing in OpenWebUI?

1. **Check OpenWebUI logs**:
   ```bash
   tail -f /home/stacy/AlphaOmega/logs/openwebui.log | grep -i openapi
   ```

2. **Try refreshing** the External Tools page

3. **Restart OpenWebUI**:
   ```bash
   pkill -f "open-webui serve"
   cd /home/stacy/AlphaOmega
   source venv/bin/activate
   nohup open-webui serve --port 8080 > logs/openwebui.log 2>&1 &
   ```

### Tool calls failing?

1. **Test endpoint directly**:
   ```bash
   # Example: List tasks
   curl -X POST http://localhost:8002/list_tasks \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

2. **Check mcpo logs**:
   ```bash
   tail -f logs/mcpo.log
   ```

3. **Verify mcpart is responding**:
   ```bash
   curl http://localhost:3000/health
   ```

## Comparison: MCP Native vs OpenAPI

| Feature | MCP Native | OpenAPI |
|---------|------------|---------|
| **Protocol** | MCP Streamable HTTP | OpenAPI 3.1.0 REST |
| **Maturity** | Experimental (v0.6.31+) | Stable, widely supported |
| **Setup** | Configure MCP server URL | Import OpenAPI spec |
| **Tool Discovery** | Via MCP protocol | Via OpenAPI spec |
| **Parameter Types** | MCP JSON schemas | OpenAPI schemas |
| **Documentation** | Limited | Comprehensive |
| **Support** | New feature | Well-established |

## Expected Result

After configuring as OpenAPI server, you should see in **Workspace → Tools**:

```
✓ check_inventory
✓ record_sale
✓ add_task
✓ list_tasks
✓ complete_task
✓ add_note
✓ list_notes
✓ add_expense
✓ list_expenses
... (76 tools total)
```

Each tool will be callable from chat conversations!

## Next Steps

1. **Go to OpenWebUI Admin Settings**
2. **Add OpenAPI server**: `http://localhost:8002/openapi.json`
3. **Verify tools appear** in Workspace → Tools
4. **Enable for your models**
5. **Test**: "What tasks do I have?"

---

**This should work!** OpenAPI is a more mature integration path than the experimental MCP native support.
