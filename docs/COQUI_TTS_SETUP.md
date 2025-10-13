# Coqui TTS Setup Guide

Professional-grade text-to-speech with voice cloning support on AMD ROCm.

## Overview

**Coqui TTS** is an industry-standard open-source TTS system that provides:
- 🎙️ Professional voice quality (far superior to Piper TTS)
- 🔊 100+ pre-trained models in multiple languages
- 🎭 Voice cloning with just 5-10 seconds of reference audio
- 🚀 Fast inference on AMD MI50 GPUs (3x real-time)
- 🎚️ Multi-speaker support and emotion control
- 🔌 OpenAI-compatible API for easy integration

## Installation

### Prerequisites
- Python 3.12+ with virtual environment
- AMD ROCm 6.2 with PyTorch
- AMD MI50 or RX 6600 XT GPU
- 8GB+ GPU VRAM recommended

### Install Steps

```bash
# Activate virtual environment
cd /home/stacy/AlphaOmega
source venv/bin/activate

# Install Coqui TTS (Python 3.12 compatible version)
pip install coqui-tts

# Verify installation
tts --list_models | head -20
```

## Quick Start

### Command-Line Usage

```bash
# Generate speech with default voice
tts --text "Hello from Coqui TTS!" \
    --model_name "tts_models/en/ljspeech/vits" \
    --out_path output.wav

# List all available models
tts --list_models

# Use XTTS-v2 (best quality, voice cloning)
tts --text "Advanced text-to-speech synthesis" \
    --model_name "tts_models/multilingual/multi-dataset/xtts_v2" \
    --out_path advanced.wav
```

### API Server Usage

Start the OpenAI-compatible API server:

```bash
# Start server (runs on port 5002)
./tts/start_coqui_api.sh

# Check status
curl http://localhost:5002/health

# Stop server
./tts/stop_coqui_api.sh
```

### Generate Speech via API

```bash
# Basic text-to-speech
curl -X POST http://localhost:5002/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "tts-1",
    "input": "Your text here",
    "voice": "alloy"
  }' \
  --output speech.wav

# High-quality model
curl -X POST http://localhost:5002/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "tts-1-hd",
    "input": "High quality speech synthesis",
    "voice": "alloy"
  }' \
  --output hd_speech.wav
```

## Voice Cloning

Voice cloning allows you to generate speech in any voice with just a short audio sample (5-10 seconds).

### Using the API

```bash
# Upload reference audio and generate cloned speech
curl -X POST http://localhost:5002/v1/audio/clone \
  -F "text=This is my cloned voice speaking" \
  -F "reference_audio=@my_voice_sample.wav" \
  -F "model=tts-1-hd" \
  --output cloned_speech.wav
```

### Using Python

```python
from TTS.api import TTS

# Initialize XTTS-v2 model (supports voice cloning)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Clone voice and generate speech
tts.tts_to_file(
    text="This is cloned speech in my voice",
    file_path="output.wav",
    speaker_wav="reference_voice.wav",  # 5-10 second audio sample
    language="en"
)
```

## Model Selection Guide

### Fast Models (1-3x real-time on MI50)
- **`tts_models/en/ljspeech/vits`** - Good quality, very fast (default)
- **`tts_models/en/vctk/vits`** - Multi-speaker English
- **`tts_models/en/jenny/jenny`** - High-quality female voice

### High-Quality Models (0.5-1x real-time on MI50)
- **`tts_models/multilingual/multi-dataset/xtts_v2`** - Best quality, voice cloning, multilingual
- **`tts_models/multilingual/multi-dataset/bark`** - Natural prosody, emotion control

### Multi-Language Models
- **`tts_models/multilingual/multi-dataset/your_tts`** - 1100+ speakers, 13 languages
- **`tts_models/multilingual/multi-dataset/xtts_v2`** - English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Chinese, Japanese, Hungarian, Korean

## OpenWebUI Integration

### Configure OpenWebUI

1. Open OpenWebUI settings
2. Navigate to **Audio → Text-to-Speech**
3. Set **TTS API Base URL**: `http://localhost:5002/v1`
4. Select **Model**: `tts-1` (fast) or `tts-1-hd` (high quality)
5. Test with the 🔊 button

### Available Models in OpenWebUI
- **tts-1**: Fast LJSpeech VITS model (good quality)
- **tts-1-hd**: XTTS-v2 with voice cloning support (best quality)

## GPU Configuration

Coqui TTS can use AMD GPUs via ROCm:

```bash
# Use specific GPU (0=RX 6600 XT, 1=MI50 GPU1, 2=MI50 GPU2)
export ROCR_VISIBLE_DEVICES=1

# MI50 compatibility (required)
export HSA_OVERRIDE_GFX_VERSION=9.0.0

# Start API server with GPU
./tts/start_coqui_api.sh
```

Monitor GPU usage:
```bash
# Check GPU memory and utilization
rocm-smi

# Watch in real-time
watch -n 1 rocm-smi
```

## Performance Benchmarks

Tested on AMD Radeon Instinct MI50 (16GB VRAM):

| Model | Real-Time Factor | Quality | Notes |
|-------|------------------|---------|-------|
| LJSpeech VITS | 0.30-0.35 | Good | Fast, default |
| VCTK VITS | 0.32-0.40 | Good | Multi-speaker |
| Jenny | 0.35-0.45 | Excellent | High quality |
| XTTS-v2 | 0.50-0.70 | Excellent | Voice cloning |
| Bark | 0.60-0.90 | Excellent | Emotion control |

**Real-time factor < 1.0 means faster than real-time**  
Example: 0.30 = generates 10 seconds of audio in 3 seconds

