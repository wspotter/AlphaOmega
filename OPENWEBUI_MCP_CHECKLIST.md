# ✅ CHECKLIST: Connect OpenWebUI to MCP Server

**Your Setup:**
- ✅ OpenWebUI v0.6.32 (supports MCP!)
- ✅ MCP Server running on port 8002
- ✅ 76 tools available
- ❌ OpenWebUI not configured to use MCP server

---

## Follow These Exact Steps:

### 1. Open OpenWebUI Admin
- [ ] Go to: http://localhost:8080
- [ ] Click **⚙️ Settings** (gear icon, top right)
- [ ] Click **Admin Panel** or **Admin Settings**

### 2. Find External Tools Section
Look for one of these:
- [ ] **Admin Settings → External Tools**
- [ ] **Admin Settings → Tools**
- [ ] **Settings → Tools → Tool Servers**

### 3. Add MCP Server
- [ ] Click **+ (Add Server)** or **Add Connection**
- [ ] Fill in these EXACT values:

```
┌─────────────────────────────────────────┐
│ Type: MCP (Streamable HTTP)             │  ← CRITICAL: Must select MCP!
│ Name: AlphaOmega Tools                  │
│ Server URL: http://localhost:8002       │
│ ID: alphaomega-mcp                      │
│ Auth: None                              │
└─────────────────────────────────────────┘
```

### 4. Save and Test
- [ ] Click **Save** or **Add**
- [ ] Refresh OpenWebUI page (F5)
- [ ] Open a new chat

### 5. Verify Tools Loaded
- [ ] In chat, click **🔧 Tools** icon (near message input)
- [ ] You should see 76 tools listed
- [ ] Example tools: `list_tasks`, `check_inventory`, `create_task`

### 6. Test Tool Execution
Try these queries in chat:

- [ ] "What tasks do I have?"
  - Should call `list_tasks` and show actual tasks
  
- [ ] "Check inventory for paint"
  - Should call `check_inventory` with search="paint"
  
- [ ] "Search my notes for customer"
  - Should call `search_notes` with query="customer"

---

## If It Works ✅

You'll see:
```
User: What tasks do I have today?

🔧 Using tool: list_tasks
{
  "status": "success",
  "tasks": [
    {
      "id": 1,
      "title": "Test OpenWebUI integration",
      "priority": "high"
    },
    ...
  ]
}