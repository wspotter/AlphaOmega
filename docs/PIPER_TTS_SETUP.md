# Piper TTS Setup Guide

## Overview
Piper TTS provides ultra-fast, local text-to-speech for OpenWebUI voice conversations.

**Performance**: 17x real-time speed (~200-300ms latency per sentence)  
**Quality**: High-quality neural voices  
**Privacy**: 100% local, no cloud services  

## Installation Complete ✅

### Components Installed
- **Piper Binary**: `/home/stacy/AlphaOmega/tts/piper/piper` (v1.2.0)
- **Voice Model**: `en_US-lessac-medium.onnx` (60MB, high-quality female voice)
- **API Server**: `piper_api.py` (OpenAI-compatible REST API)
- **Port**: 5002

### Files Created
```
tts/
├── piper/
│   ├── piper                    # TTS engine binary
│   └── piper.so                 # Shared library
├── en_US-lessac-medium.onnx     # Voice model
├── en_US-lessac-medium.onnx.json
└── piper_api.py                 # API server (port 5002)
```

## Auto-Start Configuration ✅
Piper TTS API now starts automatically with AlphaOmega:

```bash
./scripts/start.sh   # Starts all services including Piper TTS
./scripts/stop.sh    # Stops all services
```

## OpenWebUI Integration

### Step 1: Access Admin Panel
1. Open OpenWebUI: http://localhost:8080 (or 8181)
2. Click your profile icon (top-right)
3. Select **Admin Panel**

### Step 2: Configure TTS Settings
1. In Admin Panel, go to **Settings** → **Audio**
2. Scroll to **Text-to-Speech** section
3. Configure:
   - **TTS Engine**: Select `OpenAI`
   - **API Base URL**: `http://localhost:5002/v1`
   - **API Key**: Leave blank (not needed for local)
   - **TTS Model**: `tts-1` (or leave default)
   - **TTS Voice**: `lessac` (or leave default)

### Step 3: Test TTS
1. Go to any chat in OpenWebUI
2. Type a message and send it
3. Click the **speaker icon** 🔊 next to the response
4. Should hear audio within ~500ms

### Step 4: Enable Voice Calls (Optional)
1. In chat, click the **microphone icon** 🎤
2. Allow microphone permissions
3. Speak to test STT → LLM → TTS pipeline
4. Total latency should be under 2 seconds

## API Endpoints

### Health Check
```bash
curl http://localhost:5002/health
# Returns: {"status":"healthy","piper":true,"model":true}
```

### Generate Speech
```bash
curl -X POST http://localhost:5002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Hello world"}' \
  --output test.wav
```

### List Models
```bash
curl http://localhost:5002/v1/models
# Returns: {"models":[{"id":"lessac","name":"en_US-lessac-medium"}]}
```

## Performance Benchmarks

| Test | Response Time | Audio Quality |
|------|--------------|---------------|
| "Hello world" | 0.47s | 45KB WAV |
| Short sentence | 0.56s | 92KB WAV |
| Direct Piper | 0.10s | 76KB WAV |

**Real-time Factor**: 0.057 (17x faster than real-time)  
**Format**: RIFF WAVE, 16-bit mono, 22050 Hz PCM

## Adding More Voices

### Download Additional Voices
Visit: https://github.com/rhasspy/piper/releases

Example voices:
- `en_US-amy-medium` (Female, American)
- `en_US-ryan-medium` (Male, American)
- `en_GB-alan-medium` (Male, British)

### Install New Voice
```bash
cd /home/stacy/AlphaOmega/tts

# Download voice model
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx.json

# Test it
echo "Testing new voice" | ./piper/piper -m en_US-amy-medium.onnx -f /tmp/test.wav
```

### Update API to Support Multiple Voices
Edit `piper_api.py` to accept voice parameter in request body.

## Troubleshooting

### Server Not Starting
```bash
# Check logs
tail -f /home/stacy/AlphaOmega/logs/piper-api.log

# Check if port is in use
lsof -i :5002

# Kill and restart
pkill -f piper_api.py
cd /home/stacy/AlphaOmega/tts && python piper_api.py > ../logs/piper-api.log 2>&1 &
```

### No Audio in OpenWebUI
1. Verify API is running: `curl http://localhost:5002/health`
2. Check OpenWebUI TTS settings: API Base URL must be `http://localhost:5002/v1`
3. Check browser console for errors (F12)
4. Test API directly: `curl -X POST http://localhost:5002/v1/audio/speech -d '{"input":"test"}' --output test.wav`

### Slow Performance
- Current performance is excellent (~500ms total)
- If slower, check system load: `htop`
- Ensure no other processes using CPU heavily

### Audio Quality Issues
- Piper uses 22050 Hz sampling (standard for TTS)
- For higher quality, download a "high" quality model instead of "medium"
- Example: `en_US-lessac-high.onnx` (larger file, slower but better quality)

## Security Notes

### Local Only
- API listens on `0.0.0.0:5002` (accessible on local network)
- For external access, use reverse proxy with authentication
- No API key required (local trust)

### Safe Mode
- No file system access beyond `/tmp`
- No shell command injection risk (uses subprocess with list args)
- Input sanitization for special characters

## Advanced Configuration

### Environment Variables
Add to `.env` file:
```bash
PIPER_PORT=5002
PIPER_MODEL=en_US-lessac-medium
PIPER_SAMPLES_RATE=22050
PIPER_TIMEOUT=30
```

### Production Deployment
For production use with Nginx reverse proxy:
```nginx
location /tts/ {
    proxy_pass http://localhost:5002/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## Resources

- **Piper GitHub**: https://github.com/rhasspy/piper
- **Voice Models**: https://github.com/rhasspy/piper/releases
- **OpenWebUI Docs**: https://docs.openwebui.com/
- **AlphaOmega Docs**: `/home/stacy/AlphaOmega/docs/`

---

**Status**: ✅ Installed and configured  
**Last Updated**: October 10, 2025  
**Maintainer**: AlphaOmega Project
