import asyncio
import json

import httpx
import pytest

from backend import llm


def wire(monkeypatch, handler):
    monkeypatch.setenv('GEMINI_API_KEY', 'test-only-secret')
    monkeypatch.setenv('GEMINI_MODEL', 'test-flash')
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kw: original(
        transport=httpx.MockTransport(handler), **kw))
    async def no_wait(_):
        pass
    monkeypatch.setattr(llm.asyncio, 'sleep', no_wait)


def success():
    return httpx.Response(200, json={'candidates': [{'content': {'parts': [
        {'text': json.dumps({'answer': 'Training is unverified.', 'citations': []})}
    ]}}]})


def test_timeout_then_success_preserves_schema(monkeypatch):
    calls = []
    def handler(request):
        calls.append(request)
        assert request.extensions['timeout']['read'] == 120
        payload = json.loads(request.content)
        assert payload['generationConfig']['responseJsonSchema']['type'] == 'object'
        assert 'temperature' not in payload['generationConfig']
        if len(calls) == 1:
            raise httpx.ReadTimeout('test', request=request)
        return success()
    wire(monkeypatch, handler)
    result, meta = asyncio.run(llm.generate('test', llm.AnswerOutput))
    assert result.answer == 'Training is unverified.'
    assert len(calls) == 2 and meta['model'] == 'test-flash'


def test_persistent_timeout_is_bounded_and_redacted(monkeypatch):
    calls = []
    def handler(request):
        calls.append(request)
        raise httpx.ReadTimeout('test-only-secret', request=request)
    wire(monkeypatch, handler)
    with pytest.raises(RuntimeError, match='Stopped after 2 attempts') as exc:
        asyncio.run(llm.generate('test', llm.AnswerOutput))
    assert len(calls) == 2 and 'test-only-secret' not in str(exc.value)


def test_auth_error_not_retried_or_leaked(monkeypatch):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(403, json={'error': 'test-only-secret'})
    wire(monkeypatch, handler)
    with pytest.raises(RuntimeError, match='Access denied') as exc:
        asyncio.run(llm.generate('test', llm.AnswerOutput))
    assert len(calls) == 1 and 'test-only-secret' not in str(exc.value)


def test_busy_response_retried(monkeypatch):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(503) if len(calls) == 1 else success()
    wire(monkeypatch, handler)
    asyncio.run(llm.generate('test', llm.AnswerOutput))
    assert len(calls) == 2


def test_model_discovery_pages_and_filters(monkeypatch):
    monkeypatch.delenv('GEMINI_MODEL', raising=False)
    def handler(request):
        if request.url.params.get('pageToken') == 'second':
            return httpx.Response(200, json={'models': [{'name': 'models/text-flash',
                'supportedGenerationMethods': ['generateContent']}]})
        return httpx.Response(200, json={'models': [{'name': 'models/embedding',
            'supportedGenerationMethods': ['embedContent']}], 'nextPageToken': 'second'})
    wire(monkeypatch, handler)
    assert asyncio.run(llm.available_models()) == ['text-flash']


def test_invalid_timeout_rejected(monkeypatch):
    monkeypatch.setenv('GEMINI_TIMEOUT_SECONDS', 'nan')
    with pytest.raises(RuntimeError, match='30 to 300'):
        llm.read_timeout()
