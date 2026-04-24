from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List


class TaiwaneseTextPostProcessor:
    def __init__(self, slang_path: Path | None = None):
        self.slang_map = self._load_slang_map(slang_path)

    @staticmethod
    def _load_slang_map(slang_path: Path | None) -> Dict[str, str]:
        if not slang_path or not slang_path.exists():
            return {}
        with slang_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def normalize(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        for src, dst in self.slang_map.items():
            cleaned = cleaned.replace(src, dst)
        cleaned = re.sub(r"([。！？!?]){2,}", r"\1", cleaned)
        return cleaned


def merge_segments_to_paragraphs(segments: List[dict], max_gap: float = 1.2) -> List[dict]:
    if not segments:
        return []

    merged: List[dict] = []
    cur = {
        "start": segments[0]["start"],
        "end": segments[0]["end"],
        "text": segments[0]["text"].strip(),
    }

    sentence_endings = ("。", "！", "？", ".", "!", "?")

    for seg in segments[1:]:
        gap = seg["start"] - cur["end"]
        should_split = gap > max_gap or cur["text"].endswith(sentence_endings)

        if should_split:
            merged.append(cur)
            cur = {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
        else:
            cur["end"] = seg["end"]
            cur["text"] = f"{cur['text']} {seg['text'].strip()}".strip()

    merged.append(cur)
    return merged
