# 🔧 FIXING THE HANGING ISSUE - Pipeline Not Loaded

## Problem
When you ask "What tasks do I have?" it hangs because **the pipeline isn't loaded into OpenWebUI**.

## Root Cause
OpenWebUI v0.6.33 doesn't automatically load pipelines from the `PIPELINES_DIR`. Instead, pipelines (called "Functions") must be:
1. Uploaded through the Admin UI, OR
2. Added via the API, OR  
3. Stored in the database

## Quick Fix - Upload via UI (RECOMMENDED)

### Step 1: Access OpenWebUI Admin
1. Open: http://localhost:8080
2. Click your profile icon (top right)
3. Go to **Admin Settings**
4. Click **Functions** (left sidebar)

### Step 2: Upload the Pipeline
1. Click **"+ Add Function"** or **"Import"**
2. Navigate to: `/home/stacy/AlphaOmega/pipelines/alphaomega_router.py`
3. Or paste the code directly
4. Click **Save**

### Step 3: Enable the Pipeline
1. Find **"AlphaOmega Router"** in the Functions list
2. Toggle it **ON** (enable it)
3. Make sure it's set as a **Manifold** type

### Step 4: Test
1. Go back to Chat
2. In the model selector dropdown, you should see: **"AlphaOmega Router"**
3. Select it
4. Ask: "What tasks do I have?"

---

## Alternative Fix - Use Separate Model Approach

If the pipeline upload doesn't work, we can configure OpenWebUI to route directly to Ollama and handle MCP in a different way:

### Option A: Use OpenWebUI's native tool/function calling
- OpenWebUI can call external APIs
- We expose MCP tools as OpenWebUI functions
- Each tool becomes selectable in the UI

### Option B: Use a middleware approach
- Keep Ollama as the main model
- Add MCP as a "tool server" in OpenWebUI settings
- Tools appear automatically in chat

### Option C: Use the Filter/Pipeline approach (simpler)
- Create a Filter pipeline (runs on every message)
- Filter detects MCP intents and routes accordingly
- Doesn't require model selection

---

## Verification Commands

### Check if pipeline is loaded:
```bash
# This won't work without authentication, but you can check in the UI
curl -s http://localhost:8080/api/v1/functions/ | jq '.'
```

### Check OpenWebUI logs for pipeline loading:
```bash
tail -f /home/stacy/AlphaOmega/logs/openwebui.log | grep -i "function\|pipeline"
```

### Test MCP server is still working:
```bash
curl -X POST http://localhost:8002/list_tasks \
  -H "Content-Type: application/json" -d '{}'
```

---

## Next Steps

I recommend **Option A** (Upload via UI) because it's the quickest.

Once uploaded and enabled:
1. You'll see "AlphaOmega Router" in model dropdown
2. Select it before asking questions
3. The router will automatically detect MCP intents and route to tools

---

## Why Did This Happen?

OpenWebUI changed how pipelines work between versions:
- **Old way** (v0.3.x): `PIPELINES_DIR` auto-loaded all .py files
- **New way** (v0.6.x): Functions stored in database, uploaded via UI/API

Your pipeline file exists and is syntactically correct, but OpenWebUI doesn't know about it yet.

---

## If You Want Automatic Loading (Advanced)

Create a startup script that registers the pipeline via API on every boot:

```bash
# Add to scripts/start-openwebui.sh (after OpenWebUI starts):
sleep 5  # Wait for OpenWebUI to be ready
python3 /home/stacy/AlphaOmega/register-pipeline.py
```

But for now, **just upload it via the UI** - it's faster!
