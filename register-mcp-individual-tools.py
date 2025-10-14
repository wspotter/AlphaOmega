#!/usr/bin/env python3
"""
Register MCP tools as individual OpenWebUI tools (one per endpoint)
This creates separate tool registrations that OpenWebUI can actually call
"""
import sqlite3
import json
import requests
from datetime import datetime

# Download OpenAPI spec
print("📥 Fetching OpenAPI spec from mcpo server...")
response = requests.get("http://localhost:8002/openapi.json")
openapi_spec = response.json()

print(f"✓ Found {len(openapi_spec['paths'])} endpoints")

# Connect to database
db_path = '/home/stacy/AlphaOmega/openwebui_data/webui.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get admin user
cursor.execute("SELECT id FROM user LIMIT 1")
user_id = cursor.fetchone()[0]

timestamp = int(datetime.now().timestamp())
registered_count = 0

# Register each tool individually
for path, methods in openapi_spec['paths'].items():
    for method, spec in methods.items():
        if method.lower() != 'post':
            continue
        
        # Generate tool details
        operation_id = spec.get('operationId', path.replace('/', '_').strip('_'))
        summary = spec.get('summary', f'Call {path}')
        description = spec.get('description', summary)
        
        # Tool ID
        tool_id = f"mcp_{operation_id}"
        tool_name = summary
        
        # Create content - direct HTTP call function
        tool_content = f'''"""
{description}
"""
import requests
from typing import Dict, Any
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        MCP_SERVER_URL: str = Field(
            default="http://localhost:8002",
            description="MCP server base URL"
        )
    
    def __init__(self):
        self.valves = self.Valves()
    
    def {operation_id}(self, **kwargs) -> Dict[str, Any]:
        """
        {description}
        """
        try:
            response = requests.post(
                f"{{self.valves.MCP_SERVER_URL}}{path}",
                json=kwargs,
                headers={{"Content-Type": "application/json"}},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {{"error": str(e)}}
'''
        
        # Specs
        tool_specs = [{
            "id": tool_id,
            "name": tool_name,
            "url": f"http://localhost:8002{path}",
            "method": "POST",
            "description": description
        }]
        
        # Meta
        tool_meta = {
            "description": description,
            "manifest": {
                "name": tool_name,
                "version": "1.0.0",
                "author": "AlphaOmega MCP",
                "endpoint": path
            }
        }
        
        # Check if exists
        cursor.execute("SELECT id FROM tool WHERE id = ?", (tool_id,))
        existing = cursor.fetchone()
        
        try:
            if existing:
                cursor.execute("""
                    UPDATE tool 
                    SET name = ?, content = ?, specs = ?, meta = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    tool_name,
                    tool_content,
                    json.dumps(tool_specs),
                    json.dumps(tool_meta),
                    timestamp,
                    tool_id
                ))
            else:
                cursor.execute("""
                    INSERT INTO tool (id, user_id, name, content, specs, meta, created_at, updated_at, valves, access_control)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tool_id,
                    user_id,
                    tool_name,
                    tool_content,
                    json.dumps(tool_specs),
                    json.dumps(tool_meta),
                    timestamp,
                    timestamp,
                    json.dumps({"MCP_SERVER_URL": "http://localhost:8002"}),
                    None
                ))
            
            registered_count += 1
            print(f"  ✓ {operation_id}")
            
        except Exception as e:
            print(f"  ✗ {operation_id}: {e}")

conn.commit()
conn.close()

print(f"\n✅ Registered {registered_count} tools!")
print(f"\n🎯 Next Steps:")
print(f"   1. Refresh OpenWebUI (Ctrl+Shift+R)")
print(f"   2. Click 🔧 Tools icon in chat")
print(f"   3. Enable the tools you want to use")
print(f"   4. Start chatting - LLM will call tools automatically!")
