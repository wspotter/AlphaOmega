#!/usr/bin/env python3
"""
Register AlphaOmega Router pipeline directly in OpenWebUI database
"""
import sqlite3
import json
from datetime import datetime

# Read pipeline code
with open('/home/stacy/AlphaOmega/pipelines/alphaomega_router.py', 'r') as f:
    pipeline_code = f.read()

# Connect to OpenWebUI database
db_path = '/home/stacy/AlphaOmega/openwebui_data/webui.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get first user (admin)
cursor.execute("SELECT id FROM user LIMIT 1")
user_id = cursor.fetchone()[0]
print(f"Using user_id: {user_id}")

# Check if function already exists
cursor.execute("SELECT id FROM function WHERE id = ?", ("alphaomega_router",))
existing = cursor.fetchone()

# Function metadata
function_id = "alphaomega_router"
name = "AlphaOmega Router"
func_type = "manifold"  # manifold type for multi-model routing
content = pipeline_code
meta = json.dumps({
    "description": "Intelligent router for AlphaOmega: vision, reasoning, code, image gen, agent, MCP",
    "manifest": {
        "name": "AlphaOmega Router",
        "version": "1.0.0",
        "author": "AlphaOmega",
        "description": "Routes requests to Ollama, ComfyUI, Agent-S, or MCP based on intent"
    }
})
timestamp = datetime.utcnow().timestamp()

try:
    if existing:
        print(f"📝 Updating existing function: {function_id}")
        cursor.execute("""
            UPDATE function 
            SET name = ?, type = ?, content = ?, meta = ?, updated_at = ?
            WHERE id = ?
        """, (name, func_type, content, meta, int(timestamp), function_id))
    else:
        print(f"✨ Creating new function: {function_id}")
        cursor.execute("""
            INSERT INTO function (id, user_id, name, type, content, meta, is_active, is_global, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            function_id,
            user_id,  # Use actual user_id
            name,
            func_type,
            content,
            meta,
            1,  # is_active
            1,  # is_global
            int(timestamp),
            int(timestamp)
        ))
    
    conn.commit()
    print("✅ Pipeline registered successfully in database!")
    print(f"\nNext steps:")
    print(f"1. Refresh OpenWebUI: http://localhost:8080")
    print(f"2. Look for 'AlphaOmega Router' in the model dropdown")
    print(f"3. Select it and ask: 'What tasks do I have?'")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
    raise
finally:
    conn.close()
