# Chatterbox TTS Emotion Control Guide

## Overview
Chatterbox TTS now supports emotion presets and fine-grained control over voice expressiveness. You can control how the AI speaks using emotion keywords or manual parameter tuning.

## Quick Start - Using Emotion Presets

### Available Emotions
- **neutral** - Balanced, natural delivery (default)
- **happy** - Upbeat and cheerful tone
- **excited** - High energy and enthusiastic
- **sad** - Slower, more somber delivery
- **calm** - Gentle and soothing tone
- **dramatic** - Theatrical and expressive
- **angry** - Intense and forceful
- **whisper** - Soft and intimate delivery

### How to Use in OpenWebUI

#### Method 1: Set in OpenWebUI Audio Settings
1. Open OpenWebUI settings (⚙️)
2. Navigate to **Audio** settings
3. Set **TTS Voice** to include emotion (if supported by UI)
4. Or use the API parameters in your requests

#### Method 2: Direct API Call
```bash
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello! I am so happy to see you!",
    "emotion": "happy"
  }' \
  --output speech.wav
```

#### Method 3: Configure in OpenWebUI Admin Panel
1. Go to **Admin Panel** → **Settings** → **Audio**
2. Set **TTS Engine URL**: `http://localhost:5003/v1/audio/speech`
3. Add custom parameters in the request body:
   ```json
   {
     "emotion": "calm"
   }
   ```

## Advanced Control - Manual Parameters

If you need more control than the presets provide, you can manually set:

### Parameters
- **exaggeration** (0.0-1.0): Controls expressiveness
  - 0.0-0.3: Subtle, monotone
  - 0.3-0.5: Natural (default)
  - 0.5-0.7: Expressive
  - 0.7-1.0: Very expressive, theatrical

- **cfg_weight** (0.0-1.0): Controls guidance/pacing
  - 0.0-0.3: Fast, energetic
  - 0.3-0.6: Natural pacing (default)
  - 0.6-1.0: Slower, more deliberate

### Example: Custom Settings
```bash
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "This is a custom voice setting.",
    "exaggeration": 0.6,
    "cfg_weight": 0.4
  }' \
  --output speech.wav
```

## Emotion Preset Technical Details

| Emotion   | Exaggeration | CFG Weight | Best For                          |
|-----------|--------------|------------|-----------------------------------|
| neutral   | 0.3          | 0.5        | General conversation, news        |
| happy     | 0.7          | 0.4        | Greetings, celebrations           |
| excited   | 0.9          | 0.3        | Announcements, enthusiasm         |
| sad       | 0.4          | 0.7        | Condolences, serious topics       |
| calm      | 0.2          | 0.6        | Meditation, bedtime stories       |
| dramatic  | 0.8          | 0.5        | Storytelling, theater             |
| angry     | 0.85         | 0.4        | Warnings, confrontation           |
| whisper   | 0.15         | 0.8        | Secrets, intimate conversation    |

## Model Selection

- **tts-1**: Standard quality, faster generation
- **tts-1-hd**: Higher quality, slightly more expressive (automatically adjusts emotion parameters)

## API Endpoints

### Generate Speech
```
POST /v1/audio/speech
```
Body:
```json
{
  "model": "tts-1",
  "input": "Text to speak",
  "emotion": "happy",
  "response_format": "wav"
}
```

### List Available Emotions
```
GET /v1/emotions
```
Returns all emotion presets with their parameter values.

### Health Check
```
GET /health
```

## Integration with OpenWebUI Pipelines

You can create a pipeline that automatically detects emotion from text and adjusts the TTS accordingly:

```python
import re
from typing import Optional

def detect_emotion(text: str) -> str:
    """Auto-detect emotion from text"""
    text_lower = text.lower()
    
    # Excitement markers
    if "!!!" in text or "wow" in text_lower or "amazing" in text_lower:
        return "excited"
    
    # Happiness markers
    if "😊" in text or ":)" in text or "happy" in text_lower:
        return "happy"
    
    # Sadness markers
    if "😢" in text or ":(" in text or "sorry" in text_lower:
        return "sad"
    
    # Questions (calm, thoughtful)
    if text.strip().endswith("?"):
        return "calm"
    
    # Emphasis (dramatic)
    if text.isupper() or text.count("!") >= 2:
        return "dramatic"
    
    return "neutral"
```

## Troubleshooting

### Emotion Not Applied
- Check that the `emotion` parameter is spelled correctly
- Verify Chatterbox server is running: `curl http://localhost:5003/health`
- Check logs: `tail -f logs/chatterbox.log`

### Voice Too Expressive/Not Expressive Enough
- Use `exaggeration` parameter to fine-tune
- Try different model (`tts-1` vs `tts-1-hd`)

### Slow Generation
- Use `tts-1` instead of `tts-1-hd`
- Lower `cfg_weight` for faster speech

## Examples

### Story Narration
```json
{
  "input": "Once upon a time, in a land far away...",
  "emotion": "dramatic",
  "model": "tts-1-hd"
}
```

### Customer Service
```json
{
  "input": "Hello! How can I help you today?",
  "emotion": "happy"
}
```

### News Reading
```json
{
  "input": "Breaking news: Scientists discover...",
  "emotion": "neutral",
  "model": "tts-1"
}
```

### Bedtime Story
```json
{
  "input": "Close your eyes and relax...",
  "emotion": "calm",
  "cfg_weight": 0.7
}
```

## Performance Tips

1. **Cache Common Phrases**: Generate frequently used phrases once and reuse
2. **Batch Processing**: Group similar emotions together
3. **Model Selection**: Use `tts-1` for real-time, `tts-1-hd` for quality
4. **Streaming**: Enable streaming for longer texts (coming soon)

## Future Enhancements

- [ ] Custom emotion presets (user-defined)
- [ ] Emotion blending (mix multiple emotions)
- [ ] Voice cloning support
- [ ] Streaming audio generation
- [ ] Multi-speaker conversations

---

**Last Updated**: October 2025  
**Chatterbox Version**: 1.0.0  
**Compatible with**: OpenWebUI, OpenAI-compatible clients
