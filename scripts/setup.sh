#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 -c 'import sys; assert sys.version_info >= (3,11), "Python 3.11+ is required"'
node -e 'const [major,minor]=process.versions.node.split(".").map(Number); if(major<22 || (major===22 && minor<12)) { console.error("Node 22.12+ is required"); process.exit(1); }'
python3 -m venv .venv
if [ -s requirements.lock.txt ]; then
  .venv/bin/python -m pip install -r requirements.lock.txt
else
  .venv/bin/python -m pip install -r requirements.txt
fi
npm ci --no-audit --no-fund
npm run build
if [ ! -f .env ]; then cp .env.example .env; fi
printf '\nReady. Run: npm run dev\nOpen: http://localhost:8000\nOptional: configure GEMINI_API_KEY in .env before restarting.\n'
