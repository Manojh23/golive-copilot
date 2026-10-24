#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
server_port="${PORT:-8000}"
server_host="127.0.0.1"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --port) server_port="$2"; shift 2 ;;
    --host) server_host="$2"; shift 2 ;;
    *) shift ;;
  esac
done
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi
exec .venv/bin/python -m uvicorn backend.app:app --host "$server_host" --port "$server_port"
