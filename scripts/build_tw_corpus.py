from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Iterable, List

import webvtt


def run(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def normalize_channel(channel: str) -> str:
    channel = channel.strip()
    if not channel:
        return ""
    if channel.startswith("http"):
        return channel
    if channel.startswith("@"):
        return f"https://www.youtube.com/{channel}"
    return channel


def download_subtitles(channel_url: str, temp_dir: Path) -> Iterable[Path]:
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-auto-sub",
        "--write-sub",
        "--sub-langs",
        "zh-TW,zh-Hant,zh,zh-Hans",
        "--sub-format",
        "vtt",
        "-o",
        str(temp_dir / "%(channel)s_%(id)s.%(ext)s"),
        channel_url,
    ]
    proc = run(cmd)
    if proc.returncode != 0:
        print(f"[WARN] failed: {channel_url}\n{proc.stderr}")
    return temp_dir.glob("*.vtt")


def vtt_to_lines(vtt_path: Path) -> List[str]:
    lines = []
    for caption in webvtt.read(str(vtt_path)):
        text = " ".join(caption.text.split())
        if text and text not in lines:
            lines.append(text)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Taiwanese YouTube subtitle corpus")
    parser.add_argument("--channels-file", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tmp-dir", default=Path(".tmp_subs"), type=Path)
    args = parser.parse_args()

    channels = [normalize_channel(x) for x in args.channels_file.read_text(encoding="utf-8").splitlines()]
    channels = [x for x in channels if x]

    args.tmp_dir.mkdir(parents=True, exist_ok=True)
    all_lines: List[str] = []

    for channel in channels:
        for vtt_path in download_subtitles(channel, args.tmp_dir):
            all_lines.extend(vtt_to_lines(vtt_path))

    cleaned = sorted(set(all_lines))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(cleaned), encoding="utf-8")

    meta = {"channels": len(channels), "lines": len(cleaned), "output": str(args.out)}
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
