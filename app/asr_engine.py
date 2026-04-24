from __future__ import annotations

import tempfile
from pathlib import Path
from typing import BinaryIO, List

from faster_whisper import WhisperModel
from pydub import AudioSegment

from app.text_postprocess import TaiwaneseTextPostProcessor, merge_segments_to_paragraphs


class ASREngine:
    def __init__(
        self,
        model_name: str = "large-v3",
        device: str = "cpu",
        compute_type: str = "int8",
        slang_path: Path | None = None,
    ):
        self.model = WhisperModel(model_name, device=device, compute_type=compute_type)
        self.postprocessor = TaiwaneseTextPostProcessor(slang_path=slang_path)

    def _ensure_wav(self, input_bytes: BinaryIO, filename: str) -> Path:
        suffix = Path(filename).suffix.lower()
        raw_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        raw_tmp.write(input_bytes.read())
        raw_tmp.flush()
        raw_path = Path(raw_tmp.name)

        if suffix == ".wav":
            return raw_path

        audio = AudioSegment.from_file(raw_path)
        wav_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav_path = Path(wav_tmp.name)
        audio.export(wav_path, format="wav")
        return wav_path

    def transcribe(self, input_bytes: BinaryIO, filename: str) -> List[dict]:
        wav_path = self._ensure_wav(input_bytes, filename)

        segments, _info = self.model.transcribe(
            str(wav_path),
            language="zh",
            beam_size=8,
            best_of=8,
            temperature=0.0,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
        )

        raw_segments = []
        for segment in segments:
            text = self.postprocessor.normalize(segment.text)
            if text:
                raw_segments.append(
                    {"start": float(segment.start), "end": float(segment.end), "text": text}
                )

        return merge_segments_to_paragraphs(raw_segments)


def format_srt_timestamp(sec: float) -> str:
    total_ms = int(sec * 1000)
    hours = total_ms // 3_600_000
    minutes = (total_ms % 3_600_000) // 60_000
    seconds = (total_ms % 60_000) // 1_000
    milliseconds = total_ms % 1_000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def to_srt(segments: List[dict]) -> str:
    lines: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        start = format_srt_timestamp(seg["start"])
        end = format_srt_timestamp(seg["end"])
        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)
