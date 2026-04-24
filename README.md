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

先切到專案資料夾（**這步沒做就會找不到 `requirements.txt`**）：

```bash
cd /workspace/game-assets
pwd
ls
```

你應該會看到 `requirements.txt` 出現在 `ls` 結果中，再執行：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> 如果你不是把專案放在 `/workspace/game-assets`，請改成你自己的資料夾路徑。

## 2) 啟動

### 一鍵啟動（建議）

```bash
bash run_web.sh
```

這個腳本會自動：
- 建立 `.venv`（若尚未建立）
- 安裝 `requirements.txt` 套件
- 檢查 `ffmpeg`
- 啟動網頁服務 `http://127.0.0.1:8000`

### 手動啟動

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

開啟：`http://localhost:8000`

## 快速上手（實際操作）

1. 先依照上方完成安裝與啟動。
2. 用瀏覽器打開 `http://localhost:8000`。
3. 點「上傳音檔」選擇 `wav` 或 `mp3`。
4. 按「開始辨識」。
5. 頁面會顯示：
   - 每段文字對應的開始/結束時間
   - 可直接檢視的 SRT 內容
6. 按「下載 SRT」即可下載字幕檔。

### GPU 建議啟動方式（較快）

```bash
ASR_DEVICE=cuda ASR_COMPUTE_TYPE=float16 uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 常見問題

- **Q: 為什麼第一次跑很慢？**  
  A: `large-v3` 初次會載入大模型，第一次請求通常較久。
- **Q: 記憶體不夠怎麼辦？**  
  A: 將模型改成較小版本，例如：`ASR_MODEL=medium`。
- **Q: `mp3` 讀不到？**  
  A: 請確認本機已安裝 `ffmpeg`（`pydub` 轉檔會使用它）。

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
