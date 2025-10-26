#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8080"

# Login
login_response = requests.post(
    f"{BASE_URL}/api/v1/auths/signin",
    json={"email": "admin@localhost", "password": "admin"}
)
token = login_response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# Quick test: Reasoning
print("Testing reasoning routing...")
response = requests.post(
    f"{BASE_URL}/api/chat/completions",
    headers=headers,
    json={
        "model": "alphaomega_router",
        "messages": [{"role": "user", "content": "Say 'Hello from AlphaOmega!' and nothing else"}],
        "stream": False
    },
    timeout=15
)

if response.status_code == 200:
    result = response.json()
    content = result['choices'][0]['message']['content']
    print(f"✅ Got response: {content}")
else:
    print(f"❌ Error: {response.status_code} - {response.text[:200]}")
