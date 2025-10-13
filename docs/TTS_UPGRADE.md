# TTS Voice System Upgrade - October 13, 2025

## Summary
Upgraded AlphaOmega's text-to-speech system with high-quality voices and added state-of-the-art Chatterbox TTS integration.

## What Changed

### 1. **Coqui TTS Improvements**
- **Default Voice**: Switched to `jenny` (48kHz high-fidelity neural voice)
- **Fallback**: `tacotron2-DDC` (stable, proven quality)
- **Downloaded Models**: 14 English models including jenny, neural_hmm, glow-tts, fast_pitch
- **Voice Management**: Added `fetch_coqui_voices.py` script to enumerate and download models
- **Testing Tool**: Added `test_voices.py` to compare voice quality

### 2. **Chatterbox TTS Integration** (NEW)
- **Model**: Resemble AI's Chatterbox - state-of-the-art open source TTS
- **Quality**: Benchmarked against ElevenLabs, consistently preferred in evaluations
- **Features**:
  - Natural prosody and emotion
  - 0.5B Llama backbone
  - Exaggeration/intensity control
  - Ultra-stable with alignment-informed inference
  - Trained on 500K hours of cleaned data
- **Deployment**: Docker container on port 5003 (Python 3.11 required)

## Architecture

### Current TTS Stack
```
OpenWebUI (Port 3000)
    ↓
┌─────────────────────────────────┐
│  TTS Router (User Choice)       │
├─────────────────────────────────┤
│  Coqui TTS (Port 5002)          │  ← jenny voice, 48kHz, stable
│  - 14 English models cached     │
│  - OpenAI-compatible API        │
└─────────────────────────────────┘
│  Chatterbox TTS (Port 5003)     │  ← Natural prosody, expressive
│  - State-of-the-art quality     │
│  - Docker (Python 3.11)         │
│  - Emotion control              │
└─────────────────────────────────┘
```

### File Structure
```
tts/
├── coqui_api.py              # OpenAI-compatible Coqui TTS API
├── fetch_coqui_voices.py     # Voice model management tool
├── test_voices.py            # Voice quality comparison tool
├── chatterbox_api.py         # Chatterbox TTS API (NEW)
├── Dockerfile.chatterbox     # Chatterbox Docker build (NEW)
├── start_chatterbox.sh       # Chatterbox startup script (NEW)
├── start_coqui_api.sh        # Coqui TTS startup
└── stop_coqui_api.sh         # Coqui TTS shutdown
```

## Usage

### Start Chatterbox TTS (Recommended for Best Quality)
```bash
cd /home/stacy/AlphaOmega
bash tts/start_chatterbox.sh
```

**Endpoints:**
- API: `http://localhost:5003/v1/audio/speech`
- Health: `http://localhost:5003/health`
- Voices: `http://localhost:5003/v1/voices`

**Test:**
```bash
curl -X POST http://localhost:5003/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"tts-1","input":"Hello from Chatterbox!","voice":"alloy"}' \
  --output test.wav && aplay test.wav
```

### Coqui TTS (Current Default)
```bash
# Already running on port 5002
curl -X POST http://localhost:5002/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"tts-1","input":"Hello from Coqui!","voice":"jenny"}' \
  --output test.wav && aplay test.wav
```

### Compare Voice Quality
```bash
source venv/bin/activate
python tts/test_voices.py
# Plays: jenny, tacotron2, glow, neural_hmm, fast_pitch
aplay /tmp/tts_test_*.wav
```

### Download Additional Voices
```bash
source venv/bin/activate
python tts/fetch_coqui_voices.py --list           # List all English models
python tts/fetch_coqui_voices.py --download top   # Download curated set
python tts/fetch_coqui_voices.py --download all   # Download all (large)
```

## OpenWebUI Configuration

