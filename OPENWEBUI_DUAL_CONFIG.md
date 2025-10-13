# OpenWebUI Configuration for MCP Integration

## 🎯 Two-Step Configuration Required

OpenWebUI v0.6.32 has **two separate sections** for external services:

### 1️⃣ Connections (for Chat)
### 2️⃣ Tool Servers (for Function Execution)

You need to configure **BOTH** for full MCP integration!

---

## Step 1: Configure Connection (Chat API)

**Location:** Settings → Connections → Add Connection

### Configuration:
```
Name: MCP Art Supply Assistant
Type: OpenAI / OpenAI Compatible
API Base URL: http://localhost:8002
Alternative: http://localhost:8002/v1
Model ID: mcp-assistant
API Key: (leave blank or use "sk-dummy")
```

### What This Does:
- Enables chat interface
- Allows model selection
- Provides basic conversational AI

### Test Connection:
Click "Test Connection" - should show ✅ Success

---

## Step 2: Configure Tool Server (Function Execution)

**Location:** Settings → Tool Servers → Add Tool Server

### Option A: If "Tool Server" supports OpenAI Functions

```
Name: MCP Tools
Type: OpenAI Functions / Function Calling
API Base URL: http://localhost:8002
Alternative: http://localhost:8002/v1
API Key: (leave blank or use "sk-dummy")
```

### Option B: If "Tool Server" expects specific format

```
Name: MCP Tools
Type: Custom / HTTP
Base URL: http://localhost:8002
Tools Endpoint: http://localhost:8002/tools
Execute Endpoint: http://localhost:8002/tools/{tool_name}/execute
```

### What This Does:
- Loads the 76 available tools
- Enables automatic tool execution
- Returns actual results instead of just suggestions

---

## 🧪 Testing Both Configurations

### Test 1: Chat Without Tools
**In OpenWebUI:**
```
"Hello, what can you help me with?"
```

**Expected Response:**
```
I have access to 76 tools including check_inventory, get_low_stock_items, 
update_stock... How can I help you?
```

### Test 2: Tool Execution
**In OpenWebUI:**
```
"What tasks do I have?"
```

**Expected Response (with Tool Server configured):**
```
You have 3 tasks:

1. Test OpenWebUI integration (high priority) - Verify that tasks work with OpenWebUI
2. Order more acrylic paint (medium priority) - Running low on primary colors
3. Reply to customer inquiry (high priority) - Sarah Martinez asked about watercolor workshops
```

**Without Tool Server configured:**
```
Your query has been processed with tool server:mcpart/chat_completions_post, 
resulting in an output that indicates the system is attempting to retrieve 
your tasks using a function call to list_tasks.
```

---

## 📊 Available Endpoints

Our MCP bridge provides multiple endpoints for different use cases:

### Chat Endpoints (for Connections)
- `GET http://localhost:8002/` - Health check
- `GET http://localhost:8002/models` - List models
- `GET http://localhost:8002/v1/models` - List models (v1)
- `POST http://localhost:8002/chat/completions` - Chat completions
- `POST http://localhost:8002/v1/chat/completions` - Chat completions (v1)

### Tool Endpoints (for Tool Servers)
- `GET http://localhost:8002/tools` - List all 76 tools
- `POST http://localhost:8002/tools/{tool_name}/execute` - Execute specific tool

### Examples:

#### List Tools
```bash
curl http://localhost:8002/tools
```

#### Execute a Tool
```bash
# List tasks
curl -X POST http://localhost:8002/tools/list_tasks/execute \
  -H "Content-Type: application/json" \
  -d '{}'

# Create a task
curl -X POST http://localhost:8002/tools/create_task/execute \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Restock paint brushes",
    "description": "Low on synthetic brush sets",
    "priority": "medium"
  }'

# Check inventory
curl -X POST http://localhost:8002/tools/check_inventory/execute \
  -H "Content-Type: application/json" \
  -d '{"search": "acrylic paint"}'

# Search notes
curl -X POST http://localhost:8002/tools/search_notes/execute \
  -H "Content-Type: application/json" \
  -d '{"query": "supplier"}'
```

---

## 🛠️ Tool Server Configuration Examples

### If OpenWebUI Tool Server UI looks like this:

**Format 1: Simple URL**
```
Tool Server URL: http://localhost:8002/tools
```

**Format 2: Detailed**
```
Base URL: http://localhost:8002
Tools List Endpoint: /tools
Execute Endpoint: /tools/{tool_name}/execute
Method: POST
Headers: Content-Type: application/json
```

