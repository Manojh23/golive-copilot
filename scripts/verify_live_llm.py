"""Optional paid-provider smoke test; needs your configured key and quota."""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from backend import llm
load_dotenv(Path(__file__).resolve().parents[1]/'.env')
async def main():
    result,metadata=await llm.generate('Source [example-1]: This is fictional rollout documentation. No training record has been supplied. Return a short answer with that exact source quote and chunk ID example-1. Do not invent any other fact.',llm.AnswerOutput)
    assert result.citations and result.citations[0].chunk_id=='example-1'
    print('Live response received and schema validated. Model:',metadata['model'])
    print('Token metadata:',metadata['usage'])
    print('This verifies connectivity and structured output, not clinical or semantic accuracy.')
asyncio.run(main())
