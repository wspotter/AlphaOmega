#!/usr/bin/env python3
"""
Test Auto Emotion Detection
"""
import sys
sys.path.insert(0, '/home/stacy/AlphaOmega/pipelines')

from auto_emotion_tts import Pipeline

# Test cases with expected emotions
TEST_CASES = [
    ("Hello! How are you today?", "happy"),
    ("This is amazing! We did it!!!", "excited"),
    ("I'm so sorry to hear about your loss.", "sad"),
    ("This is completely unacceptable!", "angry"),
    ("Please take a deep breath and relax.", "calm"),
    ("And then, everything changed forever.", "dramatic"),
    ("I have a secret to tell you...", "whisper"),
    ("The weather is 72 degrees today.", "neutral"),
    ("WOW! That's incredible!!!", "excited"),
    ("I HATE this! Stop it now!", "angry"),
    ("Thank you so much! Great job!", "happy"),
    ("Unfortunately, we failed the test.", "sad"),
    ("What do you think about this?", "calm"),
    ("Between you and me, don't tell anyone...", "whisper"),
]

def test_emotion_detection():
    """Test emotion detection on various texts"""
    pipeline = Pipeline()
    
    print("🎭 Testing Auto Emotion Detection\n")
    print("=" * 70)
    
    correct = 0
    total = len(TEST_CASES)
    
    for text, expected in TEST_CASES:
        detected = pipeline.detect_emotion(text)
        is_correct = detected == expected
        
        if is_correct:
            correct += 1
            icon = "✅"
        else:
            icon = "❌"
        
        print(f"\n{icon} Text: {text}")
        print(f"   Expected: {expected:10} | Detected: {detected:10}")
    
    print("\n" + "=" * 70)
    print(f"\n📊 Results: {correct}/{total} correct ({100*correct//total}%)")
    
    if correct == total:
        print("🎉 Perfect score! All emotions detected correctly!")
    elif correct >= total * 0.8:
        print("👍 Good performance! Most emotions detected correctly.")
    else:
        print("⚠️  Some emotions need better detection patterns.")
    
    return correct == total


def test_edge_cases():
    """Test edge cases"""
    pipeline = Pipeline()
    
    print("\n\n🔍 Testing Edge Cases\n")
    print("=" * 70)
    
    edge_cases = [
        ("", "neutral"),  # Empty string
        (".", "neutral"),  # Just punctuation
        ("OK", "neutral"),  # Short response
        ("HELP!!!! EMERGENCY!!!", "excited"),  # Mixed urgency
        ("I'm happy but sad at the same time.", "happy"),  # Mixed emotions (first wins)
    ]
    
    for text, expected in edge_cases:
        detected = pipeline.detect_emotion(text)
        print(f"\nText: '{text}'")
        print(f"  Expected: {expected:10} | Detected: {detected:10}")


def interactive_test():
    """Interactive testing mode"""
    pipeline = Pipeline()
    
    print("\n\n💬 Interactive Mode (type 'quit' to exit)\n")
    print("=" * 70)
    
    while True:
        try:
            text = input("\nEnter text: ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            
            if not text:
                continue
            
            emotion = pipeline.detect_emotion(text)
            print(f"🎭 Detected emotion: {emotion}")
            
        except (KeyboardInterrupt, EOFError):
            break
    
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        success = test_emotion_detection()
        test_edge_cases()
        
        print("\n\n💡 Tips:")
        print("  - Run 'python test_auto_emotion.py interactive' for interactive testing")
        print("  - Emotion patterns can be tuned in pipelines/auto_emotion_tts.py")
        
        sys.exit(0 if success else 1)
