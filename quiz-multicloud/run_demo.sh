#!/usr/bin/env bash
# Run the QuizCloud demo locally (macOS / Linux). Usage: ./run_demo.sh   (add --reset to wipe demo data)
set -euo pipefail
cd "$(dirname "$0")"

PY=$(command -v python3 || command -v python || true)
if [ -z "$PY" ]; then
  echo "[!] Chưa cài Python 3. Tải tại https://www.python.org/downloads/ rồi chạy lại."
  exit 1
fi

if [ "${1:-}" = "--reset" ]; then
  rm -rf web/instance
  echo "Đã xoá dữ liệu demo."
fi

if [ ! -x .venv/bin/python ]; then
  echo "[1/3] Tạo môi trường ảo .venv ..."
  "$PY" -m venv .venv
fi

echo "[2/3] Cài thư viện (lần đầu mất khoảng 1 phút) ..."
.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements-local.txt

cd web
if [ ! -f instance/quiz.db ]; then
  echo "[3/3] Tạo dữ liệu mẫu ..."
  ../.venv/bin/python -m flask --app app init-db --demo
fi

URL="http://127.0.0.1:5000"
echo
echo "  QuizCloud đang chạy tại $URL  (Ctrl+C để tắt)"
echo
( sleep 3; (command -v open >/dev/null && open "$URL") || (command -v xdg-open >/dev/null && xdg-open "$URL") || true ) >/dev/null 2>&1 &
exec ../.venv/bin/python -m flask --app app run --port 5000
