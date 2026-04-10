#!/usr/bin/env python3
"""Export model statistics as JSON.

This script reads the saved model artifacts on disk, computes their sizes,
and combines them with the training times provided in the script.
"""

from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

TRAINING_TIMES = {
    "bilstm": {
        "en": "3m 45s",
        "es": "3m 36s",
        "de": "3m 49s",
    },
    "xgboost": {
        "en": "12m 45s",
        "es": "12m 38s",
        "de": "10m 36s",
    },
    "bert": {
        "en": "34m 34s",
        "es": "34m 37s",
        "de": "34m 57s",
    },
}


def format_size(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes} B"


def file_size(path: Path) -> str:
    return format_size(path.stat().st_size)


def build_payload() -> dict:
    payload = {}

    for lang in ["en", "es", "de"]:
        payload.setdefault("bert", {})[lang] = {
            "training_time": TRAINING_TIMES["bert"][lang],
            "model_size": file_size(BASE_DIR / "DistilBERT" / lang / "model.safetensors"),
            "tokenizer_size": file_size(BASE_DIR / "DistilBERT" / lang / "tokenizer.json"),
        }

        payload.setdefault("bilstm", {})[lang] = {
            "training_time": TRAINING_TIMES["bilstm"][lang],
            "model_size": file_size(BASE_DIR / "bilstm" / f"bilstm_model_{lang}.h5"),
            "tokenizer_size": file_size(BASE_DIR / "bilstm" / f"bilstm_tokenizer_{lang}.json"),
        }

        payload.setdefault("xgboost", {})[lang] = {
            "training_time": TRAINING_TIMES["xgboost"][lang],
            "model_size": file_size(BASE_DIR / "xgboost" / f"xgb_model_{lang}.joblib"),
            "tokenizer_size": file_size(BASE_DIR / "xgboost" / f"tfidf_{lang}.joblib"),
        }

    return payload


def main() -> None:
    print(json.dumps(build_payload(), indent=2))


if __name__ == "__main__":
    main()