#!/usr/bin/env python3
"""
Chatterbox TTS API Server - OpenAI-compatible TTS endpoint
Uses Resemble AI's state-of-the-art Chatterbox model for natural, expressive speech.
"""
import io
import os
import logging
from pathlib import Path
from typing import Optional

import torchaudio as ta
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from chatterbox.tts import ChatterboxTTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Chatterbox TTS API",
    description="OpenAI-compatible TTS API using Chatterbox",
    version="1.0.0"
)

# Global model instance (lazy loaded)
chatterbox_model: Optional[ChatterboxTTS] = None

# Emotion presets for easy control
EMOTION_PRESETS = {
    "neutral": {"exaggeration": 0.3, "cfg_weight": 0.5},
    "happy": {"exaggeration": 0.7, "cfg_weight": 0.4},
    "excited": {"exaggeration": 0.9, "cfg_weight": 0.3},
    "sad": {"exaggeration": 0.4, "cfg_weight": 0.7},
    "calm": {"exaggeration": 0.2, "cfg_weight": 0.6},
    "dramatic": {"exaggeration": 0.8, "cfg_weight": 0.5},
    "angry": {"exaggeration": 0.85, "cfg_weight": 0.4},
    "whisper": {"exaggeration": 0.15, "cfg_weight": 0.8},
}


def get_model() -> ChatterboxTTS:
    """Lazy load Chatterbox model."""
    global chatterbox_model
    if chatterbox_model is None:
        logger.info("Loading Chatterbox TTS model...")
        device = "cpu"  # Force CPU for now
        chatterbox_model = ChatterboxTTS.from_pretrained(device=device)
        logger.info(f"Chatterbox model loaded on {device}")
    return chatterbox_model


def auto_detect_emotion(text: str) -> str:
    """
    Automatically detect emotion from text content
    Returns the most appropriate emotion based on keywords, punctuation, and patterns
    """
    import re
    
    text_lower = text.lower()
    scores = {}
    
    # Emotion detection patterns
    patterns = {
        "excited": [
            r"\b(amazing|incredible|awesome|wonderful|fantastic|wow|omg)\b",
            r"!!!+", r"\b(won|achieved|breakthrough)\b"
        ],
        "happy": [
            r"\b(happy|glad|great|excellent|good|nice|thank|love)\b",
            r"[😊😃😄😁]+", r":\)+", r"\b(perfect|wonderful|delighted)\b"
        ],
        "sad": [
            r"\b(sad|sorry|unfortunate|terrible|awful|disappointing)\b",
            r"[😢😭😞]+", r":\(+", r"\b(loss|failed|died|regret)\b"
        ],
        "angry": [
            r"\b(angry|furious|unacceptable|ridiculous|disgusting)\b",
            r"\b(stop|enough|hate|worst)\b", r"!!.*!!"
        ],
        "calm": [
            r"\b(relax|calm|peace|breathe|gently|slowly)\b",
            r"\?$", r"\b(please|kindly)\b"
        ],
        "dramatic": [
            r"\b(forever|never|always|everything|nothing)\b",
            r"\b(suddenly|moment|destiny|epic)\b"
        ],
        "whisper": [
            r"\b(secret|whisper|quietly|shh|confidential)\b",
            r"\.{3,}", r"\b(between us|don't tell)\b"
        ]
    }
    
    # Pattern matching
    for emotion, emotion_patterns in patterns.items():
        score = sum(len(re.findall(p, text_lower, re.IGNORECASE)) for p in emotion_patterns)
        if score > 0:
            scores[emotion] = score
    
    # Punctuation analysis
    exclamations = text.count("!")
    if exclamations >= 3:
        scores["excited"] = scores.get("excited", 0) + 2
    elif exclamations >= 1:
        scores["happy"] = scores.get("happy", 0) + 1
    
    # ALL CAPS = anger
    if len(re.findall(r'\b[A-Z]{2,}\b', text)) >= 2:
        scores["angry"] = scores.get("angry", 0) + 1
    
    # Return best match with priority order
    if scores:
        priority = ["excited", "angry", "sad", "happy", "whisper", "dramatic", "calm"]
        max_score = max(scores.values())
        for emotion in priority:
            if emotion in scores and scores[emotion] == max_score:
                return emotion
    
    return "neutral"


class TTSRequest(BaseModel):
    """OpenAI-compatible TTS request"""
    model: str = "tts-1"
    input: str
    voice: str = "alloy"
    response_format: str = "wav"
    speed: float = 1.0
    # Chatterbox-specific parameters
    exaggeration: float = 0.5  # 0.0-1.0, higher = more expressive
    cfg_weight: float = 0.5  # 0.0-1.0, guidance weight
    # Emotion preset (overrides exaggeration/cfg_weight if set)
    emotion: Optional[str] = None  # neutral, happy, sad, excited, calm, dramatic
    # Voice cloning
    audio_prompt_path: Optional[str] = None  # Path to audio sample for voice cloning


