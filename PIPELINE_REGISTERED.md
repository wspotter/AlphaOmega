# ✅ FIXED: Pipeline Now Registered!

## What Was The Problem?

When you asked "What tasks do I have?" it hung because:
1. The pipeline file (`alphaomega_router.py`) existed but wasn't loaded
2. OpenWebUI v0.6.33 doesn't auto-load pipelines from directories
3. Pipelines must be registered in the database as "Functions"

## What I Did

✅ Registered the pipeline directly in OpenWebUI's database
✅ Pipeline is now available as "AlphaOmega Router" 
✅ Set to active and global (available to all users)

## How To Use It NOW

### Step 1: Refresh Browser
Press `Ctrl+Shift+R` or `F5` to refresh OpenWebUI

### Step 2: Select the Pipeline
1. Look at the top of the chat where it shows the model name
2. You should currently see "llama3.2-vision:latest" 
3. Click on it to open the dropdown
4. Scroll down and find **"AlphaOmega Router"**
5. Click to select it

### Step 3: Ask Your Question
Now type: **"What tasks do I have?"**

The router will:
1. Detect "tasks" keyword → MCP intent
2. Call `_detect_mcp_tool()` → identifies `list_tasks`  
3. Make HTTP POST to `http://localhost:8002/list_tasks`
4. Format the response with emojis (✅⏳🔴🟡🟢)
5. Stream it back to you

---

## Test Queries To Try

Once you've selected "AlphaOmega Router", try these:

### ✅ Should Route to MCP:
```
What tasks do I have?
Check inventory for paint
Show me all customers
Create a note: Meeting with supplier tomorrow
What were last month's sales?
Post to Instagram: New product launch!
```

### 🎨 Should Route to ComfyUI:
```
Generate an image of a sunset over mountains
Create a picture of a futuristic city
```

### 💻 Should Route to Ollama (code):
```
Write Python code to sort a list
Create a bash script to backup files
```

### 🖱️ Should Route to Agent-S:
```
What's on my screen?
Click the save button
Take a screenshot
```

---

## Troubleshooting

### If you don't see "AlphaOmega Router" in dropdown:

1. **Check OpenWebUI logs:**
   ```bash
   tail -20 /home/stacy/AlphaOmega/logs/openwebui.log | grep -i error
   ```

2. **Verify it's in database:**
   ```bash
   sqlite3 /home/stacy/AlphaOmega/openwebui_data/webui.db \
     "SELECT id, name, type, is_active FROM function;"
   ```
   Should show: `alphaomega_router|AlphaOmega Router|manifold|1`

3. **Re-register if needed:**
   ```bash
   python3 /home/stacy/AlphaOmega/register-pipeline-db.py
   ```

### If it still hangs after selection:

1. **Check MCP server is running:**
   ```bash
   curl -X POST http://localhost:8002/list_tasks \
     -H "Content-Type: application/json" -d '{}'
   ```

2. **Check OpenWebUI can reach MCP:**
   ```bash
   docker exec -it $(docker ps -q -f name=openwebui) curl http://host.docker.internal:8002/openapi.json
   ```
   *(Only if OpenWebUI is in Docker)*

3. **Check pipeline logs:**
   ```bash
   tail -f /home/stacy/AlphaOmega/logs/openwebui.log | grep -i "mcp\|route\|alphaomega"
   ```

---

## How It Works

```
User selects "AlphaOmega Router" model
    ↓
User types: "What tasks do I have?"
    ↓
OpenWebUI calls pipeline's pipe() method
    ↓
_detect_intent("What tasks do I have?") → returns "mcp"
    ↓
_route_to_mcp() called
    ↓
_detect_mcp_tool("What tasks do I have?") → returns ("list_tasks", {})
    ↓
HTTP POST to http://localhost:8002/list_tasks
    ↓
MCP server returns: [{"id": 1, "title": "Task 1", ...}, ...]
    ↓
_format_mcp_response() formats with emojis
    ↓
Streams formatted response back to chat
```

---

## Key Files

- **Pipeline Code**: `/home/stacy/AlphaOmega/pipelines/alphaomega_router.py`
- **Database**: `/home/stacy/AlphaOmega/openwebui_data/webui.db`
- **Registration Script**: `/home/stacy/AlphaOmega/register-pipeline-db.py`
- **OpenWebUI Logs**: `/home/stacy/AlphaOmega/logs/openwebui.log`

---

## Important Notes

### You MUST Select the Pipeline!
- Pipelines of type "manifold" act as models in the dropdown
- You must actively select "AlphaOmega Router" before asking questions
- Once selected, it routes all your messages intelligently

### Why Not Automatic?
- OpenWebUI doesn't have a "default pipeline" concept
- The pipeline acts as a virtual model that you choose
- Think of it like selecting "GPT-4" vs "Claude" - you're selecting "AlphaOmega Router"

### Alternative Approach (Future)
If you want truly automatic routing without selection:
- Create a "Filter" pipeline (runs on ALL messages)
- Or configure OpenWebUI with a proxy that intercepts all traffic
- But for now, model selection is the standard approach

---

## Status

✅ Pipeline registered in database  
✅ Set to active and global  
✅ MCP server running (76 tools)  
✅ OpenWebUI running on port 8080  
✅ Ready to test!

**Next:** Refresh browser, select "AlphaOmega Router", ask "What tasks do I have?"
