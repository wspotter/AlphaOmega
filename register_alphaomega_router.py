#!/usr/bin/env python3
"""
Register AlphaOmega unified router pipeline in OpenWebUI database
"""
import sqlite3
import time
import bcrypt

DB_PATH = "/home/stacy/AlphaOmega/openwebui_data/webui.db"
PIPELINE_PATH = "/home/stacy/AlphaOmega/pipelines/alphaomega_router.py"

# Read the pipeline code
with open(PIPELINE_PATH, 'r') as f:
    pipeline_code = f.read()

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Get admin user ID
    cursor.execute("SELECT id FROM user WHERE email = 'admin@localhost'")
    user_result = cursor.fetchone()
    
    if not user_result:
        print("❌ Admin user not found!")
        exit(1)
    
    user_id = user_result[0]
    print(f"✅ Found admin user: {user_id}")
    
    # Delete any existing registration
    cursor.execute("DELETE FROM function WHERE id = 'alphaomega_router'")
    
    # Register the pipeline
    timestamp = int(time.time())
    
    # Meta information for the function
    meta = {
        "description": "Intelligent router for AlphaOmega multi-backend system. Automatically detects intent and routes to Ollama, Agent-S, ComfyUI, or MCP.",
        "manifest": {
            "name": "AlphaOmega Router",
            "id": "alphaomega_router",
            "version": "1.0.0"
        }
    }
    
    import json
    meta_json = json.dumps(meta)
    
    cursor.execute("""
        INSERT INTO function 
        (id, user_id, name, type, content, meta, is_active, is_global, updated_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "alphaomega_router",  # id
        user_id,  # user_id
        "AlphaOmega",  # name (from Pipeline.__init__)
        "pipe",  # type (standard pipe, not manifold)
        pipeline_code,  # content
        meta_json,  # meta
        1,  # is_active
        1,  # is_global
        timestamp,  # updated_at
        timestamp  # created_at
    ))
    
    conn.commit()
    print("✅ AlphaOmega Router registered successfully!")
    print("\nNext steps:")
    print("1. Refresh OpenWebUI in your browser: http://localhost:8080")
    print("2. Look for 'AlphaOmega' in the model dropdown")
    print("3. Test with:")
    print("   - 'What's on my screen?' (Agent-S)")
    print("   - 'List my tasks' (MCP)")
    print("   - 'Write a Python function to sort a list' (Code)")
    print("   - 'What is the meaning of life?' (Reasoning)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    raise
finally:
    conn.close()
