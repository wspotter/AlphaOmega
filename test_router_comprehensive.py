#!/usr/bin/env python3
"""
Comprehensive test of AlphaOmega Router intent detection and routing
"""
import requests
import json

BASE_URL = "http://localhost:8080"

# Login
print("🔐 Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auths/signin",
    json={"email": "admin@localhost", "password": "admin"}
)
token = login_response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Logged in\n")

# Test cases with expected routing
test_cases = [
    {
        "name": "Agent-S Screenshot",
        "message": "What's on my screen right now?",
        "expected_intent": "agent",
        "expected_keywords": ["screen", "capture", "Agent-S"]
    },
    {
        "name": "MCP Task List",
        "message": "List my tasks",
        "expected_intent": "mcp",
        "expected_keywords": ["task", "MCP"]
    },
    {
        "name": "Code Generation",
        "message": "Write a Python function to reverse a string",
        "expected_intent": "code",
        "expected_keywords": ["def", "return", "python"]
    },
    {
        "name": "General Reasoning",
        "message": "What is the capital of France?",
        "expected_intent": "reasoning",
        "expected_keywords": ["Paris", "France", "capital"]
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"{'='*60}")
    print(f"Test {i}/{len(test_cases)}: {test['name']}")
    print(f"Message: '{test['message']}'")
    print(f"Expected Intent: {test['expected_intent']}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat/completions",
            headers=headers,
            json={
                "model": "alphaomega_router",
                "messages": [{"role": "user", "content": test['message']}],
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Response received ({len(content)} chars)")
            print(f"Preview: {content[:200]}...")
            
            # Check if expected keywords appear
            matched_keywords = [kw for kw in test['expected_keywords'] if kw.lower() in content.lower()]
            if matched_keywords:
                print(f"✨ Matched keywords: {matched_keywords}")
            else:
                print(f"⚠️  Expected keywords not found: {test['expected_keywords']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        print(f"⏱️  Request timed out after 30s")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    print()

print("\n🎉 All tests complete!")
print("\n💡 Note: To verify routing is working correctly:")
print("   1. Check /home/stacy/AlphaOmega/logs/agent-s.log for Agent-S requests")
print("   2. Check MCP server logs for tool calls")
print("   3. Monitor Ollama logs for model inference")
