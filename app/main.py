from __future__ import annotations

import io
import json
import logging
import os
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.asr_engine import ASREngine, to_srt

app = FastAPI(title="Taiwanese Chinese Audio to Text")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

MODEL_NAME = os.getenv("ASR_MODEL", "large-v3")
DEVICE = os.getenv("ASR_DEVICE", "cpu")
COMPUTE_TYPE = os.getenv("ASR_COMPUTE_TYPE", "int8")

engine = ASREngine(
    model_name=MODEL_NAME,
    device=DEVICE,
    compute_type=COMPUTE_TYPE,
    slang_path=Path("app/data/tw_slang_map.json"),
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "segments": None,
            "srt": None,
            "filename": None,
            "txt": None,
            "json_text": None,
            "error": None,
            "profile": "balanced",
            "max_segment_duration": 8.0,
            "stats": None,
        },
    )


@app.post("/transcribe", response_class=HTMLResponse)
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    profile: str = Form("balanced"),
    max_segment_duration: float = Form(8.0),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".wav", ".mp3"}:
        raise HTTPException(status_code=400, detail="只支援 WAV / MP3")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="檔案是空的")
    max_segment_duration = min(max(2.0, max_segment_duration), 8.0)

    try:
        segments = engine.transcribe(
            io.BytesIO(data),
            file.filename or "audio.wav",
            profile=profile,
            max_segment_duration=max_segment_duration,
        )
        srt_text = to_srt(segments)
    except Exception as e:  # noqa: BLE001
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "segments": None,
                "srt": None,
                "filename": None,
                "txt": None,
                "json_text": None,
                "error": f"辨識失敗：{e}",
                "profile": profile,
                "max_segment_duration": max_segment_duration,
                "stats": None,
            },
            status_code=500,
        )

    plain_text = "\n".join([seg["text"] for seg in segments])
    stats = {
        "segment_count": len(segments),
        "profile": profile,
        "max_segment_duration": max_segment_duration,
    }

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "segments": segments,
            "srt": srt_text,
            "filename": f"{Path(file.filename or 'output').stem}.srt",
            "txt": plain_text,
            "json_text": json.dumps(segments, ensure_ascii=False, indent=2),
            "error": None,
            "profile": profile,
            "max_segment_duration": max_segment_duration,
            "stats": stats,
        },
    )


@app.post("/download_srt")
async def download_srt(srt: str = Form(...), filename: str = Form("output.srt")):
    return PlainTextResponse(
        content=srt,
        media_type="application/x-subrip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/download_txt")
async def download_txt(txt: str = Form(...), filename: str = Form("output.txt")):
    return PlainTextResponse(
        content=txt,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
