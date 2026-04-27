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
        cleaned = self._dedupe_repeated_words(cleaned, keep=2, trigger=3)
        cleaned = self._dedupe_repeated_phrases(cleaned, keep=2, trigger=3)
        cleaned = re.sub(r"([。！？!?]){2,}", r"\1", cleaned)
        return cleaned

    @staticmethod
    def _dedupe_repeated_words(text: str, keep: int = 2, trigger: int = 3) -> str:
        words = text.split()
        if len(words) < trigger + 1:
            return text

        reduced: List[str] = []
        i = 0
        while i < len(words):
            j = i + 1
            while j < len(words) and words[j] == words[i]:
                j += 1
            run_len = j - i
            if run_len > trigger:
                reduced.extend([words[i]] * keep)
            else:
                reduced.extend(words[i:j])
            i = j
        return " ".join(reduced)

    @staticmethod
    def _dedupe_repeated_phrases(text: str, keep: int = 2, trigger: int = 3) -> str:
        # 例如：阿達斯杜倫阿達斯杜倫阿達斯杜倫... 或中間夾空白
        pattern = re.compile(r"(.{2,20}?)(?:\s*\1){" + str(trigger) + r",}")
        while True:
            new_text = pattern.sub(lambda m: (m.group(1).strip() + " ") * keep, text).strip()
            if new_text == text:
                break
            text = re.sub(r"\s+", " ", new_text).strip()
        return text


def split_segment_by_max_duration(segment: dict, max_duration: float = 8.0) -> List[dict]:
    duration = float(segment["end"]) - float(segment["start"])
    if duration <= max_duration:
        return [segment]

    text = segment["text"].strip()
    if not text:
        return []

    chunks = [x.strip() for x in re.split(r"([。！？!?，,；;])", text) if x.strip()]
    if len(chunks) <= 1:
        chunk_size = max(1, len(text) // int(duration // max_duration + 1))
        chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    part_count = max(1, int(duration // max_duration) + (1 if duration % max_duration else 0))
    if len(chunks) < part_count:
        avg = max(1, len(text) // part_count)
        chunks = [text[i : i + avg] for i in range(0, len(text), avg)]

    # 均分時間軸（無逐詞時間戳時的折衷方案）
    total = len(chunks)
    sub_segments: List[dict] = []
    for idx, chunk in enumerate(chunks):
        start = segment["start"] + duration * idx / total
        end = segment["start"] + duration * (idx + 1) / total
        sub_segments.append({"start": start, "end": min(end, start + max_duration), "text": chunk})
    return sub_segments


def merge_segments_to_paragraphs(
    segments: List[dict], max_gap: float = 1.2, max_duration: float = 8.0
) -> List[dict]:
    if not segments:
        return []

    expanded: List[dict] = []
    for seg in segments:
        expanded.extend(split_segment_by_max_duration(seg, max_duration=max_duration))
    if not expanded:
        return []

    merged: List[dict] = []
    cur = {
        "start": expanded[0]["start"],
        "end": expanded[0]["end"],
        "text": expanded[0]["text"].strip(),
    }

    sentence_endings = ("。", "！", "？", ".", "!", "?")

    for seg in expanded[1:]:
        gap = seg["start"] - cur["end"]
        next_duration = seg["end"] - cur["start"]
        should_split = (
            gap > max_gap
            or cur["text"].endswith(sentence_endings)
            or next_duration > max_duration
            or (cur["end"] - cur["start"]) >= max_duration
        )

        if should_split:
            cur["end"] = min(cur["end"], cur["start"] + max_duration)
            merged.append(cur)
            cur = {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip(),
            }
        else:
            cur["end"] = seg["end"]
            cur["text"] = f"{cur['text']} {seg['text'].strip()}".strip()

    cur["end"] = min(cur["end"], cur["start"] + max_duration)
    merged.append(cur)
    return merged
