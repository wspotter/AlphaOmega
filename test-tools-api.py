#!/usr/bin/env python3
"""
Test if OpenWebUI tools API returns MCP tools
"""
import requests
import json

# Login first
print("🔐 Logging in...")
login_response = requests.post(
    "http://localhost:8080/api/v1/auths/signin",
    json={"email": "admin@localhost", "password": "admin"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"   Trying default password...")
    # Try common default passwords
    for pwd in ["admin", "password", "12345678"]:
        login_response = requests.post(
            "http://localhost:8080/api/v1/auths/signin",
            json={"email": "admin@localhost", "password": pwd}
        )
        if login_response.status_code == 200:
            print(f"   ✅ Logged in with password: {pwd}")
            break
    else:
        print("   ❌ Could not log in. Check your password.")
        print("   You may need to reset or create the admin account.")
        exit(1)

token = login_response.json().get("token")
print(f"✅ Logged in, got token")

# Get tools
print("\n📥 Fetching tools...")
tools_response = requests.get(
    "http://localhost:8080/api/v1/tools/",
    headers={"Authorization": f"Bearer {token}"}
)

if tools_response.status_code != 200:
    print(f"❌ Tools API failed: {tools_response.status_code}")
    print(f"   Response: {tools_response.text}")
    exit(1)

tools = tools_response.json()
print(f"✅ Tools API returned {len(tools)} tools\n")

# Check for MCP tools
mcp_tools = [t for t in tools if t.get('id', '').startswith('mcp_')]
print(f"📊 MCP Tools Found: {len(mcp_tools)}")

if mcp_tools:
    print("\n✅ Sample MCP Tools:")
    for tool in mcp_tools[:5]:
        print(f"   • {tool.get('name')} ({tool.get('id')})")
    
    if len(mcp_tools) > 5:
        print(f"   ... and {len(mcp_tools) - 5} more")
    
    print("\n🎉 SUCCESS: MCP tools are available in the API!")
    print("   If you don't see them in UI, try:")
    print("   - Clear browser cache (Ctrl+Shift+Delete)")
    print("   - Hard refresh (Ctrl+Shift+R)")
    print("   - Open incognito/private window")
    print("   - Check browser console (F12) for JS errors")
else:
    print("\n⚠️ WARNING: No MCP tools in API response")
    print("   But they exist in database...")
    print("   This suggests a caching or loading issue.")
    print("\n   Returned tools:")
    for tool in tools[:5]:
        print(f"   • {tool.get('name')} ({tool.get('id')})")
