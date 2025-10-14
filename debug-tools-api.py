#!/usr/bin/env python3
"""
Debug: Check what OpenWebUI's tools API actually returns
"""
import sqlite3
import json

db_path = '/home/stacy/AlphaOmega/openwebui_data/webui.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get user
cursor.execute("SELECT id, email FROM user LIMIT 1")
user = cursor.fetchone()
print(f"👤 User: {user[1]} ({user[0]})")

# Query tools like OpenWebUI might
print("\n📊 Direct DB Query (all tools):")
cursor.execute("SELECT id, name, user_id FROM tool WHERE id LIKE 'mcp_%' LIMIT 5")
tools = cursor.fetchall()
print(f"   Found {len(tools)} tools")
for tool in tools:
    print(f"   • {tool[1]} (id: {tool[0]}, user_id: {tool[2]})")

# Check total count
cursor.execute("SELECT COUNT(*) FROM tool WHERE id LIKE 'mcp_%'")
total = cursor.fetchone()[0]
print(f"\n📈 Total MCP tools in DB: {total}")

# Check if any tools have issues
print("\n🔍 Checking for issues:")
cursor.execute("SELECT id FROM tool WHERE id LIKE 'mcp_%' AND (content IS NULL OR content = '')")
bad_content = cursor.fetchall()
if bad_content:
    print(f"   ⚠️ {len(bad_content)} tools with empty/null content")
else:
    print("   ✅ All tools have content")

cursor.execute("SELECT id FROM tool WHERE id LIKE 'mcp_%' AND (specs IS NULL OR specs = '')")
bad_specs = cursor.fetchall()
if bad_specs:
    print(f"   ⚠️ {len(bad_specs)} tools with empty/null specs")
else:
    print("   ✅ All tools have specs")

cursor.execute("SELECT id FROM tool WHERE id LIKE 'mcp_%' AND (meta IS NULL OR meta = '')")
bad_meta = cursor.fetchall()
if bad_meta:
    print(f"   ⚠️ {len(bad_meta)} tools with empty/null meta")
else:
    print("   ✅ All tools have meta")

conn.close()

print("\n" + "="*60)
print("💡 DIAGNOSIS:")
print("="*60)
print("If tools are in DB but not in UI, possible causes:")
print("1. OpenWebUI filtering by different user_id")
print("2. Frontend JavaScript error (check browser console)")
print("3. Tools need to be 'activated' or 'published' (check OpenWebUI docs)")
print("4. Cache issue (try: pkill open-webui && restart)")
print("\n🎯 Next: Check browser DevTools Network tab for /api/v1/tools/ response")
