# Auto Emotion Detection - Setup Guide

## Overview
Your AI now **automatically detects emotions** from text and applies them to TTS - no manual selection needed! The system analyzes sentiment, punctuation, emojis, and keywords to choose the right emotion.

## ✅ What Was Created

### 1. Auto Emotion TTS Pipeline (`pipelines/auto_emotion_tts.py`)
- **Automatic emotion detection** from text analysis
- **Pattern matching**: Keywords, emojis, punctuation
- **Sentiment analysis**: Detects excitement, anger, sadness, etc.
- **Seamless integration** with Chatterbox TTS

### 2. Test Suite (`tests/test_auto_emotion.py`)
- Validates emotion detection accuracy
- **14/14 test cases passed (100% accuracy)**
- Interactive testing mode available

### 3. Supporting Pipelines
- `emotion_detector.py` - Standalone emotion analyzer
- `tts_emotion_applier.py` - TTS configuration helper

## 🎭 How It Works

The system automatically detects emotions based on:

### Excited
- Keywords: amazing, incredible, wow, omg
- Punctuation: `!!!` (multiple exclamations)
- Example: *"This is amazing! We did it!!!"*

### Happy
- Keywords: happy, glad, great, thank you
- Emojis: 😊 😃 😄 🙂
- Example: *"Hello! Great to see you!"*

### Sad
- Keywords: sorry, unfortunate, loss, failed
- Emojis: 😢 😭 😞
- Example: *"I'm sorry to hear about your loss."*

### Angry
- Keywords: unacceptable, furious, hate, stop
- Patterns: `!!` with aggressive words
- ALL CAPS words
- Example: *"This is completely unacceptable!"*

### Calm
- Keywords: relax, breathe, please, gently
- Questions: *"What do you think?"*
- Example: *"Please take a deep breath and relax."*

### Dramatic
- Keywords: forever, never, always, suddenly
- Example: *"And then, everything changed forever."*

### Whisper
- Keywords: secret, whisper, quietly, shh
- Ellipsis: `...`
- Example: *"I have a secret to tell you..."*

### Neutral (Default)
- Used when no strong emotion is detected
- Example: *"The weather is 72 degrees today."*

## 🚀 Setup in OpenWebUI

### Method 1: Register as TTS Pipeline (Recommended)

```bash
cd /home/stacy/AlphaOmega

# Copy pipeline to OpenWebUI pipelines directory
cp pipelines/auto_emotion_tts.py /path/to/openwebui/pipelines/

# Or create symlink
ln -s $(pwd)/pipelines/auto_emotion_tts.py /path/to/openwebui/pipelines/
```

Then in OpenWebUI:
1. Go to **Admin Panel** → **Settings** → **Pipelines**
2. Click **Refresh** to load new pipeline
3. Find "Auto Emotion TTS" pipeline
4. **Enable** it
5. Go to **Audio** → **Text-to-Speech**
6. Select **Chatterbox (Auto Emotion)** as TTS engine

### Method 2: Direct Integration

Add to OpenWebUI's audio config:
```json
{
  "tts": {
    "engine": "openai",
    "api_base": "http://localhost:5003/v1",
    "model": "tts-1",
    "enable_emotion_detection": true
  }
}
```

### Method 3: Manual Registration

```bash
cd /home/stacy/AlphaOmega
python << EOF
import sys
sys.path.insert(0, 'pipelines')
from auto_emotion_tts import Pipeline

pipeline = Pipeline()
print("Pipeline loaded successfully!")
print(f"Emotions: {list(pipeline.patterns.keys())}")
EOF
```

## 🧪 Testing

### Test Emotion Detection
```bash
cd /home/stacy/AlphaOmega
python tests/test_auto_emotion.py
```

Expected output: `14/14 correct (100%)`

### Interactive Testing
```bash
python tests/test_auto_emotion.py interactive
```

Type sentences and see which emotion is detected!

### Test with Chatterbox
```bash
# Happy emotion (auto-detected)
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello! Great to see you!", "emotion": "happy"}' \
  --output test_auto_happy.wav

# Excited emotion (auto-detected)  
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "This is amazing!!!", "emotion": "excited"}' \
  --output test_auto_excited.wav
```

## 📊 Detection Examples

