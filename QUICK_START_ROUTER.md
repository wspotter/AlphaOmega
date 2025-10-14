# 🚀 QUICK START - Using AlphaOmega Router

## Issue Fixed! ✅

The hanging was because the pipeline wasn't loaded. **It's now registered!**

---

## Steps To Use (30 seconds):

### 1. Refresh Browser
Press **F5** or **Ctrl+Shift+R** at http://localhost:8080

### 2. Select Pipeline
- Click the model name at top (currently shows "llama3.2-vision:latest")
- Find **"AlphaOmega Router"** in dropdown
- Click it to select

### 3. Ask Your Question
Type: **"What tasks do I have?"**

**It should now respond with your task list!** ✅

---

## What If It's Still Not There?

Run this to re-register:
```bash
python3 /home/stacy/AlphaOmega/register-pipeline-db.py
```

Then refresh browser again.

---

## Quick Test Commands

After selecting AlphaOmega Router:

| Query | Expected Route | Tool Called |
|-------|---------------|-------------|
| What tasks do I have? | MCP | list_tasks |
| Check inventory for paint | MCP | check_inventory |
| Show me all customers | MCP | list_customers |
| Generate a sunset image | ComfyUI | image_generation |
| Write Python sorting code | Ollama | code_model |

---

## Key Point

**You MUST select "AlphaOmega Router" in the model dropdown.**

It acts as a smart model that routes to the right backend automatically.

Think of it as: **You pick the router, it picks the tool.**

---

## Files Created

- ✅ `/home/stacy/AlphaOmega/register-pipeline-db.py` - Registration script
- ✅ `/home/stacy/AlphaOmega/FIX_HANGING_ISSUE.md` - Detailed explanation  
- ✅ `/home/stacy/AlphaOmega/PIPELINE_REGISTERED.md` - Complete guide
- ✅ `/home/stacy/AlphaOmega/QUICK_START_ROUTER.md` - This file

---

**TL;DR:** Refresh → Select "AlphaOmega Router" → Ask "What tasks do I have?" → Should work! 🎉
