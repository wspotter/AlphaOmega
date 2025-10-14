#!/usr/bin/env python3
"""
Register MCP tools with proper parameter schemas for OpenWebUI
"""
import sqlite3
import json
import requests
from datetime import datetime
from typing import get_type_hints

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

# Helper to convert JSON schema type to Python type hint
def json_type_to_python(prop_schema):
    json_type = prop_schema.get('type', 'string')
    if json_type == 'string':
        return 'str'
    elif json_type == 'integer':
        return 'int'
    elif json_type == 'number':
        return 'float'
    elif json_type == 'boolean':
        return 'bool'
    elif json_type == 'array':
        items_type = json_type_to_python(prop_schema.get('items', {}))
        return f'List[{items_type}]'
    elif json_type == 'object':
        return 'Dict[str, Any]'
    else:
        return 'Any'

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
        
        # Get parameter schema
        params = {}
        param_fields = []
        request_body = spec.get('requestBody', {})
        if request_body:
            schema_ref = request_body.get('content', {}).get('application/json', {}).get('schema', {})
            if '$ref' in schema_ref:
                # Extract schema name from reference
                schema_name = schema_ref['$ref'].split('/')[-1]
                schema_def = openapi_spec['components']['schemas'].get(schema_name, {})
                params = schema_def.get('properties', {})
        
        # Build parameter list for function signature and Field definitions
        if params:
            for param_name, param_schema in params.items():
                py_type = json_type_to_python(param_schema)
                param_desc = param_schema.get('description', '')
                param_title = param_schema.get('title', param_name)
                
                # Use Optional for all parameters
                param_fields.append(f"        {param_name}: Optional[{py_type}] = Field(default=None, description=\"{param_desc}\")")
        
        # Create content - direct HTTP call function with proper typing
        imports = "import json\nimport requests\nfrom typing import Dict, Any, Optional, List\nfrom pydantic import BaseModel, Field\n\n"
        
        tool_content = f'''{imports}
class Tools:
    class Valves(BaseModel):
        MCP_SERVER_URL: str = Field(
            default="http://localhost:8002",
            description="MCP server base URL"
        )
    
    class UserValves(BaseModel):
        """User-specific settings (currently none)"""
        pass
'''
        
        if param_fields:
            tool_content += f'''
    class {operation_id}_params(BaseModel):
        """Parameters for {summary}"""
{chr(10).join(param_fields)}
'''
        
        tool_content += f'''
    def __init__(self):
        self.valves = self.Valves()
        self.user_valves = self.UserValves()
    
    def {operation_id}(
        self'''
        
        # Add typed parameters to function signature (multi-line for readability)
        if param_fields:
            tool_content += ',\n        __user__: dict = {}'
            param_names = [f.split(':')[0].strip() for f in param_fields]
            for param_name in param_names:
                py_type = json_type_to_python(params[param_name])
                tool_content += f',\n        {param_name}: Optional[{py_type}] = None'
        
        tool_content += f'\n    ) -> str:
        """
        {description}
        """
        try:
            # Build request body from non-None parameters
            body = {{}}
'''
        
        if params:
            for param_name in params.keys():
                tool_content += f'''            if {param_name} is not None:
                body["{param_name}"] = {param_name}
'''
        
        tool_content += f'''
            response = requests.post(
                f"{{self.valves.MCP_SERVER_URL}}{path}",
                json=body,
                headers={{"Content-Type": "application/json"}},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Return formatted string result
            if isinstance(result, dict):
                return json.dumps(result, indent=2)
            return str(result)
        except Exception as e:
            return f"Error calling {summary}: {{str(e)}}"
'''
        
        # Specs
        tool_specs = [{
            "id": tool_id,
            "name": tool_name,
            "url": f"http://localhost:8002{path}",
            "method": "POST",
            "description": description,
            "parameters": params
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
            print(f"  ✓ {operation_id} ({len(params)} params)")
            
        except Exception as e:
            print(f"  ✗ {operation_id}: {e}")

conn.commit()
conn.close()

print(f"\n✅ Registered {registered_count} tools with proper parameter schemas!")
print(f"\n🎯 Next Steps:")
print(f"   1. Refresh OpenWebUI (Ctrl+Shift+R)")
print(f"   2. Click 🔧 Tools icon in chat")
print(f"   3. Enable the tools you want to use")
print(f"   4. Start chatting - parameters should now work!")