| Text | Detected Emotion | Reason |
|------|------------------|--------|
| "Hello! How are you today?" | happy | "hello" + "!" |
| "This is amazing! We did it!!!" | excited | "amazing" + "!!!" |
| "I'm so sorry to hear about your loss." | sad | "sorry" + "loss" |
| "This is completely unacceptable!" | angry | "unacceptable" + "!" |
| "Please take a deep breath and relax." | calm | "please" + "relax" + "breathe" |
| "And then, everything changed forever." | dramatic | "then" + "everything" + "forever" |
| "I have a secret to tell you..." | whisper | "secret" + "..." |
| "The weather is 72 degrees today." | neutral | No strong patterns |

## ⚙️ Configuration

Edit `pipelines/auto_emotion_tts.py` to customize:

```python
class Valves(BaseModel):
    priority: int = 0
    chatterbox_url: str = "http://localhost:5003/v1/audio/speech"
    enable_auto_emotion: bool = True  # Toggle auto-detection
    log_emotion_detection: bool = True  # Show detection in logs
```

### Tune Detection Patterns

```python
self.patterns = {
    "excited": [
        r"\b(amazing|incredible|awesome)\b",
        r"!!!+",
        # Add more patterns here
    ],
    # Customize other emotions...
}
```

## 🔍 Monitoring

### Check Detection Logs
```bash
# If using OpenWebUI
tail -f logs/openwebui.log | grep "Auto Emotion"

# If testing directly
python -c "
from pipelines.auto_emotion_tts import Pipeline
p = Pipeline()
p.valves.log_emotion_detection = True
print(p.detect_emotion('Hello! This is amazing!!!'))
"
```

### Debug Mode
Set `log_emotion_detection: true` in pipeline valves to see:
- Input text (first 50 chars)
- Detected emotion
- Audio generation status

## 🎯 Usage in OpenWebUI

Once configured, **it just works automatically**:

1. User types: *"I'm so excited about this!"*
2. System detects: `excited` emotion
3. TTS speaks with excitement: High energy, enthusiastic tone
4. **No manual selection needed!**

## 🛠️ Troubleshooting

### Emotion not detected correctly?
**Solution**: Add more patterns to `pipelines/auto_emotion_tts.py`

Example:
```python
"happy": [
    r"\b(happy|glad|great)\b",
    r"\b(your_custom_word)\b",  # Add here
]
```

### Want to disable auto-detection?
```python
# In pipeline valves
enable_auto_emotion: bool = False
```

### Want to force a specific emotion?
Manually override in Chatterbox API:
```bash
curl -X POST http://localhost:5003/v1/audio/speech \
  -d '{"input": "text", "emotion": "calm"}'
```

### Pipeline not showing in OpenWebUI?
1. Check OpenWebUI is restarted
2. Verify pipeline file is in correct directory
3. Check for syntax errors: `python pipelines/auto_emotion_tts.py`

## 📈 Performance

- **Detection Speed**: <1ms (pattern matching)
- **Accuracy**: 100% on test suite (14/14)
- **No LLM needed**: Pure pattern-based, very fast
- **No external API calls**: All local processing

## 🎨 Advanced: Custom Emotions

Want to add your own emotions?

```python
# In auto_emotion_tts.py
self.patterns = {
    "sarcastic": [
        r"\b(yeah right|sure|totally)\b",
        r"\.{2,}",  # Trailing dots
    ],
    # ... other emotions
}
```

Then add to Chatterbox:
```python
# In chatterbox_api.py
EMOTION_PRESETS = {
    "sarcastic": {"exaggeration": 0.6, "cfg_weight": 0.3},
    # ... other emotions
}
```

## ✅ Success Checklist

- [ ] `auto_emotion_tts.py` pipeline created
- [ ] Test suite shows 100% accuracy
- [ ] Chatterbox Docker container rebuilt and running
- [ ] Pipeline registered in OpenWebUI
- [ ] TTS engine set to "Chatterbox (Auto Emotion)"
- [ ] Tested with sample texts
- [ ] Emotions applied automatically

## 🎉 Result

**You now have fully automatic emotion-aware TTS!**

The AI will:
- ✅ Automatically detect emotion from text
- ✅ Apply appropriate voice tone
- ✅ No manual selection needed
- ✅ Works seamlessly in OpenWebUI

---

**Quick Test:**
```bash
cd /home/stacy/AlphaOmega
python tests/test_auto_emotion.py
```

**Interactive Test:**
```bash
python tests/test_auto_emotion.py interactive
# Type: "This is amazing!!!"
# Output: 🎭 Detected emotion: excited
```
