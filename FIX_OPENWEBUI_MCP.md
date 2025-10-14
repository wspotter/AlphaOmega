# 🔧 FIX: OpenWebUI Not Calling MCP Tools

## The Problem

- MCP server is running on port 8002 ✅
- OpenWebUI is checking `/openapi.json` ✅  
- But when you ask "What are my tasks?", OpenWebUI doesn't call the tools ❌

## Why?

**You haven't configured OpenWebUI to USE the MCP server yet!**

The server is running but OpenWebUI doesn't know about it.

---

## The Solution (2 minutes)

### Step 1: Open OpenWebUI Admin Settings

1. Go to http://localhost:8080
2. Click **⚙️** (Settings) in top right
3. Click **Admin Panel** or **Admin Settings**
4. Navigate to **External Tools** (or **Tools** section)

### Step 2: Add MCP Server

Click **+ (Add Server)** and configure:

```
Type: MCP (Streamable HTTP)  ← IMPORTANT: Select MCP, NOT OpenAPI!
Name: AlphaOmega Tools
Server URL: http://localhost:8002
ID: alphaomega-mcp
Auth: None
```

**Screenshot reference:** You should see a dropdown for "Type" - select **MCP (Streamable HTTP)**

### Step 3: Save and Restart (if prompted)

- Click **Save**
- If prompted, restart Open WebUI (or just refresh the page)

### Step 4: Test

In a new chat, ask:
```
What tasks do I have today?
```

OpenWebUI should now:
1. Detect this needs the `list_tasks` tool
2. Call http://localhost:8002/list_tasks
3. Show you the actual task list

---

## Alternative: If "MCP (Streamable HTTP)" Option Doesn't Appear

Some OpenWebUI versions might not show "MCP" as an option if you're on an older version.

**Check your OpenWebUI version:**

1. In OpenWebUI, click profile icon
2. Look for "About" or "Version"
3. You need **v0.6.31+** for native MCP support

**If you're on an older version:**

```bash
# Upgrade OpenWebUI
cd ~
source open-webui-venv/bin/activate
pip install --upgrade open-webui
open-webui serve --port 8080
```

---

## Verify Tools Are Loaded

After adding the MCP server:

1. Go to chat
2. Click the **🔧 Tools** icon (usually near the message input)
3. You should see all 76 tools listed:
   - list_tasks
   - create_task
   - check_inventory
   - add_customer
   - etc.

---

## Quick Test Commands

### Direct API Test (bypass OpenWebUI):
```bash
curl -X POST http://localhost:8002/list_tasks \
  -H "Content-Type: application/json" \
  -d '{}'
```

Should return your task list.

### In OpenWebUI Chat:

```
User: What tasks do I have?
Expected: Shows actual task list from data/tasks.json

User: Check inventory for paint
Expected: Shows paint inventory items

User: Search my notes for customer
Expected: Shows notes containing "customer"
```

---

## Troubleshooting

### Issue: Can't find "External Tools" in Admin

**Location varies by version:**
- Try: **Admin Settings → Tools**
- Try: **Settings → Admin → External Tools**
- Try: **Settings → Connections → Tool Servers**

### Issue: MCP option not available

**You need OpenWebUI v0.6.31+**

Check version and upgrade if needed.

### Issue: Tools show but don't execute

**Check logs:**
```bash
# OpenWebUI logs
journalctl -u openwebui -f

# MCP server logs
tail -f logs/mcp-unified.log
```

You should see incoming POST requests when tools are called.

### Issue: "Connection failed" when testing

**Verify MCP server is accessible:**
```bash
curl http://localhost:8002/openapi.json
```

If this fails, restart MCP server:
```bash
./scripts/start-mcp-unified.sh
```

---

## What You Should See

### Before Configuration:
```
User: What tasks do I have?
Assistant: I don't have access to task information...
```

### After Configuration:
```
User: What tasks do I have?
Assistant: [Calls list_tasks tool] You have 3 tasks:
1. Test OpenWebUI integration (high priority)
2. Order more acrylic paint (medium priority)
3. Reply to customer inquiry (high priority)
```

---

## Summary

**The Fix:**
1. Admin Settings → External Tools
2. Add Server → Type: **MCP (Streamable HTTP)**
3. URL: http://localhost:8002
4. Save

**That's it!** OpenWebUI will now automatically call your MCP tools when relevant.

---

**Last Updated:** October 13, 2025  
**MCP Server:** Running on port 8002 with 76 tools  
**Required OpenWebUI Version:** v0.6.31+
