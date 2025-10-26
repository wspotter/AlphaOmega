"""
TTS Emotion Applier Pipeline for OpenWebUI
Intercepts TTS requests and applies auto-detected emotions to Chatterbox
"""
from typing import Optional, Dict, Any
import httpx
from pydantic import BaseModel


class Pipeline:
    """
    Applies auto-detected emotions to TTS requests
    Works in conjunction with emotion_detector pipeline
    """
    
    class Valves(BaseModel):
        priority: int = 10  # Run after emotion detector
        chatterbox_url: str = "http://localhost:5003/v1/audio/speech"
        default_model: str = "tts-1"
        override_emotion: Optional[str] = None  # Manual override if needed
        enable_logging: bool = True
        
    def __init__(self):
        self.type = "filter"
        self.name = "TTS Emotion Applier"
        self.valves = self.Valves()
    
    async def on_valves_updated(self):
        """Called when valves are updated"""
        pass
    
    def pipe(self, user_message: str, model_id: str, messages: list, body: dict) -> dict:
        """
        Apply detected emotion to TTS configuration
        """
        # Check if emotion was detected
        emotion = None
        if "metadata" in body and "tts_emotion" in body["metadata"]:
            emotion = body["metadata"]["tts_emotion"]
        
        # Allow manual override
        if self.valves.override_emotion:
            emotion = self.valves.override_emotion
        
        # Apply emotion to TTS config
        if emotion:
            if "tts" not in body:
                body["tts"] = {}
            
            body["tts"]["engine"] = "openai"
            body["tts"]["url"] = self.valves.chatterbox_url
            body["tts"]["model"] = self.valves.default_model
            body["tts"]["emotion"] = emotion
            
            if self.valves.enable_logging:
                print(f"[TTS Emotion] Applying '{emotion}' emotion to TTS")
        
        return body
