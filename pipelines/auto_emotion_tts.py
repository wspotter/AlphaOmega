"""
Auto Emotion TTS Pipeline for OpenWebUI + Chatterbox
Automatically detects emotion from text and applies it to TTS responses
"""
from typing import List, Optional, Generator, Iterator
import re
import httpx
import json
from pydantic import BaseModel
from pathlib import Path


class Pipeline:
    """
    Analyzes text sentiment and automatically applies appropriate emotion to Chatterbox TTS
    No manual emotion selection needed - it's all automatic!
    """
    
    class Valves(BaseModel):
        priority: int = 0
        chatterbox_url: str = "http://localhost:5003/v1/audio/speech"
        enable_auto_emotion: bool = True
        log_emotion_detection: bool = True
        voice_prompt_path: str = ""
        
    def __init__(self):
        self.type = "manifold"
        self.name = "Auto Emotion TTS"
        self.valves = self.Valves()
        
        # Emotion detection patterns
        self.patterns = {
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
    
    def detect_emotion(self, text: str) -> str:
        """Auto-detect emotion from text"""
        if not self.valves.enable_auto_emotion:
            return "neutral"
        
        text_lower = text.lower()
        scores = {}
        
        # Pattern matching
        for emotion, patterns in self.patterns.items():
            score = sum(len(re.findall(p, text_lower, re.IGNORECASE)) for p in patterns)
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
        
        # Return best match
        if scores:
            priority = ["excited", "angry", "sad", "happy", "whisper", "dramatic", "calm"]
            max_score = max(scores.values())
            for emotion in priority:
                if emotion in scores and scores[emotion] == max_score:
                    return emotion
        
        return "neutral"
    
    def pipes(self) -> List[dict]:
        """Return available TTS engines"""
        return [
            {
                "id": "chatterbox-auto-emotion",
                "name": "Chatterbox (Auto Emotion)"
            }
        ]
    
    async def pipe(self, body: dict) -> str:
        """
        Generate TTS with auto-detected emotion
        This is called by OpenWebUI's TTS system
        """
        # Extract text
        text = body.get("input", "")
        if not text:
            return ""
        
        # Detect emotion
        emotion = self.detect_emotion(text)
        
        if self.valves.log_emotion_detection:
            print(f"[Auto Emotion TTS] Text: '{text[:50]}...'")
            print(f"[Auto Emotion TTS] Detected: {emotion}")
        
        # Prepare request for Chatterbox
        chatterbox_request = {
            "input": text,
            "model": body.get("model", "tts-1"),
            "emotion": emotion,
            "voice": body.get("voice", "alloy"),
            "response_format": body.get("response_format", "wav")
        }

        prompt_path = self.valves.voice_prompt_path.strip()
        if prompt_path:
            resolved = Path(prompt_path).expanduser()
            if resolved.exists():
                chatterbox_request["audio_prompt_path"] = str(resolved)
            elif self.valves.log_emotion_detection:
                print(f"[Auto Emotion TTS] Voice sample missing: {resolved}")
        
        # Call Chatterbox
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.valves.chatterbox_url,
                    json=chatterbox_request
                )
                
                if response.status_code == 200:
                    if self.valves.log_emotion_detection:
                        print(f"[Auto Emotion TTS] Generated audio with '{emotion}' emotion")
                    return response.content
                else:
                    print(f"[Auto Emotion TTS] Error: {response.status_code} - {response.text}")
                    return b""
                    
        except Exception as e:
            print(f"[Auto Emotion TTS] Exception: {e}")
            return b""
