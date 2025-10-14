# MCP Routing Test Guide

## ✅ Completed Setup

1. ✅ **MCP Server Running**: 76 business tools on port 8002
2. ✅ **Pipeline Updated**: `alphaomega_router.py` now has automatic MCP tool detection
3. ✅ **OpenWebUI Restarted**: Running on port 8080 with updated pipeline loaded
4. ✅ **Syntax Validated**: No Python errors in router code

## 🧪 Testing the MCP Routing

### Step 1: Access OpenWebUI
Open your browser to: http://localhost:8080

### Step 2: Verify Pipeline is Loaded
1. Go to **Admin Settings** → **Pipelines**
2. Look for **"AlphaOmega Router"**
3. Make sure it's **enabled** (toggle should be ON)

### Step 3: Test MCP Tool Routing

The router automatically detects when you need MCP tools based on keywords. Try these test queries:

#### 🔴 **Task Management Tests**
```
User: What tasks do I have?
User: Show me all my tasks
User: Add a new task: Review quarterly report
User: Mark task #1 as complete
```

**Expected**: Router detects "tasks" keyword → routes to `/list_tasks` → returns formatted task list with status emojis (✅⏳)

---

#### 📦 **Inventory Tests**
```
User: Check inventory for paint
User: What's in stock for nails?
User: Show me low stock items
User: Do we have hammers in stock?
```

**Expected**: Router detects "inventory/stock" keywords → routes to `/check_inventory` → returns product details with quantity

---

#### 👥 **Customer Management Tests**
```
User: List all customers
User: Show me customer details for John Doe
User: Find customers in New York
User: Add new customer: Jane Smith
```

**Expected**: Router detects "customer" keyword → routes to `/list_customers` → returns customer list with contact info

---

#### 📝 **Notes Tests**
```
User: Show my notes
User: Create a note: Meeting with client tomorrow
User: Search notes for "budget"
```

**Expected**: Router detects "notes" keyword → routes to `/list_notes` or `/create_note` → returns formatted notes

---

#### 💰 **Sales/Expenses Tests**
```
User: Show sales report
User: List recent expenses
User: What was revenue last month?
User: Add expense: Office supplies $50
```

**Expected**: Router detects "sales/expenses/revenue" keywords → routes to appropriate tool → returns financial data

---

#### 📱 **Social Media Tests**
```
User: Check Instagram notifications
User: Show Facebook messages
User: Post to Instagram: "New product launch!"
```

**Expected**: Router detects "Instagram/Facebook" keywords → routes to social media tools → returns status/messages

---

## 🔍 Debugging If Something Goes Wrong

### Check Pipeline Logs
```bash
tail -f /home/stacy/AlphaOmega/logs/openwebui.log | grep -i "mcp\|route\|intent"
```

### Verify MCP Server is Responding
```bash
curl -X POST http://localhost:8002/list_tasks -H "Content-Type: application/json" -d '{}'
```

### Check Router Intent Detection
The router uses these keywords to detect MCP intent:
- **Tasks**: task, tasks, todo, todos
- **Inventory**: inventory, stock, product, supply
- **Customers**: customer, customers, client, clients, contact
- **Notes**: note, notes, memo, reminder
- **Sales/Expenses**: sales, expenses, expense, revenue, profit, cost
- **Appointments**: appointment, appointments, schedule, calendar, meeting
- **Social Media**: instagram, facebook, social, post, message
- **VIP/Tier**: vip, tier, membership, premium, level

### Manual Tool Testing
Test individual MCP tools directly:

```bash
# List tasks
curl -X POST http://localhost:8002/list_tasks \
  -H "Content-Type: application/json" -d '{}'

# Check inventory
curl -X POST http://localhost:8002/check_inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name":"paint"}'

# List customers
curl -X POST http://localhost:8002/list_customers \
  -H "Content-Type: application/json" -d '{}'

# Create note
curl -X POST http://localhost:8002/create_note \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Note","content":"This is a test"}'
```

## 📊 Expected Behavior

### ✅ Success Indicators
- Router responds within 1-2 seconds
- Results include emoji formatting (🔴🟡🟢 for priorities, ✅⏳ for status)
- Data matches what you see in manual curl tests
- No error messages about "tool not found" or "endpoint not found"

### ❌ Failure Indicators
- Error: "MCP server not responding" → Check if MCP server is running
- Error: "Tool not found" → Check `_detect_mcp_tool()` method in router
- No response at all → Check OpenWebUI logs for Python exceptions
- Generic response → Router didn't detect MCP intent, check keywords

## 🎯 What We Changed

### Before (Problem):
- Python bridge created fake "mcp-assistant" model
- OpenWebUI showed 76 tools as single on/off switch
- Tools weren't being called automatically

### After (Solution):
- Direct HTTP routing to MCP server tools
- AI automatically detects which tool to use based on conversation
- No manual tool selection required
- Formatted, user-friendly responses

## 🚀 Next Steps After Testing

1. **If tests pass**: You're done! MCP tools now work automatically via AI detection
2. **If tests fail**: Check debugging section above and report specific error messages
3. **Optional**: Add more keywords to `_detect_intent()` method for better detection
4. **Future enhancement**: Migrate to pure FastAPI OpenAPI server for even better tool discovery

## 📌 Key Files
- Pipeline: `/home/stacy/AlphaOmega/pipelines/alphaomega_router.py`
- MCP Server Start: `/home/stacy/AlphaOmega/scripts/start-mcp-unified.sh`
- OpenWebUI Logs: `/home/stacy/AlphaOmega/logs/openwebui.log`
- MCP Server Logs: `/home/stacy/AlphaOmega/logs/mcp-server.log`

## 💡 Pro Tips
- Use natural language: "What tasks do I have?" works better than "list_tasks"
- Be specific: "Check inventory for paint" is better than "inventory"
- Test one category at a time to isolate issues
- Check logs frequently during testing to see router decisions

---

**Status**: ✅ Ready to test! MCP routing is deployed and active.

**Your goal**: Confirm AI automatically uses the right tools without you having to select them manually.
