# 🎙️ Voice Selection Guide for OpenWebUI

## Available Voices (6 Total)

Your AlphaOmega TTS system includes a diverse selection of high-quality voices:

### American Voices (4)

#### Female American Voices
1. **lessac** - `en_US-lessac-medium`
   - **Gender**: Female
   - **Accent**: American
   - **Best For**: Professional, clear, articulate
   - **Sample**: "Hello, I'm Lessac, your AI assistant."

2. **amy** - `en_US-amy-medium`
   - **Gender**: Female
   - **Accent**: American
   - **Best For**: Friendly, approachable, warm
   - **Sample**: "Hi there! I'm Amy, happy to help you today."

#### Male American Voices
3. **ryan** - `en_US-ryan-medium`
   - **Gender**: Male
   - **Accent**: American
   - **Best For**: Confident, authoritative, professional
   - **Sample**: "Hello, I'm Ryan, your technical assistant."

4. **joe** - `en_US-joe-medium`
   - **Gender**: Male
   - **Accent**: American
   - **Best For**: Casual, conversational, friendly
   - **Sample**: "Hey, I'm Joe. Let's get started!"

### British Voices (2)

5. **alan** - `en_GB-alan-medium`
   - **Gender**: Male
   - **Accent**: British
   - **Best For**: Formal, sophisticated, educational
   - **Sample**: "Good day, I'm Alan, at your service."

6. **alba** - `en_GB-alba-medium`
   - **Gender**: Female
   - **Accent**: British
   - **Best For**: Professional, elegant, refined
   - **Sample**: "Hello, I'm Alba, pleased to assist you."

---

## OpenWebUI Configuration

### Method 1: Set Default Voice (Admin)

1. **Access Admin Panel**
   - Click profile icon (top-right)
   - Select "Admin Panel"

2. **Navigate to Audio Settings**
   - Settings → Audio → Text-to-Speech

3. **Configure TTS**
   ```
   TTS Engine:     OpenAI
   API Base URL:   http://localhost:5002/v1
   API Key:        (leave blank)
   TTS Model:      tts-1
   TTS Voice:      lessac
   ```
   
4. **Select Voice**
   - Replace `lessac` with your preferred voice:
     - `lessac` - Female US (default)
     - `amy` - Female US (friendly)
     - `ryan` - Male US (professional)
     - `joe` - Male US (casual)
     - `alan` - Male UK (formal)
     - `alba` - Female UK (elegant)

5. **Save** and test with any chat

### Method 2: Per-Message Voice Selection (Advanced)

Users can request specific voices in their messages:
- "Read this in Ryan's voice"
- "Use the British female voice"
- "Switch to Amy's voice"

(Requires pipeline integration - see ADVANCED.md)

---

## Testing Voices

### Quick Test via API
```bash
# Test any voice
curl -X POST http://localhost:5002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello, this is a test.","voice":"ryan"}' \
  --output test.wav

# Play it
ffplay -nodisp -autoexit test.wav
```

### Test All Voices
```bash
cd /home/stacy/AlphaOmega/tts
python voice_preview.py
```

This will:
1. Generate previews of all 6 voices
2. Save to `/tmp/voice_previews/`
3. Offer interactive testing mode

---

## Voice Recommendations by Use Case

### Customer Service
**Recommended**: `lessac` (Female US) or `alba` (Female UK)
- Professional and approachable
- Clear articulation
- Pleasant tone

### Technical Support
**Recommended**: `ryan` (Male US) or `alan` (Male UK)
- Authoritative voice
- Good for step-by-step instructions
- Professional demeanor

### Casual Chat
**Recommended**: `amy` (Female US) or `joe` (Male US)
- Friendly and conversational
- Less formal
- Engaging tone

### Educational Content
**Recommended**: `alan` (Male UK) or `lessac` (Female US)
- Clear enunciation
- Good pacing
- Professional quality

### Accessibility
**All voices** work well for accessibility:
- 22050 Hz sample rate
- Clear pronunciation
- Consistent volume levels

---

## Performance Metrics

All voices perform at similar speeds:
- **Response Time**: 0.5-1.0 seconds per sentence
- **Real-time Factor**: 0.05-0.07 (15-20x faster than real-time)
- **Audio Quality**: 16-bit, 22050 Hz, mono WAV

### File Sizes (Approximate)
- Short phrase: 40-80 KB
- Medium sentence: 80-140 KB
- Long paragraph: 200-400 KB

---

## Advanced: Voice Characteristics

### Voice Comparison

| Voice    | Gender | Accent   | Pitch | Speed   | Formality |
|----------|--------|----------|-------|---------|-----------|
| lessac   | Female | American | Med   | Med     | High      |
| amy      | Female | American | Med-Hi| Med     | Medium    |
| ryan     | Male   | American | Med-Lo| Med     | High      |
| joe      | Male   | American | Med   | Med-Fast| Low       |
| alan     | Male   | British  | Med-Lo| Slow    | Very High |
| alba     | Female | British  | Med   | Med     | High      |

### Technical Details

All voices use:
- **Model**: Piper neural TTS
- **Architecture**: VITS (Variational Inference with adversarial learning)
- **Quality**: Medium (balanced speed/quality)
- **Size**: ~60 MB per voice model
- **Language**: English (US/UK)

---

## Troubleshooting

### Voice Not Working
```bash
# Check voice is installed
ls -lh /home/stacy/AlphaOmega/tts/*.onnx

# Test voice directly
echo "Test" | /home/stacy/AlphaOmega/tts/piper/piper \
  -m /home/stacy/AlphaOmega/tts/en_US-ryan-medium.onnx \
  -f /tmp/test.wav
```

### Wrong Voice Playing
- Check OpenWebUI Admin Settings → Audio → TTS Voice
- Verify API Base URL is `http://localhost:5002/v1` (not 5000!)

### Voice Sounds Distorted
- Check audio file: `file /tmp/test.wav` should show "RIFF WAVE audio"
- Verify sample rate: Should be 22050 Hz
- Check system audio settings

---

## API Reference

### List Available Voices
```bash
curl http://localhost:5002/v1/voices
```

Returns:
```json
{
  "voices": [
    {
      "id": "ryan",
      "name": "en_US-ryan-medium",
      "language": "en_US",
      "gender": "male",
      "accent": "American"
    },
    ...
  ]
}
```

### Generate Speech
```bash
curl -X POST http://localhost:5002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Text to speak",
    "voice": "ryan",
    "model": "tts-1"
  }' \
  --output output.wav
```

### Health Check
```bash
curl http://localhost:5002/health
```

---

## Adding More Voices

Want more voices? Visit:
**https://huggingface.co/rhasspy/piper-voices**

Download from the web UI or use:
```bash
cd /home/stacy/AlphaOmega/tts

# Example: Add Jenny voice
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/jenny/medium/en_US-jenny-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/jenny/medium/en_US-jenny-medium.onnx.json

# Restart API
pkill -f piper_api.py
python piper_api.py > ../logs/piper-api.log 2>&1 &
```

---

## Support

- **API Logs**: `/home/stacy/AlphaOmega/logs/piper-api.log`
- **Health Check**: `http://localhost:5002/health`
- **Voice List**: `http://localhost:5002/v1/voices`
- **Documentation**: `/home/stacy/AlphaOmega/docs/PIPER_TTS_SETUP.md`

**Quick Test**: `curl http://localhost:5002/health` should return healthy status
