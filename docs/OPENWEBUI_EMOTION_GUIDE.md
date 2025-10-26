# Using Chatterbox Emotions in OpenWebUI - Visual Guide

## 🎯 Goal
Make your AI speak with emotions: happy, sad, excited, calm, dramatic, angry, whisper, or neutral.

## 📖 Step-by-Step Setup

### Step 1: Restart Chatterbox
```bash
cd /home/stacy/AlphaOmega
./scripts/restart-chatterbox.sh
```

**Expected Output:**
```
🎤 Restarting Chatterbox TTS...
Stopping current Chatterbox instance...
Starting Chatterbox with emotion support...
✅ Chatterbox is running!
```

### Step 2: Verify Emotions Available
```bash
curl http://localhost:5003/v1/emotions | jq '.emotions[].id'
```

**Expected Output:**
```
"neutral"
"happy"
"excited"
"sad"
"calm"
"dramatic"
"angry"
"whisper"
```

### Step 3: Test an Emotion
```bash
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello! I am so excited to meet you!",
    "emotion": "excited"
  }' \
  --output test_excited.wav

aplay test_excited.wav  # Play the audio
```

## 🔧 OpenWebUI Configuration

### Method 1: Admin Panel Configuration

1. **Open OpenWebUI Admin Panel**
   - Navigate to http://localhost:8080
   - Click ⚙️ (Settings) → Admin Panel

2. **Configure Audio Settings**
   - Go to **Settings** → **Audio**
   - Find **Text-to-Speech (TTS)** section
   - Set **TTS Engine**: `OpenAI`
   - Set **API Base URL**: `http://localhost:5003/v1`
   - Set **API Key**: (leave empty or use dummy value)

3. **Add Emotion Parameter** (if supported)
   - Look for "Additional Parameters" or "Custom Request Body"
   - Add: `{"emotion": "neutral"}`
   - Save settings

### Method 2: User Settings

1. **Open User Settings**
   - Click your avatar → Settings
   - Go to **Audio** tab

2. **Configure TTS**
   - Enable **Text-to-Speech**
   - Select **Voice**: Any (emotion is separate)
   - Set **Speed**: 1.0 (default)

3. **Test TTS**
   - Type a message in chat
   - Click the speaker icon 🔊 to hear it
   - The emotion you configured will be applied

### Method 3: Dynamic Emotion Selection (Advanced)

Create a custom pipeline that detects emotion from text:

```python
# pipelines/emotion_detector.py
class Pipeline:
    def __init__(self):
        self.emotions = [
            "neutral", "happy", "excited", "sad", 
            "calm", "dramatic", "angry", "whisper"
        ]
    
    def detect_emotion(self, text: str) -> str:
        """Detect emotion from text content"""
        text_lower = text.lower()
        
        # Excitement markers
        if text.count("!") >= 2 or "wow" in text_lower or "amazing" in text_lower:
            return "excited"
        
        # Happiness markers
        if "😊" in text or ":)" in text or "happy" in text_lower or "great" in text_lower:
            return "happy"
        
        # Sadness markers
        if "😢" in text or ":(" in text or "sorry" in text_lower or "sad" in text_lower:
            return "sad"
        
        # Anger markers
        if "!!!" in text or "unacceptable" in text_lower or "angry" in text_lower:
            return "angry"
        
        # Calm markers (questions, instructions)
        if text.strip().endswith("?") or "please" in text_lower:
            return "calm"
        
        # Dramatic markers
        if text.isupper() or "forever" in text_lower or "never" in text_lower:
            return "dramatic"
        
        # Whisper markers
        if "secret" in text_lower or "whisper" in text_lower:
            return "whisper"
        
        # Default
        return "neutral"
    
    def pipe(self, body: dict) -> dict:
        """Process request and add emotion"""
        messages = body.get("messages", [])
        if messages:
            last_message = messages[-1].get("content", "")
            emotion = self.detect_emotion(last_message)
            
            # Add emotion to TTS request
            if "tts_config" not in body:
                body["tts_config"] = {}
            body["tts_config"]["emotion"] = emotion
        
        return body
```

## 🎭 Emotion Usage Examples

### Example 1: Greeting (Happy)
```json
{
  "input": "Hello! Welcome back! Great to see you!",
  "emotion": "happy"
}
```
**Voice:** Upbeat, cheerful, welcoming

### Example 2: Announcement (Excited)
```json
{
  "input": "Breaking news! We just achieved 100% success rate!!!",
  "emotion": "excited"
}
```
**Voice:** High energy, enthusiastic, fast-paced

### Example 3: Condolence (Sad)
```json
{
  "input": "I'm sorry to hear about your loss. My deepest condolences.",
  "emotion": "sad"
}
```
**Voice:** Slower, somber, gentle

### Example 4: Meditation (Calm)
```json
{
  "input": "Take a deep breath. Relax your shoulders. Feel the peace.",
  "emotion": "calm"
}
```
**Voice:** Gentle, soothing, slow-paced

