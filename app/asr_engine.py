from __future__ import annotations

import tempfile
import logging
from pathlib import Path
from typing import Any, BinaryIO, Dict, List

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
        self.logger = logging.getLogger("asr_engine")

    @staticmethod
    def _decode_profile(profile: str) -> Dict[str, Any]:
        profile = profile.lower().strip()
        presets = {
            "fast": {"beam_size": 3, "best_of": 3, "temperature": 0},
            "balanced": {"beam_size": 5, "best_of": 5, "temperature": 0},
            "accurate": {"beam_size": 8, "best_of": 8, "temperature": 0},
        }
        return presets.get(profile, presets["balanced"])

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

    def transcribe(
        self,
        input_bytes: BinaryIO,
        filename: str,
        profile: str = "balanced",
        max_segment_duration: float = 8.0,
    ) -> List[dict]:
        wav_path = self._ensure_wav(input_bytes, filename)
        profile_cfg = self._decode_profile(profile)

        segments, _info = self.model.transcribe(
            str(wav_path),
            language="zh",
            beam_size=profile_cfg["beam_size"],
            best_of=profile_cfg["best_of"],
            temperature=profile_cfg["temperature"],
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500, "speech_pad_ms": 200},
            condition_on_previous_text=False,
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.6,
        )

        raw_segments = []
        for segment in segments:
            no_speech_prob = float(getattr(segment, "no_speech_prob", 0.0) or 0.0)
            avg_logprob = float(getattr(segment, "avg_logprob", 0.0) or 0.0)
            compression_ratio = float(getattr(segment, "compression_ratio", 0.0) or 0.0)

            self.logger.info(
                "segment start=%.2f end=%.2f no_speech=%.3f avg_logprob=%.3f compression_ratio=%.3f text=%s",
                float(segment.start),
                float(segment.end),
                no_speech_prob,
                avg_logprob,
                compression_ratio,
                segment.text.strip(),
            )

            if no_speech_prob > 0.6:
                continue
            if avg_logprob < -1.0:
                continue
            if compression_ratio > 2.4:
                continue

            text = self.postprocessor.normalize(segment.text)
            if text:
                raw_segments.append(
                    {"start": float(segment.start), "end": float(segment.end), "text": text}
                )

        return merge_segments_to_paragraphs(raw_segments, max_duration=max_segment_duration)


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
