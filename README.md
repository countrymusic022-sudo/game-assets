# Taiwanese Chinese Audio-to-Text (SRT) Web App

這個專案提供一個「中文為主、偏台灣口語」的 Audio-to-Text 系統，支援：

- 上傳音檔（`wav` / `mp3`）
- 自動語音辨識（中文）
- 自動分段（段落 + 時間軸）
- 匯出並下載 `SRT` 字幕
- 可選：匯入台灣流行用語字典做後處理修正
- 可選：蒐集 YouTube 字幕語料，建立台灣語感參考語料

> 核心辨識模型預設使用 `faster-whisper`（`large-v3`），可依硬體切換到 `medium`。

## 1) 安裝

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) 啟動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

開啟：`http://localhost:8000`

## 3) 功能說明

### Web 介面

- 音檔上傳（`wav` / `mp3`）
- 顯示辨識結果（含時間軸）
- 下載 `SRT`

### 台灣語感後處理

- `app/data/tw_slang_map.json` 可維護常見口語詞替換
- 會在不破壞原句意前提下做輕量修正

### YouTube 字幕語料蒐集（可選）

你可以準備台灣前百大 YouTuber 的頻道清單，執行：

```bash
python scripts/build_tw_corpus.py --channels-file channels.txt --out data/tw_youtube_corpus.txt
```

- `channels.txt` 每行一個頻道 URL 或 `@handle`
- 腳本會嘗試抓取可用字幕（含自動字幕），並整理成純文字語料
- 這份語料可做後續語言模型微調、詞頻統計、口語辭典擴充

## 4) 架構

- `app/main.py`：FastAPI 路由、檔案上傳、結果頁與下載
- `app/asr_engine.py`：Whisper 推論、分段策略、SRT 產生
- `app/text_postprocess.py`：台灣口語詞修正、段落整理
- `scripts/build_tw_corpus.py`：YouTube 字幕語料蒐集工具

## 5) 備註

- 初次載入 `large-v3` 可能較慢，且需較高記憶體。
- 建議有 NVIDIA GPU 時使用 `--device cuda --compute-type float16`。
- 僅供合法、取得授權之音訊與字幕資料使用。
