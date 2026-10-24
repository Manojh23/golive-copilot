"""Discover available model IDs without printing API credentials."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from backend.llm import available_models
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
async def main():
    try:
        for model in sorted(await available_models()):print(model)
    except RuntimeError as exc:
        print(str(exc),file=sys.stderr);sys.exit(1)
asyncio.run(main())
