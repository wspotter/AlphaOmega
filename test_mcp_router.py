#!/usr/bin/env python3
"""
Quick test of MCP routing logic in alphaomega_router.py
Tests intent detection and tool selection without needing full OpenWebUI
"""
import sys
sys.path.insert(0, '/home/stacy/AlphaOmega/pipelines')

from alphaomega_router import Pipeline

# Initialize pipeline
pipeline = Pipeline()

# Test cases
test_messages = [
    "What tasks do I have?",
    "Check inventory for paint",
    "Show me all customers",
    "Create a note: Meeting tomorrow",
    "What were last month's sales?",
    "Post to Instagram",
    "Schedule an appointment",
    "Show VIP customers",
    "Generate an image of a sunset",  # Should route to ComfyUI, not MCP
    "Write Python code for sorting",  # Should route to Ollama, not MCP
]

print("=" * 60)
print("MCP Router Intent Detection Test")
print("=" * 60)

for msg in test_messages:
    intent = pipeline._detect_intent(msg)
    print(f"\n📝 Message: '{msg}'")
    print(f"🎯 Intent: {intent}")
    
    if intent == "mcp":
        tool_name, params = pipeline._detect_mcp_tool(msg)
        print(f"🔧 Tool: {tool_name}")
        print(f"📦 Params: {params}")
    
print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
print("\n✅ If you see 'mcp' intent for business tools (tasks, inventory, etc.)")
print("   and OTHER intents for image/code, the router is working correctly!")