**Format 3: OpenAI-Compatible**
```
API Type: OpenAI Functions
Base URL: http://localhost:8002
API Key: sk-dummy (or leave blank)
```

---

## 🔍 Troubleshooting

### Issue 1: Tools Detected But Not Executed

**Symptom:** OpenWebUI shows "attempting to retrieve your tasks using function call to list_tasks" but no actual results.

**Cause:** Connection configured but Tool Server not configured.

**Fix:** Add Tool Server configuration (Step 2 above).

### Issue 2: Connection Test Fails

**Check:**
```bash
# Verify bridge is running
curl http://localhost:8002/

# Should return:
# {"service":"MCP OpenAI Bridge","tools_loaded":76,"status":"running"}
```

**If not running:**
```bash
cd /home/stacy/AlphaOmega
python agent_s/mcp/openai_bridge.py &
```

### Issue 3: Tools Not Showing Up

**Check:**
```bash
# Verify tools are loaded
curl http://localhost:8002/tools | jq '.count'

# Should return: 76
```

### Issue 4: Tool Execution Returns Empty Results

**Create sample data first:**
```bash
# Create a task
curl -X POST http://localhost:8002/tools/create_task/execute \
  -d '{"title":"Test task","priority":"high"}'

# Now list tasks should return results
curl -X POST http://localhost:8002/tools/list_tasks/execute -d '{}'
```

---

## 📝 Complete Configuration Checklist

- [ ] **Connection configured** in Settings → Connections
  - [ ] URL: http://localhost:8002
  - [ ] Type: OpenAI Compatible
  - [ ] Test Connection: ✅ Success

- [ ] **Tool Server configured** in Settings → Tool Servers
  - [ ] Base URL: http://localhost:8002
  - [ ] Tools endpoint accessible
  - [ ] Test shows 76 tools loaded

- [ ] **Sample data created** (for testing)
  - [ ] At least one task
  - [ ] At least one note
  - [ ] At least one expense

- [ ] **Test queries working**
  - [ ] "What tasks do I have?" → Shows actual task list
  - [ ] "Search notes for supplier" → Shows note content
  - [ ] "Check inventory for paint" → Shows inventory data

---

## 🎯 Quick Setup Commands

### Start the Bridge
```bash
cd /home/stacy/AlphaOmega
python agent_s/mcp/openai_bridge.py > logs/openai-bridge.log 2>&1 &
```

### Create Sample Data
```bash
# Tasks
curl -X POST http://localhost:8002/tools/create_task/execute \
  -d '{"title":"Restock paint","priority":"high"}'

# Notes
curl -X POST http://localhost:8002/tools/create_note/execute \
  -d '{"title":"Supplier info","content":"ArtCo offers 15% bulk discount"}'

# Expenses
curl -X POST http://localhost:8002/tools/log_expense/execute \
  -d '{"description":"Lunch meeting","amount":45.50,"category":"Meals"}'
```

### Verify Tools
```bash
# Check bridge status
curl http://localhost:8002/ | jq .

# List all tools
curl http://localhost:8002/tools | jq '.count'

# Test a tool
curl -X POST http://localhost:8002/tools/list_tasks/execute -d '{}' | jq .
```

---

## 📖 Current Sample Data

You already have this data loaded:

### Tasks (3)
1. ✅ "Test OpenWebUI integration" (high) - Verify that tasks work
2. ✅ "Order more acrylic paint" (medium) - Running low on primary colors
3. ✅ "Reply to customer inquiry" (high) - Sarah asked about workshops

### Notes (1)
- ✅ "Supplier meeting notes" - 15% discount on bulk orders over $500

### Expenses (1)
- ✅ $45.50 - Business lunch with new supplier (Meals category)

### Inventory (Mock Data)
- 8 products pre-loaded in mcpart
- Includes: Acrylic Paint Sets, Watercolor Sets, Canvas, Brushes, etc.

---

## 🚀 What to Do Next

1. **In OpenWebUI Settings:**
   - Go to **Connections** → Configure chat API
   - Go to **Tool Servers** → Configure tool execution

2. **Test Both Configurations:**
   - Basic chat: "Hello"
   - Tool execution: "What tasks do I have?"

3. **Report Back:**
   - Does Tool Server section have an "Add" or "Configure" button?
   - What fields does the Tool Server form have?
   - Are tools now executing and showing results?

Once both are configured, you'll get the full experience with automatic tool execution! 🎉

---

**Bridge Status:** ✅ Running on http://localhost:8002  
**Tools Available:** 76  
**Sample Data:** Loaded  
**Ready for:** Dual configuration in OpenWebUI
