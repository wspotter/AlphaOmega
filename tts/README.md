# Chatterbox TTS Module

This folder collects everything needed for local text-to-speech inside AlphaOmega.

## Start the main Chatterbox API
- Command: `./scripts/start-tts.sh`
- Service URL: [http://localhost:5003/v1/audio/speech](http://localhost:5003/v1/audio/speech)
- Health check: [http://localhost:5003/health](http://localhost:5003/health)
- Logs land in `logs/chatterbox*.log`.

## Voice cloning GUI
We ship a ready-to-use graphical interface so you can try voice cloning without writing code.

1. Run `./scripts/start-chatterbox-gui.sh`.
2. Wait for the log message that says the GUI started (PID shown in the terminal).
3. Open your browser to [http://localhost:7861](http://localhost:7861).
4. Upload a short voice sample and type text to hear the cloned result.

The GUI runs on top of `tts/chatterbox_official_gui.py`. You can stop it anytime with `pkill -f chatterbox_official_gui.py` or by running `./scripts/stop-tts.sh` to shut down every Chatterbox process.

## Helpful extras
- `chatterbox_gui.py` offers a lighter demo GUI on port 7860 (run `python tts/chatterbox_gui.py`).
- `VOICES.md` lists quick links for Piper voices if you want classic TTS without cloning.
- `start_chatterbox.sh` builds and runs the Docker image manually if you need to operate outside the helper scripts.
