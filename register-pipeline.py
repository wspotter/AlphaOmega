#!/usr/bin/env python3
"""
Register the AlphaOmega router pipeline with OpenWebUI
"""
import requests
import json
import sys

# Read the pipeline file
with open('/home/stacy/AlphaOmega/pipelines/alphaomega_router.py', 'r') as f:
    pipeline_code = f.read()

# OpenWebUI API endpoint
API_URL = "http://localhost:8080/api/v1/functions"

# Pipeline metadata
pipeline_data = {
    "id": "alphaomega_router",
    "name": "AlphaOmega Router",
    "type": "manifold",
    "content": pipeline_code,
    "meta": {
        "description": "Intelligent router for AlphaOmega multi-backend system",
        "author": "AlphaOmega",
        "version": "1.0.0"
    }
}

print("Registering AlphaOmega Router pipeline...")
print(f"API URL: {API_URL}")

try:
    # Try to create/update the pipeline
    response = requests.post(
        f"{API_URL}/create",
        json=pipeline_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        print("✅ Pipeline registered successfully!")
        print(f"Response: {response.json()}")
    elif response.status_code == 409:
        # Pipeline already exists, try to update
        print("Pipeline already exists, updating...")
        response = requests.post(
            f"{API_URL}/update",
            json=pipeline_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Pipeline updated successfully!")
        else:
            print(f"❌ Failed to update: {response.status_code}")
            print(response.text)
    else:
        print(f"❌ Failed to register pipeline: {response.status_code}")
        print(response.text)
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n🎯 Next step: Refresh OpenWebUI and select 'AlphaOmega Router' in the model dropdown")
