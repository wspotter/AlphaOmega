# OpenWebUI MCP Pipeline Activation Guide

## Issue
OpenWebUI is not routing task queries like "what tasks do i have today" to the MCP server, even though:
- ✅ MCP server is running (port 8002)
- ✅ AlphaOmega pipeline exists and works (`/pipelines/alphaomega_router.py`)
- ✅ Pipeline correctly detects "task" intent and routes to MCP
- ✅ MCP tools are registered in OpenWebUI

## Root Cause
**The AlphaOmega pipeline needs to be selected as the active model in OpenWebUI.**

By default, OpenWebUI uses direct Ollama models. The pipeline acts as a "model" that routes to different backends.

## Solution: Activate the Pipeline

### Step 1: Check if Pipeline is Loaded
1. Open OpenWebUI: http://localhost:8080
2. Click the **model dropdown** (top of chat)
3. Look for **"AlphaOmega"** or **"alphaomega_router"** in the list

### Step 2: Select the Pipeline as Your Model
- If you see it: **Click to select "AlphaOmega"**
- This will route ALL your queries through the intelligent pipeline

### Step 3: Test Task Query
Ask: **"what tasks do i have today"**

Expected behavior:
- Pipeline detects "mcp" intent
- Calls `list_tasks` MCP tool
- Returns formatted task list:
  ```
  **Your Tasks:**
  ⏳ 🔴 Test OpenWebUI integration - Verify that tasks work with OpenWebUI
  ⏳ 🔴 Reply to customer inquiry - Sarah Martinez asked about watercolor workshops
  ⏳ 🟡 Order more acrylic paint - Running low on primary colors
  ```

## If Pipeline Not in List

### Option A: Restart OpenWebUI (picks up pipeline changes)
```bash
pkill -f "open-webui"
cd /home/stacy/AlphaOmega
source venv/bin/activate
open-webui serve --host 0.0.0.0 --port 8080 > logs/openwebui.log 2>&1 &
```

Wait 10 seconds, then refresh browser and check model dropdown again.

### Option B: Manually Load Pipeline via Admin
1. Go to **Settings → Admin Settings → Pipelines**
2. Click **"+ Add Pipeline"** or **"Refresh"**
3. Browse to: `/home/stacy/AlphaOmega/pipelines/alphaomega_router.py`
4. Click **Enable**

## Verification

### Test Different MCP Queries
Once pipeline is active, try:
- "what tasks do i have today" → lists tasks
- "show my inventory" → shows stock
- "list customers" → shows customer list
- "what notes do i have" → shows notes

### Check Routing Status
The pipeline logs routing decisions. To see them:
```bash
tail -f /home/stacy/AlphaOmega/logs/openwebui.log | grep -i "routing\|intent"
```

You should see:
```
Routing to mcp...
Intent: mcp
```

## What's Changed

### Pipeline Improvements (just applied)
1. **Fixed syntax error** - Added missing `except` block
2. **Improved task detection** - Now catches:
   - "what tasks do i have today"
   - "show my tasks"
   - "list all tasks"  
   - "what do i need to do today" ← NEW
   
3. **Better MCP keywords** - Added broader patterns:
   - "what do i need to do"
   - "what should i do"
   - "do i have any"

## Architecture Reminder

```
User Query → OpenWebUI → AlphaOmega Pipeline (alphaomega_router.py)
                              ↓
                         Intent Detection
                              ↓
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
    MCP (tasks)          Ollama (chat)      ComfyUI (images)
    port 8002            port 11434         port 8188
```

**The pipeline MUST be selected as the active model for intelligent routing!**

## Quick Test Command

Test pipeline directly (without OpenWebUI):
```bash
cd /home/stacy/AlphaOmega
python test_pipeline_tasks.py
```

This confirms the pipeline logic works. If it does but OpenWebUI doesn't use it, then OpenWebUI isn't configured to use the pipeline as the model.
