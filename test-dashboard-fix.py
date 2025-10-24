#!/usr/bin/env python3
"""
Test script for dashboard service startup fixes
"""

import subprocess
import time
import requests
import json
from pathlib import Path

def test_dashboard_api():
    """Test the dashboard API service startup"""
    print("Testing Dashboard API Service Startup...")

    # Start dashboard in background
    dashboard_proc = subprocess.Popen(
        ["python", "dashboard.py"],
        cwd="/home/stacy/AlphaOmega",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    try:
        # Wait for dashboard to start
        time.sleep(3)

        # Test status endpoint
        print("1. Testing status endpoint...")
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ Status endpoint working")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
            return False

        # Test starting TTS service
        print("2. Testing TTS service startup...")
        response = requests.get("http://localhost:5000/api/start/tts", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("   ✅ TTS service started successfully")
                status = data.get("status", {})
                print(f"   📊 Running: {status.get('running')}, Responsive: {status.get('responsive')}")
            else:
                print(f"   ❌ TTS service failed: {data.get('error')}")
                return False
        else:
            print(f"   ❌ TTS start request failed: {response.status_code}")
            return False

        # Check if log file was created
        log_file = Path("/home/stacy/AlphaOmega/logs/tts.log")
        if log_file.exists():
            print("   ✅ Log file created")
        else:
            print("   ⚠️  Log file not found (might be normal)")

        print("3. Testing start_all endpoint...")
        response = requests.get("http://localhost:5000/api/start_all", timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", {})
            print("   📋 Start results:")
            for service, result in results.items():
                status = "✅" if result == "starting" else "❌"
                print(f"      {status} {service}: {result}")
        else:
            print(f"   ❌ Start all failed: {response.status_code}")

        return True

    finally:
        # Clean up
        dashboard_proc.terminate()
        dashboard_proc.wait()

if __name__ == "__main__":
    success = test_dashboard_api()
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed'}")