# OpenWebUI External Tools Configuration - Step by Step

## Based on Your Screenshot

I can see you already have the External Tools configuration open. Here's what to do next:

## Option 1: Try OpenAPI Instead of MCP

### Current Configuration (MCP - Not Working)
- Type: `MCP Streamable HTTP`
- URL: `http://localhost:8002`
- ID: `mcpstrean`
- Name: `mcp`

### **NEW: Try OpenAPI Configuration**

1. **Delete the current MCP server** (click the trash icon or delete button)

2. **Click "+ Add Server"** (or similar button in the top-right)

3. **Configure as OpenAPI**:
   ```
   Type: OpenAPI
   URL: http://localhost:8002/openapi.json
   Name: MCP Tools (OpenAPI)
   Auth: None (or Bearer if you have a token)
   Visibility: Public
   ```

4. **Save** the configuration

5. **Restart OpenWebUI**:
   ```bash
   pkill -f "open-webui serve"
   cd /home/stacy/AlphaOmega
   source venv/bin/activate
   nohup open-webui serve --port 8080 > logs/openwebui.log 2>&1 &
   ```

6. **Check Workspace → Tools** - You should now see 76 tools!

## Why This Should Work

OpenWebUI's OpenAPI support is **more mature** than MCP native support:

- ✅ OpenAPI 3.1.0 is a standard, proven protocol
- ✅ Your mcpo proxy already exposes a full OpenAPI spec
- ✅ Better auto-discovery of tools and parameters
- ✅ Wider tooling support in OpenWebUI

## What the OpenAPI Spec Provides

```bash
curl http://localhost:8002/openapi.json | jq '.paths | keys'
```

This returns all 76 tool endpoints:
```json
[
  "/add_customer",
  "/add_expense",
  "/add_note",
  "/add_task",
  "/check_inventory",
  "/complete_task",
  "/create_post",
  "/delete_note",
  "/delete_task",
  "/list_customers",
  "/list_expenses",
  "/list_notes",
  "/list_orders",
  "/list_posts",
  "/list_tasks",
  "/record_sale",
  "/reorder_supplies",
  "/schedule_social_post",
  "/update_customer",
  "/update_inventory",
  ... (76 total)
]
```

Each endpoint has:
- ✅ Description
- ✅ Parameter schemas (JSON Schema)
- ✅ Request/response models
- ✅ Operation IDs

## Verification After Setup

1. **Check External Tools page**:
   - Should show "MCP Tools (OpenAPI)" with green status

2. **Check Workspace → Tools**:
   - Should list all 76 tools
   - Each tool should have its description
   - Parameters should be auto-populated

3. **Test in chat**:
   ```
   "What tasks do I have?"
   "List my inventory"
   "Show me my notes"
   ```

## Troubleshooting

### Tools still not showing?

1. **Check the OpenAPI spec is accessible**:
   ```bash
   curl http://localhost:8002/openapi.json
   ```
   Should return valid JSON

2. **Check OpenWebUI logs**:
   ```bash
   tail -f /home/stacy/AlphaOmega/logs/openwebui.log | grep -i "openapi\|tool"
   ```

3. **Verify mcpo is running**:
   ```bash
   curl http://localhost:8002/health
   ps aux | grep mcpo
   ```

4. **Try a different URL format**:
   - `http://localhost:8002/openapi.json` (with /openapi.json)
   - `http://localhost:8002` (base URL, let OpenWebUI find the spec)
   - `http://127.0.0.1:8002/openapi.json` (use 127.0.0.1 instead of localhost)

### Authentication Issues?

If you configured Bearer auth in your MCP server:
```
Auth Type: Bearer
Token: YOUR_TOKEN_HERE
```

## Next Steps After It Works

1. **Enable tools for your models**:
   - Workspace → Tools → Click each tool
   - Toggle "Enable for all models" or select specific models

2. **Test different tool categories**:
   - Task management: "Add a task", "List tasks", "Complete task X"
   - Note taking: "Add a note", "List my notes"
   - Inventory: "Check inventory for art supplies"
   - Sales: "Record a sale", "List recent orders"

3. **Monitor usage**:
   ```bash
   # Watch tool calls in real-time
   tail -f logs/openwebui.log logs/mcpo.log
   ```

## Expected Result

After switching to OpenAPI, you should see:

```
✅ External Tools page shows "MCP Tools (OpenAPI)" connected
✅ Workspace → Tools shows 76 tools
✅ Chat queries trigger appropriate tool calls
✅ Results display in chat conversations
```

---

**Try this now!** The OpenAPI approach should work better than MCP native support.
