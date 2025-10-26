#!/usr/bin/env python3
"""
Auto Emotion TTS Demo - See it in action!
Generates audio files with auto-detected emotions
"""
import sys
import requests
from pathlib import Path

sys.path.insert(0, '/home/stacy/AlphaOmega/pipelines')
from auto_emotion_tts import Pipeline

CHATTERBOX_URL = "http://localhost:5003/v1/audio/speech"

# Demo sentences with expected emotions
DEMO_TEXTS = [
    "Hello! Welcome back! Great to see you!",
    "This is absolutely amazing! We achieved 100% success!!!",
    "I'm so sorry to hear about that. My condolences.",
    "This is completely unacceptable! Stop this immediately!",
    "Please take a deep breath and relax. Everything will be okay.",
    "And then, in that very moment, everything changed forever.",
    "Come closer... I have a secret to tell you...",
    "The weather forecast shows partly cloudy skies today.",
]

def generate_demo():
    """Generate audio demos with auto-detected emotions"""
    pipeline = Pipeline()
    pipeline.valves.log_emotion_detection = True
    
    print("🎤 Auto Emotion TTS Demo")
    print("=" * 70)
    print("\nGenerating audio samples with auto-detected emotions...\n")
    
    output_dir = Path("/tmp/emotion_demos")
    output_dir.mkdir(exist_ok=True)
    
    for i, text in enumerate(DEMO_TEXTS, 1):
        # Detect emotion
        emotion = pipeline.detect_emotion(text)
        
        print(f"{i}. Text: {text}")
        print(f"   🎭 Detected: {emotion}")
        
        # Generate audio
        try:
            response = requests.post(
                CHATTERBOX_URL,
                json={
                    "input": text,
                    "emotion": emotion,
                    "model": "tts-1"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                output_file = output_dir / f"demo_{i}_{emotion}.wav"
                output_file.write_bytes(response.content)
                print(f"   ✅ Generated: {output_file}")
                print(f"   📊 Size: {len(response.content)} bytes\n")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   {response.text}\n")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}\n")
    
    print("=" * 70)
    print(f"\n🎉 Demo complete! Audio files saved to: {output_dir}")
    print("\nPlay them with:")
    print(f"  aplay {output_dir}/*.wav")
    print("\nOr one at a time:")
    for f in sorted(output_dir.glob("*.wav")):
        print(f"  aplay {f}")


if __name__ == "__main__":
    # Check Chatterbox is running
    try:
        response = requests.get("http://localhost:5003/health", timeout=5)
        if response.status_code != 200:
            print("❌ Chatterbox not healthy!")
            sys.exit(1)
    except:
        print("❌ Cannot connect to Chatterbox at http://localhost:5003")
        print("\nMake sure Chatterbox is running:")
        print("  docker ps | grep chatterbox")
        sys.exit(1)
    
    generate_demo()
