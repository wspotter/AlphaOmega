#!/usr/bin/env python3
"""
Test Chatterbox TTS Emotion Presets
"""
import sys
import json
import requests
from pathlib import Path

API_URL = "http://localhost:5003"

def test_emotion(emotion: str, text: str):
    """Test a specific emotion preset"""
    print(f"\n🎭 Testing emotion: {emotion}")
    print(f"   Text: {text}")
    
    response = requests.post(
        f"{API_URL}/v1/audio/speech",
        json={
            "model": "tts-1",
            "input": text,
            "emotion": emotion,
            "response_format": "wav"
        }
    )
    
    if response.status_code == 200:
        output_file = Path(f"test_emotion_{emotion}.wav")
        output_file.write_bytes(response.content)
        print(f"   ✅ Generated: {output_file} ({len(response.content)} bytes)")
        return True
    else:
        print(f"   ❌ Failed: {response.status_code} - {response.text}")
        return False


def list_emotions():
    """List available emotions"""
    response = requests.get(f"{API_URL}/v1/emotions")
    if response.status_code == 200:
        data = response.json()
        print("\n📋 Available Emotions:")
        for emotion in data["emotions"]:
            print(f"   - {emotion['name']}: {emotion['description']}")
            print(f"     (exaggeration={emotion['exaggeration']}, cfg_weight={emotion['cfg_weight']})")
        return data["emotions"]
    else:
        print(f"❌ Failed to list emotions: {response.status_code}")
        return []


def test_all_emotions():
    """Test all emotion presets"""
    test_texts = {
        "neutral": "This is a neutral statement about the weather today.",
        "happy": "I'm so excited to see you! This is wonderful news!",
        "excited": "Oh my gosh! This is absolutely amazing!!!",
        "sad": "I'm sorry to hear about that. It's truly unfortunate.",
        "calm": "Take a deep breath. Everything will be alright.",
        "dramatic": "And then, in that very moment, everything changed forever!",
        "angry": "This is completely unacceptable! I demand an explanation!",
        "whisper": "Come closer, I have a secret to tell you."
    }
    
    results = []
    for emotion, text in test_texts.items():
        success = test_emotion(emotion, text)
        results.append((emotion, success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("   ✅ All emotion tests passed!")
    else:
        print("   ⚠️  Some tests failed:")
        for emotion, success in results:
            if not success:
                print(f"      - {emotion}")


def test_manual_params():
    """Test manual exaggeration/cfg_weight parameters"""
    print("\n🔧 Testing manual parameters:")
    
    tests = [
        {"exaggeration": 0.1, "cfg_weight": 0.8, "label": "Very calm"},
        {"exaggeration": 0.9, "cfg_weight": 0.3, "label": "Very expressive"},
        {"exaggeration": 0.5, "cfg_weight": 0.5, "label": "Balanced"}
    ]
    
    text = "This is a test of manual parameter control."
    
    for test in tests:
        print(f"\n   Testing: {test['label']}")
        print(f"   (exaggeration={test['exaggeration']}, cfg_weight={test['cfg_weight']})")
        
        response = requests.post(
            f"{API_URL}/v1/audio/speech",
            json={
                "model": "tts-1",
                "input": text,
                "exaggeration": test['exaggeration'],
                "cfg_weight": test['cfg_weight'],
                "response_format": "wav"
            }
        )
        
        if response.status_code == 200:
            output_file = Path(f"test_manual_{test['label'].replace(' ', '_')}.wav")
            output_file.write_bytes(response.content)
            print(f"   ✅ Generated: {output_file}")
        else:
            print(f"   ❌ Failed: {response.status_code}")


def main():
    print("🎤 Chatterbox TTS Emotion Test Suite")
    print("="*60)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            print(f"❌ Server not healthy: {response.status_code}")
            sys.exit(1)
        print("✅ Chatterbox server is running")
    except Exception as e:
        print(f"❌ Cannot connect to Chatterbox server at {API_URL}")
        print(f"   Error: {e}")
        print("\n💡 Make sure Chatterbox is running:")
        print("   cd /home/stacy/AlphaOmega")
        print("   source venv/bin/activate")
        print("   python tts/chatterbox_api.py")
        sys.exit(1)
    
    # List available emotions
    emotions = list_emotions()
    
    if not emotions:
        print("⚠️  No emotions available")
        sys.exit(1)
    
    # Run tests based on command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            # Already listed above
            pass
        elif sys.argv[1] == "manual":
            test_manual_params()
        elif sys.argv[1] in [e["id"] for e in emotions]:
            # Test specific emotion
            text = sys.argv[2] if len(sys.argv) > 2 else "This is a test of the emotion preset."
            test_emotion(sys.argv[1], text)
        else:
            print(f"\n❌ Unknown emotion: {sys.argv[1]}")
            print(f"   Available: {', '.join([e['id'] for e in emotions])}")
            sys.exit(1)
    else:
        # Test all emotions
        test_all_emotions()
        test_manual_params()
    
    print("\n" + "="*60)
    print("🎉 Testing complete!")
    print("\n💡 To test a specific emotion:")
    print("   python test_chatterbox_emotions.py happy")
    print("   python test_chatterbox_emotions.py happy 'Custom text here'")


if __name__ == "__main__":
    main()
