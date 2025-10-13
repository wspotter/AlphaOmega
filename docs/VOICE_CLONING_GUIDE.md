# Voice Cloning Guide

Clone any voice with just 5-10 seconds of audio using Coqui TTS XTTS-v2.

## What is Voice Cloning?

Voice cloning allows you to:
- 🎙️ Generate speech in any voice from a short audio sample
- 🗣️ Create custom voices for applications, games, assistants
- 🌍 Synthesize speech in multiple languages with the same cloned voice
- 🎭 Preserve natural speech characteristics (accent, tone, cadence)

## Requirements

### Audio Sample Quality

For best results, your reference audio should:
- ✅ Be 5-10 seconds long (longer doesn't necessarily help)
- ✅ Contain clear, clean speech (no background music or noise)
- ✅ Be in WAV format (16-bit, 22050Hz or higher)
- ✅ Feature natural speaking (not reading or monotone)
- ✅ Have consistent volume (not too quiet or clipping)

### What to Avoid
- ❌ Multiple speakers in the same audio
- ❌ Background music, noise, or echo
- ❌ Very short samples (< 3 seconds)
- ❌ Overly compressed audio (low bitrate MP3)
- ❌ Robot or synthesized voices

## Quick Start

### 1. Prepare Reference Audio

Record or extract a clean 5-10 second voice sample:

```bash
# Record from microphone (Linux)
arecord -f cd -d 10 -r 22050 my_voice.wav

# Extract from video (requires ffmpeg)
ffmpeg -i video.mp4 -ss 00:01:30 -t 10 -vn -acodec pcm_s16le -ar 22050 voice_sample.wav

# Convert existing audio to correct format
ffmpeg -i audio.mp3 -ar 22050 -ac 1 -sample_fmt s16 voice_sample.wav
```

### 2. Clone Voice via API

```bash
curl -X POST http://localhost:5002/v1/audio/clone \
  -F "text=This is my cloned voice speaking. It sounds just like me!" \
  -F "reference_audio=@voice_sample.wav" \
  -F "model=tts-1-hd" \
  --output cloned_speech.wav
```

### 3. Generate More Speech

Once you have a reference audio saved, you can reuse it:

```bash
# Clone with custom text
curl -X POST http://localhost:5002/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "tts-1-hd",
    "input": "Any text you want in my voice",
    "voice": "/tmp/coqui_speakers/my_voice.wav"
  }' \
  --output output.wav
```

## Python Examples

### Basic Voice Cloning

```python
from TTS.api import TTS

# Initialize XTTS-v2 (voice cloning model)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Clone voice
tts.tts_to_file(
    text="This is cloned speech in a custom voice.",
    file_path="output.wav",
    speaker_wav="reference_voice.wav",
    language="en"
)
```

### Multi-Language Cloning

Clone a voice and generate speech in different languages:

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Clone English voice
tts.tts_to_file(
    text="Hello, this is my cloned voice speaking English.",
    file_path="english.wav",
    speaker_wav="my_voice_english.wav",
    language="en"
)

# Same voice speaking Spanish
tts.tts_to_file(
    text="Hola, esta es mi voz clonada hablando español.",
    file_path="spanish.wav",
    speaker_wav="my_voice_english.wav",
    language="es"
)

# Same voice speaking French
tts.tts_to_file(
    text="Bonjour, c'est ma voix clonée parlant français.",
    file_path="french.wav",
    speaker_wav="my_voice_english.wav",
    language="fr"
)
```

### Batch Voice Cloning

Clone multiple voices and generate speech:

```python
from TTS.api import TTS
import os

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Directory with voice samples
voice_samples_dir = "/tmp/voice_samples/"
text_to_speak = "This is a test of voice cloning technology."

# Clone each voice
for voice_file in os.listdir(voice_samples_dir):
    if voice_file.endswith(".wav"):
        speaker_path = os.path.join(voice_samples_dir, voice_file)
        output_path = f"cloned_{voice_file}"
        
        print(f"Cloning voice: {voice_file}")
        tts.tts_to_file(
            text=text_to_speak,
            file_path=output_path,
            speaker_wav=speaker_path,
            language="en"
        )
        print(f"Saved to: {output_path}")
```

### Interactive Voice Cloning

Create an interactive voice cloning demo:

```python
from TTS.api import TTS
import os

def clone_voice_interactive():
    """Interactive voice cloning"""
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    # Get reference audio
    reference_audio = input("Path to reference audio (WAV): ").strip()
    if not os.path.exists(reference_audio):
        print(f"Error: File not found: {reference_audio}")
        return
    
    # Get text to synthesize
    print("\nEnter text to synthesize (or 'quit' to exit):")
    while True:
        text = input("> ").strip()
        if text.lower() == 'quit':
            break
        
        if not text:
            continue
        
        # Generate speech
        output_path = f"cloned_{len(text)}.wav"
        print(f"Generating speech... (saving to {output_path})")
        
        try:
            tts.tts_to_file(
                text=text,
                file_path=output_path,
                speaker_wav=reference_audio,
                language="en"
            )
            print(f"✓ Saved to {output_path}")
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    clone_voice_interactive()
```

## Advanced Techniques

### Improving Clone Quality

#### 1. Use High-Quality Reference Audio

```python
from TTS.api import TTS
import torchaudio

# Load and enhance reference audio
waveform, sample_rate = torchaudio.load("raw_voice.wav")

# Normalize audio
waveform = waveform / waveform.abs().max()

# Save enhanced version
torchaudio.save("enhanced_voice.wav", waveform, sample_rate)

# Use enhanced version for cloning
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.tts_to_file(
    text="Speech with enhanced reference audio.",
    file_path="output.wav",
    speaker_wav="enhanced_voice.wav",
    language="en"
)
```

#### 2. Multiple Reference Samples

Use multiple samples to capture voice variations:

```python
from TTS.api import TTS
import numpy as np
import soundfile as sf

def merge_audio_samples(audio_files, output_file):
    """Merge multiple audio samples into one"""
    samples = []
    for file in audio_files:
        data, sr = sf.read(file)
        samples.append(data)
    
    # Concatenate samples
    merged = np.concatenate(samples)
    sf.write(output_file, merged, sr)
    return output_file

# Merge multiple samples
voice_samples = [
    "sample1.wav",
    "sample2.wav",
    "sample3.wav"
]
merged_sample = merge_audio_samples(voice_samples, "merged_voice.wav")

# Use merged sample for cloning
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.tts_to_file(
    text="Cloned with multiple reference samples.",
    file_path="output.wav",
    speaker_wav=merged_sample,
    language="en"
)
```

### Voice Style Transfer

Control prosody and emotion:

```python
from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Excited/energetic version
tts.tts_to_file(
    text="This is amazing! Voice cloning is incredible!",
    file_path="excited.wav",
    speaker_wav="excited_sample.wav",  # Use excited reference
    language="en"
)

# Calm/professional version
tts.tts_to_file(
    text="This is a professional demonstration of voice cloning.",
    file_path="calm.wav",
    speaker_wav="calm_sample.wav",  # Use calm reference
    language="en"
)
```

## Use Cases

### 1. Custom Voice Assistants

```python
from TTS.api import TTS

class VoiceAssistant:
    def __init__(self, voice_sample):
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self.voice_sample = voice_sample
    
    def speak(self, text):
        """Generate speech in custom voice"""
        self.tts.tts_to_file(
            text=text,
            file_path="assistant_response.wav",
            speaker_wav=self.voice_sample,
            language="en"
        )
        # Play audio here (using pygame, playsound, etc.)
        print(f"Assistant: {text}")

# Usage
assistant = VoiceAssistant("my_voice.wav")
assistant.speak("Hello! How can I help you today?")
assistant.speak("Your order has been confirmed.")
```

### 2. Content Localization

```python
from TTS.api import TTS

def localize_content(text_translations, voice_sample):
    """Generate voiceovers in multiple languages"""
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    for lang_code, text in text_translations.items():
        output_file = f"localized_{lang_code}.wav"
        
        tts.tts_to_file(
            text=text,
            file_path=output_file,
            speaker_wav=voice_sample,
            language=lang_code
        )
        print(f"Created {lang_code} voiceover: {output_file}")

# Usage
translations = {
    "en": "Welcome to our application.",
    "es": "Bienvenido a nuestra aplicación.",
    "fr": "Bienvenue dans notre application.",
    "de": "Willkommen in unserer Anwendung."
}
localize_content(translations, "narrator_voice.wav")
```

### 3. Audiobook Production

```python
from TTS.api import TTS
import re

def create_audiobook(text_file, voice_sample, output_file):
    """Convert text to audiobook with cloned voice"""
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    
    # Read text
    with open(text_file, 'r') as f:
        text = f.read()
    
    # Split into chapters/sections
    chapters = re.split(r'\n\n+', text)
    
    audio_segments = []
    for i, chapter in enumerate(chapters):
        if not chapter.strip():
            continue
        
        chapter_file = f"chapter_{i}.wav"
        print(f"Generating chapter {i+1}/{len(chapters)}...")
        
        tts.tts_to_file(
            text=chapter.strip(),
            file_path=chapter_file,
            speaker_wav=voice_sample,
            language="en"
        )
        audio_segments.append(chapter_file)
    
    print(f"Created {len(audio_segments)} audio segments")
    return audio_segments

# Usage
create_audiobook("book.txt", "narrator_voice.wav", "audiobook.wav")
```

## Best Practices

### 1. Reference Audio Quality Checklist

Before using audio for voice cloning:

```bash
# Check audio properties
ffprobe -i voice_sample.wav

# Should show:
# - Duration: 5-10 seconds
# - Sample rate: 22050 Hz or higher
# - Channels: 1 (mono) or 2 (stereo)
# - Bit depth: 16-bit or higher

# Listen for issues
# - Background noise
# - Echo or reverb
# - Distortion or clipping
# - Multiple speakers
```

### 2. Text Preparation

Prepare text for natural-sounding speech:

```python
import re

def prepare_text_for_tts(text):
    """Clean and format text for TTS"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Add pauses after sentences
    text = re.sub(r'\.', '. ', text)
    text = re.sub(r'\!', '! ', text)
    text = re.sub(r'\?', '? ', text)
    
    # Expand common abbreviations
    text = text.replace("Dr.", "Doctor")
    text = text.replace("Mr.", "Mister")
    text = text.replace("Mrs.", "Missus")
    text = text.replace("etc.", "et cetera")
    
    return text.strip()

# Usage
raw_text = "Dr. Smith said,  'Hello!  How are you?'  etc."
clean_text = prepare_text_for_tts(raw_text)
print(clean_text)
# Output: "Doctor Smith said, 'Hello! How are you?' et cetera."
```

### 3. Caching Voice Models

Avoid reloading models for better performance:

```python
from TTS.api import TTS

class VoiceCloningService:
    def __init__(self):
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
        self.voices = {}  # Cache voice embeddings
    
    def register_voice(self, voice_id, voice_sample_path):
        """Register a voice for reuse"""
        self.voices[voice_id] = voice_sample_path
    
    def synthesize(self, text, voice_id, language="en"):
        """Generate speech with cached voice"""
        if voice_id not in self.voices:
            raise ValueError(f"Voice {voice_id} not registered")
        
        output_path = f"{voice_id}_output.wav"
        self.tts.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=self.voices[voice_id],
            language=language
        )
        return output_path

# Usage
service = VoiceCloningService()
service.register_voice("narrator", "narrator_voice.wav")
service.register_voice("character1", "character1_voice.wav")

service.synthesize("Narration text", "narrator")
service.synthesize("Character dialogue", "character1")
```

## Troubleshooting

### Clone Doesn't Sound Like Reference

**Possible causes:**
1. Reference audio is too short (< 5 seconds)
2. Poor audio quality (noise, compression)
3. Multiple speakers in reference
4. Reference voice is very different from training data

**Solutions:**
- Use 7-10 second samples
- Clean audio with audio editing software
- Use single-speaker clips only
- Try different reference samples

### Generated Speech Sounds Robotic

**Solutions:**
- Use natural, conversational reference audio
- Avoid monotone or reading-style samples
- Include prosody variation in reference
- Try XTTS-v2 instead of older models

### Different Languages Sound Wrong

**Note:** Voice cloning works best when:
- Reference audio is in the target language, OR
- Using XTTS-v2 which supports cross-lingual cloning

**Example:**
```python
# English reference, Spanish speech (cross-lingual)
tts.tts_to_file(
    text="Hola, ¿cómo estás?",
    file_path="spanish.wav",
    speaker_wav="english_reference.wav",  # English sample
    language="es"
)
```

## Resources

- **XTTS-v2 Paper**: https://arxiv.org/abs/2406.04904
- **Voice Sample Guidelines**: https://tts.readthedocs.io/en/latest/voice_cloning.html
- **Supported Languages**: English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Chinese, Japanese, Hungarian, Korean

## Ethics & Legal Considerations

⚠️ **Important Guidelines:**

1. **Consent Required**: Only clone voices with explicit permission
2. **Disclosure**: Inform listeners if voice is synthesized
3. **No Impersonation**: Don't use cloned voices to deceive or defraud
4. **Copyright**: Respect intellectual property and voice actor rights
5. **Privacy**: Don't share voice samples without consent

**Legal uses:**
- ✅ Your own voice
- ✅ Licensed voice actors
- ✅ Public domain recordings
- ✅ Educational/research purposes
- ✅ With written consent

**Illegal/unethical uses:**
- ❌ Impersonation for fraud
- ❌ Deepfakes without disclosure
- ❌ Copyright infringement
- ❌ Non-consensual cloning

## License

Voice cloning technology should be used responsibly. Coqui TTS is MPL-2.0 licensed.
