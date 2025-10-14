#!/usr/bin/env python3
"""
Register MCP tools via OpenAPI in OpenWebUI database
This is the CORRECT way - no pipelines, no fake models, just tools!
"""
import sqlite3
import json
import requests
from datetime import datetime

# Download OpenAPI spec
print("📥 Fetching OpenAPI spec from mcpo server...")
response = requests.get("http://localhost:8002/openapi.json")
openapi_spec = response.json()

print(f"✓ Found {len(openapi_spec['paths'])} tools")
print(f"  Server: {openapi_spec['info']['title']}")
print(f"  Version: {openapi_spec['info']['version']}")

# Connect to OpenWebUI database
db_path = '/home/stacy/AlphaOmega/openwebui_data/webui.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get admin user
cursor.execute("SELECT id FROM user LIMIT 1")
user_id = cursor.fetchone()[0]
print(f"✓ Using user_id: {user_id}")

# Prepare tool data
tool_id = "mcp_tools_openapi"
tool_name = "AlphaOmega MCP Tools"
timestamp = int(datetime.now().timestamp())

# Create tool content (Python code that calls the OpenAPI endpoints)
tool_content = '''"""
AlphaOmega MCP Tools - OpenAPI Integration
Auto-generated tool wrapper for all MCP server endpoints
"""
import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Tools:
    """OpenAPI tool wrapper for MCP server"""
    
    def __init__(self):
        self.base_url = "http://localhost:8002"
    
    class Valves(BaseModel):
        """Configuration"""
        MCP_SERVER_URL: str = Field(
            default="http://localhost:8002",
            description="MCP server base URL"
        )
'''

# Add a method for each tool from the OpenAPI spec
for path, methods in openapi_spec['paths'].items():
    for method, spec in methods.items():
        if method.lower() != 'post':
            continue
            
        operation_id = spec.get('operationId', path.replace('/', '_'))
        summary = spec.get('summary', f'Call {path}')
        description = spec.get('description', summary)
        
        # Create method
        tool_content += f'''
    def {operation_id}(self, **kwargs) -> Dict[str, Any]:
        """
        {description}
        """
        response = requests.post(
            f"{{self.base_url}}{path}",
            json=kwargs,
            headers={{"Content-Type": "application/json"}}
        )
        return response.json()
'''

# Specs (OpenAPI definition for OpenWebUI)
specs = [
    {
        "id": tool_id,
        "name": tool_name,
        "url": "http://localhost:8002",
        "openapi_spec": openapi_spec
    }
]

# Meta
meta = {
    "description": "All 76 MCP business management tools",
    "manifest": {
        "name": tool_name,
        "version": "1.0.0",
        "author": "AlphaOmega",
        "description": "Tasks, inventory, customers, notes, sales, expenses, appointments, social media tools"
    }
}

# Check if exists
cursor.execute("SELECT id FROM tool WHERE id = ?", (tool_id,))
existing = cursor.fetchone()

try:
    if existing:
        print(f"\n📝 Updating existing tool: {tool_id}")
        cursor.execute("""
            UPDATE tool 
            SET name = ?, content = ?, specs = ?, meta = ?, updated_at = ?
            WHERE id = ?
        """, (
            tool_name,
            tool_content,
            json.dumps(specs),
            json.dumps(meta),
            timestamp,
            tool_id
        ))
    else:
        print(f"\n✨ Creating new tool: {tool_id}")
        cursor.execute("""
            INSERT INTO tool (id, user_id, name, content, specs, meta, created_at, updated_at, valves, access_control)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tool_id,
            user_id,
            tool_name,
            tool_content,
            json.dumps(specs),
            json.dumps(meta),
            timestamp,
            timestamp,
            json.dumps({"MCP_SERVER_URL": "http://localhost:8002"}),
            None
        ))
    
    conn.commit()
    print("✅ MCP tools registered successfully!")
    
    print(f"\n📋 Summary:")
    print(f"   • Tool ID: {tool_id}")
    print(f"   • Tool Name: {tool_name}")
    print(f"   • Endpoints: {len(openapi_spec['paths'])}")
    print(f"   • Base URL: http://localhost:8002")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Refresh OpenWebUI: http://localhost:8080")
    print(f"   2. In any chat, click the 🔧 Tools icon")
    print(f"   3. You should see all 76 MCP tools listed")
    print(f"   4. Enable the tools you want to use")
    print(f"   5. Ask: 'What tasks do I have?'")
    print(f"   6. The LLM will automatically call the tools as needed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
    import traceback
    traceback.print_exc()
finally:
    conn.close()