### Example 5: Storytelling (Dramatic)
```json
{
  "input": "And then, in that very moment, everything changed forever!",
  "emotion": "dramatic"
}
```
**Voice:** Theatrical, expressive, dynamic

### Example 6: Warning (Angry)
```json
{
  "input": "Stop immediately! This is unacceptable behavior!",
  "emotion": "angry"
}
```
**Voice:** Intense, forceful, urgent

### Example 7: Secret (Whisper)
```json
{
  "input": "Come closer... I have something important to tell you...",
  "emotion": "whisper"
}
```
**Voice:** Soft, intimate, quiet

### Example 8: News (Neutral)
```json
{
  "input": "The weather forecast for today is partly cloudy with a high of 72 degrees.",
  "emotion": "neutral"
}
```
**Voice:** Balanced, natural, professional

## 🧪 Testing Workflow

### Quick Test
```bash
cd /home/stacy/AlphaOmega
source venv/bin/activate

# Test all emotions at once
python tests/test_chatterbox_emotions.py

# Test specific emotion
python tests/test_chatterbox_emotions.py happy "I'm so happy to see you!"

# List available emotions
python tests/test_chatterbox_emotions.py list
```

### Manual Test
```bash
# Create test audio file
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Test message", "emotion": "happy"}' \
  --output test.wav

# Play it
aplay test.wav
```

## 📊 Emotion Parameter Reference

| Emotion  | When to Use                          | Example Scenario                    |
|----------|--------------------------------------|-------------------------------------|
| neutral  | Default, factual information         | Weather reports, definitions        |
| happy    | Greetings, good news, celebrations   | "Welcome!", "Great job!"            |
| excited  | Major announcements, enthusiasm      | "We did it!!!", "Amazing news!"     |
| sad      | Apologies, condolences, bad news     | "I'm sorry", "Unfortunately..."     |
| calm     | Instructions, meditation, comfort    | "Breathe slowly", "It's okay"       |
| dramatic | Storytelling, important moments      | "And then...", "Forever changed"    |
| angry    | Warnings, urgent alerts, frustration | "Stop!", "This must change!"        |
| whisper  | Secrets, intimate moments, emphasis  | "Just between us...", "Listen..."   |

## 🔍 Troubleshooting

### Issue: Emotion not applied
**Check:**
```bash
# Is Chatterbox running?
curl http://localhost:5003/health

# Does emotion endpoint work?
curl http://localhost:5003/v1/emotions | jq '.'

# Check logs
tail -f logs/chatterbox.log | grep emotion
```

**Fix:**
```bash
./scripts/restart-chatterbox.sh
```

### Issue: Audio sounds the same for all emotions
**Possible causes:**
1. Chatterbox not restarted after update
2. Emotion parameter not being passed
3. Emotion name misspelled

**Debug:**
```bash
# Check what emotion is being received
tail -f logs/chatterbox.log | grep "TTS request"
```

### Issue: OpenWebUI not sending emotion parameter
**Solution:**
- Create a pipeline filter to add emotion
- Or configure in TTS settings custom parameters
- Or manually add emotion in API calls

## 🎨 Advanced: Custom Emotions

You can create custom emotions by mixing parameters:

```bash
# Gentle whisper (even softer than regular whisper)
curl -X POST http://localhost:5003/v1/audio/speech \
  -d '{"input": "Shh...", "exaggeration": 0.05, "cfg_weight": 0.9}'

# Super excited (maximum energy)
curl -X POST http://localhost:5003/v1/audio/speech \
  -d '{"input": "YES!!!", "exaggeration": 1.0, "cfg_weight": 0.2}'

# Formal announcement (controlled but expressive)
curl -X POST http://localhost:5003/v1/audio/speech \
  -d '{"input": "Ladies and gentlemen", "exaggeration": 0.5, "cfg_weight": 0.6}'
```

## 📚 Additional Resources

- **Full Documentation**: `docs/CHATTERBOX_EMOTIONS.md`
- **Quick Start**: `CHATTERBOX_EMOTIONS_QUICKSTART.md`
- **API Reference**: See `/v1/audio/speech` endpoint
- **Test Suite**: `tests/test_chatterbox_emotions.py`

## ✅ Success Checklist

- [ ] Chatterbox restarted with new code
- [ ] `/v1/emotions` endpoint returns 8 emotions
- [ ] Test audio file generated successfully
- [ ] Audio sounds different for different emotions
- [ ] OpenWebUI configured to use Chatterbox
- [ ] Tested in OpenWebUI chat interface

**All done?** 🎉 You now have emotion-aware TTS in OpenWebUI!

---

**Quick Command Reference:**
```bash
# Restart
./scripts/restart-chatterbox.sh

# List emotions
curl http://localhost:5003/v1/emotions | jq '.emotions[].id'

# Test
python tests/test_chatterbox_emotions.py

# Use
curl -X POST http://localhost:5003/v1/audio/speech \
  -d '{"input": "Hello!", "emotion": "happy"}' -o test.wav
```
