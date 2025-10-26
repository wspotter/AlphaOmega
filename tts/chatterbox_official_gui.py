#!/usr/bin/env python3
"""Gradio GUI for the Chatterbox TTS Docker service."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple

import gradio as gr
import requests


API_URL = os.getenv("CHATTERBOX_API_URL", "http://localhost:5003/v1/audio/speech")
HEALTH_URL = API_URL.replace("/v1/audio/speech", "/health")
SHARED_TMP = Path(os.getenv("CHATTERBOX_SHARED_TMP", "/tmp"))
SHARED_TMP.mkdir(parents=True, exist_ok=True)

DEFAULT_TEXT = "Hello from Chatterbox! Let's make something amazing together."


def _prepare_audio_prompt(uploaded_path: Optional[str]) -> Optional[str]:
    """Copy uploaded audio into /tmp so the Docker container can read it."""
    if not uploaded_path:
        return None

    src = Path(uploaded_path)
    if not src.exists():
        return None

    target = SHARED_TMP / "chatterbox_prompt.wav"
    shutil.copy(src, target)
    return str(target)


def synthesize(
    text: str,
    reference_audio: Optional[str],
    model: str,
    temperature: float,
    exaggeration: float,
    top_p: float,
    min_p: float,
    repetition_penalty: float,
) -> Tuple[Optional[str], str]:
    """Send a synthesis request to the local Chatterbox API."""
    text = (text or "").strip()
    if not text:
        return None, "Please type something to speak."

    payload: dict = {
        "input": text,
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "min_p": min_p,
        "repetition_penalty": repetition_penalty,
        "exaggeration": exaggeration,
    }

    prompt_path = _prepare_audio_prompt(reference_audio)
    if prompt_path:
        payload["audio_prompt_path"] = prompt_path

    try:
        response = requests.post(API_URL, json=payload, timeout=180)
        if response.status_code != 200:
            return None, f"Error {response.status_code}: {response.text[:200]}"

        output_path = SHARED_TMP / "chatterbox_output.wav"
        output_path.write_bytes(response.content)

        detail = f"Generated audio ({len(response.content)} bytes)"
        if prompt_path:
            detail += f" using prompt {Path(prompt_path).name}"
        return str(output_path), f"✅ {detail}"
    except requests.exceptions.ConnectionError:
        return None, "Could not reach Chatterbox. Is the Docker container running?"
    except Exception as exc:  # noqa: BLE001
        return None, f"Unexpected error: {exc}"


def create_interface() -> gr.Blocks:
    with gr.Blocks(title="Chatterbox Voice Cloner") as demo:
        gr.Markdown("""
        # 🎙️ Chatterbox Voice Cloner
        Generate speech with the local Chatterbox Docker service. Optional voice cloning works best with 3-10 seconds of clean audio.
        """)

        health_text = gr.Markdown(value="Checking Chatterbox status…")

        def check_health() -> str:
            try:
                resp = requests.get(HEALTH_URL, timeout=5)
                if resp.status_code == 200:
                    return "✅ Chatterbox API is reachable."
                return f"⚠️ Chatterbox health check returned {resp.status_code}."
            except Exception:
                return "❌ Unable to reach Chatterbox. Make sure `./scripts/start-tts.sh` is running."

        health_text.value = check_health()

        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="Text to speak",
                    placeholder="Type what the cloned voice should say…",
                    value=DEFAULT_TEXT,
                    lines=5,
                )

                reference_audio = gr.Audio(
                    label="Voice sample (optional)",
                    type="filepath",
                    sources=["upload", "microphone"],
                )

                model_choice = gr.Dropdown(
                    label="Model",
                    choices=["tts-1", "tts-1-hd"],
                    value="tts-1",
                )

                generate_btn = gr.Button("🎵 Generate", variant="primary")

            with gr.Column():
                output_audio = gr.Audio(label="Generated audio", type="filepath")
                status_box = gr.Textbox(label="Status", interactive=False)

        with gr.Accordion("Advanced settings", open=False):
            temperature = gr.Slider(0.1, 2.0, value=0.8, step=0.05, label="Temperature (creativity)")
            exaggeration = gr.Slider(0.1, 2.0, value=0.5, step=0.05, label="Emotion exaggeration")
            top_p = gr.Slider(0.0, 1.0, value=1.0, step=0.01, label="Top-p")
            min_p = gr.Slider(0.0, 0.5, value=0.05, step=0.01, label="Min-p")
            repetition_penalty = gr.Slider(1.0, 2.0, value=1.2, step=0.05, label="Repetition penalty")

        generate_btn.click(
            synthesize,
            inputs=[
                text_input,
                reference_audio,
                model_choice,
                temperature,
                exaggeration,
                top_p,
                min_p,
                repetition_penalty,
            ],
            outputs=[output_audio, status_box],
        )

    return demo


if __name__ == "__main__":
    iface = create_interface()
    iface.launch(server_name="0.0.0.0", server_port=7861, share=False)
