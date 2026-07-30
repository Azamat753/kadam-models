#!/usr/bin/env python3
"""Rebuild manifest.json sizes and SHA-256 digests from model artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = {
    "tts": ("tts/model.onnx", "tts/tokens.txt"),
    "asr": ("asr/model.onnx", "asr/vocab.json", "asr/asr-meta.json"),
}
PLACEHOLDER = "URL_БУДЕТ_УКАЗАН_ПОСЛЕ_ПУБЛИКАЦИИ"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-version", default="1.0.0")
    parser.add_argument(
        "--base-url",
        help=(
            "Release asset base, e.g. "
            "https://github.com/OWNER/kadam-models/releases/download/v1.0.0"
        ),
    )
    args = parser.parse_args()

    manifest: dict[str, object] = {
        "manifestVersion": 1,
        "modelVersion": args.model_version,
    }
    for group, relative_paths in FILES.items():
        entries = []
        for relative in relative_paths:
            path = ROOT / relative
            if not path.is_file():
                raise SystemExit(f"Missing required file: {relative}")
            entries.append(
                {
                    "name": path.name,
                    "path": relative,
                    "url": (
                        f"{args.base_url.rstrip('/')}/{relative.replace('/', '-')}"
                        if args.base_url
                        else PLACEHOLDER
                    ),
                    "size": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
        manifest[group] = {"files": entries}

    output = ROOT / "manifest.json"
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {output}")


if __name__ == "__main__":
    main()
