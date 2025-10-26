#!/usr/bin/env python3
"""
Test the unified AlphaOmega router via OpenWebUI API
"""
import requests
import json

BASE_URL = "http://localhost:8080"

# 1. Login
print("1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/api/v1/auths/signin",
    json={"email": "admin@localhost", "password": "admin"}
)
print(f"Login status: {login_response.status_code}")
token = login_response.json()["token"]
print(f"Got token: {token[:20]}...")

# 2. List available models
print("\n2. Listing available models...")
headers = {"Authorization": f"Bearer {token}"}
models_response = requests.get(f"{BASE_URL}/api/models", headers=headers)
print(f"Models status: {models_response.status_code}")

if models_response.status_code == 200:
    models_data = models_response.json()
    print(f"\nFound {len(models_data.get('data', []))} models:")
    for model in models_data.get('data', []):
        model_id = model.get('id', 'unknown')
        model_name = model.get('name', 'unknown')
        print(f"  - {model_id}: {model_name}")

# 3. Test the unified router with a screenshot request
print("\n3. Testing unified router with screenshot request...")
test_message = "What's on my screen right now?"

chat_response = requests.post(
    f"{BASE_URL}/api/chat/completions",
    headers=headers,
    json={
        "model": "alphaomega_router",  # Should be the unified router now
        "messages": [
            {"role": "user", "content": test_message}
        ],
        "stream": False
    },
    timeout=30
)

print(f"Chat status: {chat_response.status_code}")
if chat_response.status_code == 200:
    result = chat_response.json()
    print(f"Response: {json.dumps(result, indent=2)[:500]}...")
else:
    print(f"Error: {chat_response.text[:500]}")

print("\n✅ Test complete!")
