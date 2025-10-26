# Chatterbox Emotion Control - Quick Start

## What Changed

✅ **Added Emotion Presets**: 8 pre-configured emotions (neutral, happy, excited, sad, calm, dramatic, angry, whisper)
✅ **New API Endpoint**: `/v1/emotions` - List all available emotions
✅ **Enhanced Documentation**: Complete guide in `docs/CHATTERBOX_EMOTIONS.md`
✅ **Test Suite**: Automated testing in `tests/test_chatterbox_emotions.py`

## Restart Chatterbox to Apply Changes

```bash
# Stop current instance
sudo pkill -f chatterbox_api

# Start with new emotion support
cd /home/stacy/AlphaOmega
source venv/bin/activate
python tts/chatterbox_api.py &

# Or use the dashboard
./scripts/restart-chatterbox.sh
```

## Quick Test

### 1. List Available Emotions
```bash
curl http://localhost:5003/v1/emotions | jq '.'
```

### 2. Test a Happy Voice
```bash
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "I am so happy to see you today!",
    "emotion": "happy"
  }' \
  --output happy_test.wav

# Play the audio
aplay happy_test.wav
```

### 3. Run Full Test Suite
```bash
cd /home/stacy/AlphaOmega
source venv/bin/activate
python tests/test_chatterbox_emotions.py
```

## Using in OpenWebUI

### Option 1: Add to Message (if OpenWebUI supports custom TTS params)
In your OpenWebUI settings, configure the TTS endpoint to accept emotion parameters.

### Option 2: Create a Pipeline Filter
Create a pipeline that detects emotion from text and adds it to TTS requests:

```python
# In pipelines/emotion_tts_filter.py
class EmotionTTSFilter:
    def process(self, text):
        emotion = self.detect_emotion(text)
        # Add emotion to TTS request
        return {"text": text, "emotion": emotion}
    
    def detect_emotion(self, text):
        if "!" in text or "wow" in text.lower():
            return "excited"
        if "?" in text:
            return "calm"
        # ... more rules
        return "neutral"
```

### Option 3: Manual API Configuration
In OpenWebUI Audio settings:
- TTS Engine URL: `http://localhost:5003/v1/audio/speech`
- Custom Request Body:
  ```json
  {
    "emotion": "calm"
  }
  ```

## Available Emotions

| Emotion  | Use Case                    | Example                                      |
|----------|-----------------------------|----------------------------------------------|
| neutral  | General conversation        | "The weather is nice today."                 |
| happy    | Greetings, good news        | "Great to see you! How are you doing?"       |
| excited  | Announcements, enthusiasm   | "This is amazing! You won't believe this!!!" |
| sad      | Condolences, serious topics | "I'm sorry to hear that."                    |
| calm     | Instructions, meditation    | "Take a deep breath and relax."              |
| dramatic | Storytelling, theater       | "And then, everything changed forever!"      |
| angry    | Warnings, urgency           | "Stop! This is unacceptable!"                |
| whisper  | Secrets, intimate           | "Come closer, I have a secret..."            |

## Advanced: Manual Control

If presets don't fit, use manual parameters:

```bash
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Custom voice control",
    "exaggeration": 0.6,
    "cfg_weight": 0.4
  }' \
  --output custom.wav
```

- **exaggeration**: 0.0-1.0 (how expressive)
- **cfg_weight**: 0.0-1.0 (pacing/guidance)

## Next Steps

1. **Restart Chatterbox** with the new code
2. **Test emotions** using the test suite
3. **Configure OpenWebUI** to use emotion parameters
4. **Read full docs**: `docs/CHATTERBOX_EMOTIONS.md`

## Troubleshooting

**Emotions not working?**
- Make sure Chatterbox restarted: `sudo systemctl restart chatterbox` or restart manually
- Check logs: `tail -f logs/chatterbox.log`
- Verify endpoint: `curl http://localhost:5003/v1/emotions`

**Need help?**
See full documentation: `/home/stacy/AlphaOmega/docs/CHATTERBOX_EMOTIONS.md`
