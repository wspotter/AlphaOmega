"""
Emotion Detection Pipeline for OpenWebUI
Automatically detects emotion from text and applies appropriate TTS emotion
"""
from typing import List, Dict, Optional
import re
from pydantic import BaseModel


class Pipeline:
    """
    Auto-detects emotion from message content and applies to TTS
    """
    
    class Valves(BaseModel):
        priority: int = 0
        default_emotion: str = "neutral"
        enable_emoji_detection: bool = True
        enable_sentiment_keywords: bool = True
        enable_punctuation_analysis: bool = True
        
    def __init__(self):
        self.type = "filter"
        self.name = "Emotion Detector"
        self.valves = self.Valves()
        
        # Emotion keyword patterns (ordered by priority)
        self.emotion_patterns = {
            "excited": [
                r"\b(amazing|incredible|awesome|wonderful|fantastic|wow|omg|yes!+)\b",
                r"!!!+",
                r"\b(won|achieved|success|breakthrough|celebration)\b"
            ],
            "happy": [
                r"\b(happy|glad|pleased|delighted|great|excellent|good|nice|enjoy)\b",
                r"[😊😃😄😁🙂☺️]+",
                r"\b(thank you|thanks|appreciate|love|perfect)\b"
            ],
            "sad": [
                r"\b(sad|sorry|unfortunate|tragic|terrible|awful|disappointing|regret)\b",
                r"[😢😭😞☹️]+",
                r"\b(died|loss|lost|failed|passed away|condolences|sympathy)\b"
            ],
            "angry": [
                r"\b(angry|furious|outraged|unacceptable|ridiculous|disgusting|horrible)\b",
                r"\b(stop|enough|never|hate|terrible|worst)\b",
                r"!!+.*!!+",  # Multiple exclamations with emphasis
            ],
            "calm": [
                r"\b(relax|calm|peace|quiet|gentle|soft|breathe|meditate|rest)\b",
                r"\b(please|kindly|gently|slowly|carefully)\b",
                r"\?$",  # Questions often need calm delivery
            ],
            "dramatic": [
                r"\b(forever|never|always|everything|nothing|everyone|nobody)\b",
                r"\b(moment|destiny|fate|epic|legendary|historic)\b",
                r"\b(suddenly|then|and then|but then)\b"
            ],
            "whisper": [
                r"\b(secret|whisper|quietly|shh|psst|confidential|private)\b",
                r"\b(just between|don't tell|between us)\b",
                r"\.{3,}",  # Ellipsis suggests suspense/whisper
            ]
        }
    
    def detect_emotion(self, text: str) -> str:
        """
        Analyze text and return appropriate emotion
        Priority: excited > angry > sad > happy > whisper > dramatic > calm > neutral
        """
        text_lower = text.lower()
        emotion_scores = {}
        
        # Check each emotion pattern
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            
            if score > 0:
                emotion_scores[emotion] = score
        
        # Punctuation analysis
        if self.valves.enable_punctuation_analysis:
            exclamation_count = text.count("!")
            question_count = text.count("?")
            all_caps_words = len(re.findall(r'\b[A-Z]{2,}\b', text))
            
            # High excitement indicators
            if exclamation_count >= 3:
                emotion_scores["excited"] = emotion_scores.get("excited", 0) + 2
            elif exclamation_count >= 1:
                emotion_scores["happy"] = emotion_scores.get("happy", 0) + 1
            
            # All caps suggests anger or excitement
            if all_caps_words >= 2:
                emotion_scores["angry"] = emotion_scores.get("angry", 0) + 1
            
            # Questions suggest calm, thoughtful delivery
            if question_count >= 1 and exclamation_count == 0:
                emotion_scores["calm"] = emotion_scores.get("calm", 0) + 1
        
        # Return highest scoring emotion, or default
        if emotion_scores:
            # Priority order for ties
            priority_order = ["excited", "angry", "sad", "happy", "whisper", "dramatic", "calm"]
            max_score = max(emotion_scores.values())
            
            # Return first priority emotion with max score
            for emotion in priority_order:
                if emotion in emotion_scores and emotion_scores[emotion] == max_score:
                    return emotion
        
        return self.valves.default_emotion
    
    async def on_valves_updated(self):
        """Called when valves are updated"""
        pass
    
    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> dict:
        """
        Process the message and add emotion detection
        This runs before the message is sent to the LLM
        """
        # Detect emotion from the latest user message
        if messages:
            last_message = messages[-1].get("content", "")
            emotion = self.detect_emotion(last_message)
            
            # Store emotion in body for TTS to use
            if "metadata" not in body:
                body["metadata"] = {}
            body["metadata"]["tts_emotion"] = emotion
            
            # Log emotion detection
            print(f"[Emotion Detector] Detected '{emotion}' from: {last_message[:50]}...")
        
        return body