### Current Settings (Coqui/Jenny)
- **TTS Engine**: OpenAI
- **URL**: `http://localhost:5002/v1`
- **Voice**: `jenny`
- **Model**: `tts-1`

### Switch to Chatterbox (After Build Complete)
1. Go to OpenWebUI → Settings → Audio
2. Change **TTS URL** to: `http://localhost:5003/v1`
3. Keep voice as `default`
4. Model: `tts-1` (standard) or `tts-1-hd` (more expressive)

### For Smoother Synthesis
- **Response splitting**: Change from "Punctuation" to **"none"**
- This prevents choppy sentence-by-sentence synthesis
- Result: Smoother prosody, more natural flow

## Voice Comparison

| Model | Sample Rate | Quality | Prosody | Speed | Expressiveness |
|-------|-------------|---------|---------|-------|----------------|
| **Chatterbox** | 24kHz | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Fast | ⭐⭐⭐⭐⭐ |
| jenny (Coqui) | 48kHz | ⭐⭐⭐⭐ | ⭐⭐⭐ | Fast | ⭐⭐ |
| neural_hmm | 22kHz | ⭐⭐⭐ | ⭐⭐⭐⭐ | Medium | ⭐⭐ |
| glow-tts | 22kHz | ⭐⭐⭐ | ⭐⭐⭐ | Very Fast | ⭐⭐ |
| tacotron2-DDC | 22kHz | ⭐⭐⭐ | ⭐⭐⭐ | Medium | ⭐⭐ |

**Recommendation**: Use **Chatterbox** for production (most natural, expressive). Use **jenny** as fallback if Chatterbox has issues.

## Technical Details

### Why Docker for Chatterbox?
- Requires Python 3.11 (AlphaOmega uses Python 3.12)
- Avoids dependency conflicts
- Clean isolation
- Easy deployment

### GPU Support
Both services use AMD MI50 GPUs via ROCm:
- **Coqui**: GPU 1 (configured in `start_coqui_api.sh`)
- **Chatterbox**: Auto-detects available GPUs

### Performance
- **Coqui/jenny**: ~1-2 seconds for typical sentence
- **Chatterbox**: ~2-3 seconds (slightly slower, much better quality)

## Troubleshooting

### Chatterbox Docker Build Fails
```bash
# Check Docker status
docker ps -a | grep chatterbox

# View build logs
docker logs alphaomega-chatterbox

# Rebuild from scratch
docker rm alphaomega-chatterbox
docker rmi alphaomega-chatterbox:latest
bash tts/start_chatterbox.sh
```

### Voice Sounds Choppy in OpenWebUI
- Change **Response splitting** to "none" in audio settings
- This synthesizes full response at once instead of sentence-by-sentence

### Coqui TTS Not Responding
```bash
# Check status
curl http://localhost:5002/health

# Restart service
bash tts/stop_coqui_api.sh
bash tts/start_coqui_api.sh

# Check logs
tail -50 logs/coqui_tts.log
```

## Future Enhancements

1. **Voice Cloning**: Use XTTS v2 for custom voices
2. **Emotion Control**: Expose Chatterbox exaggeration parameters in OpenWebUI
3. **Multi-language**: Enable Chatterbox multilingual support (23 languages)
4. **Voice Selection UI**: Add voice picker in OpenWebUI
5. **Caching**: Pre-generate common responses

## References

- **Chatterbox**: https://github.com/resemble-ai/chatterbox
- **Coqui TTS**: https://github.com/coqui-ai/TTS
- **Demo**: https://resemble-ai.github.io/chatterbox_demopage/
- **Benchmarks**: https://podonos.com/resembleai/chatterbox

## Docker Permissions Note

**Authorized Docker Usage:**
- ✅ **Chatterbox TTS** (port 5003) - Approved
- ✅ **ComfyUI** (port 8188) - Approved
- ❌ **Other services** - Not approved, use host processes

---

*Updated: October 13, 2025*
*Contact: Stacy (wspotter)*
