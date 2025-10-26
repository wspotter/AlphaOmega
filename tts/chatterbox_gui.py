cd /home/stacy/AlphaOmega
./scripts/stop-dashboard.sh
./scripts/start-dashboard.sh#!/usr/bin/env python3
"""
Chatterbox TTS GUI - Gradio interface for testing voices and emotions
"""
import gradio as gr
import requests
import io
from pathlib import Path

API_URL = "http://localhost:5003/v1/audio/speech"

EMOTIONS = [
    "auto (detect from text)",
    "neutral",
    "happy", 
    "excited",
    "sad",
    "calm",
    "dramatic",
    "angry",
    "whisper"
]

def generate_speech(text, emotion, model, voice_file):
    """Generate speech using the Chatterbox API with optional voice cloning"""
    if not text.strip():
        return None, "Please enter some text"
    
    # Prepare request
    payload = {
        "input": text,
        "model": model
    }
    
    # Add emotion if not auto-detect
    if emotion != "auto (detect from text)":
        payload["emotion"] = emotion
    
    # Add voice file path for cloning
    if voice_file:
        payload["audio_prompt_path"] = voice_file
    
    try:
        # Call API
        response = requests.post(
            API_URL,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            return None, f"Error: {response.status_code} - {response.text}"
        
        # Return audio
        audio_data = response.content
        
        # Save to temp file
        temp_path = Path("/tmp/chatterbox_output.wav")
        temp_path.write_bytes(audio_data)
        
        status = f"✅ Generated {len(audio_data)} bytes"
        if voice_file:
            status += f" (voice cloned from {Path(voice_file).name})"
        if emotion == "auto (detect from text)":
            status += " (emotion auto-detected)"
        else:
            status += f" (emotion: {emotion})"
        
        return str(temp_path), status
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# Example texts for testing emotions
EXAMPLES = [
    ["Hello! Great to see you today!", "auto (detect from text)", "tts-1"],
    ["This is absolutely amazing!!!", "auto (detect from text)", "tts-1"],
    ["I'm sorry to hear about that.", "auto (detect from text)", "tts-1"],
    ["This is completely unacceptable!", "auto (detect from text)", "tts-1"],
    ["Please take a deep breath and relax.", "auto (detect from text)", "tts-1"],
    ["Everything changed in that moment forever.", "auto (detect from text)", "tts-1"],
    ["I have a secret to tell you...", "auto (detect from text)", "tts-1"],
    ["The weather is nice today.", "auto (detect from text)", "tts-1"],
]

# Create Gradio interface
with gr.Blocks(title="Chatterbox TTS", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎙️ Chatterbox TTS with Voice Cloning & Auto-Emotion")
    gr.Markdown("Generate natural speech with voice cloning, automatic emotion detection, or manual emotion control")
    
    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="Text to speak",
                placeholder="Enter text here...",
                lines=5
            )
            
            voice_file_input = gr.Audio(
                label="Voice Sample (optional - for voice cloning)",
                type="filepath",
                sources=["upload"]
            )
            
            emotion_select = gr.Dropdown(
                choices=EMOTIONS,
                value="auto (detect from text)",
                label="Emotion"
            )
            
            model_select = gr.Radio(
                choices=["tts-1", "tts-1-hd"],
                value="tts-1",
                label="Model Quality (HD = more expressive)"
            )
            
            generate_btn = gr.Button("🎵 Generate Speech", variant="primary")
            
        with gr.Column():
            audio_output = gr.Audio(
                label="Generated Speech",
                type="filepath"
            )
            
            status_output = gr.Textbox(
                label="Status",
                lines=2
            )
    
    gr.Markdown("### 📝 Example Texts")
    gr.Examples(
        examples=EXAMPLES,
        inputs=[text_input, emotion_select, model_select],
        label="Click to try:"
    )
    
    gr.Markdown("""
    ### 🎭 How It Works
    
    **Voice Cloning (Optional):**
    - Upload a 3-10 second audio sample of any voice
    - Chatterbox will clone that voice's style and characteristics
    - Works with any language/accent in the sample
    
    **Emotion Detection (Auto):**
    When set to "auto", the system detects emotion from:
    - **Keywords**: "amazing" → excited, "sorry" → sad, "relax" → calm
    - **Punctuation**: "!!!" → excited, "..." → whisper
    - **Context**: "thank you" → happy, "unacceptable" → angry
    
    **Manual Mode:**
    - Select a specific emotion to override auto-detection
    - Combine voice cloning + emotion control for precise results
    """)
    
    # Connect button
    generate_btn.click(
        fn=generate_speech,
        inputs=[text_input, emotion_select, model_select, voice_file_input],
        outputs=[audio_output, status_output]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