@app.get("/")
async def root():
    return {
        "name": "Chatterbox TTS API",
        "version": "1.0.0",
        "model": "Chatterbox (ResembleAI)",
        "description": "State-of-the-art open source TTS with natural prosody"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": chatterbox_model is not None}


@app.post("/v1/audio/speech")
async def create_speech(request: TTSRequest):
    """
    Generate speech from text (OpenAI compatible)
    
    Supports:
    - model: "tts-1" (standard), "tts-1-hd" (high quality, more expressive)
    - voice: ignored for now (uses default Chatterbox voice)
    - response_format: "wav" (others not yet implemented)
    - emotion: preset name (neutral, happy, sad, excited, calm, dramatic, angry, whisper)
    - exaggeration: 0.0-1.0 (Chatterbox-specific, default 0.5)
    - cfg_weight: 0.0-1.0 (Chatterbox-specific, default 0.5)
    
    Note: If 'emotion' is set, it overrides exaggeration/cfg_weight values.
    """
    try:
        logger.info(f"TTS request: model={request.model}, emotion={request.emotion}, text length={len(request.input)}")
        
        # Auto-detect emotion if not specified
        emotion_to_use = request.emotion
        if not emotion_to_use or emotion_to_use.lower() not in EMOTION_PRESETS:
            emotion_to_use = auto_detect_emotion(request.input)
            logger.info(f"Auto-detected emotion: '{emotion_to_use}' from text: '{request.input[:50]}...'")
        
        # Apply emotion preset
        exaggeration = request.exaggeration
        cfg_weight = request.cfg_weight
        
        if emotion_to_use and emotion_to_use.lower() in EMOTION_PRESETS:
            preset = EMOTION_PRESETS[emotion_to_use.lower()]
            exaggeration = preset["exaggeration"]
            cfg_weight = preset["cfg_weight"]
            logger.info(f"Applied emotion preset '{emotion_to_use}': exaggeration={exaggeration}, cfg_weight={cfg_weight}")
        
        # Adjust parameters for HD model (more expressive)
        if request.model in ("tts-1-hd", "hd"):
            exaggeration = min(1.0, exaggeration * 1.2)  # More expressive
            cfg_weight = max(0.2, cfg_weight * 0.9)  # Slightly more controlled
            logger.info(f"HD mode adjustment: exaggeration={exaggeration}, cfg_weight={cfg_weight}")
        
        # Get model
        model = get_model()
        
        # Generate audio
        logger.info(f"Generating speech with exaggeration={exaggeration}, cfg_weight={cfg_weight}, audio_prompt={request.audio_prompt_path}")
        wav = model.generate(
            request.input,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            audio_prompt_path=request.audio_prompt_path
        )
        
        # Convert to bytes
        buffer = io.BytesIO()
        ta.save(buffer, wav, model.sr, format="wav")
        buffer.seek(0)
        audio_data = buffer.read()
        
        logger.info(f"Generated {len(audio_data)} bytes of audio")
        
        # Return audio
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=speech.{request.response_format}"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/voices")
async def list_voices():
    """List available voices (for compatibility)"""
    return {
        "voices": [
            {
                "id": "chatterbox",
                "name": "Chatterbox",
                "description": "State-of-the-art neural voice with natural prosody"
            }
        ]
    }


@app.get("/v1/emotions")
async def list_emotions():
    """List available emotion presets"""
    return {
        "emotions": [
            {
                "id": emotion,
                "name": emotion.capitalize(),
                "exaggeration": params["exaggeration"],
                "cfg_weight": params["cfg_weight"],
                "description": _get_emotion_description(emotion)
            }
            for emotion, params in EMOTION_PRESETS.items()
        ]
    }


def _get_emotion_description(emotion: str) -> str:
    """Get description for emotion preset"""
    descriptions = {
        "neutral": "Balanced, natural delivery",
        "happy": "Upbeat and cheerful tone",
        "excited": "High energy and enthusiastic",
        "sad": "Slower, more somber delivery",
        "calm": "Gentle and soothing tone",
        "dramatic": "Theatrical and expressive",
        "angry": "Intense and forceful",
        "whisper": "Soft and intimate delivery"
    }
    return descriptions.get(emotion, "Custom emotion preset")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "5003"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("Starting Chatterbox API")
    logger.info(f"Starting Chatterbox TTS API on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