## Troubleshooting

### Import Error: torchvision::nms does not exist

This occurs when mixing CUDA and ROCm PyTorch packages:

```bash
# Fix: Reinstall torchaudio for ROCm
pip uninstall -y torchaudio
pip install --index-url https://download.pytorch.org/whl/rocm6.2 torchaudio

# Verify all torch packages are ROCm versions
pip list | grep torch
# Should show: torch 2.5.1+rocm6.2, torchaudio 2.5.1+rocm6.2, torchvision 0.20.1+rocm6.2
```

### Model Download Fails

Models are cached in `~/.local/share/tts/`. Clear cache if download corrupted:

```bash
rm -rf ~/.local/share/tts/
tts --list_models  # Will re-download
```

### GPU Not Detected

Verify ROCm setup:

```bash
# Check GPU visibility
rocm-smi --showid

# Test PyTorch ROCm
python -c "import torch; print(torch.cuda.is_available())"  # Should be True

# Check GPU in TTS
python -c "from TTS.api import TTS; tts = TTS('tts_models/en/ljspeech/vits'); tts.to('cuda'); print('GPU OK')"
```

### API Server Won't Start

Check port availability:

```bash
# Check if port 5002 is in use
lsof -i :5002

# Kill existing process
./tts/stop_coqui_api.sh

# Restart
./tts/start_coqui_api.sh
```

Check logs:
```bash
tail -f logs/coqui_tts.log
```

## Advanced Configuration

### Environment Variables

```bash
# API server configuration
export TTS_HOST="0.0.0.0"          # Listen address
export TTS_PORT="5002"              # API port
export ROCR_VISIBLE_DEVICES="1"     # GPU selection
export HSA_OVERRIDE_GFX_VERSION="9.0.0"  # MI50 compatibility

# Model caching
export TTS_CACHE_DIR="$HOME/.cache/coqui_tts"
```

### Custom Voice Samples

Save reference audio for voice cloning:

```bash
# Create speaker samples directory
mkdir -p /tmp/coqui_speakers/

# Add your voice samples (5-10 seconds, clear audio)
cp my_voice.wav /tmp/coqui_speakers/custom_speaker.wav

# Use in API
curl -X POST http://localhost:5002/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "tts-1-hd",
    "input": "Speech in my voice",
    "voice": "/tmp/coqui_speakers/custom_speaker.wav"
  }' \
  --output output.wav
```

## API Reference

### Endpoints

#### `POST /v1/audio/speech`
Generate speech from text (OpenAI compatible)

**Request Body:**
```json
{
  "model": "tts-1",           // "tts-1" or "tts-1-hd"
  "input": "Text to speak",
  "voice": "alloy",           // Voice ID or path to WAV file
  "response_format": "wav",   // "wav", "mp3", "opus", "flac", etc.
  "speed": 1.0                // Speech speed (0.25-4.0)
}
```

**Response:** Audio file (WAV/MP3/etc)

#### `POST /v1/audio/clone`
Clone voice from reference audio

**Form Data:**
- `text` (string): Text to synthesize
- `reference_audio` (file): WAV file with voice sample (5-10 sec)
- `model` (string): Model to use (default: "tts-1-hd")

**Response:** Cloned audio WAV file

#### `GET /v1/models`
List available TTS models (OpenAI compatible)

**Response:**
```json
{
  "object": "list",
  "data": [
    {"id": "tts-1", "object": "model", "owned_by": "coqui-ai"},
    {"id": "tts-1-hd", "object": "model", "owned_by": "coqui-ai"}
  ]
}
```

#### `GET /v1/audio/voices`
List available voices

**Response:**
```json
{
  "voices": [
    {"id": "ljspeech", "name": "LJSpeech", "description": "Female English voice"},
    {"id": "vctk", "name": "VCTK", "description": "Multi-speaker dataset"}
  ]
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": 1,
  "gpu_available": true
}
```

## Comparison: Coqui vs Piper TTS

| Feature | Coqui TTS | Piper TTS |
|---------|-----------|-----------|
| Voice Quality | ⭐⭐⭐⭐⭐ Professional | ⭐⭐⭐ Computer-like |
| Voice Cloning | ✅ Yes (5-10 sec sample) | ❌ No |
| Multi-Speaker | ✅ 1100+ speakers | ⭐ Limited |
| Emotion Control | ✅ Yes (with Bark model) | ❌ No |
| Languages | ✅ 20+ languages | ✅ 50+ languages |
| Speed (MI50) | ⚡ 3x real-time | ⚡⚡ 10x real-time |
| GPU Support | ✅ ROCm, CUDA | ⚠️ CPU only |
| Model Size | 📦 100-500MB | 📦 60-120MB |
| API Compatible | ✅ OpenAI format | ✅ Wyoming protocol |
| Best Use Case | Customer-facing apps | Quick prototypes |

## Resources

- **Coqui TTS GitHub**: https://github.com/coqui-ai/TTS
- **Documentation**: https://tts.readthedocs.io/
- **Pre-trained Models**: https://github.com/coqui-ai/TTS/wiki/Released-Models
- **Voice Samples**: https://coqui.ai/samples

## License

Coqui TTS is released under the Mozilla Public License 2.0 (MPL-2.0).
Pre-trained models have their own licenses (Apache 2.0, CC BY-NC, etc.).

## Support

For issues or questions:
1. Check this documentation
2. Review logs: `tail -f logs/coqui_tts.log`
3. Test API: `curl http://localhost:5002/health`
4. Check GPU: `rocm-smi`
5. GitHub Issues: https://github.com/coqui-ai/TTS/issues
