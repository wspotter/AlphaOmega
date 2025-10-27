# OpenWebUI TTS Setup - Simple Steps

## What You Need to Do in OpenWebUI

### Step 1: Open OpenWebUI Settings
1. Go to http://localhost:8080
2. Click your **profile icon** (top right)
3. Click **Settings**

### Step 2: Configure Audio/TTS
1. In Settings, click **Audio** (left sidebar)
2. Find the **Text-to-Speech (TTS)** section
3. Look for these settings:
   - **TTS Engine**: Set to `OpenAI`
   - **API Base URL**: Enter `http://localhost:5003/v1`
   - **API Key**: Leave blank or enter anything (not needed for local)
   - **Model**: `tts-1` (or `tts-1-hd` for higher quality)

### Step 3: Enable TTS
1. Toggle **Enable Text-to-Speech** to ON
2. Click **Save** or **Apply**

### Step 4: Test It
1. Go back to chat
2. Type a message: "Hello! Great to see you!"
3. Click the **speaker icon 🔊** next to the AI's response
4. You should hear it speak with a happy tone (auto-detected from "Great!")

## That's It!

The system will now automatically:
- Detect emotions from text ("amazing!!!" = excited, "sorry" = sad, etc.)
- Apply the appropriate voice tone
- No manual emotion selection needed

## Use Your Cloned Voice

1. Run the Chatterbox GUI with `./scripts/start-chatterbox-gui.sh` and upload your voice sample (for example `/tmp/chatterbox_voice.wav`).
2. Copy the final sample into `/tmp` so the Docker container can read it:
  ```bash
  cp tts/voice-sample-merged.wav /tmp/chatterbox_voice.wav
  ```
3. In OpenWebUI go to **Settings → Pipelines → Auto Emotion TTS → Configure**.
4. Set `voice_prompt_path` to `/tmp/chatterbox_voice.wav` (or whatever path you chose) and save.
5. Back in chat, click the speaker icon—the pipeline now sends the sample path to Chatterbox so every response clones that voice.

## Troubleshooting

### Can't find TTS settings?
- Look for **Audio**, **Voice**, or **Speech** in settings
- Might be under **Admin Panel** → **Settings** → **Audio**

### TTS not working?
```bash
# Check Chatterbox is running
docker ps | grep chatterbox

# Should see: alphaomega-chatterbox ... Up ... 0.0.0.0:5003->5003/tcp
```

### Want to test manually?
```bash
# Test TTS directly
curl -X POST http://localhost:5003/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello! This is amazing!"}' \
  --output test.wav

aplay test.wav
```

## Emotion Examples

The system automatically detects:
- "Hello! Great to see you!" → **happy** (cheerful)
- "This is amazing!!!" → **excited** (high energy)
- "I'm sorry about that." → **sad** (somber)
- "This is unacceptable!" → **angry** (intense)
- "Please relax and breathe." → **calm** (soothing)
- "Everything changed forever." → **dramatic** (theatrical)
- "I have a secret..." → **whisper** (quiet)
- "The weather is nice." → **neutral** (balanced)

No configuration needed - it just works!
