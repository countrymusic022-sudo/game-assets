#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] 找不到 python3，請先安裝 Python 3.10+"
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "[INFO] 建立虛擬環境 .venv"
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[INFO] 安裝/更新套件"
pip install -r requirements.txt

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[WARN] 尚未安裝 ffmpeg，MP3 可能無法轉檔。"
  echo "       macOS 可執行：brew install ffmpeg"
fi

echo "[INFO] 啟動服務中：http://127.0.0.1:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000
