#!/usr/bin/env python3
"""
Fetch and optionally pre-download Coqui TTS English models to the local cache.

Usage:
  python tts/fetch_coqui_voices.py --list            # list available English models
  python tts/fetch_coqui_voices.py --download top    # download curated top English models
  python tts/fetch_coqui_voices.py --download all    # download all English models (large)

Notes:
  - Uses Coqui TTS model registry via TTS().list_models()
  - Filters for English models by simple heuristics ("/en/" in model id)
  - Pre-download by running a tiny synth to force cache population
"""
import argparse
import sys
from pathlib import Path

from TTS.api import TTS

CURATED = [
    # Fast, stable single-speaker English
    "tts_models/en/ljspeech/tacotron2-DDC",
    "tts_models/en/ljspeech/vits",
    # Multi-speaker English
    "tts_models/en/vctk/vits",
    # Voice cloning (multilingual, includes en)
    "tts_models/multilingual/multi-dataset/xtts_v2",
]

def list_english_models() -> list[str]:
    tts = TTS()
    models = tts.list_models()
    english = [m for m in models if "/en/" in m or m.endswith("xtts_v2")]
    return sorted(set(english))

def predownload(models: list[str]) -> None:
    print(f"Prefetching {len(models)} model(s) into cache...")
    for m in models:
        try:
            print(f"  • {m}")
            t = TTS(model_name=m)
            # Minimal warm-up: build vocoder and save a tiny wav to trigger cache
            t.tts_to_file(text="hello", file_path=str(Path("/tmp")/"coqui_warmup.wav"))
        except Exception as e:
            print(f"    ! Failed to prefetch {m}: {e}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--list", action="store_true", help="List English models")
    p.add_argument("--download", choices=["top", "all"], help="Download curated top or all English models")
    args = p.parse_args()

    if args.list:
        english = list_english_models()
        print("English-capable models:")
        for m in english:
            print(f"- {m}")
        return

    if args.download:
        if args.download == "top":
            predownload(CURATED)
        else:
            predownload(list_english_models())
        print("Done.")
        return

    p.print_help()

if __name__ == "__main__":
    main()
