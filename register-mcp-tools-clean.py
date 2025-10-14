#!/usr/bin/env python3
"""
Register MCP tools with proper parameter schemas for OpenWebUI (CLEAN VERSION)
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

def generate_tool_code(operation_id, path, summary, description, params):
    """Generate clean tool code with proper formatting"""
    
    # Start with imports
    code = """import json
import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        MCP_SERVER_URL: str = Field(
            default="http://localhost:8002",
            description="MCP server base URL"
        )
    
    class UserValves(BaseModel):
        pass
"""
    
    # Add parameter model if there are params
    if params:
        code += f"""
    class {operation_id}_params(BaseModel):
        \"\"\"Parameters for {summary}\"\"\"\n"""
        for param_name, param_schema in params.items():
            py_type = json_type_to_python(param_schema)
            param_desc = param_schema.get('description', '').replace('"', '\\"')
            code += f'        {param_name}: Optional[{py_type}] = Field(default=None, description="{param_desc}")\n'
    
    # Add __init__
    code += """
    def __init__(self):
        self.valves = self.Valves()
        self.user_valves = self.UserValves()
"""
    
    # Add the main function
    func_desc = description.replace('"""', '\'\'\'')
    code += f"""
    def {operation_id}(
        self,
        __user__: dict = {{}}\n"""
    
    # Add parameters
    if params:
        for param_name, param_schema in params.items():
            py_type = json_type_to_python(param_schema)
            code += f'        ,{param_name}: Optional[{py_type}] = None\n'
    
    code += f"""    ) -> str:
        \"\"\"
        {func_desc}
        \"\"\"
        try:
            # Build request body from non-None parameters
            body = {{}}\n"""
    
    # Add parameter building
    if params:
        for param_name in params.keys():
            code += f"""            if {param_name} is not None:
                body["{param_name}"] = {param_name}\n"""
    
    code += f"""
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
"""
    
    return code

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
        request_body = spec.get('requestBody', {})
        if request_body:
            schema_ref = request_body.get('content', {}).get('application/json', {}).get('schema', {})
            if '$ref' in schema_ref:
                schema_name = schema_ref['$ref'].split('/')[-1]
                schema_def = openapi_spec['components']['schemas'].get(schema_name, {})
                params = schema_def.get('properties', {})
        
        # Generate tool code
        tool_content = generate_tool_code(operation_id, path, summary, description, params)
        
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

print(f"\n✅ Registered {registered_count} tools with clean code!")
print(f"\n🎯 Next Steps:")
print(f"   1. Restart OpenWebUI to clear cache")
print(f"   2. Refresh browser (Ctrl+Shift+R)")
print(f"   3. Tools should load without spinning!")
